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
import re


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

    @staticmethod
    def parse_note_to_pitch(input_note: str) -> int:
        """Takes in a note string and converts it to a pitch value

        Example:
            input: C#2
            output: 25

        Notes are interpreted in the project's ``C0 == 0`` pitch system.
        Accidentals are applied within the given octave only; they do not wrap
        across octave boundaries. For example, ``B#0`` resolves to ``12``,
        while ``Cb0`` resolves to ``-1`` and is therefore rejected as out of
        the MIDI range. Notes can range from C0 up to G10.

        Args:
            input_note (str): note label

        Returns:
            int: corresponding integer value of note
        """
        if not isinstance(input_note, str):
            raise TypeError("input_note must be a string")

        match = re.fullmatch(r"\s*([A-Ga-g])([#b]?)(\d+)\s*", input_note)
        if match is None:
            raise ValueError(f"{input_note} is not a valid note label")

        note = match.group(1).upper()
        accidental = match.group(2)
        octave = int(match.group(3))

        note_num = 0
        accidental_num = 0

        match accidental:
            case '#':
                accidental_num = 1
            case 'b':
                accidental_num = -1

        match note:
            case "C":
                note_num = 0
            case "D":
                note_num = 2
            case "E":
                note_num = 4
            case "F":
                note_num = 5
            case "G":
                note_num = 7
            case "A":
                note_num = 9
            case "B":
                note_num = 11

        value = (12 * octave) + note_num + accidental_num
        if value < 0 or value > 127:
            raise ValueError(f"{input_note} is not a valid midi note")
        return value

    @staticmethod
    def parse_pitch_to_note(pitch_value: int) -> str:
        """Takes in an integer value and converts it to a string representing
            the note's letter and octave.

        Args:
            pitch_value (int): 0-127

        Returns:
            str: note and octave Ex: C#2
        """
        note_str = ""
        if pitch_value > 127 or pitch_value < 0:
            raise ValueError

        note = pitch_value % 12
        octave = pitch_value // 12

        # get the note type
        match note:
            case 0:
                note_str = 'C'
            case 1:
                note_str = 'C#'
            case 2:
                note_str = 'D'
            case 3:
                note_str = 'D#'
            case 4:
                note_str = 'E'
            case 5:
                note_str = 'F'
            case 6:
                note_str = 'F#'
            case 7:
                note_str = 'G'
            case 8:
                note_str = 'G#'
            case 9:
                note_str = 'A'
            case 10:
                note_str = 'A#'
            case 11:
                note_str = 'B'

        return note_str + str(octave)

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
