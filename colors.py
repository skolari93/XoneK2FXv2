from ableton.v3.control_surface.elements import Color, SimpleColor
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

    def draw(self, interface):
        interface.send_value((self._value), channel=(self._channel))



class Rgb:
    logger.info("rgb init")

    amber = SimpleColor(AMBER)
    green = SimpleColor(GREEN)
    red = SimpleColor(RED)
    black = SimpleColor(1)
    # black = SimpleColor(0)