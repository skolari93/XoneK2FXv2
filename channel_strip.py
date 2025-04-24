from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
from ableton.v3.control_surface.controls import MappedControl, control_list
from ableton.v3.live import get_parameter_by_name
from ableton.v3.base import listens_group
from itertools import chain

import logging
logger = logging.getLogger("XoneK2FXv2")
MAX_NUM_SENDS = 12


class ChannelStripComponent(ChannelStripComponentBase):
    gain_control = MappedControl()
    # send_controls = control_list(MappedControl, control_count=MAX_NUM_SENDS)

    def __init__(self,  *a, **k):
        super().__init__( *a, **k)

    @listens_group("devices")
    def __on_devices_changed(self, _):
        self._connect_gain_control()

    def _connect_parameters(self):
        super()._connect_parameters()  # Call base method
        self._connect_gain_control()

    def _connect_gain_control(self):
        if self.check_if_last_device_is_utility():
            last_device = self._track.devices[-1]
            gain_parameter = get_parameter_by_name("Gain", last_device)
            self.gain_control.mapped_parameter = gain_parameter
    
    def update(self):
        super().update()
        if self.is_enabled():
            self._update_listeners()

    def _update_listeners(self):
        if self._track:
            self._ChannelStripComponent__on_devices_changed.replace_subjects([self._track]) #ignore racks and chains

    def set_gain_control(self, encoder):
        self.gain_control.set_control_element(encoder)

    def check_if_last_device_is_utility(self):
        # Check if devices list is not empty
        if self._track.devices:
            # Assuming the utility device is identified by its name or type
            last_device = self._track.devices[-1]
            # Compare if the name of the last device is "Utility"
            if last_device.name == "Utility":
                return True
            else:
                return False
        else:
            return False
        

    def _all_controls(self):
        return chain([
         self.volume_control, self.pan_control, self.gain_control], self.send_controls, self.indexed_send_controls,)
    


# from itertools import chain
# from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
# from ableton.v3.control_surface.controls import MappedControl, control_list
# from ableton.v3.live import get_parameter_by_name, liveobj_valid
# from ableton.v3.base import listens_group, clamp, task
# from .control import ParameterControl

# MAX_NUM_SENDS = 12

# MAX_NUM_SENDS = 12

# class StepAutomationMixin:
#     def _get_envelope(self, clip, parameter):
#         if liveobj_valid(clip) and liveobj_valid(parameter):
#             envelope = clip.automation_envelope(parameter)
#             if not liveobj_valid(envelope):
#                 envelope = clip.create_automation_envelope(parameter)
#             if liveobj_valid(envelope):
#                 if parameter.automation_state == 1:  # AutomationState.overridden
#                     parameter.re_enable_automation()
#                 return envelope
#         return None

#     def _insert_step(self, envelope, parameter, parameter_index, time_step, value):
#         value_to_insert = clamp(value, parameter.min, parameter.max)
#         envelope.insert_step(time_step[0], time_step[1], value_to_insert)

#     def _update_envelope_value(self, parameter):
#         value = parameter.value
#         self.envelope_value = value
#         self.envelope_value_string = parameter.str_for_value(value)

#     def _can_automate_parameters(self):
#         return hasattr(self, '_note_editor') and self._note_editor and self._note_editor.active_steps and liveobj_valid(self._track.clip_slots[0].clip)

#     def _show_envelope_view(self, clip, parameter):
#         clip.view.select_envelope_parameter(parameter)
#         clip.view.show_envelope()

#     def _hide_envelope_view(self):
#         if liveobj_valid(self._track.clip_slots[0].clip):
#             self._track.clip_slots[0].clip.view.hide_envelope()


# class ChannelStripComponent(ChannelStripComponentBase, StepAutomationMixin):
#     gain_control = MappedControl()
#     send_controls = control_list(ParameterControl, control_count=MAX_NUM_SENDS)

#     def __init__(self, *a, **k):
#         super().__init__(*a, **k)
#         self._note_editor = None
#         self.envelope_value = None
#         self.envelope_value_string = None
#         self._tasks = task.TaskGroup()
#         self._hide_envelope_view_task = self._tasks.add(task.sequence(task.wait(3.0), task.run(self._hide_envelope_view)))
#         self._hide_envelope_view_task.kill()

#     def set_note_editor(self, note_editor):
#         self._note_editor = note_editor
#         self.register_slot(note_editor, self._update_envelope_for_steps, 'active_steps')

#     @listens_group("devices")
#     def __on_devices_changed(self, _):
#         self._connect_gain_control()

#     def _connect_parameters(self):
#         super()._connect_parameters()
#         self._connect_gain_control()

#     def _connect_gain_control(self):
#         if self.check_if_last_device_is_utility():
#             last_device = self._track.devices[-1]
#             gain_parameter = get_parameter_by_name("Gain", last_device)
#             self.gain_control.mapped_parameter = gain_parameter

#     def update(self):
#         super().update()
#         if self.is_enabled():
#             self._update_listeners()

#     def _update_listeners(self):
#         if self._track:
#             self._ChannelStripComponent__on_devices_changed.replace_subjects([self._track])

#     def set_gain_control(self, encoder):
#         self.gain_control.set_control_element(encoder)

#     def check_if_last_device_is_utility(self):
#         if self._track.devices:
#             last_device = self._track.devices[-1]
#             return last_device.name == "Utility"
#         return False

#     def _all_controls(self):
#         return chain([self.volume_control, self.pan_control, self.gain_control], self.send_controls, self.indexed_send_controls)

#     @send_controls.value
#     def send_controls(self, value, control):
#         parameter = control.control_element.mapped_object
#         if self._can_automate_parameters():
#             clip = self._track.clip_slots[0].clip
#             envelope = self._get_envelope(clip, parameter)
#             if liveobj_valid(envelope):
#                 value = control.control_element.normalize_value(value)
#                 for step in self._note_editor.active_steps:
#                     self._insert_step(envelope, parameter, control.index, step, value)
#                 self._update_envelope_value(parameter)
#                 self._show_envelope_view(clip, parameter)
#                 self._hide_envelope_view_task.restart()

#     def _update_envelope_for_steps(self):
#         pass  # Optional: Update logic if needed when steps change
