def create_mappings(cs):
    return {
        'Modifier_Background': dict(
            shift="shift_button"
        ),
        'Transport': dict(
            play_pause_button='play_button',
            play_button='play_button_with_shift',
            stop_button='stop_button',
            tempo_coarse_encoder="tempo_encoder",
            tempo_fine_encoder="tempo_encoder_with_shift",
            re_enable_automation_button="automation_re-enable_button",
            automation_arm_button="automation_arm_button",
        ),
        'Recording': dict(
            arrangement_record_button='record_button',
            session_record_button='session_record_button',
            new_button='new_button' # not working
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
            variations_recall_button='variations_recall_button',
            variations_stash_button='variations_recall_button_with_shift',
            variations_launch_button='variations_launch_button',
            variations_overwrite_button='variations_launch_button_with_shift',
            variations_select_encoder='variations_select_encoder'
        ),
        'Clip_Actions': dict(
            quantize_button='quantize_button',
            double_button='delete_button'
        ),
        'Mixer': dict(
            solo_buttons='mixer_solo_buttons',
            mute_buttons='mixer_mute_buttons',
            arm_buttons='mixer_arm_buttons',
            track_select_buttons='mixer_track_select_buttons',
            send_a_controls='mixer_send_a_encoders',
            send_b_controls='mixer_send_b_encoders',
            send_c_controls='mixer_send_c_encoders',
            volume_controls='mixer_volume_faders',
            gain_controls='mixer_gain_encoders',
            crossfade_cycle_buttons='mixer_solo_buttons_with_shift',
            pan_controls='mixer_gain_encoders_with_shift'
        ),
        'ViewControl': dict(
            scene_encoder='scene_select_encoder',
        ),
        # 'Session': dict(
        #     launch_scene_and_advance='launch_scene_button',
        #     scene_launch_buttons="scene_launch_buttons",
        #     stop_all_clips_button="stop_all_clips_button",
        #     clip_launch_buttons="pads_rows_0_2",
        #     stop_track_clip_buttons="pads_row_3",
        #     clip_slot_select_button = 'shift_button',
        # ),
        'Session_Navigation': dict(
            vertical_encoder='vertical_scene_select_encoder',
            horizontal_encoder='horizontal_scene_select_encoder',
        ),
        'Undo_Redo': dict(
            undo_button='undo_button',
            redo_button='redo_button'
        ),
        'Note_Modes': dict(
            instrument = dict(
                component= 'Instrument',
                matrix='pads_columns_4_7'         
            ),
            drum = dict(
                component= 'Drum_Group',
                matrix='pads_columns_4_7'         
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
                        'launch_scene_and_advance':'launch_scene_button',
                        'scene_launch_buttons':"scene_launch_buttons",
                        'stop_all_clips_button':"stop_all_clips_button",
                        'clip_launch_buttons':"pads_rows_0_2",
                        'stop_track_clip_buttons':"pads_row_3",
                        'clip_slot_select_button' : 'shift_button',
                    }
                ]
            ),
           note= dict(
                modes= [
                        {'component': 'Note_Modes'},
                    {
                        'component': 'Step_Sequence',
                        'step_buttons': 'pads_columns_0_3'
                    }
                ]
            )
        ),
    }