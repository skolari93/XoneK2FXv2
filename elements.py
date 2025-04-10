from ableton.v3.control_surface import MIDI_NOTE_TYPE, ElementsBase, MapMode, PrioritizedResource
from ableton.v3.control_surface.elements import ButtonElement

from functools import partial
from .k2_button import create_k2_button
CHANNEL = 14


class Elements(ElementsBase):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        self.add_element("shift_button", create_k2_button, 12, resource_type=PrioritizedResource, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="big")

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

        self.add_encoder_matrix(
            [range(0, 3)],
            base_name="gain_encoders",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.AccelTwoCompliment,
        )
        self.add_modified_control(control=self.gain_encoders, modifier=self.shift_button)

        # master track
        self.add_encoder_matrix(
            [[19]],
            base_name="master_volume_fader",
            channels=CHANNEL,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )
        self.add_matrix([[55]], "master_track_select_button", channels=CHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        # cue
        self.add_encoder(11, 'cue_encoder', channel=CHANNEL, is_feedback_enabled=True, needs_takeover=True, map_mode=MapMode.Absolute)

        # Tempo
        self.add_encoder(3, 'tempo_encoder', channel=CHANNEL, is_feedback_enabled=True, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment)
        self.add_modified_control(control=(self.tempo_encoder), modifier=(self.shift_button))

        # crossfader
        self.add_encoder(15, 'crossfader_encoder', channel=CHANNEL, is_feedback_enabled=True, needs_takeover=True, map_mode=MapMode.Absolute)
        self.add_matrix([range(48, 51)], "crossfade_assign_buttons", channels=CHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")

        # transport
        self.add_element("play_button", create_k2_button, 24, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_element("stop_button", create_k2_button, 25, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_element("automation_arm_button", create_k2_button, 28, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_element("automation_re-enable_button", create_k2_button, 29, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")

        # recording
        self.add_element("record_button", create_k2_button, 26, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_element("session_record_button", create_k2_button, 30, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")

        # scene select
        self.add_encoder(21, 'scene_select_encoder', channel=CHANNEL, is_feedback_enabled=True, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment)
        self.add_button(14, 'launch_scene_button', channel=CHANNEL, msg_type=MIDI_NOTE_TYPE)

        self.add_matrix([[39,35,31]], "scene_launch_buttons", channels=CHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_element("stop_all_clips_button", create_k2_button, 27, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")

        # variations
        self.add_button(13, 'variations_launch_button', channel=CHANNEL, msg_type=MIDI_NOTE_TYPE)
        self.add_element("variations_recall_button", create_k2_button, 15, channel=CHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="big")
        self.add_modified_control(control=(self.variations_recall_button), modifier=(self.shift_button))
        self.add_modified_control(control=(self.variations_launch_button), modifier=(self.shift_button))
        self.add_encoder(20, 'variations_select_encoder', channel=CHANNEL, is_feedback_enabled=True, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment)
        
        # scene nav
        self.add_modified_control(control=(self.scene_select_encoder), modifier=(self.shift_button))