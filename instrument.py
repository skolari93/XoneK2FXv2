from ableton.v3.base import EventObject, MultiSlot, depends, find_if, index_if, listenable_property, listens, task
from ableton.v3.control_surface import LiveObjSkinEntry
from ableton.v3.control_surface.components import Pageable, PageComponent, PitchProvider, PlayableComponent
from ableton.v3.control_surface.controls import ButtonControl, StepEncoderControl
from ableton.v3.control_surface.display import Renderable
from ableton.v3.live import action
from .melodic_pattern import CHROMATIC_MODE_OFFSET, SCALES, MelodicPattern

DEFAULT_SCALE = SCALES[0]
import logging
logger = logging.getLogger("XoneK2FXv2")

class NoteLayout(EventObject, Renderable):
    @depends(song=None)
    def __init__(self, song=None, preferences=None, *a, **k):
        super().__init__(*a, **k)
        self._song = song
        self._scale = self._get_scale_from_name(self._song.scale_name)
        self._preferences = preferences if preferences is not None else {}
        self._scale_mode = True #self._preferences.setdefault('scale_mode', False)
        self.__on_root_note_changed.subject = self._song
        self.__on_scale_name_changed.subject = self._song
        self.__on_scale_mode_changed.subject = self._song

    @property
    def notes(self):
        return self.scale.to_root_note(self.root_note).notes

    @listenable_property
    def root_note(self):
        return self._song.root_note

    @root_note.setter
    def root_note(self, root_note):
        self._song.root_note = root_note

    @listenable_property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale
        self._song.scale_name = scale.name
        self.notify_scale(self._scale)

    @listenable_property
    def scale_mode(self):
        return self._scale_mode

    @scale_mode.setter
    def scale_mode(self, scale_mode):
        self._scale_mode = scale_mode
        self._song.scale_mode = self._scale_mode
        self.notify_scale_mode(self._scale_mode)

    def toggle_scale_mode(self):
        self._scale_mode = not self._scale_mode

    def _get_scale_from_name(self, name):
        return find_if(lambda scale: scale.name == name, SCALES) or DEFAULT_SCALE

    @listens('root_note')
    def __on_root_note_changed(self):
        self.notify_root_note(self._song.root_note)

    @listens('scale_name')
    def __on_scale_name_changed(self):
        self._scale = self._get_scale_from_name(self._song.scale_name)
        self.notify_scale(self._scale)

    @listens('scale_mode')
    def __on_scale_mode_changed(self):
        self.toggle_scale_mode()
        self.notify_scale(self._scale_mode)

