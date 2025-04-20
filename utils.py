import logging
logger = logging.getLogger("XoneK2FXv2")
from ableton.v3.live import liveobj_valid

def print_all_parameter_names(device):
    if liveobj_valid(device):
        for param in device.parameters:
            if liveobj_valid(param):
                logger.info(param.original_name)
