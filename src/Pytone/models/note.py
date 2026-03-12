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
