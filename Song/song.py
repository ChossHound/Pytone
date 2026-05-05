from typing import Tuple, Optional
# import Track class


class Song:
    _instance = Optional["Song"] = None
    """Class to represent an entire song in the Pytone app.

    - Singleton???

    Args:
        - tempo: (int) tempo of song
        - length (int) # of bars/measures in the song
        - signature: (Tuple(int, int)): Time Signature of song
        - loop: (bool): if tracks should loop back to
                beginning and keep playing after end is reached

    """

    def __new__(cls) -> None:
        pass

    def __init__(self,
                 tempo: int = 100,
                 length: int = 16,
                 signature: Tuple[int, int] = (4, 4),
                 loop: bool = True
                 ) -> None:
        self.tempo = tempo
        self.length = length
        self.signature = signature
        self.loop = loop
        self.track_1 = None
        self.track_2 = None
        self.track_3 = None
        self.track_4 = None

    def play_song(self) -> None:
        # run compile_tracks, then send the midi file to a synth/ soundcard?
        pass

    def compile_tracks(self) -> None:
        # compile the notes into midi from
        pass

    def save_as_midi(self) -> None:
        # save your song as midi at a selected folder
        pass