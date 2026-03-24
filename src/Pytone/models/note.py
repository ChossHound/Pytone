from dataclasses import dataclass


@dataclass
class Note:
    """object used to represent a midi note

    pitch (int): 0 - 127
    velocity (int): 0 - 127

    start: note start time relative to song beginning in ticks
    duration: note end time relative to note start time in ticks
    """
    pitch: int
    start: int
    duration: int
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
        
    def __eq__(self, other: "Note") -> bool:
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
