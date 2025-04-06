from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from functools import partial
from .special_channel_strip_component import SpecialChannelStripComponent
from future.moves.itertools import zip_longest
from ableton.v3.control_surface.components import SessionRingComponent

def _init_session_ring(self):
    self._session_ring = SessionRingComponent(num_tracks=NUM_TRACKS,
        num_scenes=NUM_SCENES,
        tracks_to_use=self.song.return_tracks,
        is_enabled=True)

class MixerComponent(MixerComponentBase):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    # def tracks_to_use(self):
    #     return tuple(self.song.return_tracks)