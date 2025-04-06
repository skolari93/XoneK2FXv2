from __future__ import absolute_import, print_function, unicode_literals
from ableton.v3.control_surface.components import ChannelStripComponent as ChannelStripComponentBase

class ChannelStripComponent(ChannelStripComponentBase):

    def set_track(self, track):
        super().set_track(track)
        self._ChannelStripComponent__on_track_name_changed.subject = self._track

    def update(self):
        super().update()
        self._ChannelStripComponent__on_track_name_changed()
