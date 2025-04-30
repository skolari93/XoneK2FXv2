import math
from sys import maxsize
from Live.Clip import MidiNoteSpecification
from ableton.v3.base import depends, clamp
from ableton.v3.control_surface import RelativeInternalParameter
from ableton.v3.control_surface.components.bar_based_sequence import NoteEditorComponent as NoteEditorComponentBase
from ableton.v3.control_surface.components.note_editor import get_notes
from ableton.v3.live import liveobj_valid, action
from .step_color_manager import StepColorManager
import threading
import logging
# K2 specific
STEP_TRANSLATION_CHANNEL = 3
logger = logging.getLogger("XoneK2FXv2")

class NoteEditorComponent(NoteEditorComponentBase):
    @depends(volume_parameters=None)
    def __init__(self, volume_parameters=None, note_length_mode=True, *a, **k):
        super().__init__(translation_channel=STEP_TRANSLATION_CHANNEL, *a, **k)
        self._step_start_times = []
        self._step_color_manager = self.register_disconnectable(StepColorManager(update_method=self._update_editor_matrix))
        self._step_color_manager.set_clip(self._clip)
        self._volume_parameters = volume_parameters
        self._velocity_offset_parameter = self.register_disconnectable(RelativeInternalParameter(name='Velocity'))
        self.register_slot(self._velocity_offset_parameter, self.set_velocity_offset, 'delta')
        
        # Track which steps are selected for note length
        self._note_length_mode = note_length_mode
        self._held_pad = None
        self._held_pad_index = None
        self._revert_timer = None
        
        # Dictionary to track active step states
        self._active_step_states = {}

    @property
    def step_color_manager(self):
        return self._step_color_manager

    @property
    def step_start_times(self):
        return self._step_start_times

    def set_velocity_offset(self, delta):
        # Set the new value
        self._modify_note_property('_velocity_offset', 8*delta) #factor 8 is k2 specific

    def get_durations_from_step(self, step):
        notes = self._time_step(step[0]).filter_notes(self._clip_notes)
        return [note.duration for note in notes]
    

    def set_clip(self, clip):
        super().set_clip(clip)
        if hasattr(self, '_step_color_manager'):
            self._step_color_manager.set_clip(self._clip)

    def notify_clip_notes(self):
        if liveobj_valid(self._clip) and self._pitches:
            try:
                from_pitch = min(self._pitches)
                pitch_span = max(self._pitches) - from_pitch + 1
                notes_dict = self._clip.get_notes_extended(from_pitch, pitch_span, 0.0, float(maxsize))
                # Extract start times from note dicts
                self._step_start_times = sorted(list({note.start_time for note in notes_dict}))
            except Exception as e:
                logger.error(f"Error using get_notes_extended: {str(e)}")
                self._step_start_times = []
        super().notify_clip_notes()

    # @property
    # def active_steps(self):
    #     """Return the current active steps for external components to reference"""
    #     return self._active_steps

    def _on_pad_pressed(self, pad):
        """
        Handle pad press events for note editing.
        The first pad defines note start, the second defines note length.
        """
        if self._note_length_mode:
            if not self.is_enabled():
                return

            if not self._has_clip():
                self.set_clip(self._sequencer_clip.create_clip())
                self._update_from_grid()

            if not self._can_press_or_release_step(pad):
                return

            x2, y2 = pad.coordinate  # Current pad (second press)
            
            if self._held_pad is not None and self._held_pad != pad:
                # The pad that was previously held (first press)
                x1, y1 = self._held_pad.coordinate

                # Adjusted for transposed matrix (assuming the matrix is transposed)
                time1 = (y1 + x1 * self.matrix.width) * self.step_length
                time2 = (y2 + x2 * self.matrix.width) * self.step_length

                # Calculate start and end times
                start_time = time1
                end_time = time2 + self.step_length  # Ensure the full second pad is included

                # Duration is simply the difference between start and end times
                duration = end_time - start_time

                # Set the note's duration property
                if duration > 0:
                    self._set_note_property("duration", duration)
                    self._show_tied_steps_temporary()
                    # probably there needs to be something à la. notify duration change()
                else:
                    self._create_note_repeats(end_time- self.step_length, abs(duration))
            else:
                # First pad: remember it
                self._held_pad = pad

                # Mark the pad as active and refresh the steps
                pad.is_active = True
                self._refresh_active_steps()
                
                # Call the parent class's function
                super()._on_pad_pressed(pad)
                
                # Add velocity parameter for the pad (if required)
                self._volume_parameters.add_parameter(pad, self._velocity_offset_parameter)
        else:
            super()._on_pad_pressed(pad)
            self._volume_parameters.add_parameter(pad, self._velocity_offset_parameter)

    def _refresh_active_steps(self):
        """Refresh the _active_steps property and notify listeners"""
        old_active_steps = self._active_steps.copy() if hasattr(self, '_active_steps') else []
        super()._refresh_active_steps()
        
        # If active steps changed, notify
        if old_active_steps != self._active_steps:
            self.notify_active_steps()
        
    def _on_pad_released(self, pad, *a, **k):
        """Handle pad release events and clean up references"""
        super()._on_pad_released(pad, *a, **k)
        self._volume_parameters.remove_parameter(pad, force=True)
        
        # Clear held pad reference if this is the held pad
        if pad == self._held_pad:
            self._held_pad = None
            self._held_pad_index = None

    def _set_note_property(self, note_property, value):
        if self.is_enabled():
            if self._active_steps and self._has_clip() and self._can_edit():
                self.set_step_notes_property(self._active_steps, note_property, value)
                self._clip.apply_note_modifications(self._clip_notes)
                self._update_editor_matrix()
                self.notify_active_steps()

    def set_step_notes_property(self, steps, property_name, value):
        notes = self._clip_notes
        for step in steps:
            time_step = self._time_step(self._get_step_start_time(step))
            for note in notes:
                self._set_single_note_property(time_step, property_name, value, note)

    def _set_single_note_property(self, time_step, property_name, value, note):
        if time_step.includes_time(note.start_time):
            if property_name == "pitch":
                note.pitch = clamp(value, 0, 127)
            elif property_name == "velocity":
                note.velocity = clamp(value, 1, 127)
            elif property_name == "duration":
                note.duration = max(time_step.length * 0.1, value)
            elif property_name == "start_time":
                note.start_time = time_step.clamp(value)
            else:
                raise ValueError(f"Unsupported property: {property_name}")

    @staticmethod
    def _modify_duration(time_step, duration_offset, note):
        threshold = 0.1
        # Ensure the duration doesn't go below the threshold
        if note.duration < threshold:
            note.duration = threshold
        else:
            # Increase duration, respecting the threshold and the offset
            note.duration = max(note.duration + duration_offset, threshold)

            # Special case: if the duration is exactly threshold and the offset is positive, set it to 0.25
            if note.duration == threshold and duration_offset > 0:
                note.duration = 0.25

    def _visible_page(self):
        """Returns the current page number (0-indexed) based on the current page_time.
        
        Returns:
            int: The current page number (0, 1, 2, etc.)
        """
        if self._page_time <= 0:
            return 0
        
        page_length = self.page_length
        if page_length <= 0:
            return 0
            
        return int(self._page_time / page_length)
    
    def _get_alternate_color_for_step(self, index, visible_steps):
        visible_page = self._visible_page()
        clip_notes = visible_steps[index].filter_notes(self._clip_notes)

        return self._step_color_manager.get_color_for_step(index, visible_steps, clip_notes, visible_page=visible_page)
    
    # K2 specific hardcoded
    def set_matrix(self, matrix):
        self.matrix.set_control_element(matrix)
        
        if matrix:
            for index, button in enumerate(self.matrix):
                # Determine which column this button belongs to
                button_column = index % 8
                
                # Set channel based on column:
                button.channel = 4 if button_column < 4 else 5 # EACH DEVICE NEEDS A SEPERATE TRANSLATION CHANNEL
        self._update_editor_matrix()

    def _show_tied_steps(self):
        colors = {}
        step_length = self.step_length
        for step in self.active_steps:
            durations = self.get_durations_from_step(step)
            if not durations:
                continue
            num_steps = max(durations) / step_length
            step_index = int(step[0] / step_length)
            step_index = step_index % self.step_count # it should be 32 for drum...BUG
            # Always color the starting step
            if num_steps > 1:
                colors[step_index] = 'NoteEditor.StepTied'
            else:
                colors[step_index] = 'NoteEditor.StepPartiallyTied'
            
            # Color the following tied steps
            for i in range(1, int(num_steps)):
                colors[step_index + i] = 'NoteEditor.StepTied'
            
            # If it does not exactly cover a whole number of steps, the last step is partially tied
            if not num_steps.is_integer():
                colors[step_index + int(num_steps)] = 'NoteEditor.StepPartiallyTied'
                
        self.step_color_manager.show_colors(colors)

    def _show_tied_steps_temporary(self):
        # Erst Farben zeigen
        self._show_tied_steps()

        # Wenn schon ein Timer läuft, abbrechen
        if self._revert_timer is not None:
            self._revert_timer.cancel()

        # Neuen Timer starten
        self._revert_timer = threading.Timer(0.1, self.step_color_manager.revert_colors) 
        self._revert_timer.start()

    def _create_note_repeats(self, start_time, total_duration):
        """
        Create multiple repeated notes from start_time spanning total_duration.
        
        Args:
            start_time: The time to start placing notes
            total_duration: The total length to fill with notes
        """
        if not self._has_clip() or not self._can_edit():
            return
            
        # Calculate how many steps are covered
        steps_covered = int(total_duration / self.step_length)
        
        # Ensure we create at least one note
        steps_covered = max(1, steps_covered)
        
        # Remove any existing notes in the region
        for pitch in self._pitches:
            self._clip.remove_notes_extended(
                from_time=start_time,
                from_pitch=pitch,
                time_span=total_duration,
                pitch_span=1
            )
        
        # Create ratchet notes
        new_notes = []
        
        # Default settings
        velocity = 127 if hasattr(self, '_full_velocity') and self._full_velocity.enabled else 100
        
        # Create a note at each step
        for step_num in range(steps_covered+1):
            step_start_time = start_time + (step_num * self.step_length)
            
            for pitch in self._pitches:
                # Create a note that exactly fills each step
                note = MidiNoteSpecification(
                    pitch=pitch,
                    start_time=step_start_time,
                    duration=self.step_length,
                    velocity=velocity,
                    mute=False
                )
                new_notes.append(note)
        
        # Add all the notes at once
        if new_notes:
            self._clip.add_new_notes(tuple(new_notes))
            self._clip.deselect_all_notes()
            
            # Extend loop if necessary to see the ratchets
            action.extend_loop_for_region(self._clip, start_time, total_duration)
            
            # Update display
            self.__on_clip_notes_changed()

    def _create_ratchet_notes(self, start_time, duration, divisions):
        """
        Create multiple repeated notes from start_time spanning total_duration,
        where the original note is divided into the specified number of divisions.
    
        Args:
            start_time: The time to start placing notes
            duration: The duration of the original note
            divisions: The number of divisions to create (1 = original note, 2 = two notes, etc.)
        """
        if not self._has_clip() or not self._can_edit():
            return
        #duration = 0.25
        if divisions <= 0:
            divisions = 1
    
        # Remove any existing notes in the region for selected pitches
        for pitch in self._pitches:
            self._clip.remove_notes_extended(
                from_time=start_time,
                from_pitch=pitch,
                time_span=duration,
                pitch_span=1
            )
    
        # Create ratchet notes
        new_notes = []
    
        # Default settings
        velocity = 127 if hasattr(self, '_full_velocity') and self._full_velocity.enabled else 100
    
        # Calculate the duration of each division
        division_duration = duration / divisions
    
        # Create a note for each division
        for div_num in range(divisions):
            div_start_time = start_time + (div_num * division_duration)
        
            for pitch in self._pitches:
                # Create a note that fits this division
                note = MidiNoteSpecification(
                    pitch=pitch,
                    start_time=div_start_time,
                    duration=division_duration,
                    velocity=velocity,
                    mute=False
                )
                new_notes.append(note)
    
        # Add all the notes at once
        if new_notes:
            self._clip.add_new_notes(tuple(new_notes))
            self._clip.deselect_all_notes()
        
            # Extend loop if necessary to see the ratchets
            action.extend_loop_for_region(self._clip, start_time, duration)
        
            # Update display
            self.__on_clip_notes_changed()
        logger.debug(f"Ratchet: start={start_time}, duration={duration}, divisions={divisions}")
        logger.debug(f"division_duration={duration/divisions}")

    def set_ratchet_divisions(self, divisions):
        """
        For each active step, remove existing notes and create `divisions` evenly spaced notes
        across the step duration (usually one step = 1/16 note).
        """
        if not self.is_enabled() or not self._active_steps or not self._has_clip() or not self._can_edit():
            return

        MAX_RATCHET_DIVISIONS = 8
        divisions = max(1, min(int(divisions), MAX_RATCHET_DIVISIONS))

        for step in self._active_steps:
            step_start_time = self._get_step_start_time(step)
            step_duration = self.step_length
            step_end_time = step_start_time + step_duration

            # Clear old notes in this step
            for pitch in self._pitches:
                self._clip.remove_notes_extended(
                    from_time=step_start_time,
                    from_pitch=pitch,
                    time_span=step_duration,
                    pitch_span=1
                )

            # Create evenly spaced notes in this step
            division_duration = step_duration / divisions
            new_notes = []

            velocity = 127 if hasattr(self, '_full_velocity') and self._full_velocity.enabled else 100

            for div in range(divisions):
                note_start_time = step_start_time + div * division_duration
                
                # For the last division, ensure its end time doesn't exceed step_end_time
                # by calculating its duration specifically
                if div == divisions - 1:  # Last division
                    note_duration = step_end_time - note_start_time
                else:
                    note_duration = division_duration
                    
                # Ensure we don't have microscopic rounding errors
                note_duration = min(note_duration, step_end_time - note_start_time)
                
                for pitch in self._pitches:
                    note = MidiNoteSpecification(
                        pitch=pitch,
                        start_time=note_start_time,
                        duration=note_duration,
                        velocity=velocity,
                        mute=False
                    )
                    new_notes.append(note)

            if new_notes:
                self._clip.add_new_notes(tuple(new_notes))

        self._clip.deselect_all_notes()
        self.__on_clip_notes_changed()
