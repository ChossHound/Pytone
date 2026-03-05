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
        pass

    def compile_tracks(self) -> None:
        pass

    def save_as_midi(self) -> None:
        pass

    def export_to_wav(self) -> str:
        """exports project to a .wav file

        returns path to file
        """
        pass
