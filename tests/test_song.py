import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from hypothesis import given
from hypothesis import strategies as st
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from tests.conftest import load_model_module


note_module = load_model_module("note")
track_module = load_model_module("track")
song_module = load_model_module("song")

Note = note_module.Note
Track = track_module.Track
Song = song_module.Song


@pytest.fixture(autouse=True)
def reset_song_singleton():
    Song.reset_instance()
    yield
    Song.reset_instance()


def fresh_song(*args, **kwargs):
    Song.reset_instance()
    return Song(*args, **kwargs)


def test_song_general_midi_lookup_maps_names_and_codes():
    assert Song.GENERAL_MIDI_INSTRUMENTS["flute"] == 73
    assert Song.instrument_code("Acoustic Grand Piano") == 0
    assert Song.instrument_code("synthstrings_1") == 50
    assert Song.instrument_name(73) == "Flute"


def midi_track_from_track(track):
    ticks_per_beat = MidiFile().ticks_per_beat

    def steps_to_ticks(steps):
        return int(round((steps * ticks_per_beat) / Song.STEPS_PER_BEAT))

    midi_track = MidiTrack()
    midi_track.append(
        Message(
            "program_change",
            channel=track.channel,
            program=track.instrument,
            time=0,
        )
    )

    timed_messages = []
    for note in track.note_list:
        timed_messages.append(
            (
                steps_to_ticks(note.start),
                Message(
                    "note_on",
                    channel=track.channel,
                    note=note.pitch,
                    velocity=note.velocity,
                    time=0,
                ),
            )
        )
        timed_messages.append(
            (
                steps_to_ticks(note.start + note.duration),
                Message(
                    "note_off",
                    channel=track.channel,
                    note=note.pitch,
                    velocity=0,
                    time=0,
                ),
            )
        )

    timed_messages.sort(
        key=lambda item: (item[0], 0 if item[1].type == "note_off" else 1)
    )

    previous_tick = 0
    for absolute_tick, message in timed_messages:
        message.time = absolute_tick - previous_tick
        midi_track.append(message)
        previous_tick = absolute_tick

    return midi_track


@st.composite
def note_strategy(draw):
    start = draw(st.integers(min_value=0, max_value=32))
    duration = draw(st.integers(min_value=1, max_value=16))
    return Note(
        pitch=draw(st.integers(min_value=0, max_value=127)),
        start=start,
        duration=duration,
        velocity=draw(st.integers(min_value=0, max_value=127)),
    )


@st.composite
def track_strategy(draw):
    notes = draw(st.lists(note_strategy(), max_size=8))
    return Track(
        channel=draw(st.integers(min_value=0, max_value=15)),
        instrument=draw(st.integers(min_value=0, max_value=127)),
        note_list=notes,
    )


@st.composite
def imported_track_strategy(draw):
    channel = draw(st.integers(min_value=0, max_value=15))
    instrument = draw(st.integers(min_value=0, max_value=127))
    note_count = draw(st.integers(min_value=0, max_value=6))

    cursor = 0
    notes = []
    for _ in range(note_count):
        gap = draw(st.integers(min_value=0, max_value=24))
        duration = draw(st.integers(min_value=1, max_value=24))
        cursor += gap
        notes.append(
            Note(
                pitch=draw(st.integers(min_value=0, max_value=127)),
                start=cursor,
                duration=duration,
                velocity=draw(st.integers(min_value=1, max_value=127)),
            )
        )
        cursor += duration

    return Track(channel=channel, instrument=instrument, note_list=notes)


