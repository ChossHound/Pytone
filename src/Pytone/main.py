from models.song import Song
from models.track import Track
from models.note import Note
from models.audioEngine import Engine
from ui.gui import GUI


def main() -> None:
    """import gaurd
    """

    GUI().run()

    # song = Song()
    # track_1 = Track()
    # track_2 = Track(instrument="Taiko Drum")

    # track_1.add_note(Note(pitch=60, start=0, duration=16))
    # track_1.add_note(Note(pitch=64, start=0, duration=16))
    # track_1.add_note(Note(pitch=67, start=0, duration=16))
    # track_2.add_note(Note(pitch=73, start=4, duration=16))
    # track_2.add_note(Note(pitch=73, start=6, duration=16))
    # track_2.add_note(Note(pitch=74, start=8, duration=16))

    # song.add_track(track=track_1)
    # song.add_track(track=track_2)
    # mid = song.create_midifile(path=None)
    # engine = Engine()
    # engine.start()
    # engine.play_midi_once(mid)
    # engine.play_midi(mid, loop=True)
    # pyramid_song()


def pyramid_song():
    song_1 = Song(bpm=130, loop=False)

    track_1 = Track(instrument=24)
    track_2 = Track(instrument="Voice Oohs")

    track_1.add_note(Note(pitch=46, start=0, duration=6))
    track_1.add_note(Note(pitch=49, start=0, duration=6))
    track_1.add_note(Note(pitch=54, start=0, duration=6))

    track_1.add_note(Note(pitch=46, start=6, duration=6))
    track_1.add_note(Note(pitch=49, start=6, duration=6))
    track_1.add_note(Note(pitch=54, start=6, duration=6))

    track_1.add_note(Note(pitch=47, start=12, duration=8))
    track_1.add_note(Note(pitch=50, start=12, duration=8))
    track_1.add_note(Note(pitch=54, start=12, duration=8))

    track_2.add_note(Note(pitch=66, start=0, duration=16))

    song_1.add_track(track_1)
    song_1.add_track(track_2)
    mid = song_1.create_midifile(path=None)
    engine = Engine()
    engine.start()
    engine.play_midi_once(mid)
    GUI().run()
    # engine.play_midi(mid, loop=True)


if __name__ == "__main__":
    main()
