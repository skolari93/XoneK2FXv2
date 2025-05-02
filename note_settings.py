from ableton.v3.base import listenable_property
from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import ButtonControl, StepEncoderControl
from ableton.v3.control_surface.display import Renderable

import logging, threading
from Live.Clip import MidiNoteSpecification
logger = logging.getLogger("XoneK2FXv2")

class NoteSettingsComponent(Component, Renderable):
    duration_range_string = listenable_property.managed('-')
    ratchet_divisions_string = listenable_property.managed('Ratchet: 1')
    
    duration_encoder = StepEncoderControl(num_steps=64)
    duration_fine_encoder = StepEncoderControl(num_steps=64)
    transpose_encoder = StepEncoderControl(num_steps=64)
    transpose_octave_encoder = StepEncoderControl(num_steps=64)
    nudge_encoder = StepEncoderControl(num_steps=64)
    nudge_coarse_encoder = StepEncoderControl(num_steps=64)
    ratchet_encoder = StepEncoderControl(num_steps=64)
    
    shift_length_button = ButtonControl(color=None)
    ratchet_button = ButtonControl(color='NoteSettings.RatchetButton', pressed_color='NoteSettings.RatchetButtonPressed')

    def __init__(self, note_editor, *a, **k):
        super().__init__(*a, name='Note_Settings', **k)
        self._note_editor = note_editor
        self.register_slot(self._note_editor, self._update_from_property_ranges, 'pitch_provider')
        self.register_slot(self._note_editor, self._on_active_steps_changed, 'active_steps')
        self.register_slot(self._note_editor, self._update_from_property_ranges, 'clip_notes')
        
        # Track current ratchet division
        self._current_ratchet_divisions = 1
        self._previous_active_steps_count = 0
        
        self._update_from_property_ranges()

    def set_duration_encoder(self, encoder):
        self.duration_encoder.set_control_element(encoder)

    def set_duration_fine_encoder(self, encoder):
        self.duration_fine_encoder.set_control_element(encoder)

    def set_transpose_encoder(self, encoder):
        self.transpose_encoder.set_control_element(encoder)

    def set_transpose_octave_encoder(self, encoder):
        self.transpose_octave_encoder.set_control_element(encoder)

    def set_nudge_encoder(self, encoder):
        self.nudge_encoder.set_control_element(encoder)

    def set_nudge_coarse_encoder(self, encoder):
        self.nudge_coarse_encoder.set_control_element(encoder)
        
    def set_ratchet_encoder(self, encoder):
        self.ratchet_encoder.set_control_element(encoder)
        
    def set_ratchet_button(self, button):
        self.ratchet_button.set_control_element(button)

    def _on_active_steps_changed(self):
        """
        Monitor changes to active steps and reset ratchet divisions when steps are removed
        """
        if hasattr(self._note_editor, 'active_steps'):
            current_active_steps_count = len(self._note_editor.active_steps)
            
            # If steps were removed (count decreased), reset ratchet divisions
            if current_active_steps_count < self._previous_active_steps_count:
                self._reset_ratchet_divisions()
            
            # Update our saved count for next comparison
            self._previous_active_steps_count = current_active_steps_count
            
        self._update_from_property_ranges()

    def _reset_ratchet_divisions(self):
        """Reset ratchet divisions to 1 (original note)"""
        self._current_ratchet_divisions = 1
        self.ratchet_divisions_string = 'Ratchet: 1'
        # Only notify if component is enabled
        #if self.is_enabled():
            #self.notify(self.notifications.Notes.ratchet, 'Reset ratchet')

    @duration_encoder.value
    def duration_encoder(self, value, _):
        offset = 0.25
        self._note_editor.set_duration_offset(value * offset)
        self._note_editor._show_tied_steps_temporary()

    @duration_fine_encoder.value
    def duration_fine_encoder(self, value, _):
        offset = 0.25 * 0.1
        self._note_editor.set_duration_offset(value * offset)
        self._note_editor._show_tied_steps_temporary()

    @shift_length_button.pressed
    def shift_length_button(self, _):
        self._note_editor._show_tied_steps()

    @shift_length_button.released
    def shift_length_button(self, _):
        self._note_editor.step_color_manager.revert_colors()

    @transpose_encoder.value
    def transpose_encoder(self, value, _):
        offset = 1
        self._transpose_notes(value * offset)

    @transpose_octave_encoder.value
    def transpose_octave_encoder(self, value, _):
        offset = 12
        self._transpose_notes(value * offset)

    @nudge_encoder.value
    def nudge_encoder(self, value, _):
        self._nudge_notes(value)

    @nudge_coarse_encoder.value
    def nudge_encoder(self, value, _):
        self.shift_notes_by_step(value)

    @ratchet_encoder.value
    def ratchet_encoder(self, value, _):
        # Determine the increment based on encoder direction
        increment = 1 if value > 0 else -1
        
        # Update current ratchet divisions
        self._current_ratchet_divisions = max(1, self._current_ratchet_divisions + increment)
        
        # Apply the ratchet divisions to selected steps
        self._note_editor.set_ratchet_divisions(self._current_ratchet_divisions)
        
        # Update display
        self.ratchet_divisions_string = f'Ratchet: {self._current_ratchet_divisions}'
        #self.notify(self.notifications.Notes.ratchet, self.ratchet_divisions_string)
    
    @ratchet_button.pressed
    def ratchet_button(self, _):
        # Reset ratchet divisions to 1 (original note)
        self._reset_ratchet_divisions()
        self._note_editor.set_ratchet_divisions(1)
        #self.notify(self.notifications.Notes.ratchet, 'Reset ratchet')

    def _nudge_notes(self, delta):
        offset = 0.0125*delta
        self._note_editor.set_nudge_offset(offset)
        self.notify(self.notifications.Notes.nudge, self._note_editor.get_nudge_offset_range_string())

    def _transpose_notes(self, amount):
        self._note_editor.set_pitch_offset(amount)
        self.notify(self.notifications.Notes.transpose)

    def _update_from_property_ranges(self):
        values = self._note_editor.get_note_property_ranges()
        can_enable = self._note_editor.pitch_provider is not None and values is not None
        is_polyphonic = can_enable and self._note_editor.pitch_provider.is_polyphonic
        pitch_min, pitch_max = values.get('pitch', (0, 0))
        
        self.duration_range_string = self._note_editor.get_duration_range_string()
        if self.shift_length_button.is_pressed:
            self._note_editor._show_tied_steps()

    def shift_notes_by_step(self, value):
        """
        Shifts selected notes by exactly one step, bypassing the nudge mechanism.
        Direction is determined by value: positive for forward, negative for backward.
        
        Args:
            value: Direction value (-1 for backward, 1 for forward)
        """
        if not self._note_editor._has_clip() or not self._note_editor._active_steps:
            return
        
        # Don't do anything if value is 0
        if value == 0:
            return
            
        # Determine direction based on value sign
        forward = value > 0
        
        clip = self._note_editor._clip
        step_length = self._note_editor.step_length
        
        # Calculate the offset (positive for forward, negative for backward)
        offset = step_length if forward else -step_length
        
        # 1. Collect all notes from active steps
        active_notes = []
        for step in self._note_editor._active_steps:
            time = self._note_editor._get_step_start_time(step)
            time_step = self._note_editor._time_step(time)
            step_notes = time_step.filter_notes(self._note_editor._clip_notes)
            active_notes.extend(step_notes)
        
        if not active_notes:
            return
        
        # 2. Create new specifications for the shifted notes
        from Live.Clip import MidiNoteSpecification
        new_notes = []
        
        for note in active_notes:
            # Ensure we're not shifting notes to negative time
            new_start_time = max(0, note.start_time + offset)
            
            # Create the new note with shifted position
            new_note = MidiNoteSpecification(
                pitch=note.pitch,
                start_time=new_start_time,
                duration=note.duration,
                velocity=note.velocity,
                mute=note.mute
            )
            new_notes.append(new_note)
        
        # 3. Delete the original notes from each step
        for step in self._note_editor._active_steps:
            self._note_editor._delete_notes_in_step(step)
        
        # 4. Add the new notes to the clip
        if new_notes:
            clip.add_new_notes(tuple(new_notes))
            
        # 5. Update the UI
        self._note_editor._NoteEditorComponent__on_clip_notes_changed()
        
        # Notify the user
        direction = "forward" if forward else "backward"
        self.notify(self.notifications.Notes.nudge, f"Shifted notes {direction} by one step")