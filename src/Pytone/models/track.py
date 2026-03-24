from typing import List, Any
from note import Note


class Track:
    """collection of notes organized by track and pitch

    Args:
        - channel (int): the midi channel that the track is on
        - instument (int): which instrumnet that the miditrack is representing
        - note_list (List[Note]): List of note objects
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
        """getter for the _channel property

        Returns:
            int: channel
        """
        return self._channel

    @channel.setter
    def channel(self, num: int) -> None:
        self._channel = num

    @channel.deleter
    def channel(self):
        del self._channel

    @property
    def instrument(self) -> int:
        """Getter for the _instument property

        Returns:
            int: instrument value
        """
        return self._instrument

    @instrument.setter
    def instrument(self, value: int) -> None:
        self._instrument = max(0, min(127, value))

    @instrument.deleter
    def instrument(self) -> None:
        del self._instrument

    @property
    def note_list(self) -> List[Note]:
        """Getter for the _note_list attribute

        Returns:
            List[Note]: _description_
        """
        return self._note_list

    def add_note(self, note: Note) -> None:
        """appends a note to the end of _note_list

        Args:
            note (Note): instance of Note

        Raises:
            TypeError: if a note is note an instance of Note
        """
        if not isinstance(note, Note):
            raise TypeError("note must be a Note")
        self._note_list.append(note)

    def extend_notes(self, notes: List[Note]) -> None:
        """appends given list of notes onto end of _note_list

        Args:
            notes (List[Note]):
        """
        for note in notes:
            self.add_note(note)

    def remove_note(self, index: int) -> Note:
        """pops a note at given index out of _note_list

        Args:
            index (int): _description_

        Returns:
            Note: _description_
        """
        return self._note_list.pop(index)

    def clear_notes(self) -> None:
        """clears self._note_list
        """
        self._note_list.clear()

    def __len__(self) -> int:
        return len(self._note_list)

    def __iter__(self):
        return iter(self._note_list)

    def sort_note_list(self) -> None:
        """sorts _note_list into chronological order

        - Currently a stub. Likely not needed on track class
        """
        pass

    def __eq__(self, other: "Track") -> bool:
        if self.instrument != other.instrument:
            return False
        elif self.channel != other.channel:
            return False
        elif self.note_list != other.note_list:
            return False
        else:
            return True
