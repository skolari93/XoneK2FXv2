from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v3.base import depends
from .channel_strip_variations import ChannelStripComponent

class MasterMixerComponent(MixerComponentBase):

    @depends(master_ring=None, target_track=None)
    def __init__(self, master_ring=None, target_track=None, channel_strip_component_type=ChannelStripComponent, *a, **k):
        super().__init__(session_ring=master_ring, target_track=target_track, channel_strip_component_type=channel_strip_component_type, *a, **k)
        self.name = 'MasterMixer'

    def set_variations_stash_button(self, button):
        self._master_strip.variations_stash_button.set_control_element(button)

    # def set_variations_recall_button(self, button):
    #     self._master_strip.variations_recall_button.set_control_element(button)

    def set_variations_launch_button(self, button):
        self._master_strip.variations_launch_button.set_control_element(button)