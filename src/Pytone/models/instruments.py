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


GENERAL_MIDI_DRUM_NOTE_NAMES = MappingProxyType(
    {
        35: "Acoustic Bass Drum",
        36: "Bass Drum 1",
        37: "Side Stick",
        38: "Acoustic Snare",
        39: "Hand Clap",
        40: "Electric Snare",
        41: "Low Floor Tom",
        42: "Closed Hi Hat",
        43: "High Floor Tom",
        44: "Pedal Hi Hat",
        45: "Low Tom",
        46: "Open Hi Hat",
        47: "Low-Mid Tom",
        48: "Hi-Mid Tom",
        49: "Crash Cymbal 1",
        50: "High Tom",
        51: "Ride Cymbal 1",
        52: "Chinese Cymbal",
        53: "Ride Bell",
        54: "Tambourine",
        55: "Splash Cymbal",
        56: "Cowbell",
        57: "Crash Cymbal 2",
        58: "Vibraslap",
        59: "Ride Cymbal 2",
        60: "Hi Bongo",
        61: "Low Bongo",
        62: "Mute Hi Conga",
        63: "Open Hi Conga",
        64: "Low Conga",
        65: "High Timbale",
        66: "Low Timbale",
        67: "High Agogo",
        68: "Low Agogo",
        69: "Cabasa",
        70: "Maracas",
        71: "Short Whistle",
        72: "Long Whistle",
        73: "Short Guiro",
        74: "Long Guiro",
        75: "Claves",
        76: "Hi Wood Block",
        77: "Low Wood Block",
        78: "Mute Cuica",
        79: "Open Cuica",
        80: "Mute Triangle",
        81: "Open Triangle",
    }
)


def normalize_instrument_name(name: str) -> str:
    """Normalize instrument names for case and punctuation-insensitive
        lookups."""
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

_DRUM_NOTE_ALIASES = {
    "kick": "acoustic_bass_drum",
    "bass_drum": "acoustic_bass_drum",
    "rimshot": "side_stick",
    "snare": "acoustic_snare",
    "closed_hihat": "closed_hi_hat",
    "closed_hi_hat": "closed_hi_hat",
    "pedal_hihat": "pedal_hi_hat",
    "pedal_hi_hat": "pedal_hi_hat",
    "open_hihat": "open_hi_hat",
    "open_hi_hat": "open_hi_hat",
    "crash": "crash_cymbal_1",
    "ride": "ride_cymbal_1",
    "woodblock": "hi_wood_block",
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

_DRUM_NOTE_LOOKUP = {
    normalize_instrument_name(name): note
    for note, name in GENERAL_MIDI_DRUM_NOTE_NAMES.items()
}
for alias, canonical in _DRUM_NOTE_ALIASES.items():
    _DRUM_NOTE_LOOKUP[alias] = _DRUM_NOTE_LOOKUP[canonical]

DRUM_NOTES = MappingProxyType(_DRUM_NOTE_LOOKUP)


def resolve_instrument(value: InstrumentInput) -> int:
    """Resolve an instrument name or integer into a General MIDI program
        number."""
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
