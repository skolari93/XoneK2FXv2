from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v3.control_surface.components import SessionRingComponent


from ableton.v3.base import depends

class FXMixerComponent(MixerComponentBase):

    @depends(master_ring=None, target_track=None)
    def __init__(self, master_ring=None, target_track=None, *a, **k):
        super().__init__(session_ring=master_ring, target_track=target_track, *a, **k)
        self.name = 'FXMixer'