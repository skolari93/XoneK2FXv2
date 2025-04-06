from ableton.v3.control_surface import MIDI_NOTE_TYPE, ElementsBase, MapMode
from ableton.v3.control_surface.elements import ButtonElement

from functools import partial
from .k2_button import create_k2_button
CHANNEL = 14

class Elements(ElementsBase):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        self.add_matrix([range(44, 47)], "solo_buttons", channels=CHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_matrix([range(40, 43)], "mute_buttons", channels=CHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_matrix([range(52, 55)], "track_select_buttons", channels=CHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_encoder_matrix(
            [range(4, 7)],
            base_name="send_a_encoders",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(8, 11)],
            base_name="send_b_encoders",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(12, 15)],
            base_name="send_c_encoders",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(16, 19)],
            base_name="volume_faders",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder(19, 'master_volume_fader', channel=CHANNEL, is_feedback_enabled=True, needs_takeover=True, map_mode=MapMode.Absolute)
        self.add_element("master_select_button", create_k2_button, 55, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")

        self.add_element("stop_button", create_k2_button, 15, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="big")
        self.add_element("play_button", create_k2_button, 12, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="big")

