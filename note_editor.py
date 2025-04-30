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
        self._note_length_mode =note_length_mode
        self._held_pad = None
        self._held_pad_index = None
        self._revert_timer = None  


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
    

    def get_duration_range_string(self):
        return self._get_property_range_string('duration', lambda value_range: (v + self.step_length for v in value_range), str_fmt='{:.1f}'.format)

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

    # def _show_velocity(self):
    #     """Display velocity as a visual bar of illuminated steps"""
    #     colors = {}
        
    #     # Get average or first velocity
    #     velocities = self.get_velocities()
    #     velocity = 0
    #     if velocities:
    #         velocity = sum(velocities) / len(velocities) if velocities else 0
        
    #     # Normalize velocity (0-127) to 0-8 step range
    #     num_steps_on = int((velocity / 127) * 8)
        
    #     for step_index in range(8):
    #         if step_index < num_steps_on:
    #             colors[step_index] = 'NoteEditor.Velocity'  # Active steps
    #         else:
    #             colors[step_index] = 'NoteEditor.StepEmpty'  # Inactive steps
                
    #     self.step_color_manager.show_colors(colors)

    # def _show_velocity_temporary(self):
    #     """Show velocity display temporarily then revert"""
    #     self._show_velocity()
        
    #     # Reset timer if one is already running
    #     if self._revert_timer is not None:
    #         self._revert_timer.cancel()
            
    #     # Set timer to revert colors after 0.3 seconds
    #     self._revert_timer = threading.Timer(0.3, self.step_color_manager.revert_colors)
    #     self._revert_timer.start()
        
    # def show_tied_steps_temporary(self):
    #     """Method to show tied notes temporarily"""
    #     colors = {}
    #     step_length = self.step_length
        
    #     # Find active steps with notes
    #     for step in self.active_steps:
    #         durations = self.get_durations_from_step(step)
    #         if not durations:
    #             continue
                
    #         # Calculate how many steps this note spans
    #         num_steps = max(durations) / step_length
    #         step_index = int(step[0] / step_length)
    #         step_index = step_index % self.step_count
            
    #         # Always color the starting step
    #         if num_steps > 1:
    #             colors[step_index] = 'NoteEditor.StepTied'
    #         else:
    #             colors[step_index] = 'NoteEditor.StepPartiallyTied'
                
    #         # Color the following tied steps
    #         for i in range(1, int(num_steps)):
    #             tied_index = (step_index + i) % self.step_count
    #             colors[tied_index] = 'NoteEditor.StepTied'
                
    #         # If it does not exactly cover a whole number of steps, the last step is partially tied
    #         if not num_steps.is_integer():
    #             partial_index = (step_index + int(num_steps)) % self.step_count
    #             colors[partial_index] = 'NoteEditor.StepPartiallyTied'
                    
    #     self._step_color_manager.show_colors(colors)
    # def get_velocities(self):
    #     """Returns the velocities of the currently selected notes"""
    #     if not liveobj_valid(self._clip) or not self._clip_notes:
    #         return []
        
    #     selected_notes = []
    #     try:
    #         # Use the newer API to get selected notes
    #         if hasattr(self._clip, 'get_selected_notes_extended'):
    #             selected_notes_dict = self._clip.get_selected_notes_extended()
    #             return [note['velocity'] for note in selected_notes_dict.values()]
    #         else:
    #             # Fallback to older API
    #             selected_notes = self._clip.get_selected_notes()
    #             return [note[3] for note in selected_notes]
    #     except Exception as e:
    #         logger.error(f"Error getting velocities: {str(e)}")
    #         return []

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
        Create ratcheting notes (multiple repeated notes) from start_time spanning total_duration.
        
        Args:
            start_time: The time to start placing ratchet notes
            total_duration: The total length to fill with ratchet notes
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