def test_create_midifile_exports_all_tracks_and_uses_delta_times(tmp_path):
    song = Song()
    first_track = Track(
        channel=2,
        instrument=10,
        note_list=[
            Note(pitch=60, start=0, duration=4, velocity=70),
            Note(pitch=64, start=6, duration=2, velocity=80),
        ],
    )
    second_track = Track(
        channel=5,
        instrument=20,
        note_list=[
            Note(pitch=67, start=2, duration=1, velocity=90),
        ],
    )
    song.add_track(first_track)
    song.add_track(second_track)

    output_path = tmp_path / "example.mid"
    midi_file = song.create_midifile()
    midi_file.save(output_path)
    midi_file = MidiFile(output_path)

    assert len(midi_file.tracks) == 2

    first_messages = [
        message for message in midi_file.tracks[0]
        if not message.is_meta
    ]
    assert first_messages[0].type == "program_change"
    assert first_messages[0].time == 0
    assert first_messages[1].type == "note_on"
    assert first_messages[1].time == 0
    assert first_messages[2].type == "note_off"
    assert first_messages[2].time == midi_file.ticks_per_beat
    assert first_messages[3].type == "note_on"
    assert first_messages[3].time == midi_file.ticks_per_beat // 2
    assert first_messages[4].type == "note_off"
    assert first_messages[4].time == midi_file.ticks_per_beat // 2

    second_messages = [
        message for message in midi_file.tracks[1]
        if not message.is_meta
    ]
    assert second_messages[0].type == "program_change"
    assert second_messages[1].type == "note_on"
    assert second_messages[1].time == midi_file.ticks_per_beat // 2


def test_create_midifile_uses_updated_track_instrument_value(tmp_path):
    song = Song()
    track = Track(
        channel=3,
        instrument=24,
        note_list=[Note(pitch=60, start=0, duration=4, velocity=90)],
    )
    track.instrument = "Voice Oohs"
    song.add_track(track)

    output_path = tmp_path / "updated_instrument.mid"
    midi_file = song.create_midifile()
    midi_file.save(output_path)
    midi_file = MidiFile(output_path)

    messages = [message for message in midi_file.tracks[0] if not message.is_meta]

    assert messages[0].type == "program_change"
    assert messages[0].channel == 3
    assert messages[0].program == Song.instrument_code("Voice Oohs")


def test_save_song_uses_dialog_selection_and_appends_mid_extension(
    monkeypatch,
    tmp_path,
):
    song = Song()
    dialog_calls = {}

    track = Track(
        channel=2,
        instrument=10,
        note_list=[Note(pitch=60, start=0, duration=4, velocity=70)],
    )
    song.add_track(track)

    class FakeRoot:
        def __init__(self):
            self.withdrawn = False
            self.destroyed = False

        def withdraw(self):
            self.withdrawn = True

        def destroy(self):
            self.destroyed = True

    fake_root = FakeRoot()

    class FakeTkModule:
        TclError = RuntimeError

        @staticmethod
        def Tk():
            return fake_root

    class FakeFileDialog:
        @staticmethod
        def asksaveasfilename(**kwargs):
            dialog_calls.update(kwargs)
            return str(tmp_path / "demo_song")

    monkeypatch.setattr(song_module, "tk", FakeTkModule)
    monkeypatch.setattr(song_module, "filedialog", FakeFileDialog)

    output_path = song.save_song(
        initial_filename="demo_song.mid",
        initial_dir="exports",
    )

    assert fake_root.withdrawn is True
    assert fake_root.destroyed is True
    assert dialog_calls["defaultextension"] == ".mid"
    assert dialog_calls["initialfile"] == "demo_song.mid"
    assert dialog_calls["initialdir"] == "exports"
    assert output_path == os.path.abspath(tmp_path / "demo_song.mid")
    assert Path(output_path).exists()

    midi_file = MidiFile(output_path)
    messages = [message for message in midi_file.tracks[0] if not message.is_meta]
    assert messages[0].type == "program_change"
    assert messages[1].type == "note_on"


def test_save_song_returns_none_when_dialog_is_cancelled(monkeypatch):
    song = Song()

    class FakeRoot:
        def withdraw(self):
            return None

        def destroy(self):
            return None

    class FakeTkModule:
        TclError = RuntimeError

        @staticmethod
        def Tk():
            return FakeRoot()

    class FakeFileDialog:
        @staticmethod
        def asksaveasfilename(**kwargs):
            return ""

    def unexpected_create_midifile():
        raise AssertionError("create_midifile should not be called")

    monkeypatch.setattr(song_module, "tk", FakeTkModule)
    monkeypatch.setattr(song_module, "filedialog", FakeFileDialog)
    monkeypatch.setattr(song, "create_midifile", unexpected_create_midifile)

    assert song.save_song() is None


