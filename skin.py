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
        PlayOff = Rgb.green
        StopOn = ON
        StopOff = OFF
        AutomationArmOn = Rgb.amber
        AutomationArmOff = OFF

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
        ArmOn = Rgb.red
        ArmOff = OFF
    class Session:
        Scene = Rgb.amber
        SceneTriggered = Rgb.green
        NoScene = OFF
        StopAllClips = Rgb.red
        ClipPlaying = Rgb.green
        ClipTriggeredPlay = Rgb.green
        ClipStopped = Rgb.amber
        ClipTriggeredPlay = Rgb.green
        ClipTriggeredRecord = Rgb.red
        ClipPlaying = Rgb.green
        ClipRecording = Rgb.red
        NoSlot = OFF
        Slot = OFF

    class Zooming:
        Playing = Rgb.green
        Empty = OFF
        Selected = Rgb.green
    
    class Recording:
        ArrangementRecordOn = ON
        ArrangementRecordOff = OFF
        ArrangementOverdubOn = ON
        ArrangementOverdubOff = OFF
        SessionRecordOn = ON
        SessionRecordTransition = ON
        SessionRecordOff = OFF
        SessionOverdubOn = ON
        SessionOverdubOff = OFF
        NewPressed = ON
        New = Rgb.green

    class ModifierBackground:
        Shift = OFF
        ShiftPressed = Rgb.amber

    class ViewControl:
        ScenePressed = Rgb.green
        Scene = Rgb.green


    class Variations:
        Off = OFF
        Recall = Rgb.green
        Stash = Rgb.green

    class NoteEditor:
        NoClip = OFF