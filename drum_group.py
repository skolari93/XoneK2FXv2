from ableton.v3.base import depends
from ableton.v3.control_surface.components import DrumGroupComponent as DrumGroupComponentBase

class DrumGroupComponent(DrumGroupComponentBase):
    pass

    @depends(volume_parameters=None)
    def __init__(self, volume_parameters=None, *a, **k):
        super().__init__(*a, matrix_always_listenable=True, **k)
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