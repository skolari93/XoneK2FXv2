from ableton.v3.control_surface import MIDI_NOTE_TYPE, ElementsBase, MapMode, PrioritizedResource
from .k2_button import create_k2_button

MIXERCHANNEL1 = 12
MIXERCHANNEL2 = 13
FXCHANNEL = 14
IS_FEEDBACK_ENABLED = False

import logging
logger = logging.getLogger("XoneK2FXv2")


def combine_identifier_matrices(ids):
    combined_identifiers = ids + ids
    return combined_identifiers

def repeat_list_three_times(a, b):
    return list(range(a, b)) * 3

def create_duplicated_list(a, b):
    return [range(a, b),range(a, b)]

def create_channel_matrix(channels, num_rows):
    """
    Creates a matrix of channels, repeating each channel value for each row.
    
    :param channels: A list of channel values.
    :param num_rows: Number of rows needed for the matrix.
    :return: A 2D list (matrix) where each row contains repeated channel values.
    """
    return [channels[i % len(channels)] * 4 for i in range(num_rows)]

class Elements(ElementsBase):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        
        # Big buttons
        self.add_element("layout_button", create_k2_button, 12, channel=MIXERCHANNEL1, msg_type=MIDI_NOTE_TYPE, button_type="big")
        self.add_element("duplicate_button", create_k2_button, 15, channel=MIXERCHANNEL1, msg_type=MIDI_NOTE_TYPE, button_type="big") 
        self.add_element("big_3_button", create_k2_button, 12, channel=MIXERCHANNEL2, msg_type=MIDI_NOTE_TYPE, button_type="big") 
        self.add_element("capture_midi_button", create_k2_button, 15, channel=MIXERCHANNEL2, msg_type=MIDI_NOTE_TYPE, button_type="big")
        self.add_element("shift_button", create_k2_button, 12, resource_type=PrioritizedResource, channel=FXCHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="big")
        self.add_element("variations_recall_button", create_k2_button, 15, channel=FXCHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="big") 

        # bottom encoders
        self.add_encoder(20, 'bottom_1_encoder', channel=MIXERCHANNEL1, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment) 
        self.add_encoder(21, 'bottom_2_encoder', channel=MIXERCHANNEL2, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment) 
        self.add_encoder(20, 'bottom_3_encoder', channel=MIXERCHANNEL2, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment) 
        self.add_encoder(21, 'bottom_4_encoder', channel=MIXERCHANNEL2, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment)
        self.add_encoder(20, 'variations_select_encoder', channel=FXCHANNEL, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment)
        self.add_encoder(21, 'scene_select_encoder', channel=FXCHANNEL, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment)

        # push encoder buttons
        self.add_button(13, 'transpose_shift', channel=MIXERCHANNEL1, msg_type=MIDI_NOTE_TYPE)
        self.add_button(14, 'shift_length_button', channel=MIXERCHANNEL1, msg_type=MIDI_NOTE_TYPE)
        self.add_button(13, 'bottom_3_encoder_shift_button', channel=MIXERCHANNEL2, msg_type=MIDI_NOTE_TYPE)
        self.add_button(14, 'loop_shift_button', channel=MIXERCHANNEL2, msg_type=MIDI_NOTE_TYPE)
        self.add_button(13, 'variations_launch_button', channel=FXCHANNEL, msg_type=MIDI_NOTE_TYPE)
        self.add_button(14, 'launch_scene_button', channel=FXCHANNEL, msg_type=MIDI_NOTE_TYPE)

        # pads

        pad_channel_list = [12, 12, 12, 12,13, 13, 13, 13,14, 14, 14, 14]
        self.add_matrix([repeat_list_three_times(36, 40), repeat_list_three_times(32, 36), repeat_list_three_times(28, 32), repeat_list_three_times(24, 28)], "pads", channels=[pad_channel_list, pad_channel_list,pad_channel_list,pad_channel_list], element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        
        # sub matrix pads
        self.add_submatrix(self.pads, 'pads_rows_0_2_cols_0_7', rows=(0, 3), columns=(0,8))
        self.add_submatrix(self.pads, 'pads_columns_0_3', columns=(0, 4))
        self.add_submatrix(self.pads, 'pads_columns_4_7', columns=(4, 8))
        self.add_submatrix(self.pads, 'pads_columns_0_7', columns=(0, 8))
        self.add_submatrix(self.pads, 'pads_rows_3_cols_0_7', rows=(3,4), columns=(0,8))
        self.add_submatrix(self.pads, 'pads_rows_0_2', rows=(0,2))
        self.add_submatrix(self.pads, 'pads_columns_0_7_rows_2_3', rows=(2,4), columns=(0,8))
        self.add_submatrix(self.pads, 'pads_columns_8_11_rows_2_3', rows=(2,4), columns=(8,12))
        self.add_submatrix(self.pads, 'pads_columns_8_11_rows_0_1', rows=(0,2), columns=(8,12))
        #self.add_submatrix(self.pads, 'pads_columns_8_11', columns=(8,12)) ###################for testing

    
        self.add_submatrix(self.pads, 'scene_launch_buttons', rows=(0,3), columns=(11,12)) 

        # editing
        #self.add_element("new_button", create_k2_button, 32, resource_type=PrioritizedResource, channel=FXCHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")
        #self.add_element("clear_button", create_k2_button, 36, resource_type=PrioritizedResource, channel=FXCHANNEL, msg_type=MIDI_NOTE_TYPE, button_type="small")



        # modified controls
        self.add_modified_control(control=self.bottom_2_encoder, modifier=self.shift_button)
        self.add_modified_control(control=self.capture_midi_button, modifier=self.shift_button)
        self.add_modified_control(control=self.pads_raw[44], modifier=self.shift_button)

        #self.add_element("prev_bank_button", create_k2_button, 12, channel=MIXERCHANNEL1, msg_type=MIDI_NOTE_TYPE, button_type="big")

        # accent/velocity button
        self.add_modified_control(control=self.bottom_4_encoder, modifier=self.transpose_shift)

        ########## FX + Master Mixer: K2.3 

        self.add_matrix([range(48, 51)], "solo_buttons", channels=FXCHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_matrix([range(40, 43)], "mute_buttons", channels=FXCHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_matrix([range(52, 55)], "track_select_buttons", channels=FXCHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")

        self.add_encoder_matrix(
            [range(4, 7)],
            base_name="send_a_encoders",
            channels=FXCHANNEL,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(8, 11)],
            base_name="send_b_encoders",
            channels=FXCHANNEL,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(12, 15)],
            base_name="send_c_encoders",
            channels=FXCHANNEL,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(16, 19)],
            base_name="volume_faders",
            channels=FXCHANNEL,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            [range(0, 3)],
            base_name="gain_encoders",
            channels=FXCHANNEL,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.AccelTwoCompliment,
        )
        self.add_modified_control(control=self.gain_encoders, modifier=self.shift_button)

        # master track
        self.add_encoder_matrix(
            [[19]],
            base_name="master_volume_fader",
            channels=FXCHANNEL,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )
        self.add_matrix([[55]], "master_track_select_button", channels=FXCHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        # cue
        self.add_encoder(11, 'cue_encoder', channel=FXCHANNEL, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.Absolute)

        # Tempo
        self.add_encoder(3, 'tempo_encoder', channel=FXCHANNEL, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.AccelTwoCompliment)
        self.add_modified_control(control=(self.tempo_encoder), modifier=(self.shift_button))

        # crossfader
        self.add_encoder(15, 'crossfader_encoder', channel=FXCHANNEL, is_feedback_enabled=IS_FEEDBACK_ENABLED, needs_takeover=True, map_mode=MapMode.Absolute)
        self.add_matrix([range(44, 47)], "crossfade_assign_buttons", channels=FXCHANNEL, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")

        # variations
        self.add_modified_control(control=(self.variations_recall_button), modifier=(self.shift_button))
        self.add_modified_control(control=(self.variations_launch_button), modifier=(self.shift_button))

        ########### Tracks Mixer  K2.1 + K2.2
        combined_button_channels = [[MIXERCHANNEL1, MIXERCHANNEL1, MIXERCHANNEL1, MIXERCHANNEL1], [MIXERCHANNEL2, MIXERCHANNEL2, MIXERCHANNEL2, MIXERCHANNEL2]]

        self.add_matrix(create_duplicated_list(44, 48), "mixer_arm_buttons", channels=combined_button_channels, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_matrix(create_duplicated_list(40, 44), "mixer_mute_buttons", channels=combined_button_channels, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_matrix(create_duplicated_list(52, 56), "mixer_track_select_buttons", channels=combined_button_channels, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_matrix(create_duplicated_list(48, 52), "mixer_solo_buttons", channels=combined_button_channels, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")
        self.add_modified_control(control=self.mixer_solo_buttons, modifier=self.shift_button)

        self.add_encoder_matrix(
            create_duplicated_list(4, 8),
            base_name="mixer_send_a_encoders",
            channels=combined_button_channels,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            create_duplicated_list(8, 12),
            base_name="mixer_send_b_encoders",
            channels=combined_button_channels,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            create_duplicated_list(12, 16),
            base_name="mixer_send_c_encoders",
            channels=combined_button_channels,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            create_duplicated_list(16, 20),
            base_name="mixer_volume_faders",
            channels=combined_button_channels,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.Absolute,
        )

        self.add_encoder_matrix(
            create_duplicated_list(0, 4),
            base_name="mixer_gain_encoders",
            channels=combined_button_channels,
            is_feedback_enabled=IS_FEEDBACK_ENABLED,
            needs_takeover=True,
            map_mode=MapMode.AccelTwoCompliment,
        )

        self.add_modified_control(control=self.mixer_gain_encoders, modifier=self.shift_button)

        self.add_matrix(create_duplicated_list(48, 52), "mixer_crossfade_assign_buttons", channels=combined_button_channels, element_factory=create_k2_button, name_factory=None, msg_type=MIDI_NOTE_TYPE, button_type="small")