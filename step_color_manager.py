
from functools import partial
from ableton.v3.base import EventObject, depends, listens, task
from ableton.v3.control_surface import ACTIVE_PARAMETER_TIMEOUT
from ableton.v3.live import liveobj_valid

from ableton.v3.control_surface.components import GRID_RESOLUTIONS

def get_value_from_label(label):
    for res in GRID_RESOLUTIONS:
        if res[0] == label:
            return res[1]
    return None  # or raise an error

import logging
logger = logging.getLogger("XoneK2FXv2")

class StepColorManager(EventObject):
    @depends(song=None, parent_task_group=None, update_method=None)
    def __init__(self, song=None, parent_task_group=None, update_method=None, *a, **k):
        super().__init__(*a, **k)
        self.song = song
        self.clip = None
        self._colors = {}
        self._update_method = update_method
        self._last_beat = None
        self.register_slot(self.song, self._update_method, 'is_playing')
        self._tasks = parent_task_group
        self._revert_colors_task = self._tasks.add(task.sequence(task.wait(ACTIVE_PARAMETER_TIMEOUT), task.run(partial(self.show_colors, {}))))
        self._revert_colors_task.kill()


    def set_clip(self, clip):
        self.clip = clip if liveobj_valid(clip) else None
        self.__on_song_time_changed.subject = None if self.clip else self.song
        self.__on_loop_end_changed.subject = self.clip
        self.__on_loop_start_changed.subject = self.clip
        if self.clip and self.song.is_playing:
            self._update_method()

    def show_colors(self, colors_for_steps):
        self._revert_colors_task.kill()
        self._colors = colors_for_steps
        self._update_method()

    def revert_colors(self, immediate=False):
        if immediate:
            self.show_colors({})
        else:
            self._revert_colors_task.restart()

    def get_color_for_step(self, index, visible_steps, clip_notes, visible_page=0):
        if self._last_beat is not None:
            if self.clip is None and self.song.is_playing and (index in visible_steps) and (index == self._last_beat*4):
                return 'NoteEditor.Playhead'

        if self.clip:
            if (index in visible_steps):
                if self.clip.loop_end <= get_value_from_label("1/16")*(index + visible_page * len(visible_steps)) : # only works with 16th notes atm
                    notes = visible_steps[index].filter_notes(clip_notes)
                    if len(notes) > 0:
                        if any((n.mute for n in notes)):
                            return 'NoteEditor.NotInLoopStepMuted'
                        else:  # inserted
                            return 'NoteEditor.NotInLoopStepFilled'
                    else:
                        return 'NoteEditor.NotInLoop'
                return self._colors.get(index, None)


    @listens('current_song_time')
    def __on_song_time_changed(self):
        beat = int(self.song.get_current_beats_song_time().beats)-  1
        if beat != self._last_beat:
            self._last_beat = beat
            self._update_method()

    @listens("loop_start")
    def __on_loop_start_changed(self):
        self._update_method()

    @listens("loop_end")
    def __on_loop_end_changed(self):
        self._update_method()