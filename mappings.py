def create_mappings(cs):
    return {
        'Transport': dict(
            play_button='play_button',
            stop_button='stop_button',
        ),
        'FXMixer': dict(
            solo_buttons='solo_buttons',
            mute_buttons='mute_buttons',
            track_select_buttons='track_select_buttons',
            send_a_controls='send_a_encoders',
            send_b_controls='send_b_encoders',
            send_c_controls='send_c_encoders',
            volume_controls='volume_faders',
            master_track_volume_control='master_volume_fader',
        ),
    #     'MasterTrack': dict(
    #         master_select_button="master_select_button"
    #     )
    }