from models.song import Song
from models.track import Track
from models.note import Note
from models.audioEngine import Engine


def main() -> None:
    """import gaurd
    """
    song = Song()
    track_1 = Track()

    track_1.add_note(Note(pitch=60, start=0, duration=1))

    song.add_track(track=track_1)
    mid = song.create_midifile(path=None)
    engine = Engine()
    engine.play_midi_once(mid)


if __name__ == "__main__":
    main()
