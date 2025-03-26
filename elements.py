from ableton.v3.control_surface import MIDI_NOTE_TYPE, ElementsBase, MapMode
from functools import partial

CHANNEL = 14



class Elements(ElementsBase):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        add_button_matrix = partial(
            (self.add_button_matrix),
            msg_type=MIDI_NOTE_TYPE,
            led_channel=0,
            is_rgb=True,
            is_momentary=True,
        )

        add_button_matrix([range(44, 46)], base_name="Solo_Buttons", channels=CHANNEL)
        add_button_matrix([range(40, 42)], base_name="Mute_Buttons", channels=CHANNEL)
        add_button_matrix([range(52, 54)], base_name="TrackSelect_Buttons", channels=CHANNEL)

        self.add_encoder_matrix(
            [range(4, 6)],
            base_name="SendA_Encoder_Matrix",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(8, 10)],
            base_name="SendB_Encoder_Matrix",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(12, 14)],
            base_name="SendC_Encoder_Matrix",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_button(12, "play_button", channel=CHANNEL, msg_type=MIDI_NOTE_TYPE)
        self.add_button(15, "stop_button", channel=CHANNEL, msg_type=MIDI_NOTE_TYPE)


  