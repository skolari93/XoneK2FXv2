import logging
import os
from ableton.v3.base import lazy_attribute

from ableton.v3.control_surface import (
    ControlSurface,
    ControlSurfaceSpecification,
    create_skin,
)
from .elements import Elements
from .mappings import create_mappings
from .skin import Skin
from .colors import Rgb
from ableton.v3.control_surface import Layer
from ableton.v3.control_surface.components import TransportComponent
#from .fx_mixer import FXMixerComponent
#from .master_ring import MasterRing
from ableton.v3.control_surface.components import MixerComponent,SessionRingComponent
from ableton.v2.control_surface.components import SimpleTrackAssigner

from functools import partial


logger = logging.getLogger("XoneK2FXv2")


def tracks_to_use_from_song(song):
    return tuple(song.visible_tracks) + tuple(song.return_tracks)

class XoneK2FXv2(ControlSurface):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        self.log_level = "info"

        self.start_logging()

        self.show_message("XoneK2FXv2: init mate")
        logger.info("XoneK2FXv2: init started ...")



    def disconnect(self):
        self.show_message("Disconnecting...")
        logger.info("Disconnecting...")
        self.stop_logging()
        super().disconnect()

    def setup(self):
        super().setup()
        self.init()

    def init(self):
        logger.info("init started:")
        with self.component_guard():
            logger.info("   adding skin")
            self._skin = create_skin(skin=Skin, colors=Rgb)
            #self._create_components()
            #self.component_map["Mixer"].master_strip().layer = Layer(select_button="master_select_button")
            #self.component_map["Mixer"].master_strip().layer = Layer(select_button="master_select_button")
        #self.set_components_enabled(True)

    def _create_components(self):
        self._init_session_ring()
        self._init_mixer()
        

    
    def _init_session_ring(self):
        self._session_ring = SessionRingComponent(
            name="session_ring",
            num_tracks=3,
            num_scenes=0,
            tracks_to_use=(partial(tracks_to_use_from_song, self.song)),
            is_enabled=False
        )

    def _create_mixer_volume_layer(self):
        return Layer(track_select_buttons="track_select_buttons",
          volume_controls="volume_faders",
        )

    def _create_mixer_mute_layer(self):
        return Layer(mute_buttons="mute_buttons")

    def set_components_enabled(self, enabled):
        with self.component_guard():
            for c in self._components:
                c.set_enabled(enabled)
    
    def _init_mixer(self):

        self._mixer = MixerComponent(
            name="FXMixer",
            session_ring=self._session_ring,
            #track_assigner=SimpleTrackAssigner(),
            is_enabled=False,
            layer=Layer(mute_buttons="mute_buttons")
        )
        #self._mixer.set_enabled(False)
        #self._mixer.name = "FXMixer"
        #self._mixer_layer = self._create_mixer_layer()
        #self._mixer_pan_send_layer = self._create_mixer_pan_send_layer()
        #self._mixer_volume_layer = self._create_mixer_volume_layer()
        #self._mixer_track_layer = self._create_mixer_track_layer()
        #self._mixer_solo_layer = self._create_mixer_solo_layer()
        #self._mixer_mute_layer = self._create_mixer_mute_layer()
        # for track in range(self.elements.matrix.width()):
        #     strip = self._mixer.channel_strip(track)
        #     strip.name = "Channel_Strip_" + str(track)
        #     strip.set_invert_mute_feedback(True)
        #     strip.set_delete_handler(self._delete_component)
        #     strip._do_select_track = self.on_select_track


        # self._mixer.selected_strip().name = "Selected_Channel_strip"
        # self._mixer.master_strip().name = "Master_Channel_strip"
        # self._mixer.master_strip()._do_select_track = self.on_select_track
        # self._mixer.master_strip().layer = Layer(select_button="master_select_button",
        #   selector_button="select_button")
        #self._mixer.set_enabled(True)

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

    # def create_master_select(self):
    #     logger.info("init master select:")
    #     self._master_selector = MasterTrackComponent(tracks_provider=(self._session_ring),
    #       is_enabled=False,
          
    #       layer=Layer(toggle_button="master_select_button"))
    #     self._master_selector.set_enabled(True)
    # heeerre:
    # def _get_additional_dependencies(self):
    #     # Return dictionary of additional dependencies
    #     return {
    #         'master_ring': const(self._master_ring)
    #     }
    
class Specification(ControlSurfaceSpecification):
    num_tracks = 3
    num_scenes = 0
    include_returns = False
    include_master = True
    right_align_non_player_tracks = False
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin, colors=Rgb)
    create_mappings_function = create_mappings
    component_map = {
        'Transport': TransportComponent,
        #'Master_Ring': MasterRing,
        'FXMixer': MixerComponent 
    }
