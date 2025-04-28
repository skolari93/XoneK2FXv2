import math
from sys import maxsize
from ableton.v3.base import depends
from ableton.v3.control_surface import RelativeInternalParameter
from ableton.v3.control_surface.components.bar_based_sequence import NoteEditorComponent as NoteEditorComponentBase
from ableton.v3.control_surface.components.note_editor import get_notes
from ableton.v3.live import liveobj_valid
from .step_color_manager import StepColorManager
import threading
# K2 specific
STEP_TRANSLATION_CHANNEL = 3 #this param here is probably overwritten, translation_channel=STEP_TRANSLATION_CHANNEL i think the translation channel ist the pseudo channel where the scripts sends
DEFAULT_VELOCITY = 100
import logging
logger = logging.getLogger("XoneK2FXv2")

class NoteEditorComponent(NoteEditorComponentBase):
    @depends(volume_parameters=None)
    def __init__(self, volume_parameters=None, *a, **k):
        super().__init__(translation_channel=STEP_TRANSLATION_CHANNEL,*a, **k)
        self._step_start_times = []
        self._step_color_manager = self.register_disconnectable(StepColorManager(update_method=self._update_editor_matrix))
        self._step_color_manager.set_clip(self._clip)
        self._volume_parameters = volume_parameters
        self._velocity_offset_parameter = self.register_disconnectable(RelativeInternalParameter(name='Velocity'))
        self.register_slot(self._velocity_offset_parameter, self.set_velocity_offset, 'delta')
        #self._full_velocity = DEFAULT_VELOCITY

    @property
    def step_color_manager(self):
        return self._step_color_manager

    @property
    def step_start_times(self):
        return self._step_start_times

    def set_velocity_offset(self, delta):
        # Set the new value
        self._modify_note_property('_velocity_offset', 8*delta) #factor 8 is k2 specific

    def get_durations_from_step(self, step):
        notes = self._time_step(step[0]).filter_notes(self._clip_notes)
        return [note.duration for note in notes]

    def get_duration_range_string(self):
        return self._get_property_range_string('duration', lambda value_range: (v + self.step_length for v in value_range), str_fmt='{:.1f}'.format)

    def set_clip(self, clip):
        super().set_clip(clip)
        if hasattr(self, '_step_color_manager'):
            self._step_color_manager.set_clip(self._clip)

    def notify_clip_notes(self):
        if liveobj_valid(self._clip) and self._pitches:
            notes = get_notes(self._clip, self._pitches, 0.0, maxsize, self._pitch_provider.is_polyphonic)
            self._step_start_times = sorted(list({n.start_time for n in notes}))
        super().notify_clip_notes()

    def _on_pad_pressed(self, pad):
        super()._on_pad_pressed(pad)
        self._volume_parameters.add_parameter(pad, self._velocity_offset_parameter)

    def _on_pad_released(self, pad, *a, **k):
        super()._on_pad_released(pad, *a, **k)
        self._volume_parameters.remove_parameter(pad, force=True)

    @staticmethod #also here quantisation options would be great
    def _modify_duration(time_step, duration_offset, note):
        threshold = 0.1
        # Ensure the duration doesn't go below the threshold
        if note.duration < threshold:
            note.duration = threshold
        else:
            # Increase duration, respecting the threshold and the offset
            note.duration = max(note.duration + duration_offset, threshold)

            # Special case: if the duration is exactly threshold and the offset is positive, set it to 0.25
            if note.duration == threshold and duration_offset > 0:
                note.duration = 0.25

    def _visible_page(self):
        """Returns the current page number (0-indexed) based on the current page_time.
        
        Returns:
            int: The current page number (0, 1, 2, etc.)
        """
        if self._page_time <= 0:
            return 0
        
        page_length = self.page_length
        if page_length <= 0:
            return 0
            
        return int(self._page_time / page_length)
    
    def _get_alternate_color_for_step(self, index, visible_steps):
        visible_page = self._visible_page()
        clip_notes = visible_steps[index].filter_notes(self._clip_notes)

        return self._step_color_manager.get_color_for_step(index, visible_steps, clip_notes, visible_page=visible_page)
    
    # K2 specific hardcoded
    def set_matrix(self, matrix):
        self.matrix.set_control_element(matrix)
        
        if matrix:

            for index, button in enumerate(self.matrix):
                # Determine which column this button belongs to
                button_column = index % 8
                
                # Set channel based on column:
                button.channel = 4 if button_column < 4 else 5 # EACH DEVICE NEEDS A SEPERATE TRANSLATION CHANNEL
        self._update_editor_matrix()


    # def _show_velocity(self):
    #     colors = {}
        
    #     # Hole die durchschnittliche oder erste Velocity
    #     velocities = self.get_velocities()  # Annahme: gibt Liste oder Dict
    #     velocity = 0
    #     if isinstance(velocities, dict):
    #         velocity = list(velocities.values())[0] if velocities else 0
    #     elif isinstance(velocities, list):
    #         velocity = velocities[0] if velocities else 0

    #     # Normiere die Velocity (0-127) auf 0-8
    #     num_steps_on = int((velocity / 127) * 8)

    #     for step_index in range(8):
    #         if step_index < num_steps_on:
    #             colors[step_index] = 'NoteEditor.Velocity'  # Eingeschaltete Steps
    #         else:
    #             colors[step_index] = 'NoteEditor.StepEmpty'  # Ausgeschaltete Steps

    #     self.step_color_manager.show_colors(colors)

    # def _show_velocity_temporary(self):
    #     # Zeige Fader-Style Velocity
    #     self._show_velocity()

    #     # Timer zurücksetzen, wenn schon einer läuft
    #     if self._revert_timer is not None:
    #         self._revert_timer.cancel()

    #     # Nach 0.3 Sekunden zurücksetzen
    #     self._revert_timer = threading.Timer(0.3, self.step_color_manager.revert_colors)
    #     self._revert_timer.start()


    