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
        CrossfadeA = Rgb.amber
        CrossfadeB = Rgb.green
        CrossfadeOff = OFF

    class Session:
        Scene = Rgb.amber
        SceneTriggered = Rgb.green
        NoScene = OFF
        StopAllClips = Rgb.red
        ClipPlaying = Rgb.green
    
    class Zooming:
        Playing = Rgb.green