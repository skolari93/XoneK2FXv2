from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from .channel_strip import ChannelStripComponent
from itertools import zip_longest
from ableton.v3.control_surface.controls import (
    control_list,
    EncoderControl
)
from ableton.v3.base import depends
import logging
logger = logging.getLogger("XoneK2FXv2")

class FXMixerComponent(MixerComponentBase):
    _gain_controls = control_list(EncoderControl)

    @depends(fx_ring=None, target_track=None)
    def __init__(self, fx_ring=None, target_track=None, channel_strip_component_type=ChannelStripComponent, *a, **k):
        super().__init__(session_ring=fx_ring, target_track=target_track, channel_strip_component_type=channel_strip_component_type, *a, **k)
        self.name = 'FXMixer'


    def set_gain_encoders(self, encoders):
        for strip, encoder in zip_longest(self._channel_strips, encoders or []):
            strip.gain_control.set_control_element(encoder)
