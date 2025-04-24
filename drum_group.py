from ableton.v3.base import depends, clamp, first
from ableton.v3.control_surface.components import DrumGroupComponent as DrumGroupComponentBase
from ableton.v3.live import liveobj_valid

BASE_DRUM_RACK_NOTE=36


import logging
logger = logging.getLogger("XoneK2FXv2")
TRANSLATION_CHANNEL = 6

class DrumGroupComponent(DrumGroupComponentBase):
    @depends(volume_parameters=None)
    def __init__(self, volume_parameters=None, translation_channel=TRANSLATION_CHANNEL, *a, **k):
        super().__init__(*a, translation_channel=translation_channel,matrix_always_listenable=True,**k)
        self._volume_parameters = volume_parameters

    def _on_matrix_pressed(self, button):
        pad = self._pad_for_button(button)
        if not self._any_modifier_pressed() and (not self._clipboard.is_copying):
            parameter = pad.chains[0].mixer_device.volume if pad and pad.chains else None
            self._volume_parameters.add_parameter(button, parameter)
        super()._on_matrix_pressed(button)

    def _on_matrix_released(self, button):
        super()._on_matrix_released(button)
        self._volume_parameters.remove_parameter(button)




    # def _button_coordinates_to_pad_index(self, first_note, coordinates):
    #     y, x = coordinates
    #     y = self.height - y - 1
        
    #     # Standard drum rack width is always 4
    #     drum_rack_width = 4
        
    #     # Calculate position within the standard drum rack grid
    #     column = x % drum_rack_width
    #     row = y % self.height
        
    #     # Calculate bank offset for button matrices wider than 4
    #     bank_offset = (x // drum_rack_width) * (drum_rack_width * self.height)
        
    #     # Calculate final index
    #     index = column + (row * drum_rack_width) + first_note + bank_offset
    #     index = 36
    #     logger.info(f"Coordinates: {coordinates}, Calculated index: {index}")


    #     return index

    # def _note_translation_for_button(self, button):

    #     return (36, 7)
    
    # def _button_coordinates_to_pad_index(self, first_note, coordinates):
    #     y, x = coordinates
    #     index = first_note + y * 4 + x
    # #     return first_note + y * 4 + x
    
    # @property
    # def width(self):
    #     w = getattr(self.matrix, "width", None)
    #     if callable(w):
    #         w = w()
    #     return w if w is not None else 4  # fallback default

    # @property
    # def height(self):
    #     h = getattr(self.matrix, "height", None)
    #     if callable(h):
    #         h = h()
    #     return h if h is not None else 2