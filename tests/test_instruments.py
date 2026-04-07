from tests.conftest import load_model_module

import pytest


instruments_module = load_model_module("instruments")

DRUM_NOTES = instruments_module.DRUM_NOTES
GENERAL_MIDI_DRUM_NOTE_NAMES = instruments_module.GENERAL_MIDI_DRUM_NOTE_NAMES
GENERAL_MIDI_INSTRUMENTS = instruments_module.GENERAL_MIDI_INSTRUMENTS
GENERAL_MIDI_INSTRUMENT_NAMES = instruments_module.GENERAL_MIDI_INSTRUMENT_NAMES
instrument_name = instruments_module.instrument_name
normalize_instrument_name = instruments_module.normalize_instrument_name
resolve_instrument = instruments_module.resolve_instrument


def test_general_midi_instrument_lookup_supports_normalized_names():
    assert GENERAL_MIDI_INSTRUMENTS["electric_piano_1"] == 4
    assert GENERAL_MIDI_INSTRUMENTS["taiko_drum"] == 116


def test_normalize_instrument_name_is_case_and_punctuation_insensitive():
    assert normalize_instrument_name("  Electric Piano 1  ") == "electric_piano_1"
    assert normalize_instrument_name("Taiko-Drum") == "taiko_drum"


def test_normalize_instrument_name_applies_known_aliases():
    assert normalize_instrument_name("clavi") == "clavinet"
    assert normalize_instrument_name("bagpipe") == "bag_pipe"


def test_resolve_instrument_accepts_int_and_general_midi_name():
    assert resolve_instrument(12) == 12
    assert resolve_instrument("Flute") == 73
    assert resolve_instrument("synthstrings_1") == 50


def test_resolve_instrument_rejects_unknown_general_midi_name():
    with pytest.raises(ValueError, match="Unknown General MIDI instrument"):
        resolve_instrument("laser harp")


def test_instrument_name_returns_canonical_general_midi_name():
    assert instrument_name(0) == "Acoustic Grand Piano"
    assert instrument_name(116) == "Taiko Drum"
    assert GENERAL_MIDI_INSTRUMENT_NAMES[73] == "Flute"


def test_instrument_name_rejects_non_integer_programs():
    with pytest.raises(TypeError, match="program must be an int"):
        instrument_name("73")


def test_instrument_name_rejects_programs_outside_general_midi_range():
    with pytest.raises(ValueError, match="between 0 and 127 inclusive"):
        instrument_name(128)


def test_general_midi_drum_note_names_expose_canonical_note_numbers():
    assert GENERAL_MIDI_DRUM_NOTE_NAMES[35] == "Acoustic Bass Drum"
    assert GENERAL_MIDI_DRUM_NOTE_NAMES[42] == "Closed Hi Hat"
    assert GENERAL_MIDI_DRUM_NOTE_NAMES[49] == "Crash Cymbal 1"


def test_drum_notes_support_common_aliases_and_normalized_names():
    assert DRUM_NOTES["kick"] == 35
    assert DRUM_NOTES["snare"] == 38
    assert DRUM_NOTES["closed_hihat"] == 42
    assert DRUM_NOTES["open_hi_hat"] == 46
    assert DRUM_NOTES["crash"] == 49
    assert DRUM_NOTES["ride"] == 51
    assert DRUM_NOTES["acoustic_bass_drum"] == 35
    assert DRUM_NOTES["closed_hi_hat"] == 42


def test_drum_notes_support_additional_percussion_aliases():
    assert DRUM_NOTES["rimshot"] == 37
    assert DRUM_NOTES["woodblock"] == 76