def test_load_song_uses_dialog_selection_and_populates_tracks(
    monkeypatch,
    tmp_path,
):
    source_song = Song()
    source_song.bpm = 132
    source_song.signature = (3, 4)
    source_song.track_list = [
        Track(
            channel=4,
            instrument=48,
            note_list=[Note(pitch=65, start=2, duration=4, velocity=84)],
        )
    ]
    source_path = tmp_path / "loaded_song.mid"
    source_song.save_song(path=str(source_path))

    Song.reset_instance()
    song = Song()
    dialog_calls = {}

    class FakeRoot:
        def __init__(self):
            self.withdrawn = False
            self.destroyed = False

        def withdraw(self):
            self.withdrawn = True

        def destroy(self):
            self.destroyed = True

    fake_root = FakeRoot()

    class FakeTkModule:
        TclError = RuntimeError

        @staticmethod
        def Tk():
            return fake_root

    class FakeFileDialog:
        @staticmethod
        def askopenfilename(**kwargs):
            dialog_calls.update(kwargs)
            return str(source_path)

    monkeypatch.setattr(song_module, "tk", FakeTkModule)
    monkeypatch.setattr(song_module, "filedialog", FakeFileDialog)

    output_path = song.load_song(initial_dir="imports")

    assert fake_root.withdrawn is True
    assert fake_root.destroyed is True
    assert dialog_calls["initialdir"] == "imports"
    assert output_path == str(source_path.resolve())
    assert song.bpm == 132
    assert song.signature == (3, 4)
    assert song.track_list == [
        Track(
            channel=4,
            instrument=48,
            note_list=[Note(pitch=65, start=2, duration=4, velocity=84)],
        )
    ]


def test_load_song_returns_none_when_dialog_is_cancelled(monkeypatch):
    song = Song()

    class FakeRoot:
        def withdraw(self):
            return None

        def destroy(self):
            return None

    class FakeTkModule:
        TclError = RuntimeError

        @staticmethod
        def Tk():
            return FakeRoot()

    class FakeFileDialog:
        @staticmethod
        def askopenfilename(**kwargs):
            return ""

    def unexpected_build_tracks_from_midifile(_midifile):
        raise AssertionError("build_tracks_from_midifile should not be called")

    monkeypatch.setattr(song_module, "tk", FakeTkModule)
    monkeypatch.setattr(song_module, "filedialog", FakeFileDialog)
    monkeypatch.setattr(
        song,
        "build_tracks_from_midifile",
        unexpected_build_tracks_from_midifile,
    )

    assert song.load_song() is None


def test_load_song_rejects_non_midi_file_selection(tmp_path):
    song = Song()
    invalid_path = tmp_path / "not_a_song.txt"
    invalid_path.write_text("definitely not midi", encoding="utf-8")

    with pytest.raises(ValueError, match="must be a MIDI file"):
        song.load_song(path=str(invalid_path))


def test_load_song_rejects_invalid_midi_contents(tmp_path):
    song = Song()
    invalid_path = tmp_path / "broken_song.mid"
    invalid_path.write_bytes(b"not actually a midi file")

    with pytest.raises(ValueError, match="not a valid MIDI file"):
        song.load_song(path=str(invalid_path))


def test_song_is_a_singleton_and_preserves_initial_configuration():
    first_song = Song(bpm=120, length=8, signature=(3, 4), loop=False)
    second_song = Song()

    first_song.add_track(Track(channel=1, instrument=5, note_list=[]))

    assert first_song is second_song
    assert first_song.bpm == 120
    assert first_song.length == 8
    assert first_song.signature == (3, 4)
    assert first_song.loop is False
    assert len(first_song.track_list) == 1
    assert second_song.bpm == 120
    assert second_song.length == 8
    assert second_song.signature == (3, 4)
    assert second_song.loop is False
    assert second_song.track_list == first_song.track_list


def test_song_reset_instance_creates_a_fresh_singleton():
    first_song = Song(bpm=120, length=8, signature=(3, 4), loop=False)
    first_song.add_track(Track(channel=1, instrument=5, note_list=[]))

    Song.reset_instance()

    replacement_song = Song()

    assert replacement_song is not first_song
    assert replacement_song.bpm == 100
    assert replacement_song.length == 16
    assert replacement_song.signature == (4, 4)
    assert replacement_song.loop is True
    assert replacement_song.track_list == []


