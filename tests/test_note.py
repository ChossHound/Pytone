from tests.conftest import load_model_module

import pytest


note_module = load_model_module("note")
Note = note_module.Note


def test_note_stores_provided_fields():
    note = Note(pitch=64, start=1.5, duration=0.75, velocity=88)

    assert note.pitch == 64
    assert note.start == 1.5
    assert note.duration == 0.75
    assert note.velocity == 88


def test_note_uses_default_velocity_when_not_provided():
    note = Note(pitch=60, start=0.0, duration=1.0)

    assert note.velocity == 100


def test_note_dataclass_equality_is_value_based():
    left = Note(pitch=67, start=2.0, duration=0.5, velocity=90)
    right = Note(pitch=67, start=2.0, duration=0.5, velocity=90)

    assert left == right


@pytest.mark.parametrize("pitch", [-1, 128])
def test_note_rejects_pitch_outside_midi_range(pitch):
    with pytest.raises(ValueError, match="pitch must be between 0 and 127"):
        Note(pitch=pitch, start=0.0, duration=1.0)


@pytest.mark.parametrize("velocity", [-1, 128])
def test_note_rejects_velocity_outside_midi_range(velocity):
    with pytest.raises(ValueError, match="velocity must be between 0 and 127"):
        Note(pitch=60, start=0.0, duration=1.0, velocity=velocity)


def test_note_rejects_non_integer_pitch():
    with pytest.raises(TypeError, match="pitch must be an int"):
        Note(pitch=60.5, start=0.0, duration=1.0)


def test_note_rejects_non_integer_velocity():
    with pytest.raises(TypeError, match="velocity must be an int"):
        Note(pitch=60, start=0.0, duration=1.0, velocity="90")
