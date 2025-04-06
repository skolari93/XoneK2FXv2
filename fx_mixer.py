from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v3.control_surface.components import SessionRingComponent



class FXMixerComponent(MixerComponentBase):
    def __init__(self, *a, **k):
        # First call super().__init__ to properly initialize the object
        super().__init__(*a, **k)
        # Then initialize the session ring
        #self._provider = self._init_session_ring()
        # Now set the tracks_provider
        self.name = 'FXMixer'
        
    # def _init_session_ring(self, num_tracks=3, num_scenes=0):
    #     return SessionRingComponent(
    #         num_tracks=num_tracks,
    #         num_scenes=num_scenes,
    #         tracks_to_use=self.song.return_tracks,
    #         is_enabled=True
    #     )