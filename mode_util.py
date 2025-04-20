from ableton.v3.control_surface.components import create_sequencer_clip
from ableton.v3.control_surface.mode import EventDescription, ModeButtonBehaviour, toggle_mode_on_property_change
from ableton.v3.live import liveobj_valid

def create_clip(control_surface):
    track = control_surface.component_map['Target_Track'].target_track
    clip = control_surface.component_map['Target_Track'].target_clip
    if not liveobj_valid(clip):
        if track.has_midi_input:
            create_sequencer_clip(track)

# def close_menus(control_surface):
#     pass

#     def inner(modes_comp, mode_name):

#         def on_event(*_):
#             modes_comp.selected_mode = mode_name

#         def on_clip_changed():
#             if modes_comp.selected_mode == 'loop_menu' and (not liveobj_valid(control_surface.component_map['Target_Track'].target_clip)):
#                 modes_comp.selected_mode = mode_name
#         modes_comp.register_slot(modes_comp.component_map['Main_Modes'], on_event, 'selected_mode')
#         modes_comp.register_slot(modes_comp.song.view, on_event, 'selected_track')
#         modes_comp.register_slot(modes_comp.component_map['Track_List'], on_event, 'track_reselected')
#         modes_comp.register_slot(modes_comp.component_map['Target_Track'], on_clip_changed, 'target_clip')
#     return inner

# def activate_note_settings(control_surface):
#     note_editor = control_surface.component_map['Step_Sequence'].note_editor
#     def inner(modes, mode_name):
#         def on_event(*_):
#             if not note_editor.active_steps:
#                 modes.pop_mode(mode_name)
#             elif modes.selected_mode != mode_name:
#                 modes.push_mode(mode_name)
#         modes.register_slot(modes, on_event, 'active_steps')
#     return inner


class MenuBehaviour(ModeButtonBehaviour):
    def press_immediate(self, component, mode):
        if component.selected_mode == mode:
            component.go_back(to_top=True)
        else:
            component.push_mode(mode)

class MenuWithLatchingBehavior(MenuBehaviour):
    def release_delayed(self, component, _):
        component.push_mode(component.modes[0])
        component.pop_unselected_modes()