def test_song_add_track_auto_assigns_distinct_channels_when_not_provided():
    song = Song()
    first_track = Track(instrument=24, note_list=[])
    second_track = Track(instrument="Voice Oohs", note_list=[])

    song.add_track(first_track)
    song.add_track(second_track)

    assert first_track.channel == 0
    assert second_track.channel == 1


def test_song_add_track_preserves_explicit_channel_and_skips_it_for_auto_assign():
    song = Song()
    explicit_track = Track(channel=3, instrument=24, note_list=[])
    implicit_track = Track(instrument="Voice Oohs", note_list=[])

    song.add_track(explicit_track)
    song.add_track(implicit_track)

    assert explicit_track.channel == 3
    assert implicit_track.channel == 0


@given(st.lists(track_strategy(), max_size=Song.MAX_TRACKS))
def test_song_add_track_preserves_order_until_capacity(tracks):
    song = fresh_song()

    for track in tracks:
        song.add_track(track)

    assert song.track_list == tracks
    assert song.is_full() is (len(tracks) == Song.MAX_TRACKS)


@given(st.lists(track_strategy(), min_size=Song.MAX_TRACKS + 1,
                max_size=Song.MAX_TRACKS + 3))
def test_song_rejects_more_tracks_than_capacity(tracks):
    song = fresh_song()

    for track in tracks[:Song.MAX_TRACKS]:
        song.add_track(track)

    try:
        song.add_track(tracks[Song.MAX_TRACKS])
    except ValueError as exc:
        assert str(Song.MAX_TRACKS) in str(exc)
    else:
        raise AssertionError("Expected add_track to reject tracks past max")


@given(
    note=note_strategy(),
    channel=st.integers(min_value=0, max_value=15),
)
def test_note_to_message_preserves_note_values(note, channel):
    song = fresh_song()

    timed_messages = song.note_to_message(note, channel)

    assert len(timed_messages) == 2

    note_on_time, note_on = timed_messages[0]
    note_off_time, note_off = timed_messages[1]

    assert note_on_time == note.start
    assert note_off_time == note.start + note.duration
    assert note_on.type == "note_on"
    assert note_off.type == "note_off"
    assert note_on.note == note.pitch
    assert note_off.note == note.pitch
    assert note_on.velocity == note.velocity
    assert note_off.velocity == 0
    assert note_on.channel == channel
    assert note_off.channel == channel


@given(tracks=st.lists(track_strategy(), max_size=Song.MAX_TRACKS))
def test_create_midifile_emits_expected_track_and_message_counts(tracks):
    song = fresh_song()
    for track in tracks:
        song.add_track(track)

    with TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "fuzz.mid"
        midi_file = song.create_midifile()
        midi_file.save(output_path)
        midi_file = MidiFile(output_path)

        assert len(midi_file.tracks) == len(tracks)

        for midi_track, track in zip(midi_file.tracks, tracks):
            messages = [message for message in midi_track if not message.is_meta]
            expected_note_count = len(track.note_list)

            assert messages[0].type == "program_change"
            assert len(messages) == 1 + (2 * expected_note_count)
            assert all(message.time >= 0 for message in messages)


