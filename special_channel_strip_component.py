from ableton.v2.control_surface import components

class SpecialChannelStripComponent(components.ChannelStripComponent):

    def __init__(self, *a, **k):
        (super(SpecialChannelStripComponent, self).__init__)(*a, **k)

    # def set_volume_control(self, control):
    #     self._update_control_sensitivities(control)
    #     super(SpecialChannelStripComponent, self).set_volume_control(control)

    # def set_send_controls(self, controls):
    #     if controls != None:
    #         for control in controls:
    #             self._update_control_sensitivities(control)

    #     super(SpecialChannelStripComponent, self).set_send_controls(controls)