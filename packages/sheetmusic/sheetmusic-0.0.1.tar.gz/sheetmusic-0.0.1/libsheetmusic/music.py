import re

import mingus.containers as containers
import mingus.core.chords as chords
import mingus.core.scales as scales
import mingus.core.intervals as intervals
import mingus.core.progressions as progressions

def scale(func_name, note):
    'http://code.google.com/p/mingus/wiki/tutorialScales'
    return [_ascending(note, getattr(scales, func_name)(note.name))]

def chord(*args, **kwargs):
    return [[x] for x in _chord(*args, **kwargs)]

def arpeggio(*args, **kwargs):
    return [_chord(*args,**kwargs)]

def progression(the_progression, root_note):
    '''
    >>> progression(['I','IV','V'], 'C3')
    [['C3', 'E3', 'G3'], ['F3', 'A4', 'C4'], ['G3', 'B4', 'D4']]
    '''
    if len(the_progression) == 1:
        the_progression = the_progression[0]
    named_chords = progressions.to_chords(the_progression, root_note.name)

    def convert(next_chord, prev = {'note':root_note}):
        result = _ascending(prev['note'], next_chord)
        prev['note'] = result[0]
        return result

    return [convert(chord) for chord in named_chords]

def nonkeyed_interval(func_name, note):
    other_note_name = getattr(intervals, func_name)(note.name)
    return _next_note(note, other_note_name)

def keyed_interval(func_name, note, key):
    other_note_name = getattr(intervals, func_name)(note.name, key)
    return _next_note(note, other_note_name)

def _next_note(first_note, second_note_name):
    '''
    mingus.containers.Note -> str -> mingus.containers.Note

    Receive a Note and a string note specifying a note name without
    an octave.

    If the second note name is greater than or equal to the first
    ("G" is greater than "C"),
    return a note of the second name in the same octave as the first.

    If the second note name is less than the first ("G" is greater than "C"),
    return a note of the second name in the octave above the first.
    '''
    if second_note_name >= first_note.name:
        second_note_octave = first_note.octave
    else:
        second_note_octave = first_note.octave + 1
    return containers.Note(second_note_name, second_note_octave)

def _chord(func_name, note, *args, **kwargs):
    'http://code.google.com/p/mingus/wiki/tutorialChords'
    return _ascending(note, getattr(chords, func_name)(note.name, *args, **kwargs))

def _ascending(note, note_names):
    prev_note = note
    output = []
    for note_name in note_names:
        next_note = _next_note(prev_note, note_name)
        output.append(next_note)
        prev_note = next_note
    return output
