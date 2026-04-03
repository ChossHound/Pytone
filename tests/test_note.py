from tests.conftest import load_model_module

import pytest


note_module = load_model_module("note")
Note = note_module.Note


def test_note_stores_provided_fields():
    note = Note(pitch=64, start=6, duration=3, velocity=88)

    assert note.pitch == 64
    assert note.start == 6
    assert note.duration == 3
    assert note.velocity == 88


def test_note_uses_default_velocity_when_not_provided():
    note = Note(pitch=60, start=0, duration=1)

    assert note.velocity == 100


def test_note_dataclass_equality_is_value_based():
    left = Note(pitch=67, start=8, duration=2, velocity=90)
    right = Note(pitch=67, start=8, duration=2, velocity=90)

    assert left == right


@pytest.mark.parametrize("pitch", [-1, 128])
def test_note_rejects_pitch_outside_midi_range(pitch):
    with pytest.raises(ValueError, match="pitch must be between 0 and 127"):
        Note(pitch=pitch, start=0, duration=1)


@pytest.mark.parametrize("velocity", [-1, 128])
def test_note_rejects_velocity_outside_midi_range(velocity):
    with pytest.raises(ValueError, match="velocity must be between 0 and 127"):
        Note(pitch=60, start=0, duration=1, velocity=velocity)


def test_note_rejects_non_integer_pitch():
    with pytest.raises(TypeError, match="pitch must be an int"):
        Note(pitch=60.5, start=0, duration=1)


def test_note_rejects_non_integer_velocity():
    with pytest.raises(TypeError, match="velocity must be an int"):
        Note(pitch=60, start=0, duration=1, velocity="90")


def test_note_rejects_non_integer_start():
    with pytest.raises(TypeError, match="start must be an int"):
        Note(pitch=60, start=0.5, duration=1)


def test_note_rejects_negative_start():
    with pytest.raises(ValueError, match="start must be at least 0"):
        Note(pitch=60, start=-1, duration=1)


def test_note_rejects_non_integer_duration():
    with pytest.raises(TypeError, match="duration must be an int"):
        Note(pitch=60, start=0, duration=1.5)


def test_note_rejects_duration_shorter_than_a_sixteenth_note():
    with pytest.raises(ValueError, match="duration must be at least 1"):
        Note(pitch=60, start=0, duration=0)
