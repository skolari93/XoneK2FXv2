from .colors import Rgb


class Skin:
    class Transport:
        PlayOn = Rgb.green
        PlayOff = Rgb.black
        StopOn = Rgb.black
        StopOff = Rgb.black
    class Mixer:
        MuteOn = Rgb.amber
        MuteOff = Rgb.black
        SoloOn = Rgb.amber
        SoloOff = Rgb.black
        Selected = Rgb.amber
        NotSelected = Rgb.black