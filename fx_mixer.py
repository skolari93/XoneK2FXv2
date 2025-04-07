from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase


from ableton.v3.base import depends

class FXMixerComponent(MixerComponentBase):

    @depends(fx_ring=None, target_track=None)
    def __init__(self, fx_ring=None, target_track=None, *a, **k):
        super().__init__(session_ring=fx_ring, target_track=target_track, *a, **k)
        self.name = 'FXMixer'