import libsheetmusic.music as m
import libsheetmusic.util as u

def scale(func_name, string_note):
    note_in = u.from_scientific(string_note)
    notes_out = m.scale(func_name, note_in)
    return u.range_apply(u.to_scientific, notes_out)

def chord(func_name, string_note, *args, **kwargs):
    return u.range_apply(u.to_scientific, m.chord(func_name, u.from_scientific(string_note), *args, **kwargs))

def arpeggio(func_name, string_note, *args, **kwargs):
    return u.range_apply(u.to_scientific, m.arpeggio(func_name, u.from_scientific(string_note), *args, **kwargs))

def progression(Gnumeric, progression_range_ref, string_root_note):
    the_progression = u.from_range_ref(Gnumeric, progression_range_ref)
    root_note = from_scientific(string_root_note)
    return u.range_apply(u.to_scientific, m.progression(the_progression, root_note))

def keyed_interval(func_name, string_note, key):
    return u.to_scientific(m.keyed_interval(func_name, u.from_scientific(string_note), key))

def nonkeyed_interval(func_name, string_note):
    return u.to_scientific(m.nonkeyed_interval(func_name, u.from_scientific(string_note)))
