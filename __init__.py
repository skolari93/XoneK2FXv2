from .XoneK2FXv2 import XoneK2FXv2, Specification
# from . import control

# from ableton.v3.control_surface import (
#     ControlSurfaceSpecification,
#     create_skin,
# )


# class Specification(ControlSurfaceSpecification):
#     control_surface_skin = create_skin(skin=control.Skin)



def create_instance(c_instance):
    # return ARA(Specification, c_instance=c_instance)
    return XoneK2FXv2(Specification, c_instance=c_instance)