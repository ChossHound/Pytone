from typing import List, Any
from note import Note


class Track:
    """collection of notes organized by track and pitch
    """
    def __init__(self, channel: int = 0,
                 instrument: int = 0,
                 note_list: list[Note] = None) -> None:
        if channel < 0:
            channel = 0
        elif channel > 15:
            self._channel = channel % 16
        else:
            self._channel = channel

        if instrument < 0:
            instrument = 0
        elif instrument > 127:
            self._instrument = instrument % 128
        else:
            self._instrument = instrument

        if note_list is not None:
            self._note_list = note_list
        
        self._midi_msg_list: List[Any]

    # ----------Getters & Setters----------
    @property
    def channel(self) -> int:
        return self._channel

    @channel.setter
    def channel(self, num: int) -> None:
        self._channel = num

    @channel.deleter
    def channel(self):
        del self._channel
    
    def add_note_list(self, note_list: List[Note]) -> None:
        """Adds a list of notes to the track.

        Args:
            piano_roll (List[Note]): _description_
        """
        pass

    def add_note(self, note: Note) -> None:
        """adds a note to the list of notes in the track

        Args:
            note (Note): 1 instance of the Note object
        """
        pass

    def sort_note_list(self) -> None:
        """sorts _note_list into chronological order
        """
        pass

