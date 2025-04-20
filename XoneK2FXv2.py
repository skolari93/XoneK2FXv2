import os
from ableton.v3.base import const, listens
from ableton.v3.control_surface import (
    ControlSurface,
    ControlSurfaceSpecification,
    create_skin,
)
from .elements import Elements
from .mappings import create_mappings
from .skin import Skin
from .colors import Rgb
from .session import SessionComponent
from .fx_mixer import FXMixerComponent
from .master_mixer import MasterMixerComponent
from .mixer import MixerComponent
from ableton.v3.control_surface.components import ViewControlComponent, SessionRingComponent, SessionNavigationComponent #,StepSequenceComponent, GRID_RESOLUTIONS
from functools import partial

from ableton.v3.live import liveobj_valid
from .instrument import InstrumentComponent, NoteLayout
from .step_sequence import DEFAULT_GRID_RESOLUTION_INDEX, GRID_RESOLUTIONS, StepSequenceComponent
from ableton.v3.control_surface.components import GridResolutionComponent, SequencerClip
PITCH_PROVIDERS = {'instrument': 'Instrument'}

import logging
logger = logging.getLogger("XoneK2FXv2")


def tracks_to_use_from_song(song):
    return tuple(song.visible_tracks) + tuple(song.return_tracks)

def note_mode_for_track(track, instrument_finder):
    if liveobj_valid(track) and track.has_midi_input:
        if liveobj_valid(instrument_finder.drum_group):
            return 'drum'
        if liveobj_valid(instrument_finder.sliced_simpler):
            return 'simpler'
        return 'instrument'
    return 'audio'

class XoneK2FXv2(ControlSurface):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        self.log_level = "info"

        self.start_logging()

        self.show_message("XoneK2FXv2: init mate")
        logger.info("XoneK2FXv2: init started ...")
        #logger.info(dir(Live.Browser.Browser.audio_effects.children))


    def disconnect(self):
        self.show_message("Disconnecting...")
        logger.info("Disconnecting...")
        self.stop_logging()
        super().disconnect()

    def setup(self):
        super().setup()
        self.init()
        note_editor = self.component_map['Step_Sequence'].note_editor
        self.component_map['Instrument'].set_note_editor(note_editor)

    def init(self):
        logger.info("init started:")
        with self.component_guard():
            logger.info("   adding skin")
            self._skin = create_skin(skin=Skin, colors=Rgb)

    def start_logging(self):
        module_path = os.path.dirname(os.path.realpath(__file__))
        log_dir = os.path.join(module_path, "logs")
        if not os.path.exists(log_dir):
            os.mkdir(log_dir, 0o755)
        log_path = os.path.join(log_dir, "xoneK2FXv2.log")
        self.log_file_handler = logging.FileHandler(log_path)
        self.log_file_handler.setLevel(self.log_level.upper())
        formatter = logging.Formatter("(%(asctime)s) [%(levelname)s] %(message)s")
        self.log_file_handler.setFormatter(formatter)
        logger.addHandler(self.log_file_handler)

    def stop_logging(self):
        logger.removeHandler(self.log_file_handler)

    def _get_additional_dependencies(self):
        fx_ring = SessionRingComponent(
            name='fx_ring',
            num_tracks=3,
            num_scenes=0,
            tracks_to_use=partial(fx_tracks, self.song),
        )
        self.component_map["FXRing"] = fx_ring

        master_ring = SessionRingComponent(
            name='master_ring',
            num_tracks=1,
            num_scenes=0,
            tracks_to_use=partial(master_track, self.song),
        )

        self.component_map["MasterRing"] = master_ring

        session_ring = SessionRingComponent(
            name='session_ring',
            num_tracks=8,
            num_scenes=3,
        )

        sequencer_clip = self.register_disconnectable(SequencerClip(target_track=self._target_track))
        note_layout = self.register_disconnectable(NoteLayout())

        return {
            "fx_ring": const(fx_ring),
            "master_ring": const(master_ring),
            "session_ring": const(session_ring),
            'grid_resolution': const(GridResolutionComponent(resolutions=GRID_RESOLUTIONS, default_index=DEFAULT_GRID_RESOLUTION_INDEX)),
            'sequencer_clip': const(sequencer_clip),
            'note_layout': const(note_layout)
        }
    
    def _update_note_mode(self):
        if self.component_map['Main_Modes'].selected_mode == 'note':
            note_mode = note_mode_for_track(self.component_map['Target_Track'].target_track, self.instrument_finder)
            self.component_map['Note_Modes'].selected_mode = note_mode
            pitch_provider = PITCH_PROVIDERS.get(note_mode, None)
            self.component_map['Step_Sequence'].set_pitch_provider(self.component_map[pitch_provider] if pitch_provider else None)

    
    @listens('in_control_surface_mode')
    def __on_control_mode_changed(self, in_control_surface_mode):
        enabled = in_control_surface_mode and self._identification.is_identified
        if enabled:
            self.component_map['Firmware'].initialize()
            self.component_map['Global_Modes'].selected_mode = 'default'
            self.component_map['Menu_Modes'].selected_mode = 'default'
            self.__on_main_mode_changed(self.component_map['Main_Modes'].selected_mode)
            self.refresh_state()
        else:
            self.component_map['Firmware'].reset()
            self.component_map['Global_Modes'].selected_mode = 'standalone'
            self.set_can_auto_arm(False)
            self.set_can_update_controlled_track(False)
        self._session_ring.set_enabled(enabled)

def fx_tracks(song):
    return tuple(song.return_tracks)

def master_track(song):
    return (song.master_track,)

def note_mode_for_track(track, instrument_finder):
    if liveobj_valid(track) and track.has_midi_input:
        if liveobj_valid(instrument_finder.drum_group):
            return 'drum'
        if liveobj_valid(instrument_finder.sliced_simpler):
            return 'simpler'
        return 'instrument'
    return 'audio'

def _update_note_mode(self):
    if self.component_map['Main_Modes'].selected_mode == 'note':
        note_mode = note_mode_for_track(self.component_map['Target_Track'].target_track, self.instrument_finder)
        self.component_map['Note_Modes'].selected_mode = note_mode
        pitch_provider = PITCH_PROVIDERS.get(note_mode, None)
        self.component_map['Step_Sequence'].set_pitch_provider(self.component_map[pitch_provider] if pitch_provider else None)



class Specification(ControlSurfaceSpecification):
    num_tracks = 8
    num_scenes = 3
    include_returns = False
    include_master = False
    #right_align_non_player_tracks = False
    #link_session_ring_to_scene_selection = True
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin, colors=Rgb)
    create_mappings_function = create_mappings
    component_map = {
        #'Step_Sequence': partial(StepSequenceComponent, grid_resolution=GRID_RESOLUTIONS[3]),
        'FXMixer': FXMixerComponent,
        'MasterMixer': MasterMixerComponent,
        'ViewControl': ViewControlComponent,
        'Mixer': MixerComponent,
        'Session': SessionComponent,
        'Session_Navigation': partial(SessionNavigationComponent, respect_borders=True, snap_track_offset=False),
        'Step_Sequence': StepSequenceComponent, 
        'Instrument': InstrumentComponent, 

    }
