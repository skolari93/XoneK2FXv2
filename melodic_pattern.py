# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: ..\..\..\output\Live\win_64_static\Release\python-bundle\MIDI Remote Scripts\Move\melodic_pattern.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-03-17 14:05:58 UTC (1742220358)

import Live
from ableton.v2.base import NamedTuple
from ableton.v3.base import PITCH_NAMES, find_if, lazy_attribute, memoize
#from .midi import NOTE_MODE_FEEDBACK_CHANNELS
CHANNEL = 1 # don't choose channel 12, 13, or 14
CHROMATIC_MODE_OFFSET = 0#3

# i think the index is the nth pad.
# channel stuff is nnot working jey probably
# this is the note layup. i could do a note mode or so.

class Scale(NamedTuple):
    name = ''
    notes = []

    def to_root_note(self, root_note):
        return Scale(name=PITCH_NAMES[root_note], notes=[root_note + x for x in self.notes])

    @memoize
    def scale_for_notes(self, notes):
        return [self.to_root_note(b) for b in notes]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return str(self.name)

    def __eq__(self, other):
        if isinstance(other, Scale):
            return self.name == other.name and self.notes == other.notes
        return False

    def __hash__(self):
        return hash((self.name,))

SCALES = tuple((Scale(name=x[0], notes=x[1]) for x in Live.Song.get_all_scales_ordered()))


def scale_by_name(name):
    return find_if(lambda m: m.name == name, SCALES)

class NoteInfo(NamedTuple):
    index = None
    channel = 0
    color = 'NoteInvalid'

class MelodicPattern(NamedTuple):
    steps = [0, 0]
    scale = list(range(12))
    root_note = 0
    origin = [0, 0]
    chromatic_mode = False
    width = None
    height = None

    @lazy_attribute
    def extended_scale(self):
        if self.chromatic_mode:
            first_note = self.scale[0]
            return list(range(first_note, first_note + 12))
        return self.scale

    @property
    def is_aligned(self):
        return not self.origin[0] and (not self.origin[1]) and (abs(self.root_note) + 12) == self.extended_scale[0]

    def note(self, x, y):
        if not self._boundary_reached(x, y):
            channel = CHANNEL 
            return self._get_note_info(self._octave_and_note(x, y), self.root_note, channel)
        return NoteInfo()

    def __getitem__(self, i):
        root_note = self.root_note
        if root_note <= (-12):
            root_note = 0 if self.is_aligned else (-12)
        return self._get_note_info(self._octave_and_note_linear(i), root_note)

    def _boundary_reached(self, x, y):
        return self.width is not None and x >= self.width or (self.height is not None and y >= self.height)

    def _octave_and_note_by_index(self, index):
        scale = self.extended_scale
        scale_size = len(scale)
        octave = index // scale_size
        note = scale[index % scale_size]
        return (octave, note)

    def _octave_and_note(self, x, y):
        index = self.steps[0] * (x - self.origin[0]) + self.steps[1] * (y - self.origin[1])
        return self._octave_and_note_by_index(index)

    def _color_for_note(self, note):
        if note == self.scale[0]:
            return 'NoteBase'
        if note in self.scale:
            return 'NoteScale'
        return 'NoteNotScale'

    def _get_note_info(self, octave_note, root_note, channel=0):
        octave, note = octave_note
        note_index = root_note + (octave * 12) + note
        if 0 <= note_index <= 127:
            return NoteInfo(index=note_index, channel=channel, color=self._color_for_note(note))
        return NoteInfo()

    def _octave_and_note_linear(self, i):
        origin = self.origin[0] or self.origin[1]
        index = origin + i or False
        return self._octave_and_note_by_index(index)