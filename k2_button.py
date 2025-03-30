from ableton.v3.control_surface.elements import ButtonElement
from ableton.v2.control_surface import MIDI_PB_TYPE, MIDI_NOTE_TYPE
import logging
logger = logging.getLogger("XoneK2FXv2")
# RED = 0
# AMBER = 36
# GREEN = 72
# BLACK = 1

RED = 0
AMBER = 4
GREEN = 8

CHANNEL = 14

class K2ButtonElement(ButtonElement):
    def __init__(self, identifier, channel=0, msg_type=MIDI_NOTE_TYPE, is_momentary=True, led_channel=None, **k):
        super().__init__(identifier, channel, msg_type, is_momentary, led_channel, **k)

    def _do_send_value(self, value, channel = CHANNEL, color=RED):
        # if int(value) == 1: 
        #     data_byte2 = 0

        data_byte1 = self._original_identifier + value # <---------------
        data_byte2 = 0
        if value == 666: 
            data_byte2 = 0
        status_byte = self._status_byte(self._original_channel if channel is None else channel)
        if self._msg_type == MIDI_PB_TYPE:
            data_byte1 = value & 127
            data_byte2 = value >> 7 & 127
        if self.send_midi((status_byte, data_byte1, data_byte2)):
            self._last_sent_message = (
             value, channel)
            if self._report_output:
                is_input = True
                self._report_value(value, not is_input)


def create_k2_button(identifier, **k):
    return K2ButtonElement(
        identifier,
        k.pop("channel", CHANNEL),  # Default to channel 0 if not provided
        k.pop("msg_type", MIDI_NOTE_TYPE),  # Default msg_type
        k.pop("is_momentary", True),  # Default to momentary button
        k.pop("led_channel", None),  # Default None
        **k  # Pass any additional arguments
    )