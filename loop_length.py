from ableton.v3.base import depends
from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import ButtonControl, StepEncoderControl
from ableton.v3.control_surface.display import Renderable
from ableton.v3.live import action
FINE_TUNE_FACTOR = 0.25

class LoopLengthComponent(Component, Renderable):
    length_encoder = StepEncoderControl(num_steps=64)
    shift_button = ButtonControl(color=None)

    @depends(sequencer_clip=None)
    def __init__(self, sequencer_clip=None, *a, **k):
        super().__init__(*a, name='Loop_Length', **k)
        self._sequencer_clip = sequencer_clip
        self.register_slot(sequencer_clip, self.update, 'clip')
        self.register_slot(sequencer_clip, self.update, 'length')

    def increment_length(self, delta, modify_end=True):
            clip = self._sequencer_clip.clip
            if not clip:
                return
            # Fine = 1/4 note, Coarse = 1 full note (i.e., 1 beat = 4/4 note)
            if modify_end:
                step_size = FINE_TUNE_FACTOR #if fine_tune else FINE_TUNE_FACTOR * 4
                new_loop_end = clip.loop_end + (delta * step_size)
                # Ensure the loop end doesn't go below one full step
                new_loop_end = max(step_size, new_loop_end)
                action.set_loop_end(clip, new_loop_end)
            else:
                step_size = FINE_TUNE_FACTOR #if fine_tune else FINE_TUNE_FACTOR * 4
                new_loop_start = clip.loop_start + (delta * step_size)
                # Allow the loop start to go all the way to zero (first step)
                new_loop_start = max(0, new_loop_start)
                # Also ensure loop_start doesn't go beyond loop_end - step_size
                new_loop_start = min(new_loop_start, clip.loop_end - step_size)
                action.set_loop_start(clip, new_loop_start)


    def use_fine_steps(self):
        if self.shift_button.control_element:
            return not self.shift_button.is_pressed
        return False

    @length_encoder.value
    def length_encoder(self, value, _):
        self.increment_length(value, modify_end=self.use_fine_steps())

    def update(self):
        super().update()
        self.length_encoder.enabled = self._sequencer_clip.clip is not None