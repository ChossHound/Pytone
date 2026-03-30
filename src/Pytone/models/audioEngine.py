from typing import Optional
from mido import MidiFile, MidiTrack
from note import Note


class Engine:
    """Simple program to pass of midi instructions to sound card to be played

    Returns:
        _type_: _description_
    """
    _instance: Optional["Engine"] = None

    def __new__(cls) -> "Engine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
            
    def __init__(self) -> None:
        pass

    def play_midi(self, song: MidiFile) -> None:
        """Sends a given Midifile to the soundcard to be played
        """
        pass

    def play_wav(self, path: str) -> None:
        """Sends a .wav file to the audiocard to be played

        Args:
            path (str): path to the given .wav file.
        """
        pass

    def send_note_on(self, pitch, velocity) -> None:
        pass

    def send_note_off(self, pitch) -> None:
        pass