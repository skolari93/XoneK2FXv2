from .XoneK2FXv2 import XoneK2FXv2, Specification

def create_instance(c_instance):
    return XoneK2FXv2(Specification, c_instance=c_instance)