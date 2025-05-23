def create_mappings(cs):
    return {
        'Modifier_Background': dict(
            shift="shift_button"
        ),
        'Transport': dict(
            #play_pause_button='pads_raw[44]',
            #play_button='play_button_with_shift',
            capture_midi_button="capture_midi_button",
        ),
        'FXMixer': dict(
            solo_buttons='solo_buttons',
            mute_buttons='mute_buttons',
            track_select_buttons='track_select_buttons',
            send_a_controls='send_a_encoders',
            send_b_controls='send_b_encoders',
            send_c_controls='send_c_encoders',
            volume_controls='volume_faders',
            gain_controls='gain_encoders',
            crossfade_cycle_buttons='crossfade_assign_buttons',
            pan_controls='gain_encoders_with_shift'
        ),
        'MasterMixer': dict(
            track_select_buttons='master_track_select_button',
            volume_controls='master_volume_fader',
            crossfader_control='crossfader_encoder',
            prehear_volume_control='cue_encoder',
            gain_controls='master_gain_encoder',
            pan_controls='master_gain_encoder_with_shift',
            variations_recall_button='variations_recall_button',
            variations_stash_button='variations_recall_button_with_shift',
        ),
        'Clip_Actions': dict(
            quantize_button='capture_midi_button_with_shift',
            #double_button='delete_button'
        ),
        'Mixer': dict(
            solo_buttons='mixer_arm_buttons_with_shift',
            mute_buttons='mixer_mute_buttons',
            arm_buttons='mixer_arm_buttons',
            track_select_buttons='mixer_track_select_buttons',
            send_a_controls='mixer_send_a_encoders',
            send_b_controls='mixer_send_b_encoders',
            send_c_controls='mixer_send_c_encoders',
            volume_controls='mixer_volume_faders',
            gain_controls='mixer_gain_encoders',
            crossfade_cycle_buttons='mixer_crossfade_assign_buttons',
            pan_controls='mixer_gain_encoders_with_shift'
        ),

        'Note_Modes': dict(
            instrument = dict(
                modes= [
                    dict(
                        component= 'Instrument',
                        matrix='pads_rows_2_3',
                        octave_encoder='bottom_6_encoder',
                        scale_mode_button= 'bottom_6_encoder_shift_button_with_shift'
                    ),
                    dict(
                        component= 'Step_Sequence',
                        step_buttons= 'pads_columns_0_7_rows_0_1',
                        matrix= 'pads_columns_8_11_rows_0_1', #bad name for loop matrix
                        transpose_encoder= 'bottom_4_encoder',
                        transpose_octave_encoder= 'bottom_4_encoder_with_bottom_4_encoder_shift',
                    )
                ]
            ),
            drum = dict(
                modes=[
                    dict(
                        component= 'Drum_Group',
                        matrix='pads_drum',
                        copy_button= 'duplicate_button',
                        mute_button='shift_button',
                        scroll_encoder='bottom_6_encoder'
                    ),
                    dict(
                        component= 'Step_Sequence',
                        step_buttons= 'pads_columns_0_7',
                        copy_button= 'duplicate_button',
                        matrix= 'pads_columns_8_11_rows_0_1', #bad name for loop matrix
                        ratchet_encoder= 'bottom_4_encoder',                          

                    )
                ]

            ),
            audio = dict(
                component= 'Background',
            )
            #'simpler': create_note_mode_layer_dict('Sliced_Simpler'),
        ),


        'Main_Modes': dict(
            cycle_mode_button = 'layout_button',
            session= dict(
                modes= [
                    {
                        'component': 'Session',
                        'scene_launch_buttons':"scene_launch_buttons",
                        'stop_all_clips_button':"pads_raw[47]",
                        'clip_launch_buttons':"pads_rows_0_2_cols_0_7",
                        'stop_track_clip_buttons':"pads_rows_3_cols_0_7",
                        'clip_slot_select_button' : 'shift_button',
                        'copy_button': 'duplicate_button',
                        'launch_scene_and_advance':'bottom_6_encoder_shift_button',

                    },
                    {
                        'component': 'ViewControl',
                        'scene_encoder':'bottom_6_encoder',
                    },
                    {
                        'component': 'Session_Navigation',
                        'horizontal_encoder': 'bottom_3_encoder',
                        'vertical_encoder': 'bottom_4_encoder',
                    },
                    {
                        'component': 'Transport',
                        'play_pause_button':'pads_raw[44]',
                        'stop_button': 'pads_raw[45]',
                        'automation_arm_button':"pads_raw[32]",
                        're_enable_automation_button': "pads_raw[33]",
                        'metronome_button':"big_3_button_with_shift",
                        'tap_tempo_button':"big_3_button",
                        'tempo_coarse_encoder': "bottom_2_encoder",
                        'tempo_fine_encoder': "bottom_2_encoder_with_bottom_2_encoder_shift",

                    },
                    {
                        'component': 'Recording',
                        'session_record_button':"pads_raw[34]",
                        'arrangement_record_button':"pads_raw[46]",
                        'new_button': 'pads_raw[20]'
                    },
                    {
                        'component': 'Undo_Redo',
                        'undo_button':'pads_raw[21]',
                        'redo_button':'pads_raw[22]'
                    },
                    {
                        'component':'MasterMixer',
                        'variations_launch_button': 'bottom_5_encoder_shift_button',
                        'variations_overwrite_button': 'bottom_5_encoder_shift_button_with_shift',
                        'variations_select_encoder': 'bottom_5_encoder'
                    },
                    {
                        'component': 'Clip_Actions',
                        'delete_button': 'pads_raw[8]',
                    },
                    
                ],
                
            ),
           note= dict(
                modes= [
                    {'component': 'Note_Modes'},
                    {
                        'component': 'Step_Sequence',
                        'duration_encoder': 'bottom_2_encoder',
                        'nudge_encoder': 'bottom_1_encoder',
                        'note_displacement_encoder': 'bottom_1_encoder_with_bottom_1_encoder_shift',
                        'duration_fine_encoder': 'bottom_2_encoder_with_bottom_2_encoder_shift',
                        'copy_button': 'duplicate_button'
                    },
                    {
                        'component': 'Clip_Actions',
                        #'delete_button': '',
                        'double_button': 'duplicate_button_with_shift'
                    },
                    {
                        'component': 'Volume_Parameters',
                        'volume_encoder':'bottom_3_encoder', 
                        'volume_encoder_shift_button':'bottom_3_encoder_shift_button'
                    },
                    {
                        'component': 'Loop_Length',
                        'length_encoder': 'bottom_5_encoder',
                        'shift_button': 'bottom_5_encoder_shift_button'
                    },
                    {
                        'component':'Accent',
                        'accent_button': 'big_3_button'
                    },
                ]
            ),
        ),
    }