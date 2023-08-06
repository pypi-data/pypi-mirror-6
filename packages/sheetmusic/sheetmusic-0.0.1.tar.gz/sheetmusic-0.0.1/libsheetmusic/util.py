import re

import mingus.containers as containers

def merge(a, b):
    '''
    (dict,dict) -> dict
    Combine two dictionaries without side-effects.
    '''
    result = dict(a)
    result.update(b)
    return result

def range_apply(func, list_list):
    return [[func(cell) for cell in column] for column in list_list]

def to_integer(scientific_note):
    '''
    :param scientific_note: Scientific representation of the note, like A4

    Returns an integer so you can feed this into spreadsheet functions
    '''
    return int(scientific_note)

def from_integer(integral_note):
    '''
    :param integral_note: Integral representation of a note, like 42

    Returns the note in scientific notation so you can feed this into
    other sheetmusic functions
    '''
    return containers.Note(integral_note)

def from_scientific(scientific_note):
    m = re.match(r'^([^0-9]+)([0-9]+)$', str(scientific_note))
    if not m:
        raise ValueError('%s is not in scientific notation' % scientific_note)
    note_within_octave = m.group(1)
    octave = int(m.group(2))
    return containers.Note(note_within_octave, octave)

def to_scientific(integral_note):
    note = containers.Note(int(integral_note))
    return note.name + str(note.octave)

def from_range_ref(Gnumeric, range_ref):
    workbook_index = 0 # Let's just hope that's always the case
    workbook = Gnumeric.workbooks()[workbook_index]
    sheet_index = int(Gnumeric.functions['sheet'](range_ref)) - 1
    sheet = workbook.sheets()[sheet_index]
    rows = map(int, Gnumeric.functions['row'](range_ref)[0])
    columns = [int(x[0]) for x in Gnumeric.functions['column'](range_ref)]
    return [[sheet.cell_fetch(int(column-1), int(row-1)).get_rendered_text() for row in rows] for column in columns]
