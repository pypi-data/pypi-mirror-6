import functools
import itertools

import libsheetmusic.spreadsheet as s
import libsheetmusic.util as u

def interval_functions():
    special = 'from_shorthand',
    maybe_useful = ['get_interval', 'measure', 'invert',]
    questions = ['is_consonant', 'is_dissonant', 'is_imperfect_consonant', 'is_perfect_consonant',]

    keyed = ['second', 'third', 'fourth','fifth', 'sixth', 'seventh', 'unison']
    not_keyed = [
        'augmented_unison',
        'major_fifth', 'major_fourth', 'major_second', 'major_seventh', 'major_sixth', 'major_third', 'major_unison',
        'minor_fifth', 'minor_fourth', 'minor_second', 'minor_seventh', 'minor_sixth', 'minor_third', 'minor_unison',
        'perfect_fifth', 'perfect_fourth', 'unison'
    ]
    keyed_functions = {name + '_interval': functools.partial(s.keyed_interval, name) for name in keyed}
    nonkeyed_functions = {name + '_interval': functools.partial(s.nonkeyed_interval, name) for name in not_keyed}
    return u.merge(keyed_functions, nonkeyed_functions)

def scale_functions():
    scale_names = [
        'aeolian',
        'chromatic',
        'diatonic',
        'diminished',
        'dorian',
        'harmonic_minor',
        'ionian',
        'locrian',
        'lydian',
        'melodic_minor',
        'mixolydian',
        'natural_minor',
        'phrygian',
        'whole_note'
    ]
    return {name + '_scale': functools.partial(s.scale, name) for name in scale_names}

def chord_functions():
    chord_names = [
        'I', 'I7', 'II', 'II7', 'III', 'III7', 'IV', 'IV7', 'V', 'V7', 'VI', 'VI7', 'VII', 'VII7',
        'augmented_major_seventh', 'augmented_minor_seventh', 'augmented_triad',
        'diminished_seventh', 'diminished_triad',
        'dominant', 'dominant7', 'dominant_flat_five', 'dominant_flat_ninth', 'dominant_ninth',
        'dominant_seventh', 'dominant_sharp_ninth', 'dominant_sixth','dominant_thirteenth',
        'eleventh', 'first_inversion',
        'half_diminished_seventh', 'hendrix_chord',
    #   'ii', 'ii7', 'iii', 'iii7', 'vi', 'vi7', 'vii', 'vii7',
        'invert', 'lydian_dominant_seventh',
        'major_ninth', 'major_seventh', 'major_sixth', 'major_thirteenth', 'major_triad',
        'mediant', 'mediant7', 'minor_eleventh', 'minor_major_seventh', 'minor_ninth',
        'minor_seventh', 'minor_seventh_flat_five', 'minor_sixth', 'minor_thirteenth',
        'minor_triad', 'second_inversion', 'seventh', 'sixth_ninth',
        'subdominant', 'subdominant7', 'submediant', 'submediant7', 'subtonic', 'subtonic7',
        'supertonic', 'supertonic7',
        'suspended_fourth_ninth', 'suspended_fourth_triad', 'suspended_second_triad',
        'suspended_seventh', 'suspended_triad', 'third_inversion',
        'tonic', 'tonic7', 'triad',
    ]
    chord = {name + '_chord': functools.partial(s.chord, name) for name in chord_names}
    arpeggio = {name + '_arpeggio': functools.partial(s.arpeggio, name) for name in chord_names}
    return u.merge(chord, arpeggio)

def progression_functions():
    try:
        import Gnumeric
    except ImportError:
        def progression(a,b):
            raise EnvironmentError('This must be run from inside Gnumeric.')
    else:
        progression = functools.partial(u.from_range_ref, Gnumeric)
    return {'progression': progression}

def util_functions():
    func_names = ['_'.join(xs) for xs in itertools.product(['from','to'],['scientific','integer'])]
    return {func_name: getattr(u, func_name) for func_name in func_names}

def functions():
    return reduce(u.merge, [scale_functions(), chord_functions(), progression_functions(), interval_functions(), util_functions()])
