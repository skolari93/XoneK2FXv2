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
from ableton.v3.control_surface.components import TransportComponent
from .mixer import MixerComponent
#from ableton.v3.control_surface.components import MixerComponent

logger = logging.getLogger("XoneK2FXv2")


class XoneK2FXv2(ControlSurface):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        self.log_level = "info"

        self.start_logging()

        self.show_message("XoneK2FXv2: init mate")
        logger.info("XoneK2FXv2: init started ...")

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

    def disconnect(self):
        self.show_message("Disconnecting...")
        logger.info("Disconnecting...")
        self.stop_logging()
        super().disconnect()

    # @lazy_attribute
    # def _create_session_ring(self):
    #     self._session_ring = self._specification.session_ring_component_type(is_enabled=False,
    #       num_tracks=(self._specification.num_tracks),
    #       num_scenes=(self._specification.num_scenes),
    #       include_returns=(self._specification.include_returns))
    #     return self._session_ring

    
class Specification(ControlSurfaceSpecification):
    num_tracks = 3
    num_scenes = 0
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin, colors=Rgb)
    create_mappings_function = create_mappings
    component_map = {
        'Transport': TransportComponent,
        'Mixer': MixerComponent
    }
