
from ableton.v3.control_surface.controls import MappedSensitivitySettingControl, is_internal_parameter
from ableton.v3.live import liveobj_valid

class ParameterControl(MappedSensitivitySettingControl):

    class State(MappedSensitivitySettingControl.State):

        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._draws_automation = False

        def set_draws_automation(self, draws):
            self._draws_automation = draws
            self._update_direct_connection()
            self._update_value_slot()

        def _update_direct_connection(self):
            if self._draws_automation and self._control_element:
                if liveobj_valid(self.mapped_parameter) and (not is_internal_parameter(self.mapped_parameter)):
                    self._control_element.soft_connect_to(self.mapped_parameter)
                else:
                    self._control_element.release_parameter()
                    self._control_value.subject = None
            else:
                super()._update_direct_connection()

        def _update_value_slot(self):
            if self._draws_automation:
                self._value_slot.subject = self._control_element
            else:
                super()._update_value_slot()

        def _notifications_enabled(self):
            return self._draws_automation or super()._notifications_enabled()

        @staticmethod
        def _is_parameter_valid(_):
            return True