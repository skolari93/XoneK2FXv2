from ableton.v3.control_surface.components import GRID_RESOLUTIONS as RESOLUTIONS_BASE
from ableton.v3.control_surface.components import StepSequenceComponent as StepSequenceComponentBase
from ableton.v3.control_surface.components.bar_based_sequence import PlayheadComponent
from itertools import chain, starmap
from .loop_selector import LoopSelectorComponent
from .note_editor import NoteEditorComponent
from .note_settings import NoteSettingsComponent
  
GRID_RESOLUTIONS = tuple(reversed(RESOLUTIONS_BASE[:-3]))
DEFAULT_GRID_RESOLUTION_INDEX = 1
PLAYHEAD_NOTES = []#[28, 29, 30, 31, 28, 29, 30, 31, 24, 25, 26, 27, 24, 25, 26, 27]
PLAYHEAD_CHANNELS = []#[12]#list(range(0,15))
from functools import partial


#not used custom_loop_selector = partial(LoopSelectorComponent, bars_per_bank=8)
class StepSequenceComponent(StepSequenceComponentBase):
    # list(chain(range(36, 40),range(32, 37),range(28, 32),range(24, 28))) 
    def __init__(self, *a, **k):
        super().__init__(*a, note_editor_component_type=NoteEditorComponent, loop_selector_component_type=LoopSelectorComponent, playhead_channels=PLAYHEAD_CHANNELS, playhead_component_type=PlayheadComponent, playhead_notes=PLAYHEAD_NOTES, playhead_triplet_notes=[16, 17, 18, 20, 21, 22, 24, 25, 26, 28, 29, 30], **k)
        #super().__init__(*a, note_editor_component_type=NoteEditorComponent, loop_selector_component_type=LoopSelectorComponent, playhead_channels=[15], playhead_component_type=PlayheadComponent, playhead_notes=list(chain(range(36, 52))), playhead_triplet_notes=[16, 17, 18, 20, 21, 22, 24, 25, 26, 28, 29, 30], **k)
        self._note_settings = NoteSettingsComponent(self._note_editor, parent=self)
        self._playhead.set_note_editor(self._note_editor)

    @property
    def note_settings(self):
        return self._note_settings

    def set_copy_button(self, button):
        self._note_editor.set_copy_button(button)

    def set_note_displacement_encoder(self, encoder):
        self._note_editor.set_note_displacement_encoder(encoder)

    def set_duration_encoder(self, encoder):
        self._note_settings.set_duration_encoder(encoder)
    
    def set_duration_fine_encoder(self, encoder):
        self._note_settings.set_duration_fine_encoder(encoder)

    def set_shift_length_button(self, button):
        self._note_settings.shift_length_button.set_control_element(button)

    def set_transpose_encoder(self, encoder):
        self._note_settings.set_transpose_encoder(encoder)

    def set_transpose_octave_encoder(self, encoder):
        self._note_settings.set_transpose_octave_encoder(encoder)

    def set_nudge_encoder(self, encoder):
        self._note_settings.set_nudge_encoder(encoder)


    def set_ratchet_encoder(self, encoder):
        self._note_settings.set_ratchet_encoder(encoder)

    def set_prev_bank_button(self, button):
        self._loop_selector.prev_bank_button.set_control_element(button)

    def set_next_bank_button(self, button):
        self._loop_selector.next_bank_button.set_control_element(button)
    
    def set_matrix(self, matrix):
        self._loop_selector.matrix.set_control_element(matrix)
        