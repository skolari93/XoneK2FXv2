from ableton.v3.control_surface import Component
from itertools import zip_longest
from ableton.v2.base import inject, const, depends, listens
from ableton.v3.control_surface.components import SceneComponent
from ableton.v3.control_surface.controls import ButtonControl, control_list
from ableton.v3.live import liveobj_valid

class SongComponent(Component):
    _song_component_ends_initialisation = True
    song_buttons = control_list(ButtonControl)

    @depends(session_ring=None)
    def __init__(self, name='Song', session_ring=None, num_scenes=8, num_songs=8,clip_slot_component_type=None, *a, **k):
        (super().__init__)(a,name=name, **k)
        self._num_scenes = num_scenes
        self._num_songs = num_songs
        self._session_ring = session_ring

        scene_component_type = scene_component_type or SceneComponent

        create_scene = lambda: scene_component_type(parent=self,
            session_ring=(self._session_ring),
            clip_slot_component_type=clip_slot_component_type)

        with inject(clipboard=(const(self._clipboard))).everywhere():
            self._selected_scene = create_scene()
            self._scenes = [create_scene() for _ in range(self._session_ring.num_scenes)]

        self.register_slot(self._session_ring, self._reassign_scenes, "scenes")
        # self._SongComponent__on_selected_scene_changed.subject = self.song.view

        if self._song_component_ends_initialisation:
            self._end_initialisation()

    def scene(self, index):
        return self._scenes[index]

    def selected_scene(self):
        return self._selected_scene

    def set_scene_launch_buttons(self, buttons):
        for scene, button in zip_longest(self._scenes, buttons or []):
            scene.set_launch_button(button)

    def _reassign_scenes(self):
        scenes = self.song.scenes
        for index, scene in enumerate(self._scenes):
            scene_index = self._session_ring.scene_offset + index
            scene.set_scene(scenes[scene_index] if len(scenes) > scene_index else None)

    # write this
    def _update_song_clip_led(self, index):
        if index < self.stop_track_clip_buttons.control_count:
            tracks = self._session_ring.tracks
            track = tracks[index] if index < len(tracks) else None
            button = self.stop_track_clip_buttons[index]
            if liveobj_valid(track) and track.clip_slots:
                button.enabled = True
                if track.fired_slot_index == -2:
                    button.color = "Song.SongClipTriggered"
                elif track.playing_slot_index >= 0:
                    button.color = "Song.SongClip"
                else:
                    button.color = "Song.SongClipDisabled"
            else:
                button.enabled = False

    @listens("selected_scene")
    def __on_selected_scene_changed(self):
        if self._selected_scene is not None:
            self._selected_scene.set_scene(self.song.view.selected_scene)

    # change this
    def _end_initialisation(self):
        self._reassign_scenes()