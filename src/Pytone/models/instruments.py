"""General MIDI instrument helpers and constants."""

from __future__ import annotations

import re
from types import MappingProxyType


InstrumentInput = int | str


GENERAL_MIDI_PROGRAM_NAMES: tuple[str, ...] = (
    "Acoustic Grand Piano",
    "Bright Acoustic Piano",
    "Electric Grand Piano",
    "Honky-tonk Piano",
    "Electric Piano 1",
    "Electric Piano 2",
    "Harpsichord",
    "Clavinet",
    "Celesta",
    "Glockenspiel",
    "Music Box",
    "Vibraphone",
    "Marimba",
    "Xylophone",
    "Tubular Bells",
    "Dulcimer",
    "Drawbar Organ",
    "Percussive Organ",
    "Rock Organ",
    "Church Organ",
    "Reed Organ",
    "Accordion",
    "Harmonica",
    "Tango Accordion",
    "Acoustic Guitar (nylon)",
    "Acoustic Guitar (steel)",
    "Electric Guitar (jazz)",
    "Electric Guitar (clean)",
    "Electric Guitar (muted)",
    "Overdriven Guitar",
    "Distortion Guitar",
    "Guitar Harmonics",
    "Acoustic Bass",
    "Electric Bass (finger)",
    "Electric Bass (pick)",
    "Fretless Bass",
    "Slap Bass 1",
    "Slap Bass 2",
    "Synth Bass 1",
    "Synth Bass 2",
    "Violin",
    "Viola",
    "Cello",
    "Contrabass",
    "Tremolo Strings",
    "Pizzicato Strings",
    "Orchestral Harp",
    "Timpani",
    "String Ensemble 1",
    "String Ensemble 2",
    "Synth Strings 1",
    "Synth Strings 2",
    "Choir Aahs",
    "Voice Oohs",
    "Synth Voice",
    "Orchestra Hit",
    "Trumpet",
    "Trombone",
    "Tuba",
    "Muted Trumpet",
    "French Horn",
    "Brass Section",
    "Synth Brass 1",
    "Synth Brass 2",
    "Soprano Sax",
    "Alto Sax",
    "Tenor Sax",
    "Baritone Sax",
    "Oboe",
    "English Horn",
    "Bassoon",
    "Clarinet",
    "Piccolo",
    "Flute",
    "Recorder",
    "Pan Flute",
    "Blown Bottle",
    "Shakuhachi",
    "Whistle",
    "Ocarina",
    "Lead 1 (square)",
    "Lead 2 (sawtooth)",
    "Lead 3 (calliope)",
    "Lead 4 (chiff)",
    "Lead 5 (charang)",
    "Lead 6 (voice)",
    "Lead 7 (fifths)",
    "Lead 8 (bass + lead)",
    "Pad 1 (new age)",
    "Pad 2 (warm)",
    "Pad 3 (polysynth)",
    "Pad 4 (choir)",
    "Pad 5 (bowed)",
    "Pad 6 (metallic)",
    "Pad 7 (halo)",
    "Pad 8 (sweep)",
    "FX 1 (rain)",
    "FX 2 (soundtrack)",
    "FX 3 (crystal)",
    "FX 4 (atmosphere)",
    "FX 5 (brightness)",
    "FX 6 (goblins)",
    "FX 7 (echoes)",
    "FX 8 (sci-fi)",
    "Sitar",
    "Banjo",
    "Shamisen",
    "Koto",
    "Kalimba",
    "Bag Pipe",
    "Fiddle",
    "Shanai",
    "Tinkle Bell",
    "Agogo",
    "Steel Drums",
    "Woodblock",
    "Taiko Drum",
    "Melodic Tom",
    "Synth Drum",
    "Reverse Cymbal",
    "Guitar Fret Noise",
    "Breath Noise",
    "Seashore",
    "Bird Tweet",
    "Telephone Ring",
    "Helicopter",
    "Applause",
    "Gunshot",
)


def normalize_instrument_name(name: str) -> str:
    """Normalize instrument names for case- and punctuation-insensitive lookups."""
    normalized = re.sub(r"[^a-z0-9]+", "_", name.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return _GENERAL_MIDI_ALIASES.get(normalized, normalized)


_GENERAL_MIDI_ALIASES = {
    "clavi": "clavinet",
    "synthstrings_1": "synth_strings_1",
    "synthstrings_2": "synth_strings_2",
    "synthbrass_1": "synth_brass_1",
    "synthbrass_2": "synth_brass_2",
    "bagpipe": "bag_pipe",
}


_GENERAL_MIDI_LOOKUP = {
    normalize_instrument_name(name): code
    for code, name in enumerate(GENERAL_MIDI_PROGRAM_NAMES)
}
for alias, canonical in _GENERAL_MIDI_ALIASES.items():
    _GENERAL_MIDI_LOOKUP[alias] = _GENERAL_MIDI_LOOKUP[canonical]


GENERAL_MIDI_INSTRUMENT_NAMES = MappingProxyType(
    dict(enumerate(GENERAL_MIDI_PROGRAM_NAMES))
)
GENERAL_MIDI_INSTRUMENTS = MappingProxyType(_GENERAL_MIDI_LOOKUP)


def resolve_instrument(value: InstrumentInput) -> int:
    """Resolve an instrument name or integer into a General MIDI program number."""
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        raise TypeError("instrument must be an int or General MIDI name")

    normalized = normalize_instrument_name(value)
    try:
        return GENERAL_MIDI_INSTRUMENTS[normalized]
    except KeyError as exc:
        raise ValueError(f"Unknown General MIDI instrument: {value}") from exc


def instrument_name(program: int) -> str:
    """Return the canonical General MIDI name for a program number."""
    if not isinstance(program, int):
        raise TypeError("program must be an int")
    try:
        return GENERAL_MIDI_INSTRUMENT_NAMES[program]
    except KeyError as exc:
        raise ValueError(
            "program must be between 0 and 127 inclusive"
        ) from exc
