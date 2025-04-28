from ableton.v3.control_surface.components import DeviceParametersComponent
from ableton.v3.control_surface.controls import control_list
from .control import ParameterControl  # dein bestehendes ParameterControl nutzen
from ableton.v3.live import liveobj_valid

MAX_NUM_SENDS =12
class ChannelParametersComponent(DeviceParametersComponent):
    controls = control_list(ParameterControl, 3 + MAX_NUM_SENDS)  # Volume, Pan, Gain + Sends

    def _get_parameters(self):
        parameters = [
            self._track.mixer_device.volume if liveobj_valid(self._track) else None,
            self._track.mixer_device.panning if liveobj_valid(self._track) else None,
            self._gain_parameter if hasattr(self, "_gain_parameter") else None
        ]
        if liveobj_valid(self._track):
            parameters.extend(self._track.mixer_device.sends[:MAX_NUM_SENDS])
        else:
            parameters.extend([None] * MAX_NUM_SENDS)
        return parameters
