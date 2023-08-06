import mingus.extra.LilyPond as LilyPond
from mingus.midi import fluidsynth, MidiFileOut
fluidsynth.init


def sheetmusic(range_ref, key = 'C', meter = (4, 4)):
    for column in cells:
        bar = containers.Bar(key, meter)
        for cell in column:
            bar += from_scientific(cell)
        LilyPond.to_png(bar, '/tmp/bar.png')
