from ableton.v3.base import depends, listenable_property
from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import ButtonControl, StepEncoderControl
from ableton.v3.control_surface.display import Renderable
from ableton.v3.live import action, get_bar_length, is_clip_new_recording
FINE_TUNE_FACTOR = 0.25
import logging
logger = logging.getLogger("XoneK2FXv2")


class LoopLengthComponent(Component, Renderable):
    length_encoder = StepEncoderControl(num_steps=64)
    shift_button = ButtonControl(color=None)

    @depends(sequencer_clip=None)
    def __init__(self, sequencer_clip=None, *a, **k):
        super().__init__(*a, name='Loop_Length', **k)
        self._sequencer_clip = sequencer_clip
        self.register_slot(sequencer_clip, self.update, 'clip')
        self.register_slot(sequencer_clip, self.update, 'length')

    @listenable_property
    def length_string(self):
        num_bars = self._sequencer_clip.num_bars
        if num_bars:
            complete_bars = int(num_bars)
            remainder = self._sequencer_clip.length % get_bar_length(clip=self._sequencer_clip.clip)
            if self.use_fine_steps() or remainder:
                bar_fraction = int(remainder + FINE_TUNE_FACTOR)
                if complete_bars:
                    return '{} + {}/16'.format(complete_bars, bar_fraction)
                return '{}/16'.format(bar_fraction)
            return '1 Bar' if num_bars == 1 else '{} Bars'.format(complete_bars)
        return ''

    def increment_length(self, delta, fine_tune=False):
        logger.info("je suis la")
        clip = self._sequencer_clip.clip
        if not clip:
            return
        bar_length = get_bar_length(clip=clip)
        num_bars = self._sequencer_clip.num_bars
        if num_bars < 1 or (delta < 0 and num_bars == 1):
            fine_tune = True
        step_size = FINE_TUNE_FACTOR if fine_tune else bar_length
        new_loop_end = clip.loop_end + (delta * step_size)
        action.set_loop_end(clip, max(step_size, new_loop_end))

    def use_fine_steps(self):
        if self.shift_button.control_element:
            return not self.shift_button.is_pressed
        return False

    @length_encoder.value
    def length_encoder(self, value, _):
        self.increment_length(value, fine_tune=self.use_fine_steps())
        self.notify_length_string()

    @shift_button.value
    def shift_button(self, *_):
        self.notify_length_string()

    def update(self):
        super().update()
        self.length_encoder.enabled = self._sequencer_clip.clip is not None
        self.notify_length_string()