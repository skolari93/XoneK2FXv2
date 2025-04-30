
from ableton.v3.base import listenable_property
from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import ButtonControl, StepEncoderControl
from ableton.v3.control_surface.display import Renderable
import logging, threading
logger = logging.getLogger("XoneK2FXv2")
class NoteSettingsComponent(Component, Renderable):
    duration_range_string = listenable_property.managed('-')
    duration_encoder = StepEncoderControl(num_steps=64)
    duration_fine_encoder = StepEncoderControl(num_steps=64)
    transpose_encoder = StepEncoderControl(num_steps=64)
    transpose_octave_encoder = StepEncoderControl(num_steps=64)
    nudge_encoder = StepEncoderControl(num_steps=64)
    shift_length_button = ButtonControl(color=None)
    cursor_skin = {'color': 'NoteSettings.CursorButton', 'pressed_color': 'NoteSettings.CursorButtonPressed'}
    nudge_left_button = ButtonControl(**cursor_skin)
    nudge_right_button = ButtonControl(**cursor_skin)

    def __init__(self, note_editor, *a, **k):
        super().__init__(*a, name='Note_Settings', **k)
        self._note_editor = note_editor
        self.register_slot(self._note_editor, self._update_from_property_ranges, 'pitch_provider')
        self.register_slot(self._note_editor, self._update_from_property_ranges, 'active_steps')
        self.register_slot(self._note_editor, self._update_from_property_ranges, 'clip_notes')

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

    @nudge_left_button.pressed
    def nudge_left_button(self, _):
        self._nudge_notes((-1))

    @nudge_right_button.pressed
    def nudge_right_button(self, _):
        self._nudge_notes(1)

    def _nudge_notes(self, delta):
        self._note_editor.set_nudge_offset(0.0125*delta)
        self.notify(self.notifications.Notes.nudge, self._note_editor.get_nudge_offset_range_string())

    def _transpose_notes(self, amount):
        self._note_editor.set_pitch_offset(amount)
        self.notify(self.notifications.Notes.transpose)

    def _update_from_property_ranges(self):
        values = self._note_editor.get_note_property_ranges()
        can_enable = self._note_editor.pitch_provider is not None and values is not None
        is_polyphonic = can_enable and self._note_editor.pitch_provider.is_polyphonic
        pitch_min, pitch_max = values.get('pitch', (0, 0))
        # self.transpose_up_button.enabled = is_polyphonic and (pitch_min!= pitch_max or pitch_max!= 127)
        # self.transpose_down_button.enabled = is_polyphonic and (pitch_min!= pitch_max or pitch_max!= 0)

        nudge_offset = self._note_editor.step_length *0.0125#self._note_editor.step_length + 0.1
        #nudge_offset = 0
        self.nudge_left_button.enabled = can_enable and self._note_editor.can_nudge_by_offset(-nudge_offset)
        self.nudge_right_button.enabled = can_enable and self._note_editor.can_nudge_by_offset(nudge_offset)
        # HERE
        self.duration_range_string = self._note_editor.get_duration_range_string()
        if self.shift_length_button.is_pressed:
            self._note_editor._show_tied_steps()