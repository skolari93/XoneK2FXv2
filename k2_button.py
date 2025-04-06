from ableton.v3.control_surface.elements import ButtonElement
from ableton.v2.control_surface import MIDI_PB_TYPE, MIDI_NOTE_TYPE
from ableton.v2.base import BooleanContext, const, has_event, in_range, listens, old_hasattr
import logging
from past.builtins import long
logger = logging.getLogger("XoneK2FXv2")


# Offsets for buttons
COLOR_OFFSETS = {
    "small": {1: 0, 2: 36, 3: 72},  # RED, AMBER, GREEN
    "big": {1: 0, 2: 4, 3: 8},      # RED, AMBER, GREEN
}

# Selector integers
RED, AMBER, GREEN, BLACK, CHANNEL = 1, 2, 3, 4, 14

class K2ButtonElement(ButtonElement):
    def __init__(self, identifier, button_type="small", channel=0, msg_type=MIDI_NOTE_TYPE, is_momentary=True, led_channel=None, **k):
        super().__init__(identifier, channel, msg_type, is_momentary, led_channel, **k)
        self._button_type = button_type

    def get_color(self, color_selector):
        """Returns the corresponding MIDI value for the given color and button type."""
        return COLOR_OFFSETS.get(self._button_type, {}).get(color_selector, 0)

    def _send_midi_message(self, value, channel, color):
        """Helper method to send MIDI messages."""
        data_byte1 = self._original_identifier + int(color)
        data_byte2 = value
        status_byte = self._status_byte(self._original_channel if channel is None else channel)

        if self._msg_type == MIDI_PB_TYPE:
            data_byte1 = value & 127
            data_byte2 = (value >> 7) & 127

        if self.send_midi((status_byte, data_byte1, data_byte2)):
            self._last_sent_message = (value, channel)
            if self._report_output:
                self._report_value(value, False)

    def light_off(self,channel=CHANNEL):
        velocity = 0
        for color in (RED, GREEN, AMBER):
            self._send_midi_message(velocity, channel, self.get_color(color))   
          
    def _do_send_value(self, value, channel=None):
        """Handles sending the value."""
        logger.info(value)
        if value == BLACK or value == 0: # sometimes it sends 0, i don't know from where
            self.light_off(channel)
        else:
            velocity = 127  # Example: Set velocity if the value is even
            self._send_midi_message(velocity, channel, self.get_color(value))

def create_k2_button(identifier, **k):
    """Factory function to create a K2ButtonElement with default parameters."""
    return K2ButtonElement(
        identifier,
        k.pop("button_type", "small"),  # Default: "small" button
        k.pop("channel", CHANNEL),  # Default channel
        k.pop("msg_type", MIDI_NOTE_TYPE),  # Default MIDI message type
        k.pop("is_momentary", True),  # Default: momentary button
        k.pop("led_channel", None),  # Default: no LED channel
        **k  # Pass any additional arguments
    )
