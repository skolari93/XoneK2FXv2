from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
from ableton.v3.control_surface.controls import EncoderControl
import logging
logger = logging.getLogger("XoneK2FXv2")

class ChannelStripComponent(ChannelStripComponentBase):
    gain_encoder = EncoderControl()

    # def __init__(self, *a, **k):
    #     (super().__init__)(*a, **k)

    @gain_encoder.value
    def _on_gain_encoder_value_changed(self, value, encoder):
        logger.info('gain value changed')

    #     current_index = self._item_provider.items.index(selected_device)
    #     new_index = clamp(current_index + value, 0, len(self._item_provider.items) - 1)
    #     target_device = self._item_provider.items[new_index]
    #     self.song.view.select_device(target_device)
    #     self.notify(self.notifications.Device.select, target_device.name)


    def check_if_utility_device_is_last_device(self):
        devices = self._track.devices
