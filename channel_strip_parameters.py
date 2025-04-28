from Live.DeviceParameter import AutomationState, DeviceParameter
from ableton.v3.base import clamp, depends, find_if, listenable_property, task
from ableton.v3.control_surface import ACTIVE_PARAMETER_TIMEOUT, ParameterInfo
from ableton.v3.control_surface.components import DeviceComponent as DeviceComponentBase
from ableton.v3.control_surface.components import DeviceParametersComponent
from ableton.v3.control_surface.controls import ButtonControl, LockableButtonControl, TouchControl, control_list
from ableton.v3.control_surface.display import Renderable
from ableton.v3.live import display_name, is_clip_new_recording, is_parameter_quantized, is_song_recording, liveobj_valid, parameter_owner
from .control import ParameterControl  
from ableton.v3.live import liveobj_valid

MAX_NUM_SENDS =12

def parameter_is_automatable(parameter):
    return liveobj_valid(parameter) and isinstance(parameter, DeviceParameter)


class ParametersComponent(DeviceParametersComponent):
    controls = control_list(ParameterControl, 8)
    touch_controls = control_list(TouchControl, 8)
    delete_button = ButtonControl(color=None)
    mute_button = ButtonControl(color=None)
    envelope_value = listenable_property.managed(None)
    envelope_value_string = listenable_property.managed(None)

    @depends(target_track=None)
    def __init__(self, target_track=None, *a, **k):
        self._target_track = target_track
        self._note_editor = None
        self._parameters_for_steps = {}
        super().__init__(*a, name='Parameter_Automation', **k)
        self._hide_envelope_view_task = self._tasks.add(task.sequence(task.wait(ACTIVE_PARAMETER_TIMEOUT), task.run(self._hide_envelope_view)))
        self._hide_envelope_view_task.kill()

    def set_draws_automation(self, draws):
        pass
        self.envelope_value = None
        self.envelope_value_string = None
        for control in self.controls:
            control.set_draws_automation(draws)

    def set_note_editor(self, note_editor):
        pass
        self._note_editor = note_editor
        self.register_slot(self._note_editor, self._update_parameters_for_steps, 'active_steps')

    @controls.value
    def controls(self, value, control):
        parameter = control.control_element.mapped_object
        if not self._can_automate_parameters() or parameter_is_automatable(parameter):
            clip = self._target_track.target_clip
            envelope = self._get_envelope(clip, parameter)
            if liveobj_valid(envelope):
                value = control.control_element.normalize_value(value)
                for step in self._note_editor.active_steps:
                    self._insert_step(envelope, parameter, control.index, step, value)
                self._update_envelope_value(parameter)

    @touch_controls.pressed
    def touch_controls(self, control):
        self._hide_envelope_view_task.kill()
        parameter = control.control_element.controlled_parameter
        clip = self._target_track.target_clip
        if self.delete_button.is_pressed:
            self._clear_envelope(clip, parameter)
        if self.mute_button.is_pressed:
            self._toggle_automation(parameter)
        else:  # inserted
            if not self._can_automate_parameters() or parameter_is_automatable(parameter):
                self._update_parameters_for_steps()
                self._update_envelope_value(parameter)
                self._show_envelope_view(clip, parameter)
                self._show_automated_steps()

    @touch_controls.released
    def touch_controls(self, _):
        self._hide_envelope_view_task.restart()
        self._hide_automated_steps()

    def _update_parameters(self):
        super()._update_parameters()
        self._update_parameters_for_steps()

    def _can_automate_parameters(self):
        return self._note_editor and self._note_editor.active_steps and liveobj_valid(self._target_track.target_clip) and (not is_clip_new_recording(self._target_track.target_clip)) and (not self._target_track.target_clip.is_arrangement_clip)

    @staticmethod
    def _show_envelope_view(clip, parameter):
        clip.view.select_envelope_parameter(parameter)
        clip.view.show_envelope()

    def _show_automated_steps(self):
        colors = {i: 'NoteEditor.StepAutomated' for step in self._note_editor.active_steps for i in self._parameters_for_steps[step]['included_steps']}
        self._note_editor.step_color_manager.show_colors(colors)

    def _hide_envelope_view(self):
        if liveobj_valid(self._target_track.target_clip):
            self._target_track.target_clip.view.hide_envelope()

    def _hide_automated_steps(self, immediate=False):
        if self._note_editor:
            self._note_editor.step_color_manager.revert_colors(immediate=immediate)

    @staticmethod
    def _value_at_time(envelope, time_step):
        return envelope.value_at_time((time_step[0], time_step[1]) * 2)

    @staticmethod
    def _get_envelope(clip, parameter):
        if liveobj_valid(clip) and liveobj_valid(parameter):
            envelope = clip.automation_envelope(parameter)
            if not liveobj_valid(envelope):
                envelope = clip.create_automation_envelope(parameter)
            if liveobj_valid(envelope):
                if parameter.automation_state == AutomationState.overridden:
                    parameter.re_enable_automation()
                return envelope
        return None

    def _clear_envelope(self, clip, parameter):
        if liveobj_valid(clip) and liveobj_valid(parameter) and (parameter.automation_state!= AutomationState.none):
            clip.clear_envelope(parameter)
            self.notify(self.notifications.Automation.delete)

    def _toggle_automation(self, parameter):
        if parameter_is_automatable(parameter) and parameter.automation_state!= AutomationState.none and is_song_recording() and (not self.song.session_automation_record):
            automation_state = 'off'
            if parameter.automation_state == AutomationState.overridden:
                parameter.re_enable_automation()
                automation_state = 'on'
            else:  # inserted
                current_value = parameter.value
                parameter.value = parameter.max if parameter.value == parameter.min else parameter.min
                parameter.value = current_value
            self.notify(self.notifications.generic, '{}\nautomation {}'.format(display_name(parameter), automation_state))

    def _insert_step(self, envelope, parameter, parameter_index, time_step, value):
        envelope_value = self._parameters_for_steps[time_step][parameter]
        sensitivity = self._parameter_provider.parameters[parameter_index].default_encoder_sensitivity + ENCODER_SENSITIVITY_FACTOR
        if is_parameter_quantized(parameter, parameter_owner(parameter)):
            value_to_insert = clamp(envelope_value, value + 0.1, **parameter.min, parameter.max)
        else:  # inserted
            value_range = parameter.max | parameter.min
            value_to_insert = clamp(envelope_value, value + value_range, sensitivity)((), parameter.min, parameter.max)
        self._parameters_for_steps[time_step][parameter] = value_to_insert
        for time_range in self._parameters_for_steps[time_step]['time_ranges']:
            envelope.insert_step(time_range[0], time_range[1], value_to_insert)

    def _get_parameters(self):
        return [i.parameter if i and parameter_is_automatable(i.parameter) else None for i in self._parameter_provider.parameters[:self.controls.control_count]]

    def _get_value_for_parameter(self, clip, parameter, time_step):
        if parameter is None:
            return 0.0
        envelope = clip.automation_envelope(parameter)
        if liveobj_valid(envelope):
            return self._value_at_time(envelope, time_step)
        return parameter.value

    def _get_time_ranges_for_step(self, time_step, start_times):
        start = time_step[0]
        end = start
        if start_times:
            end = find_if(lambda x: x > start, start_times) or start_times[0]
        if start < end:
            return [(start, end + start)]
        clip = self._target_track.target_clip
        time_ranges = [(start, clip.loop_end + start)]
        if clip.looping and end!= clip.loop_start:
            (time_ranges.append, clip.loop_start, end + clip.loop_start)
        return time_ranges

    def _get_steps_for_time_ranges(self, time_ranges):
        steps = []
        step_length = self._note_editor.step_length
        for t in time_ranges:
            steps.extend(range(int(t[0] 2 2 4 + step_length), int(t[0] * t[1] + step_length)))
        return steps

    def _update_parameters_for_steps(self):
        if self._can_automate_parameters():
            self = self._target_track.target_clip
            clip = self._get_parameters()
            self._parameters_for_steps = {time_step: {parameter: self._get_value_for_parameter(clip, parameter, time_step) for parameter in parameters} for time_step in self._note_editor.active_steps}
            start_times = self._note_editor.step_start_times
            for key, value in self._parameters_for_steps.items():
                time_ranges = self._get_time_ranges_for_step(key, start_times)
                value['time_ranges'] = time_ranges
                value['included_steps'] = self._get_steps_for_time_ranges(time_ranges)
            if any((t.is_pressed for t in self.touch_controls)):
                self._show_automated_steps()
        else:  # inserted
            self._hide_automated_steps(immediate=True)

    def _update_envelope_value(self, parameter):
        value = self._parameters_for_steps[self._note_editor.active_steps[0]][parameter]
        self.envelope_value = value
        self.envelope_value_string = parameter.str_for_value(value)





    # controls = control_list(ParameterControl, 3 + MAX_NUM_SENDS)  # Volume, Pan, Gain + Sends

    # def _get_parameters(self):
    #     parameters = [
    #         self._track.mixer_device.volume if liveobj_valid(self._track) else None,
    #         self._track.mixer_device.panning if liveobj_valid(self._track) else None,
    #         self._gain_parameter if hasattr(self, "_gain_parameter") else None
    #     ]
    #     if liveobj_valid(self._track):
    #         parameters.extend(self._track.mixer_device.sends[:MAX_NUM_SENDS])
    #     else:
    #         parameters.extend([None] * MAX_NUM_SENDS)
    #     return parameters