def test_build_tracks_from_midifile_populates_song_from_midi_data():
    midi_file = MidiFile(type=1)
    metadata_track = MidiTrack()
    metadata_track.append(MetaMessage("set_tempo",
                                      tempo=bpm2tempo(140),
                                      time=0))
    metadata_track.append(
        MetaMessage("time_signature", numerator=3, denominator=4, time=0)
    )
    midi_file.tracks.append(metadata_track)

    instrument_track = MidiTrack()
    instrument_track.append(Message("program_change",
                                    channel=7,
                                    program=42,
                                    time=0))
    instrument_track.append(Message("note_on",
                                    channel=7,
                                    note=60,
                                    velocity=96,
                                    time=0))
    instrument_track.append(
        Message("note_off", channel=7, note=60, velocity=0, time=240)
    )
    instrument_track.append(Message("note_on",
                                    channel=7,
                                    note=64,
                                    velocity=88,
                                    time=120))
    instrument_track.append(
        Message("note_off",
                channel=7,
                note=64,
                velocity=0,
                time=120)
    )
    midi_file.tracks.append(instrument_track)

    song = Song(bpm=100, length=16, signature=(4, 4))
    song.add_track(Track(channel=1, instrument=1, note_list=[]))

    song.build_tracks_from_midifile(midi_file)

    assert song.bpm == 140
    assert song.signature == (3, 4)
    assert song.length == 1
    assert len(song.track_list) == 1

    track = song.track_list[0]
    assert track.channel == 7
    assert track.instrument == 42
    assert track.note_list == [
        Note(pitch=60, start=0, duration=2, velocity=96),
        Note(pitch=64, start=3, duration=1, velocity=88),
    ]


def test_build_tracks_from_midifile_replaces_existing_tracks():
    midi_file = MidiFile(type=1)
    midi_track = MidiTrack()
    midi_track.append(Message("program_change", channel=3, program=11, time=0))
    midi_track.append(Message("note_on",
                              channel=3,
                              note=72,
                              velocity=64,
                              time=120))
    midi_track.append(Message("note_off",
                              channel=3,
                              note=72,
                              velocity=0,
                              time=240))
    midi_file.tracks.append(midi_track)

    song = Song()
    song.add_track(Track(channel=1,
                         instrument=1,
                         note_list=[Note(60, 0, 1, 80)]))

    song.build_tracks_from_midifile(midi_file)

    assert len(song.track_list) == 1
    assert song.track_list[0] == Track(
        channel=3,
        instrument=11,
        note_list=[Note(pitch=72, start=1, duration=2, velocity=64)],
    )


def test_build_tracks_from_midifile_treats_zero_velocity_note_on_as_note_off():
    midi_file = MidiFile(type=1)
    midi_track = MidiTrack()
    midi_track.append(Message("program_change", channel=4, program=8, time=0))
    midi_track.append(Message("note_on",
                              channel=4,
                              note=65,
                              velocity=70,
                              time=120))
    midi_track.append(Message("note_on",
                              channel=4,
                              note=65,
                              velocity=0,
                              time=240))
    midi_file.tracks.append(midi_track)

    song = Song()
    song.build_tracks_from_midifile(midi_file)

    assert song.track_list == [
        Track(
            channel=4,
            instrument=8,
            note_list=[Note(pitch=65, start=1, duration=2, velocity=70)],
        )
    ]


def test_build_tracks_from_midifile_rejects_non_midifile_inputs():
    song = Song()

    try:
        song.build_tracks_from_midifile("not-a-midi-file")
    except TypeError as exc:
        assert "MidiFile" in str(exc)
    else:
        raise AssertionError("Expected build_tracks_from_midifile to reject bad input")


@given(
    tracks=st.lists(
        imported_track_strategy(),
        max_size=Song.MAX_TRACKS,
    ),
    bpm=st.integers(min_value=40, max_value=220),
    numerator=st.integers(min_value=1, max_value=7),
    denominator=st.sampled_from([1, 2, 4, 8, 16]),
)
def test_build_tracks_from_midifile_round_trips_generated_midi_data(
    tracks,
    bpm,
    numerator,
    denominator,
):
    midi_file = MidiFile(type=1)
    metadata_track = MidiTrack()
    metadata_track.append(MetaMessage("set_tempo",
                                      tempo=bpm2tempo(bpm),
                                      time=0))
    metadata_track.append(
        MetaMessage(
            "time_signature",
            numerator=numerator,
            denominator=denominator,
            time=0,
        )
    )
    midi_file.tracks.append(metadata_track)

    for track in tracks:
        midi_file.tracks.append(midi_track_from_track(track))

    song = fresh_song(bpm=100, length=16, signature=(4, 4))
    song.build_tracks_from_midifile(midi_file)

    assert song.bpm == bpm
    assert song.signature == (numerator, denominator)
    assert song.track_list == tracks
    if tracks:
        assert song.length >= 1
