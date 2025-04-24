from bisect import bisect_left, bisect_right
from ableton.v3.base import listenable_property, round_to_multiple
from ableton.v3.control_surface.components.bar_based_sequence import LoopSelectorComponent as LoopSelectorComponentBase
from ableton.v3.control_surface.components.bar_based_sequence import get_relative_page_time
from ableton.v3.control_surface.controls import ButtonControl
from ableton.v3.control_surface import LiveObjSkinEntry
from ableton.v3.live import is_clip_new_recording, is_clip_playing
from typing import NamedTuple
from ableton.v3.live import liveobj_changed

BARS_PER_BANK = 8
HEIGHT = 4 # this is inversed. the code thinks transposed
WIDTH = 2

class LoopOverviewData(NamedTuple):
    overview_start_position: float
    overview_end_position: float
    current_position: float
    loop_start_position: float
    loop_end_position: float
    playing_position: float
    length_of_one_bar_in_beats: float


class LoopSelectorComponent(LoopSelectorComponentBase):
    next_bank_button = ButtonControl(color='LoopSelector.Navigation', pressed_color='LoopSelector.NavigationPressed')
    prev_bank_button = ButtonControl(color='LoopSelector.Navigation', pressed_color='LoopSelector.NavigationPressed')
    loop_overview_data = listenable_property.managed(None)

    def __init__(self, bars_per_bank=BARS_PER_BANK, *a, **k):
        self._bars_per_bank = bars_per_bank
        self._bank_offset = 0.0
        super().__init__(*a, **k)
        self.matrix.dimensions = (WIDTH, HEIGHT)

    @property
    def bank_end(self):
        return self._bank_offset + self.bank_length

    @property
    def bank_length(self):
        return self.bar_length * self._bars_per_bank

    @property
    def bank_offset(self):
        return self._bank_offset

    @prev_bank_button.pressed
    def prev_bank_button(self, _):
        self._increment_bank(-1)

    @next_bank_button.pressed
    def next_bank_button(self, _):
        self._increment_bank(1)

    def _increment_bank(self, delta):
        bank_length = self.bank_length
        bank_start = round_to_multiple(self._paginator.page_time, bank_length)
        loop_start = self._get_loop_start()
        positions = sorted([bank_start, bank_length * delta + bank_start, loop_start])

        fn = bisect_right if delta > 0 else lambda pos, val: max(0, bisect_left(pos, val) - 1)
        index = fn(positions, self._paginator.page_time)

        # Sicherheits-Check für den Index
        index = max(0, min(index, len(positions) - 1))

        self._set_bank_offset(positions[index], set_page_time=True)
        self._notify_page_time()


    def _increment_page_time(self, delta):
        bar_length = self.bar_length
        page_time = get_relative_page_time(self._paginator.page_time, self._paginator.page_length, bar_length, delta)
        if self._should_drag_bank_offset(page_time, bar_length, delta):
            self._set_bank_offset(self._bank_offset + bar_length * delta)
        self._paginator.page_time = page_time
        self._notify_page_time()

    def _should_drag_bank_offset(self, page_time, bar_length, delta):
        is_at_bar_start = round_to_multiple(page_time, bar_length) == page_time
        if is_at_bar_start:
            loop_start = self._get_loop_start()
            loop_end = self._clip.loop_end
            bank_start = self._bank_offset
            bank_end = self.bank_end
            loop_outside_bank = loop_start < bank_start or loop_end > bank_end
            if delta > 0 and (page_time >= bank_end or (loop_outside_bank and page_time <= loop_start)):
                return True
            if delta < 0 and (page_time < bank_start or (loop_outside_bank and page_time == loop_end < bar_length)):
                return True
        return False

    def _set_bank_offset(self, offset, set_page_time=False):
        if self._bank_offset != offset:
            self._bank_offset = max(offset, self.min_page_time)
        if set_page_time and self._paginator.page_time != self._bank_offset:
            self._paginator.page_time = self._bank_offset

    def _button_position(self, button_index):
        return button_index * self.bar_length + self._bank_offset

    def _on_clip_changed(self):
        if self._clip and self._paginator.can_change_page:
            self._set_bank_offset(self._get_bank_offset_for_clip())

    def _get_bank_offset_for_clip(self):
        loop_start = self._get_loop_start()
        bank_start = self._get_loop_start(round_to_bank=True)
        if loop_start >= bank_start and self._clip.loop_end <= bank_start + self.bank_length:
            return bank_start
        return loop_start

    def _get_loop_start(self, round_to_bank=False):
        return round_to_multiple(self._clip.loop_start, self.bank_length if round_to_bank else self.bar_length)

    def _update_matrix(self):
        super()._update_matrix()
        self.loop_overview_data = self._get_loop_overview_data()


    #i use this to overwrite the playhead color. atm it does not really work.
    def _update_matrix_button(self, button, selected, playing, inside_loop):
        color = "OutsideLoop"
        # if playing:
        #     color = "PlayheadRecord" if self.song.session_record else "Playhead"
        # else:
        if inside_loop:
            color = "InsideLoopSelected" if selected else "InsideLoop"
        else:
            if selected:
                color = "OutsideLoopSelected"
        button.color = LiveObjSkinEntry("LoopSelector.{}".format(color), self._target_track.target_track)
    
    #this as well
    def set_clip(self, clip):
        if liveobj_changed(clip, self._clip):
            #self._LoopSelectorComponent__on_playing_position_changed.subject = clip
            #self._LoopSelectorComponent__on_playing_status_changed.subject = clip
            self._clip = clip
            if clip:
                if self._paginator.can_change_page:
                    self._paginator.page_time = clip.loop_start
            self.update()

    def _get_loop_overview_data(self):
        if not self._has_clip():
            return None
            
        # If this is a newly recorded clip, use alternate data generation
        if is_clip_new_recording(self._clip):
            return self._get_new_clip_loop_overview_data(self._clip)

        # Round the current page time to the nearest bar length
        current = round_to_multiple(self._paginator.page_time, self.bar_length)

        # Apply a positive offset if the bank offset is negative
        current_offset = abs(self._bank_offset) if self._bank_offset < 0.0 else 0.0
        current += current_offset

        # Define the visible bank's start and end times
        bank_start = self._bank_offset + current_offset
        bank_end = self.bank_end + current_offset

        # Determine loop start and end positions, with offset applied
        loop_start = self._get_loop_start() + current_offset
        loop_end = self._clip.loop_end + current_offset

        # Establish the overview's time range
        overview_start = min(current, loop_start)
        overview_end = max(current + self.bar_length, loop_end)

        # Clamp the overview if the loop range exceeds the visible bank
        if loop_start < bank_start or loop_end > bank_end:
            overview_start = bank_start
            overview_end = bank_end

        # Determine if the clip is playing and, if so, whether it's in view
        playing = -1.0  # Default: not playing
        position = None
        if is_clip_playing(self._clip):
            position = self._clip.playing_position + current_offset
            if overview_start <= position <= overview_end:
                playing = position

        # Package and return overview data
        return self._make_loop_overview_data(
            overview_start,
            overview_end,
            current,
            loop_start,
            loop_end,
            playing
        )

    def _get_new_clip_loop_overview_data(self, clip):
        position = min(clip.playing_position, self.bank_length)
        return self._make_loop_overview_data(
            overview_start=0.0,
            overview_end=position,
            current=0.0,
            loop_start=0.0,
            loop_end=position,
            playing=position
        )

    def _make_loop_overview_data(self, overview_start=0.0, overview_end=0.0, current=0.0, loop_start=0.0, loop_end=0.0, playing=-1.0):
        return LoopOverviewData(
            overview_start_position=overview_start,
            overview_end_position=overview_end,
            current_position=current,
            loop_start_position=loop_start,
            loop_end_position=loop_end,
            playing_position=playing,
            length_of_one_bar_in_beats=self.bar_length
        )

    def _update_page_buttons(self):
        super()._update_page_buttons()
        has_clip = self._has_clip()
        self.prev_bank_button.enabled = has_clip and self._bank_offset > self.min_page_time
        self.next_bank_button.enabled = has_clip