class InstrumentComponent(PlayableComponent, PageComponent, Pageable, Renderable, PitchProvider):
    delete_button = ButtonControl(color=None)
    octave_encoder = StepEncoderControl(num_steps=64)

    is_polyphonic = True
    
    # Constants for the 4x4 grid
    GRID_WIDTH = 12
    GRID_HEIGHT = 2
    DEFAULT_FIRST_NOTE = 36  # C2 by default

    @depends(note_layout=None, target_track=None)
    def __init__(self, note_layout=None, target_track=None, *a, **k):
        super().__init__(
            *a, 
            name='Instrument', 
            scroll_skin_name='Instrument.Scroll', 
            matrix_always_listenable=True, 
            **k
        )
        self._note_layout = note_layout
        self._target_track = target_track
        self._first_note = self.DEFAULT_FIRST_NOTE
        self._pattern = self._get_pattern()
        self._note_editor = None
        self.pitches = [self._pattern.note(0, 0).index]
        self._last_page_length = self.page_length
        self._last_page_offset = self.page_offset
        
        # Register for note layout events
        for event in ['scale', 'root_note', 'scale_mode']:
            self.register_slot(self._note_layout, self._on_note_layout_changed, event)
        
        # Register for track events
        self.register_slot(
            MultiSlot(
                subject=self._target_track, 
                listener=self._update_led_feedback, 
                event_name_list=('target_track', 'color_index')
            )
        )
        
        # Setup chord detection task
        self._chord_detection_task = self._tasks.add(task.wait(0.3))
        self._chord_detection_task.kill()
        
        self._update_pattern()

    @property
    def note_layout(self):
        return self._note_layout

    @octave_encoder.value
    def octave_encoder(self, value, _):
        offset = 6 #somehow i have to do 6 mpt 12
        logger.info(self.position)
        logger.info(value * offset)
        self.position = max(0, min(127, self.position + value * offset))   

    def set_octave_encoder(self, encoder):
        self.octave_encoder.set_control_element(encoder)

    @property
    def page_length(self):
        return len(self._note_layout.notes) if self._note_layout.scale_mode else 12

    @property
    def position_count(self):
        """Calculate the total number of available positions"""
        if not self._note_layout.scale_mode:
            return 128  # Standard MIDI note range
        
        # Calculate based on scale notes and octaves
        octaves = 10  # Standard octave range
        return len(self._note_layout.notes) * octaves

    def _get_first_scale_note_offset(self):
        """Calculate the offset for the first note in the scale"""
        if not self._note_layout.scale_mode:
            return self._note_layout.notes[0]
        
        if self._note_layout.notes[0] == 0:
            return 0
        
        # Find the index of the first note that's >= 12, or use the length if none found
        for i, note in enumerate(self._note_layout.notes):
            if note >= 12:
                return i
        return len(self._note_layout.notes)

    @property
    def page_offset(self):
        return self._get_first_scale_note_offset()

    @property
    def position(self):
        return self._first_note

    @position.setter
    def position(self, note):
        self._first_note = note
        self._update_pattern()
        self._update_matrix()
        self.notify_position()

    @property
    def min_pitch(self):
        return self.pattern.note(0, 0).index

    @property
    def max_pitch(self):
        identifiers = [control.identifier for control in self.matrix if control.identifier is not None]
        return max(identifiers) if identifiers else 127

    @property
    def pattern(self):
        return self._pattern

    def set_note_editor(self, note_editor):
        self._note_editor = note_editor
        self.__on_active_steps_changed.subject = note_editor

    def _on_matrix_pressed(self, button):
        """Handle matrix button press events"""
        pitch = self._get_note_info_for_coordinate(button.coordinate).index
        
        if pitch is None:
            return
            
        if self.delete_button.is_pressed:
            button.color = 'Instrument.PadAction'
            if action.delete_notes_with_pitch(self._target_track.target_clip, pitch):
                self.notify(self.notifications.Notes.Pitch.delete, pitch)
            else:
                self.notify(self.notifications.Notes.error_no_notes_to_delete)
            return
            
        if self.select_button.is_pressed and pitch not in self.pitches:
            self.notify(self.notifications.Notes.Pitch.select, pitch)
            
        if self._note_editor and self._note_editor.active_steps:
            self._note_editor.toggle_pitch_for_all_active_steps(pitch)
        else:
            if self._chord_detection_task.is_running:
                self.pitches.append(pitch)
            else:
                self.pitches = [pitch]
                self._chord_detection_task.restart()
                
        self._update_button_color(button)

    @delete_button.value
    def delete_button(self, _, button):
        self._set_control_pads_from_script(button.is_pressed)

    def scroll_page_up(self):
        """Scroll up by octaves"""
        super().scroll_page_up()
        self.notify(self.notifications.Notes.Octave.up)

    def scroll_page_down(self):
        """Scroll down by octaves"""
        super().scroll_page_down()
        self.notify(self.notifications.Notes.Octave.down)

    def scroll_up(self):
        """Scroll up by scale degrees"""
        super().scroll_up()
        self.notify(self.notifications.Notes.ScaleDegree.up)

    def scroll_down(self):
        """Scroll down by scale degrees"""
        super().scroll_down()
        self.notify(self.notifications.Notes.ScaleDegree.down)

    def _align_first_note(self):
        """Align the first note based on the current scale and key settings"""
        # Calculate a sensible default position based on the current page settings
        scale_length = len(self._note_layout.notes)
        
        # Adjust for changes in scale length or offset
        if self._last_page_length != self.page_length or self._last_page_offset != self.page_offset:
            # Calculate a middle octave position
            middle_octave = 3
            self._first_note = self.page_offset + middle_octave * scale_length
            
            # Ensure we're within the valid range
            if self._first_note >= self.position_count:
                self._first_note = scale_length  # Reset to first octave
                
        self._last_page_length = self.page_length
        self._last_page_offset = self.page_offset

    def _on_note_layout_changed(self, _):
        self._update_scale()

    def _update_scale(self):
        self._align_first_note()
        self._update_pattern()
        self._update_matrix()
        self.notify_position()



    def update(self):
        super().update()
        if self.is_enabled():
            self._update_matrix()

    def _update_pattern(self):
        self._pattern = self._get_pattern()

    def _invert_and_swap_coordinates(self, coordinates):
        """Transform the coordinates for the 4x4 grid layout"""
        # For a 4x4 grid with inverted coordinates (bottom-to-top)
        x, y = coordinates
        return (y, self.GRID_HEIGHT - 1 - x)

    def _get_note_info_for_coordinate(self, coordinate):
        x, y = self._invert_and_swap_coordinates(coordinate)
        return self.pattern.note(x, y)

    def _update_button_color(self, button):
        """Update the color of a specific button based on its state"""
        note_info = self._get_note_info_for_coordinate(button.coordinate)
        color = LiveObjSkinEntry(f'Instrument.{note_info.color}', self._target_track.target_track)
        
        if self._note_editor:
            if self._note_editor.active_steps and self._note_editor.is_pitch_active(button.identifier):
                color = 'Instrument.NoteInStep'
            elif button.identifier in self.pitches:
                color = 'Instrument.NoteSelected'
                
        button.color = color

    def _button_should_be_enabled(self, button):
        return self._get_note_info_for_coordinate(button.coordinate).index is not None

    def _note_translation_for_button(self, button):
        note_info = self._get_note_info_for_coordinate(button.coordinate)
        return (note_info.index, note_info.channel)

    def _update_matrix(self):
        """Update the entire matrix display"""
        self._update_control_from_script()
        self._update_note_translations()
        self._update_led_feedback()

    @listens('active_steps')
    def __on_active_steps_changed(self):
        self._update_led_feedback()

    def _get_pattern(self, first_note=None):
        """Create a melodic pattern based on current settings"""
        if first_note is None:
            first_note = int(round(self._first_note))
            
        interval = len(self._note_layout.notes)
        notes = self._note_layout.notes
        width = self.GRID_WIDTH
        height = self.GRID_HEIGHT
        
        # Calculate octave based on first note and scale length
        octave = first_note // len(self._note_layout.notes)
        offset = self._get_first_scale_note_offset()
        
        if self._note_layout.scale_mode:
            # In-key mode: each row is consecutive scale notes
            steps = [1, int(interval*0.5)]  # Move right by 1 scale note, up by octave
        else:
            # Chromatic mode: each row is a perfect fourth (5 semitones)
            interval = 12
            offset = offset + CHROMATIC_MODE_OFFSET
            steps = [1, interval]  # Move right by semitone, up by perfect fourth
            
        origin = [offset, 0]
        
        return MelodicPattern(
            steps=steps, # steps
            scale=notes,
            origin=origin,
            root_note=octave * 12,
            chromatic_mode=not self._note_layout.scale_mode,
            width=width,
            height=height
        )