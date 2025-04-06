from .colors import Rgb


OFF = Rgb.black
ON = Rgb.red

class Skin:
    class DefaultButton:
        On = ON
        Off = OFF
        Disabled = OFF

    class Transport:
        PlayOn = Rgb.green
        PlayOff = OFF
        StopOn = OFF
        StopOff = OFF

    class Mixer:
        MuteOn = Rgb.amber
        MuteOff = OFF
        SoloOn = Rgb.amber
        SoloOff = OFF
        Selected = Rgb.amber
        NotSelected = OFF
        NoTrack = OFF
