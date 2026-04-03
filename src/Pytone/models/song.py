""" Module providing Song class to represent Midisong """
import os
from collections import defaultdict
from typing import Any, List, Tuple, Optional
from track import Track
from mido import Message, MidiTrack, MidiFile, bpm2tempo, tempo2bpm
from note import Note


class Song:
    MAX_TRACKS = 4
    """Class to represent an entire song in the Pytone app.

    Args:
        - bpm: (int) tempo of song
        - length (int) # of bars/measures in the song
        - signature: (Tuple(int, int)): Time Signature of song
        - loop: (bool): if tracks should loop back to
                beginning and keep playing after end is reached

    """
    def __init__(self,
                 bpm: int = 100,
                 length: int = 16,
                 signature: Tuple[int, int] = (4, 4),
                 loop: bool = True
                 ) -> None:
        self.bpm = bpm
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

    def create_midifile(self, path: Optional[str]) -> str | MidiFile:
        """Create a type-1 MIDI file from every track in the song.

        Notes are stored with absolute times in the app model, while MIDI
        messages must be written with delta times. This method converts each
        track's notes into sorted note-on/note-off messages, then rewrites the
        absolute note timings as per-track delta times before saving.

        Args:
            path (Optional[str]): Destination path for the MIDI file. When
                omitted, defaults to ``song.mid`` in the current working
                directory.

        Returns:
            str | Midifile: Absolute path to the saved MidiFile if path is
            given, otherwise returns the Midifile itself.
        """
        

        
        mid = MidiFile(type=1)

        for track in self.track_list:
            mid_track = MidiTrack()
            instrument = track.instrument
            channel = track.channel

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
        if path is None:
            return mid
        else:
            output_path = os.path.abspath(path)
            mid.save(output_path)
        return output_path

    # def export_to_midi(self, path: str) -> str:
    #     """Export all notes in `track_list` to a type-1 MIDI file."""
    #     return self.create_midifile(path)

    # def export_to_wav(self, midi_path: str) -> str:
    #     """exports project to a .wav file

    #     returns path to file
    #     """
    #     pass

    def load_from_midi(self, path: str) -> None:
        pass

    # def notes_to_midi(self) -> None:
    #     """Converts the list of notes into list of midi messages
    #     """
    #     pass

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
            off_message (Message): note_off midi message for given pitch of 
                note

        Returns:
            Note: _description_
        """
        # NOTES:
        # note_off might not be necessary, just need delta time for duration

        # Testing this Function:
        # - Messages cannot have differing pitches
        # - Messages cannot be mismatched ( "note_off" in on_message argument)
        # - velocity comes from note on message

        # Logic:
        # 
        pass

    def build_tracks_from_midifile(self, midifile: MidiFile) -> None:
        """Builds the track_list from a given Midifile

        Args:
            midifile (MidiFile): midifile object to build tracks from.
        """
        if not isinstance(midifile, MidiFile):
            raise TypeError("midifile must be a MidiFile")

        self.track_list = []

        midi_tempo = bpm2tempo(self.bpm)
        numerator, denominator = self.signature
        max_song_tick = 0

        for midi_track in midifile.tracks:
            absolute_tick = 0
            instrument = 0
            channel: Optional[int] = None
            notes: List[Note] = []
            active_notes: dict[tuple[int, int], list[tuple[int, int]]] = (
                defaultdict(list)
            )

            for message in midi_track:
                absolute_tick += message.time
                max_song_tick = max(max_song_tick, absolute_tick)

                if message.is_meta:
                    if message.type == "set_tempo":
                        midi_tempo = message.tempo
                    elif message.type == "time_signature":
                        numerator = message.numerator
                        denominator = message.denominator
                    continue

                if channel is None and hasattr(message, "channel"):
                    channel = message.channel

                if message.type == "program_change":
                    instrument = message.program
                    continue

                is_note_on = (
                    message.type == "note_on" and message.velocity > 0
                )
                is_note_off = (
                    message.type == "note_off"
                    or (message.type == "note_on" and message.velocity == 0)
                )

                if is_note_on:
                    active_notes[(message.channel, message.note)].append(
                        (absolute_tick, message.velocity)
                    )
                    continue

                if not is_note_off:
                    continue

                active_key = (message.channel, message.note)
                if not active_notes[active_key]:
                    continue

                start_tick, velocity = active_notes[active_key].pop(0)
                notes.append(
                    Note(
                        pitch=message.note,
                        start=start_tick,
                        duration=max(0, absolute_tick - start_tick),
                        velocity=velocity,
                    )
                )

            if notes or channel is not None or instrument != 0:
                notes.sort(key=lambda note: (note.start, note.pitch))
                self.add_track(
                    Track(
                        channel=channel or 0,
                        instrument=instrument,
                        note_list=notes,
                    )
                )

        self.bpm = int(round(tempo2bpm(midi_tempo)))
        self.signature = (numerator, denominator)

        beats_per_bar = numerator * (4 / denominator) if denominator else 0
        if beats_per_bar and midifile.ticks_per_beat:
            total_beats = max_song_tick / midifile.ticks_per_beat
            self.length = max(1, int(total_beats / beats_per_bar))

    def select_instrument(self, track: int, instrument: int) -> None:
        """function to be called for selecting an instument for a track

        Args:
            track (int): _description_
            instrument (int): _description_
        """
        pass
