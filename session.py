from ableton.v3.control_surface.components import SessionComponent as SessionComponentBase
from ableton.v3.control_surface.controls import ButtonControl
from ableton.v3.base import clamp
from ableton.v3.live import scene_index
import logging
logger = logging.getLogger("XoneK2FXv2")


class SessionComponent(SessionComponentBase):
    launch_scene_and_advance = ButtonControl()
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    @launch_scene_and_advance.pressed
    def _on_launch_scene_and_advance_pressed(self, _):
        self._selected_scene._on_launch_button_pressed()
        next_index = scene_index() + 1
        n_scenes= len(self.song.scenes)
        logger.info([clamp(next_index, 1, n_scenes)])
        logger.info(self.song.scenes[clamp(next_index, 0, n_scenes-1)])
        self.song.view.selected_scene = self.song.scenes[clamp(next_index, 0, n_scenes - 1)]
