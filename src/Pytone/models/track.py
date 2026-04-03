"""_summary_

    Raises:
        TypeError: _description_

    Returns:
        _type_: _description_
    """
from typing import List, Any, Optional
from .note import Note


class Track:
    """collection of notes organized by track and pitch

    Args:
        - channel (int): the midi channel that the track is on
        - instument (int): which instrumnet that the miditrack is representing
        - note_list (List[Note]): List of note objects
    """

    # Implementation notes:
    # - note_list could be better implemented as a dictionary probably.

    def __init__(self, note_list: Optional[list[Note]] = None,
                 channel: int = 0,
                 instrument: int = 0) -> None:
        self._note_list = [] if note_list is None else note_list

        if channel < 0:
            channel = 0
        if channel > 15:
            self._channel = channel % 16
        else:
            self._channel = channel

        if instrument < 0:
            instrument = 0
        if instrument > 127:
            self._instrument = instrument % 128
        else:
            self._instrument = instrument

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

    def remove_note(self, index_or_pitch: int, start: Optional[int] = None
                    ) -> Optional[Note]:
        """Remove a note by index or by pitch/start location.

        Args:
            index_or_pitch (int): Note index when ``start`` is omitted, or the
                MIDI pitch when ``start`` is provided.
            start (Optional[int]): Absolute start time in 16th-note steps.

        Returns:
            Optional[Note]: The removed note, or ``None`` when no note matches
            the given pitch/start pair.
        """
        if start is None:
            return self._note_list.pop(index_or_pitch)

        for index, note in enumerate(self.note_list):
            if note.start == start and note.pitch == index_or_pitch:
                return self.note_list.pop(index)
        return None

    def clear_notes(self) -> None:
        """clears self._note_list
        """
        self._note_list.clear()

    def __len__(self) -> int:
        return len(self._note_list)

    def __iter__(self):
        return iter(self._note_list)

    # def sort_note_list(self) -> None:
    #     """sorts _note_list into chronological order

    #     - Currently a stub. Likely not needed on track class
    #     """
    #     pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Track):
            return NotImplemented

        if self.instrument != other.instrument:
            return False
        elif self.channel != other.channel:
            return False
        elif self.note_list != other.note_list:
            return False
        else:
            return True
