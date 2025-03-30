from ableton.v3.control_surface.elements import Color, SimpleColor
from ableton.v2.control_surface import MIDI_PB_TYPE
CHANNEL = 15
import logging
logger = logging.getLogger("XoneK2FXv2")
# RED = 0
# AMBER = 36
# GREEN = 72
BLACK = 1


RED = 0
AMBER = 4
GREEN = 8
BLACK = 666
DEFAULTVALUE=127

class K2Color(Color):
    def __init__(self, value, color=RED, channel=None, *a, **k):
        (super().__init__)(*a, **k)
        self._value = value
        self._channel = channel
        self._color = color

    @property
    def midi_value(self):
        return self._value

    def send_color(value, interface, channel=CHANNEL,color=RED):
        data_byte1 = interface._original_identifier + color # <---------------
        data_byte2 = value
        status_byte = interface._status_byte(interface._original_channel if channel is None else channel)
        if interface._msg_type == MIDI_PB_TYPE:
            data_byte1 = value & 127
            data_byte2 = value >> 7 & 127
        if interface.send_midi((status_byte, data_byte1, data_byte2)):
            interface._last_sent_message = (
             value, channel)
            if interface._report_output:
                is_input = True
                interface._report_value(value, not is_input)
        interface.send_value((value), channel=(channel))        

    def draw(self, interface):
        data_byte1 = interface._original_identifier + self._color # <---------------
        data_byte2 = self._value
        status_byte = interface._status_byte(interface._original_channel if self._channel is None else self._channel)
        if interface._msg_type == MIDI_PB_TYPE:
            data_byte1 = self._value & 127
            data_byte2 = self._value >> 7 & 127
        if interface.send_midi((status_byte, data_byte1, data_byte2)):
            interface._last_sent_message = (
             self._value, self._channel)
            if interface._report_output:
                is_input = True
                interface._report_value(self._value, not is_input)
        interface.send_value((self._value), channel=(self._channel))



class Rgb:
    logger.info("rgb init")

    amber = K2Color(127,color=AMBER)
    green = K2Color(127,color=GREEN)
    red = K2Color(127,color=RED)
    black = K2Color(0, color=GREEN)
    # black = SimpleColor(0)