# from tests.conftest import load_model_module
from src.Pytone.models.note import Note
from src.Pytone.models.track import Track

# note_module = load_model_module("note")
# track_module = load_model_module("track")

# Note = note_module.Note
# Track = track_module.Track


def test_track_stores_channel_in_valid_range():
    track = Track(channel=7, instrument=10)

    assert track.channel == 7


def test_track_wraps_channel_above_midi_limit():
    track = Track(channel=17, instrument=10)

    assert track.channel == 1


def test_track_stores_instrument_in_valid_range():
    track = Track(channel=0, instrument=42)

    assert track.instrument == 42


def test_track_accepts_general_midi_instrument_names():
    track = Track(channel=0, instrument="flute")

    assert track.instrument == 73


def test_track_wraps_instrument_above_midi_limit():
    track = Track(channel=0, instrument=130)

    assert track.instrument == 2


def test_track_keeps_provided_note_list():
    notes = [Note(pitch=60, start=0, duration=4)]
    track = Track(channel=3, instrument=11, note_list=notes)

    assert track._note_list is notes


def test_track_channel_property_setter_updates_value():
    track = Track(channel=0, instrument=0, note_list=[])

    track.channel = 12

    assert track.channel == 12


def test_track_instrument_property_setter_accepts_general_midi_name():
    track = Track(channel=0, instrument=0, note_list=[])

    track.instrument = "Electric Piano 1"

    assert track.instrument == 4


def test_track_rejects_unknown_general_midi_name():
    try:
        Track(channel=0, instrument="laser harp")
    except ValueError as exc:
        assert "Unknown General MIDI instrument" in str(exc)
    else:
        raise AssertionError("Expected an unknown instrument name to fail")
