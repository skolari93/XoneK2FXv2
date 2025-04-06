import logging
import os
from ableton.v3.base import lazy_attribute

from ableton.v3.control_surface import (
    ControlSurface,
    ControlSurfaceSpecification,
    create_skin,
)
from .elements import Elements
from .mappings import create_mappings
from .skin import Skin
from .colors import Rgb
from ableton.v3.control_surface import Layer
from ableton.v3.control_surface.components import TransportComponent
from .fx_mixer import FXMixerComponent
from .master_track import MasterTrackComponent
#from ableton.v3.control_surface.components import MixerComponent

from functools import partial


logger = logging.getLogger("XoneK2FXv2")


class XoneK2FXv2(ControlSurface):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        self.log_level = "info"

        self.start_logging()

        self.show_message("XoneK2FXv2: init mate")
        logger.info("XoneK2FXv2: init started ...")

        # with self.component_guard():
            


    def _create_components(self):
        self.create_master_select()

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
            #self._create_components()

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

    def create_master_select(self):
        logger.info("init master select:")
        self._master_selector = MasterTrackComponent(tracks_provider=(self._session_ring),
          is_enabled=False,
          
          layer=Layer(toggle_button="master_select_button"))
        self._master_selector.set_enabled(True)
    
class Specification(ControlSurfaceSpecification):
    num_tracks = 3
    num_scenes = 0
    include_returns = False
    include_master = True
    right_align_non_player_tracks = False
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin, colors=Rgb)
    create_mappings_function = create_mappings
    component_map = {
        'Transport': TransportComponent,
        'FXMixer': FXMixerComponent 
    }
