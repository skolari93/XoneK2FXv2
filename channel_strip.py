from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
from ableton.v3.control_surface.controls import EncoderControl
#from ableton.v3.control_surface import create_parameter_bank, BankingInfo
from ableton.v3.live import get_parameter_by_name
from ableton.v3.control_surface.default_bank_definitions import (
    BANK_DEFINITIONS,
    BANK_MAIN_KEY,
    BANK_PARAMETERS_KEY
)
from ableton.v3.live import liveobj_valid

import logging
logger = logging.getLogger("XoneK2FXv2")






# something with connect_to and get_parameter_by_name, _direct_mapping







class ChannelStripComponent(ChannelStripComponentBase):
    gain_control = EncoderControl()

    @gain_control.value
    def _on_gain_control_value_changed(self, value, encoder):
        if self.check_if_last_device_is_utility():
            last_device = self._track.devices[-1]


            # Create a banking info object
            #banking_info = BankingInfo(BANK_DEFINITIONS["StereoGain"]["Utility"])


            # Create a parameter bank for the device
            #parameter_bank = create_parameter_bank(last_device, banking_info)

            # Access the Gain parameter (it's at index 6 in the bank definition)
            gain_parameter = get_parameter_by_name("Gain", last_device)
            self.print_all_parameter_names(last_device)
            # Now you can use the gain parameter
            if gain_parameter:
                print(f"Current gain value: {gain_parameter.value}")

    def set_gain_control(self, encoder):
        self.gain_control.set_control_element(encoder)

    def check_if_last_device_is_utility(self):
        # Check if devices list is not empty
        if self._track.devices:
            # Assuming the utility device is identified by its name or type
            last_device = self._track.devices[-1]
            # Compare if the name of the last device is "Utility"
            if last_device.name == "Utility":
                logger.info("The last device is a Utility device.")
                return True
            else:
                logger.info("The last device is NOT a Utility device.")
                return False
        else:
            logger.info("No devices in the list.")
            return False
        
    def print_all_parameter_names(self, device):
        if liveobj_valid(device):
            for param in device.parameters:
                if liveobj_valid(param):
                    logger.info(param.original_name)