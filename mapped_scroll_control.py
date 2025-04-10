# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.12.2 (main, Feb  6 2024, 20:19:44) [Clang 15.0.0 (clang-1500.1.0.2.5)]
# Embedded file name: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v3/control_surface/components/scroll.py
# Compiled at: 2024-03-11 15:53:16
# Size of source mod 2**32: 5388 bytes
from __future__ import absolute_import, print_function, unicode_literals
from ...base import task
from .. import MOMENTARY_DELAY, Component
from ..controls import ButtonControl, StepEncoderControl
from ableton.v3.live import action

class Scrollable:
    can_scroll_up = NotImplemented
    can_scroll_down = NotImplemented
    scroll_up = NotImplemented
    scroll_down = NotImplemented


class ScrollComponent(Component, Scrollable):
    scrolling_delay = MOMENTARY_DELAY
    scrolling_step_delay = 0.1
    scroll_encoder = StepEncoderControl(num_steps=64)
    scroll_up_button = MappedButtonControl()
    scroll_down_button = MappedButtonControl()

    def __init__(self, scrollable=None, scroll_skin_name=None, *a, **k):
        (super().__init__)(*a, **k)

        self._scroll_task_up = self._make_scroll_task(self._do_scroll_up)
        self._scroll_task_down = self._make_scroll_task(self._do_scroll_down)
        self._scrollable = scrollable or self

    def _make_scroll_task(self, scroll_step):
        t = self._tasks.add(task.sequence(task.wait(self.scrolling_delay), task.loop(task.wait(self.scrolling_step_delay), task.run(scroll_step))))
        t.kill()
        return t

    def can_scroll_up(self):
        return self._scrollable.can_scroll_up()

    def can_scroll_down(self):
        return self._scrollable.can_scroll_down()

    def scroll_up(self):
        return self._scrollable.scroll_up()

    def scroll_down(self):
        return self._scrollable.scroll_down()

    def set_scroll_encoder(self, encoder):
        self.scroll_encoder.set_control_element(encoder)

    @scroll_encoder.value
    def scroll_encoder(self, value, _):
        if value < 0:
            if self.can_scroll_up():
                self.scroll_up()
        elif self.can_scroll_down():
            self.scroll_down()

    def _do_scroll_up(self):
        self.scroll_up()
        self._update_scroll_buttons()

    def _do_scroll_down(self):
        self.scroll_down()
        self._update_scroll_buttons()

    def update(self):
        super().update()
        self._update_scroll_buttons()

    def _on_scroll_released(self, scroll_task):
        scroll_task.kill()
        self._ensure_scroll_one_direction()

    def _ensure_scroll_one_direction(self):
        if self.scroll_up_button.is_pressed and self.scroll_down_button.is_pressed:
            self._scroll_task_up.pause()
            self._scroll_task_down.pause()
        else:
            self._scroll_task_up.resume()
            self._scroll_task_down.resume()
