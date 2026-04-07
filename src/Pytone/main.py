from models.song import Song
from models.track import Track
from models.note import Note
from models.audioEngine import Engine


def main() -> None:
    """import gaurd
    """
    song = Song()
    track_1 = Track()
    track_2 = Track(instrument="Taiko Drum")

    track_1.add_note(Note(pitch=60, start=0, duration=16))
    track_1.add_note(Note(pitch=64, start=0, duration=16))
    track_1.add_note(Note(pitch=67, start=0, duration=16))
    track_2.add_note(Note(pitch=73, start=4, duration=16))
    track_2.add_note(Note(pitch=73, start=6, duration=16))
    track_2.add_note(Note(pitch=74, start=8, duration=16))

    song.add_track(track=track_1)
    song.add_track(track=track_2)
    mid = song.create_midifile(path=None)
    engine = Engine()
    engine.start()
    engine.play_midi_once(mid)
    # engine.play_midi(mid, loop=True)


if __name__ == "__main__":
    main()
