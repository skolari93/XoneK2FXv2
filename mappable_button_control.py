from ableton.v3.control_surface.controls import MappedButtonControl
from ableton.v3.live import action


# Erweiterung der ButtonControl mit doppeltem Action-Aufruf
class MappedButtonControlwithReleasedAction(MappedButtonControl):
    class State(MappedButtonControl.State):
        def _call_listener(self, listener_name, *args):
            if listener_name == "pressed" and self.mapped_parameter is not None:
                action.toggle_or_cycle_parameter_value(self.mapped_parameter)
            if listener_name == "released" and self.mapped_parameter is not None:
                action.toggle_or_cycle_parameter_value(self.mapped_parameter)