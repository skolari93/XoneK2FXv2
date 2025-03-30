from ableton.v3.control_surface.elements import Color
CHANNEL = 15
import logging
logger = logging.getLogger("XoneK2FXv2")

class K2Color(Color):
    def __init__(self, button_note, color, channel=CHANNEL, *a, **k):
        (super().__init__)(*a, **k)
        self._color = color
        self.button_note = button_note
        self._channel = channel
        logger.info("trytodraw")

    @property
    def midi_value(self):
        logger.info("trytodraw")
        return self._color

    def draw(self, interface):
        logger.info("trytodraw")
        data_byte1 = interface._original_identifier + self._color
        data_byte2 = self.button_note
        status_byte = interface._status_byte(self._channel)
        # interface.send_midi((status_byte, data_byte1, data_byte2))
        if self._msg_type == 2:
            data_byte1 = self.button_note & 127
            data_byte2 = self.button_note >> 7 & 127
        if interface.send_midi((status_byte, data_byte1, data_byte2)):
            interface._last_sent_message = (data_byte2, self._channel)
            if interface._report_output:
                is_input = True
                interface._report_value(data_byte2, not is_input) 

RED = 0
AMBER = 36
GREEN = 72
BLACK = 1

class Rgb:
    logger.info("rgb init")
    def amberfun(button_note):
        K2Color(button_note, AMBER)
    
    def redfun(button_note):
        K2Color(button_note, RED)

    def greenfun(button_note):
        logger.info("ggreenfun")
        K2Color(button_note, GREEN)

    def blackfun(button_note):
        K2Color(button_note, BLACK)

    amber = amberfun(12)
    green = greenfun(12)
    red = redfun(12)