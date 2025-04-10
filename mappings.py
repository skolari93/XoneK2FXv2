def create_mappings(cs):
    return {
        'Transport': dict(
            play_button='play_button',
            stop_button='stop_button',
            tempo_coarse_encoder="tempo_encoder",
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
        ),
        'MasterMixer': dict(
            track_select_buttons='master_track_select_button',
            volume_controls='master_volume_fader',
            crossfader_control='crossfader_encoder',
            prehear_volume_control='cue_encoder',
            variations_stash_button='variations_stash_button',
            variations_launch_button='variations_launch_button'
        ),
        'ViewControl': dict(
            scene_encoder='scene_select_encoder',
        ),
        'Session': dict(
            launch_scene_and_advance='launch_scene_button',
            scene_launch_buttons="scene_launch_buttons",
            stop_all_clips_button="stop_all_clips_button"
        ),
        'Session_Navigation': dict(
            vertical_encoder='vertical_encoder',
        )
    }