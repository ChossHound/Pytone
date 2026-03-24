from typing import Any, List, Tuple, Optional
from track import Track
from mido import Message, MidiTrack, MidiFile
from note import Note


class Song:
    MAX_TRACKS = 4
    _instance = Optional["Song"] = None
    """Class to represent an entire song in the Pytone app.

    - Singleton???

    Args:
        - tempo: (int) tempo of song
        - length (int) # of bars/measures in the song
        - signature: (Tuple(int, int)): Time Signature of song
        - loop: (bool): if tracks should loop back to
                beginning and keep playing after end is reached

    """
    def __new__(cls) -> None:
        return super().__new__(cls)

    def __init__(self,
                 tempo: int = 100,
                 length: int = 16,
                 signature: Tuple[int, int] = (4, 4),
                 loop: bool = True
                 ) -> None:
        self.tempo = tempo
        self.length = length
        self.signature = signature
        self.track_list: list[Track] = []
        self.loop = loop

    @classmethod
    def get_max_tracks(cls) -> int:
        """Return the maximum number of tracks allowed per song."""
        return cls.MAX_TRACKS

    def add_track(self, track: Any) -> None:
        """Add a track to the song if capacity allows."""
        if len(self.track_list) >= self.get_max_tracks():
            raise ValueError(
                f"Song can only contain {self.get_max_tracks()} tracks."
            )

        self.track_list.append(track)

    def remove_track(self, index: int) -> Any:
        """Remove and return the track at the given index."""
        return self.track_list.pop(index)

    def is_full(self) -> bool:
        """Return True when the song already has the maximum tracks."""
        return len(self.track_list) >= self.get_max_tracks()

    def play_song(self) -> None:
        # run compile_tracks, then send the midi file to a synth/ soundcard?
        pass

    def create_midifile(self, path: Optional[str]) -> str:
        """_summary_

        Args:
            path (Optional[str]): _description_

        Returns:
            str: _description_
        """
        # NOTES:

        # Note tracks things in abs_time but midi is delta_time

        # LOGIC:

        # Start with an empty file

        # for each track in our app:

            # Channel 0 is for meta messages

            # create a new MidiTrack object, with only one channel
            # for each note in a track:
                # Seperate into two messages
                    # note_on
                    # 
                    # note_off
                
                # !!! Track the timing of the notes!!!

        # 
        pass

    def export_to_midi(self, path: str) -> str:
        """Export all notes in `track_list` to a type-1 MIDI file."""
        mid = MidiFile(type=1)
        for track in self.track_list:
            mid_track = MidiTrack()

            instrument = getattr(track, "_instrument", 0)
            channel = getattr(track, "channel", 0)
            mid_track.append(
                Message(
                    "program_change",
                    program=instrument,
                    channel=channel,
                    time=0,
                )
            )

            timed_messages: List[Tuple[float, Message]] = []
            for note in getattr(track, "_note_list", []):
                timed_messages.extend(self.note_to_message(note, channel))

            timed_messages.sort(
                key=lambda item: (
                    item[0],
                    0 if item[1].type == "note_off" else 1,
                )
            )

            previous_tick = 0
            for absolute_time, message in timed_messages:
                absolute_tick = int(round(absolute_time * mid.ticks_per_beat))
                message.time = max(0, absolute_tick - previous_tick)
                mid_track.append(message)
                previous_tick = absolute_tick

            mid.tracks.append(mid_track)

        mid.save(path)
        return path

    def export_to_wav(self, midi_path: str) -> str:
        """exports project to a .wav file

        returns path to file
        """
        pass

    def load_from_midi(self, path: str) -> None:
        pass

    def notes_to_midi(self) -> None:
        """Converts the list of notes into list of midi messages
        """
        pass

    def note_to_message(self,
                        note: Note,
                        channel: int = 0) -> List[Tuple[float, Message]]:
        """Converts a Note object into corresponding midi messages

        Args:
            note (Note): Note object to be converted to midi message
            channel (int): MIDI channel for the note's track

        Returns:
            List[Tuple[float, Message]]: List[(absolute_time, message)]
            this should theoretically only be 2 midi messages.
        """
        return [(note.start,
                 Message("note_on",
                         note=note.pitch,
                         velocity=note.velocity,
                         channel=channel)),
                (note.start + note.duration,
                 Message("note_off",
                         note=note.pitch,
                         velocity=0,
                         channel=channel))]

    def message_to_note(self, on_message: Message,
                        off_message: Message, duration: int) -> Note:
        """

        Args:
            on_message (Message): note_on midi message for given pitch of note
            off_message (Message): note_off midi message for given pitch of note

        Returns:
            Note: _description_
        """
        # NOTES:
        # note_off might not be necessary, just need delta time for duration

        # Testing this Function:
        # - Messages cannot have differing pitches
        # - Messages cannot be mismatched (ie "note off" in on_message argument)
        # - velocity comes from note on message

        # Logic:
        # 
        pass

    def build_tracks_from_midifile(self, file: MidiFile) -> None:
        """Builds the track_list from a given Midifile

        Args:
            file (MidiFile): _description_
        """
        pass

    def select_instrument(self, track: int, instrument: int) -> None:
        """function to be called for selecting an instument for a track

        Args:
            track (int): _description_
            instrument (int): _description_
        """
        pass