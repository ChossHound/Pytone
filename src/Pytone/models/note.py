"""_summary_

    Raises:
        TypeError: _description_
        ValueError: _description_
        TypeError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """
from dataclasses import dataclass


@dataclass
class Note:
    """object used to represent a midi note

    pitch (int): 0 - 127, 0 corresponde to a C, so anything % 12 == 0 is a C.
    velocity (int): 0 - 127, Effectively synonymous with volume

    start: note start time relative to song beginning in 16th notes
    duration: note length in 16th notes
    """
    STEPS_PER_BEAT = 4
    MIN_DURATION = 1

    pitch: int
    start: int
    duration: int
    velocity: int = 100

    def __post_init__(self) -> None:
        self._validate_midi_value("pitch", self.pitch)
        self._validate_midi_value("velocity", self.velocity)
        self._validate_time_value("start", self.start, minimum=0)
        self._validate_time_value(
            "duration",
            self.duration,
            minimum=self.MIN_DURATION,
        )

    @staticmethod
    def _validate_midi_value(name: str, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an int")
        if not 0 <= value <= 127:
            raise ValueError(f"{name} must be between 0 and 127")

    @staticmethod
    def _validate_time_value(name: str, value: int, minimum: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an int")
        if value < minimum:
            raise ValueError(f"{name} must be at least {minimum}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented

        if self.pitch != other.pitch:
            return False
        elif self.velocity != other.velocity:
            return False
        elif self.start != other.start:
            return False
        elif self.duration != other.duration:
            return False
        else:
            return True
