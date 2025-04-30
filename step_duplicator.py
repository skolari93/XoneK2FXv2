from __future__ import absolute_import, print_function, unicode_literals
from builtins import object
from functools import partial
from ableton.v3.base import nop
from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import ButtonControl
from ableton.v3.live import liveobj_valid
ALL_NOTES = -1

def get_transposition_amount(source_step, destination_step):
    transposition = destination_step[0] - source_step[0]
    if ALL_NOTES == source_step[0]:
        transposition = 0
    else:
        if destination_step[0] == ALL_NOTES:
            transposition = source_step[0]
    return transposition


class NullStepDuplicator(object):

    @property
    def is_duplicating(self):
        return False

    def set_clip(self, _):
        pass


def set_loop(clip, loop_start, loop_end):
    if loop_start >= clip.loop_end:
        clip.loop_end = loop_end
        if clip.loop_end == loop_end:
            clip.loop_start = loop_start
            clip.end_marker = loop_end
            clip.start_marker = loop_start
    else:
        clip.loop_start = loop_start
        if clip.loop_start == loop_start:
            clip.loop_end = loop_end
            clip.end_marker = loop_end
            clip.start_marker = loop_start


class StepDuplicatorComponent(Component):
    duplicate_button = ButtonControl()

    def __init__(self, *a, **k):
        (super(StepDuplicatorComponent, self).__init__)(*a, **k)
        self._clip = None
        self._source_step = None
        self._notification_reference = partial(nop, None)

    @property
    def is_duplicating(self):
        return self.duplicate_button.is_pressed and liveobj_valid(self._clip)

    def set_clip(self, clip):
        self._cancel_duplicate()
        self._clip = clip

    def add_step_with_pitch(self, note, step_start, step_end, nudge_offset=0, is_page=False):
        if self.is_enabled():
            if self.is_duplicating:
                current_step = (
                 note,
                 step_start,
                 step_end - step_start,
                 nudge_offset,
                 is_page)
                if self._source_step is not None:
                    self._duplicate_to(current_step)
                else:
                    self._duplicate_from(current_step)

    def add_step(self, step_start, step_end, nudge_offset=0, is_page=False):
        self.add_step_with_pitch(ALL_NOTES, step_start, step_end, nudge_offset, is_page)

    def _duplicate_from(self, source_step):
        from_pitch = source_step[0]
        pitch_span = 1
        if from_pitch == ALL_NOTES:
            from_pitch = 0
            pitch_span = 127
        notes = self._clip.get_notes_extended(from_time=(source_step[1]),
          from_pitch=from_pitch,
          time_span=(source_step[2]),
          pitch_span=pitch_span)
        if len(notes) > 0:
            self._source_step = source_step

    def _duplicate_to(self, destination_step):
        if self._source_step[4] == destination_step[4]:
            if destination_step != self._source_step:
                self._clip.duplicate_region(self._source_step[1], self._source_step[2], destination_step[1] + self._source_step[3], self._source_step[0], get_transposition_amount(self._source_step, destination_step))
        loop_start = destination_step[1]
        loop_end = loop_start + self._source_step[2]
        if destination_step[4]:
            loop_start >= self._clip.loop_start and loop_end <= self._clip.loop_end or set_loop(self._clip, loop_start, loop_end)
        self._source_step = None

    def _cancel_duplicate(self):
        self._source_step = None
        if self._notification_reference() is not None:
            self._notification_reference().hide()

    @duplicate_button.released
    def duplicate_button(self, _):
        self._cancel_duplicate()

    def update(self):
        super(StepDuplicatorComponent, self).update()
        self._cancel_duplicate()
