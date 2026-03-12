from typing import List
from note import Note


class Track:
    """collection of notes organized by track and pitch
    """
    def __init__(self, channel: int = 0,
                 instrument: int = 0,
                 piano_roll: list[Note] = None) -> None:
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

        if piano_roll is not None:
            self._piano_roll = piano_roll

