
from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
# from ableton.v3.control_surface.controls import MappedButtonControl
from .mappable_button_control import MappedButtonControlwithReleasedAction as MappedButtonControl
from ableton.v3.live import get_parameter_by_name
from ableton.v3.base import listens_group
from .utils import print_all_parameter_names
from itertools import chain

import logging
logger = logging.getLogger("XoneK2FXv2")


class ChannelStripComponent(ChannelStripComponentBase):
    variations_stash_button = MappedButtonControl()
    variations_recall_button = MappedButtonControl()
    variations_launch_button = MappedButtonControl()
    variations_overwrite_button = MappedButtonControl()

    variations_up_button = MappedButtonControl()
    variations_down_button = MappedButtonControl()

    def __init__(self,  *a, **k):
        super().__init__( *a, **k)

    @listens_group("devices")
    def __on_devices_changed(self, _):
        self._connect_variations_buttons()

    def _connect_parameters(self):
        super()._connect_parameters()  # Call base method
        self._connect_variations_buttons()

    def _connect_variations_buttons(self):
        for device in self._track.devices:
            if device.name == "Variations":
                #logger.info(print_all_parameter_names(device))
                stash_parameter = get_parameter_by_name("Stash", device)
                self.variations_stash_button.mapped_parameter = stash_parameter
                recall_parameter = get_parameter_by_name("Recall", device)
                self.variations_recall_button.mapped_parameter = recall_parameter
                launch_parameter = get_parameter_by_name("Launch", device)
                self.variations_launch_button.mapped_parameter = launch_parameter
                overwrite_parameter = get_parameter_by_name("Overwrite", device)
                self.variations_overwrite_button.mapped_parameter = overwrite_parameter
                up_parameter = get_parameter_by_name("Navigate Up", device)
                self.variations_up_button.mapped_parameter = up_parameter
                down_parameter = get_parameter_by_name("Navigate Down", device)
                self.variations_down_button.mapped_parameter = down_parameter
                break
    
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
        self.variations_up_button.mapped_parameter = None
        self.variations_down_button.mapped_parameter = None