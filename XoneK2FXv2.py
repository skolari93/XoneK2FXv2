import os
from ableton.v3.base import const
from ableton.v3.control_surface import (
    ControlSurface,
    ControlSurfaceSpecification,
    create_skin,
)
from .elements import Elements
from .mappings import create_mappings
from .skin import Skin
from .colors import Rgb
from .session import SessionComponent
from .fx_mixer import FXMixerComponent
from .master_mixer import MasterMixerComponent
from .mixer import MixerComponent
from ableton.v3.control_surface.components import ViewControlComponent, SessionRingComponent, SessionNavigationComponent #,StepSequenceComponent, GRID_RESOLUTIONS
from functools import partial
#import Live
from functools import partial

import logging
logger = logging.getLogger("XoneK2FXv2")


def tracks_to_use_from_song(song):
    return tuple(song.visible_tracks) + tuple(song.return_tracks)

class XoneK2FXv2(ControlSurface):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        self.log_level = "info"

        self.start_logging()

        self.show_message("XoneK2FXv2: init mate")
        logger.info("XoneK2FXv2: init started ...")
        #logger.info(dir(Live.Browser.Browser.audio_effects.children))


    def disconnect(self):
        self.show_message("Disconnecting...")
        logger.info("Disconnecting...")
        self.stop_logging()
        super().disconnect()

    def setup(self):
        super().setup()
        self.init()

    def init(self):
        logger.info("init started:")
        with self.component_guard():
            logger.info("   adding skin")
            self._skin = create_skin(skin=Skin, colors=Rgb)

    def start_logging(self):
        module_path = os.path.dirname(os.path.realpath(__file__))
        log_dir = os.path.join(module_path, "logs")
        if not os.path.exists(log_dir):
            os.mkdir(log_dir, 0o755)
        log_path = os.path.join(log_dir, "xoneK2FXv2.log")
        self.log_file_handler = logging.FileHandler(log_path)
        self.log_file_handler.setLevel(self.log_level.upper())
        formatter = logging.Formatter("(%(asctime)s) [%(levelname)s] %(message)s")
        self.log_file_handler.setFormatter(formatter)
        logger.addHandler(self.log_file_handler)

    def stop_logging(self):
        logger.removeHandler(self.log_file_handler)

    def _get_additional_dependencies(self):
        fx_ring = SessionRingComponent(
            name='fx_ring',
            num_tracks=3,
            num_scenes=0,
            tracks_to_use=partial(fx_tracks, self.song),
        )
        self.component_map["FXRing"] = fx_ring

        master_ring = SessionRingComponent(
            name='master_ring',
            num_tracks=1,
            num_scenes=0,
            tracks_to_use=partial(master_track, self.song),
        )

        self.component_map["MasterRing"] = master_ring

        session_ring = SessionRingComponent(
            name='session_ring',
            num_tracks=4,
            num_scenes=3,
        )

        return {
            "fx_ring": const(fx_ring),
            "master_ring": const(master_ring),
            "session_ring": const(session_ring)
        }
    


    
def fx_tracks(song):
    return tuple(song.return_tracks)

def master_track(song):
    return (song.master_track,)


class Specification(ControlSurfaceSpecification):
    num_tracks = 3
    num_scenes = 3
    include_returns = False
    include_master = False
    #right_align_non_player_tracks = False
    #link_session_ring_to_scene_selection = True
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin, colors=Rgb)
    create_mappings_function = create_mappings
    component_map = {
        #'Step_Sequence': partial(StepSequenceComponent, grid_resolution=GRID_RESOLUTIONS[3]),
        'FXMixer': FXMixerComponent,
        'MasterMixer': MasterMixerComponent,
        'ViewControl': ViewControlComponent,
        'Mixer': MixerComponent,
        'Session': SessionComponent,
        'Session_Navigation': partial(SessionNavigationComponent, respect_borders=True, snap_track_offset=False)
    }
