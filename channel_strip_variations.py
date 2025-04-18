
from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
from .mappable_button_control import MappedButtonControlwithReleasedAction as MappedButtonControl
from ableton.v3.live import get_parameter_by_name
from ableton.v3.base import listens_group
from .mapped_scroll_control import MappedScrollEncoderControl

import logging
logger = logging.getLogger("XoneK2FXv2")


class ChannelStripComponent(ChannelStripComponentBase):
    variations_stash_button = MappedButtonControl(color="Variations.Off", on_color="Variations.Stash")
    variations_recall_button = MappedButtonControl(color="Variations.Off", on_color="Variations.Recall")
    variations_launch_button = MappedButtonControl()
    variations_overwrite_button = MappedButtonControl()
    variations_select_encoder = MappedScrollEncoderControl()

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