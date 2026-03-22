from dataclasses import dataclass


@dataclass
class Note:
    """object used to represent a midi note

    pitch (int): 0 - 127
    velocity (int): 0 - 127

    start: time started
    duration: length of note until release
    """
    pitch: int
    start: float
    duration: float
    velocity: int = 100

    def __post_init__(self) -> None:
        self._validate_midi_value("pitch", self.pitch)
        self._validate_midi_value("velocity", self.velocity)

    @staticmethod
    def _validate_midi_value(name: str, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an int")
        if not 0 <= value <= 127:
            raise ValueError(f"{name} must be between 0 and 127")
