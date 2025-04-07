from ableton.v3.control_surface.components import SessionRingComponent
from ableton.v3.base import depends
from functools import partial

def tracks_to_use_from_song(song):
    return tuple(song.visible_tracks) + tuple(song.return_tracks)

class MasterRing(SessionRingComponent):

    @depends(song=None)
    def __init__(self, song=None, num_tracks=3, num_scenes=0, *a, **k):
        super().__init__(
            name='Master_Ring',
            num_tracks=num_tracks,
            num_scenes=num_scenes,
            tracks_to_use=partial(tracks_to_use_from_song, song),
            is_enabled=False,
            *a,
            **k
        )