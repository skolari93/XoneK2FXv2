from ableton.v3.base import EventObject, listenable_property
from ableton.v3.control_surface.components import ClipActionsComponent as ClipActionsComponentBase
from ableton.v3.control_surface.controls import ButtonControl
from ableton.v3.live import action

class ClipActionsComponent(ClipActionsComponentBase):
    delete_button = ButtonControl(color=None)
    duplicate_button = ButtonControl(color=None)

    def __init__(self, sequencer_clip=None, *a, **k):
        self._sequencer_clip = sequencer_clip
        super().__init__(*a, **k)
        self.register_slot(sequencer_clip, self._update_double_button, 'length')

    @delete_button.released_immediately
    def delete_button(self, _):
        clip = self._target_track.target_clip
        if action.delete(clip):
            self.notify(self.notifications.Clip.delete, 'Clip')
        else:
            self.notify(self.notifications.Clip.error_delete_empty_slot)

    @duplicate_button.released_immediately
    def duplicate_button(self, _):
        if not self.any_clipboard_has_content:
            clip = self._target_track.target_clip
            if action.duplicate_clip_special(clip):
                self.notify(self.notifications.Clip.duplicate, 'Clip')

    def _update_delete_button(self):
        return

    def _update_duplicate_button(self):
        return