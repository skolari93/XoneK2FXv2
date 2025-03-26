from ableton.v2.control_surface import components
from .special_channel_strip_component import SpecialChannelStripComponent
from future.moves.itertools import zip_longest

class SpecialMixerComponent(components.MixerComponent):

    def __init__(self, *a, **k):
        (super(SpecialMixerComponent, self).__init__)(a, channel_strip_component_type=SpecialChannelStripComponent, **k)
    
    def tracks_to_use(self):
        return tuple(self.song.return_tracks)

    def _create_strip(self):
        return SpecialChannelStripComponent()
    
    # setters
    def set_solo_buttons(self, buttons):
        for strip, button in zip_longest(self._channel_strips, buttons or []):
            strip.set_solo_button(button)

    def set_mute_buttons(self, buttons):
        for strip, button in zip_longest(self._channel_strips, buttons or []):
            strip.set_mute_button(button)