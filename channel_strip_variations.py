
from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
from .mappable_button_control import MappedButtonControlwithReleasedAction as MappedButtonControl
from ableton.v3.live import get_parameter_by_name
from ableton.v3.base import listens_group
from ableton.v3.control_surface.controls import MappedControl
from .mapped_scroll_control import MappedScrollEncoderControl

import logging
logger = logging.getLogger("XoneK2FXv2")


class ChannelStripComponent(ChannelStripComponentBase):
    variations_stash_button = MappedButtonControl(color="Variations.Off", on_color="Variations.Stash")
    variations_recall_button = MappedButtonControl(color="Variations.Off", on_color="Variations.Recall")
    variations_launch_button = MappedButtonControl()
    variations_overwrite_button = MappedButtonControl()
    variations_select_encoder = MappedScrollEncoderControl()

    gain_control = MappedControl()


    def __init__(self,  *a, **k):
        super().__init__( *a, **k)

    @listens_group("devices")
    def __on_devices_changed(self, _):
        self._connect_variations_buttons()
        self._connect_gain_control()

    def _connect_parameters(self):
        super()._connect_parameters()  # Call base method
        self._connect_variations_buttons()
        self._connect_gain_control()

    def _connect_variations_buttons(self):
        for device in self._track.devices:
            if device.name == "Variations":
                stash_parameter = get_parameter_by_name("Stash", device)
                self.variations_stash_button.mapped_parameter = stash_parameter
                recall_parameter = get_parameter_by_name("Recall", device)
                self.variations_recall_button.mapped_parameter = recall_parameter
                launch_parameter = get_parameter_by_name("Launch", device)
                self.variations_launch_button.mapped_parameter = launch_parameter
                overwrite_parameter = get_parameter_by_name("Overwrite", device)
                self.variations_overwrite_button.mapped_parameter = overwrite_parameter
                up_parameter = get_parameter_by_name("Navigate Up", device)
                down_parameter = get_parameter_by_name("Navigate Down", device)

                self.variations_select_encoder.mapped_parameter_up = up_parameter
                self.variations_select_encoder.mapped_parameter_down = down_parameter
                break
    
    def _connect_gain_control(self):
        if self.check_if_last_device_is_utility():
            last_device = self._track.devices[-1]
            gain_parameter = get_parameter_by_name("Gain", last_device)
            self.gain_control.mapped_parameter = gain_parameter


    def set_gain_control(self, encoder):
        self.gain_control.set_control_element(encoder)

    def check_if_last_device_is_utility(self):
        # Check if devices list is not empty
        if self._track.devices:
            # Assuming the utility device is identified by its name or type
            last_device = self._track.devices[-1]
            # Compare if the name of the last device is "Utility"
            if last_device.name == "Utility":
                return True
            else:
                return False
        else:
            return False
        
    def update(self):
        super().update()
        if self.is_enabled():
            self._update_listeners()

    def _update_listeners(self):
        if self._track:
            self._ChannelStripComponent__on_devices_changed.replace_subjects([self._track]) #ignore racks and chains

    def _disconnect_parameters(self):
        super()._disconnect_parameters()
        self.variations_stash_button.mapped_parameter = None
        self.variations_recall_button.mapped_parameter = None
        self.variations_launch_button.mapped_parameter = None
        self.variations_overwrite_button.mapped_parameter = None

        self.variations_select_encoder.mapped_parameter_up = None
        self.variations_select_encoder.mapped_parameter_down = None