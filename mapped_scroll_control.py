from ableton.v3.control_surface.controls import StepEncoderControl
from ableton.v3.live import action
from ableton.v3.live import liveobj_valid
from ableton.v2.base import EventObject
from ableton.v3.base import listens, task
MOMENTARY_DELAY = 0.3
class MappableScrollEncoder(EventObject):
    def __init__(self, *a, **k):
        (super().__init__)(*a, **k)
        self._parameter_up = None
        self._parameter_down = None
    
    def disconnect(self):
        self._parameter_up = None
        self._parameter_down = None
        super().disconnect()

    @property
    def mapped_parameter_up(self):
        return self._parameter_up
    
    @property
    def mapped_parameter_down(self):
        return self._parameter_down
    
    @mapped_parameter_up.setter
    def mapped_parameter_up(self, parameter):
        self._parameter_up = parameter if liveobj_valid(parameter) else None
        self.enabled = self._parameter_up is not None
        self._MappableScrollEncoder__on_parameter_up_value_changed.subject = self._parameter_up
        self._MappableScrollEncoder__on_parameter_up_value_changed()

    @mapped_parameter_down.setter
    def mapped_parameter_down(self, parameter):
        self._parameter_down = parameter if liveobj_valid(parameter) else None
        self.enabled = self._parameter_down is not None

        self._MappableScrollEncoder__on_parameter_down_value_changed.subject = self._parameter_down
        self._MappableScrollEncoder__on_parameter_down_value_changed()

    @listens("value")
    def __on_parameter_up_value_changed(self):
        self.is_on = liveobj_valid(self._parameter_up) and self._parameter_up.value

    @listens("value")
    def __on_parameter_down_value_changed(self):
        self.is_on = liveobj_valid(self._parameter_down) and self._parameter_down.value

class MappedScrollEncoderControl(StepEncoderControl):
    class State(StepEncoderControl.State, MappableScrollEncoder):
        def __init__(self, num_steps=64, *a, **k):
            super().__init__(num_steps=num_steps, *a, **k)
        
        def _on_stepped(self, steps):
            super()._on_stepped(steps)
            # Handle scrolling up or down based on step direction
            if steps < 0 and liveobj_valid(self._parameter_up):
                self._execute_parameter_action(self._parameter_up)
            elif steps > 0 and liveobj_valid(self._parameter_down):
                self._execute_parameter_action(self._parameter_down)

        def _execute_parameter_action(self, parameter):
            # Execute the action once immediately
            def execute_action():
                action.toggle_or_cycle_parameter_value(parameter)
            
            # Schedule the second execution after MOMENTARY_DELAY
            self.tasks.add(task.sequence(
                task.run(execute_action),
                task.wait(MOMENTARY_DELAY),
                task.run(execute_action),
                task.wait(MOMENTARY_DELAY)
            ))