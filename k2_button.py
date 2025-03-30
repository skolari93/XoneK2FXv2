from ableton.v3.control_surface.elements import ButtonElement
from ableton.v2.control_surface import MIDI_PB_TYPE, MIDI_NOTE_TYPE
import logging

logger = logging.getLogger("XoneK2FXv2")

# OFFSETS SMALL BUTTONS
REDSMALLBUTTONS = 0
AMBERSMALLBUTTONS = 36
GREENSMALLBUTTONS = 72

# OFFSETS BIG BUTTONS
REDBIGBUTTONS = 0
AMBERBIGBUTTONS = 4
GREENBIGBUTTONS = 8

# Selector Integers
RED = 1
AMBER = 2
GREEN = 3
BLACK = 4
CHANNEL = 14

class K2ButtonElement(ButtonElement):
    def __init__(self, identifier, button_type="small", channel=0, msg_type=MIDI_NOTE_TYPE, is_momentary=True, led_channel=None, **k):
        super().__init__(identifier, channel, msg_type, is_momentary, led_channel, **k)
        self._button_type = button_type

    def get_color(self, color_selector):
        """Returns the corresponding MIDI value for the given color and button type."""
        if self._button_type == "small":
            if color_selector == RED:
                return REDSMALLBUTTONS
            elif color_selector == AMBER:
                return AMBERSMALLBUTTONS
            elif color_selector == GREEN:
                return GREENSMALLBUTTONS
        elif self._button_type == "big":  # "big" button type
            if color_selector == RED:
                return REDBIGBUTTONS
            elif color_selector == AMBER:
                return AMBERBIGBUTTONS
            elif color_selector == GREEN:
                return GREENBIGBUTTONS
        return 0  # Default case if an invalid color is given

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
                is_input = True
                self._report_value(value, not is_input)

    def _do_send_value(self, value, channel=None):
        """Handles sending the value."""
        logger.info(value)

        if value == BLACK:
            velocity = 0
            self._send_midi_message(velocity, channel, self.get_color(RED))
            self._send_midi_message(velocity, channel, self.get_color(GREEN))
            self._send_midi_message(velocity, channel, self.get_color(AMBER))
        else:
            velocity = 127  # Example: Set velocity if the value is even
            self._send_midi_message(velocity, channel, self.get_color(value))


def create_k2_button(identifier, **k):
    return K2ButtonElement(
        identifier,
        k.pop("button_type", "small"),  # Default to "small" button
        k.pop("channel", CHANNEL),  # Default to predefined CHANNEL
        k.pop("msg_type", MIDI_NOTE_TYPE),  # Default msg_type
        k.pop("is_momentary", True),  # Default to momentary button
        k.pop("led_channel", None),  # Default None
        **k  # Pass any additional arguments
    )
