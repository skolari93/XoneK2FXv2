import logging
import os

from ableton.v3.control_surface import (
    ControlSurface,
    ControlSurfaceSpecification,
    create_skin,
)
from .special_mixer_component import SpecialMixerComponent
from .elements import Elements
from .mappings import create_mappings
from .skin import Skin
from ableton.v3.control_surface.components import TransportComponent

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
            logger.info("   adding sking")
            # self._skin = create_skin(skin=ara.Skin, colors=ara.Rgb)

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

    
class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin)
    create_mappings_function = create_mappings
    component_map = {
        'Transport': TransportComponent
    }
