from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
from ableton.v3.control_surface.controls import MappedControl
from ableton.v3.live import get_parameter_by_name
from ableton.v3.base import listens_group
from itertools import chain

import logging
logger = logging.getLogger("XoneK2FXv2")


class ChannelStripComponent(ChannelStripComponentBase):
    gain_control = MappedControl()
    def __init__(self,  *a, **k):
        super().__init__( *a, **k)

    @listens_group("devices")
    def __on_devices_changed(self, _):
        self._connect_gain_control()

    def _connect_parameters(self):
        super()._connect_parameters()  # Call base method
        self._connect_gain_control()

    def _connect_gain_control(self):
        if self.check_if_last_device_is_utility():
            last_device = self._track.devices[-1]
            gain_parameter = get_parameter_by_name("Gain", last_device)
            self.gain_control.mapped_parameter = gain_parameter
    
    def update(self):
        super().update()
        if self.is_enabled():
            self._update_listeners()

    def _update_listeners(self):
        if self._track:
            self._ChannelStripComponent__on_devices_changed.replace_subjects([self._track]) #ignore racks and chains

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
        

    def _all_controls(self):
        return chain([
         self.volume_control, self.pan_control, self.gain_control], self.send_controls, self.indexed_send_controls,)