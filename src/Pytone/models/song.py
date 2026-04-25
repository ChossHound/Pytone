""" Module providing Song class to represent Midisong """
import os
from collections import defaultdict
from typing import Any, List, Tuple, Optional
from mido import Message, MetaMessage, MidiTrack, MidiFile, bpm2tempo, tempo2bpm
import tkinter as tk
from tkinter import filedialog

from .track import Track
from .instruments import (
    GENERAL_MIDI_INSTRUMENT_NAMES,
    GENERAL_MIDI_INSTRUMENTS,
    InstrumentInput,
    instrument_name,
    resolve_instrument,
)
from .note import Note


class Song:
    _instance: Optional["Song"] = None
    MAX_TRACKS = 4
    STEPS_PER_BEAT = Note.STEPS_PER_BEAT
    GENERAL_MIDI_INSTRUMENTS = GENERAL_MIDI_INSTRUMENTS
    GENERAL_MIDI_INSTRUMENT_NAMES = GENERAL_MIDI_INSTRUMENT_NAMES
    """Class to represent an entire song in the Pytone app.

    Args:
        - bpm: (int) tempo of song
        - length (int) # of bars/measures in the song
        - signature: (Tuple(int, int)): Time Signature of song
        - loop: (bool): if tracks should loop back to
                beginning and keep playing after end is reached

    """
    def __new__(cls, *args, **kwargs) -> "Song":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 bpm: int = 120,
                 length: int = 16,
                 signature: Tuple[int, int] = (4, 4),
                 loop: bool = True
                 ) -> None:
        if getattr(self, "_initialized", False):
            return
        self.bpm = bpm
        self.length = length
        self.signature = signature
        self.track_list: list[Track] = []
        self._overflow_track = None
        self.loop = loop
        self._initialized = True

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance.

        Primarily intended for tests so each test can start with a clean Song.
        """
        cls._instance = None

    @classmethod
    def get_max_tracks(cls) -> int:
        """Return the maximum number of tracks allowed per song."""
        return cls.MAX_TRACKS

    @staticmethod
    def instrument_code(instrument: InstrumentInput) -> int:
        """Resolve a General MIDI instrument name into its program number."""
        return resolve_instrument(instrument)

    @staticmethod
    def instrument_name(program: int) -> str:
        """Return the canonical General MIDI name for a program number."""
        return instrument_name(program)

    def add_track(self, track: Any) -> None:
        """Add a track to the song if capacity allows."""
        if len(self.track_list) >= self.get_max_tracks():
            raise ValueError(
                f"Song can only contain {self.get_max_tracks()} tracks."
            )

        if getattr(track, "channel_was_provided", True) is False:
            track._channel = self._next_available_channel()

        self.track_list.append(track)

    def _next_available_channel(self) -> int:
        """Return the lowest MIDI channel not currently used by the song."""
        used_channels = {track.channel for track in self.track_list}

        for channel in range(16):
            if channel not in used_channels:
                return channel
        return 0

    def remove_track(self, index: int) -> Any:
        """Remove and return the track at the given index."""
        return self.track_list.pop(index)

    def is_full(self) -> bool:
        """Return True when the song already has the maximum tracks."""
        return len(self.track_list) >= self.get_max_tracks()

    def create_midifile(self) -> MidiFile:
        """Create a type-1 MIDI file from every track in the song.

        Notes are stored as 16th-note steps in the app model, while MIDI
        messages must be written with delta times. This method converts each
        track's notes into sorted note-on/note-off messages, then rewrites the
        absolute note timings as per-track delta times before saving.

        Args:
            path (Optional[str]): Destination path for the MIDI file. When
                omitted, a Midifile object is returned instead

        Returns:
            str | Midifile: Absolute path to the saved MidiFile if path is
            given, otherwise returns the Midifile itself.
        """

        mid = MidiFile(type=1)

        for track in self.track_list:
            mid_track = MidiTrack()
            instrument = track.instrument
            channel = track.channel

            if not mid.tracks:
                numerator, denominator = self.signature
                mid_track.append(
                    MetaMessage(
                        "set_tempo",
                        tempo=bpm2tempo(self.bpm),
                        time=0,
                    )
                )
                mid_track.append(
                    MetaMessage(
                        "time_signature",
                        numerator=numerator,
                        denominator=denominator,
                        time=0,
                    )
                )

            mid_track.append(
                Message(
                    "program_change",
                    program=instrument,
                    channel=channel,
                    time=0,
                )
            )

            timed_messages: List[Tuple[int, Message]] = []
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
                absolute_tick = self.steps_to_ticks(
                    absolute_time,
                    mid.ticks_per_beat,
                )
                message.time = max(0, absolute_tick - previous_tick)
                mid_track.append(message)
                previous_tick = absolute_tick

            mid.tracks.append(mid_track)
        return mid
    
    def create_midifile_from(self, starting_beat: int = 0) -> MidiFile:
        """creates a midifile from the current track list starting
            at starting_beat


        Args:
            starting_beat (int, optional): the 16th note possition in the song
            to start from. Defaults to 0.

        Raises:
            RuntimeError: _description_
            RuntimeError: _description_
            ValueError: _description_
            TypeError: _description_

        Returns:
            MidiFile: a midifile of the sub-song starting from
                position starting_beat
        """
        if not isinstance(starting_beat, int):
            raise TypeError("starting_beat must be an int")
        if starting_beat < 0:
            raise ValueError("starting_beat must be at least 0")

        mid = MidiFile(type=1)

        for track in self.track_list:
            mid_track = MidiTrack()
            instrument = track.instrument
            channel = track.channel

            if not mid.tracks:
                numerator, denominator = self.signature
                mid_track.append(
                    MetaMessage(
                        "set_tempo",
                        tempo=bpm2tempo(self.bpm),
                        time=0,
                    )
                )
                mid_track.append(
                    MetaMessage(
                        "time_signature",
                        numerator=numerator,
                        denominator=denominator,
                        time=0,
                    )
                )

            mid_track.append(
                Message(
                    "program_change",
                    program=instrument,
                    channel=channel,
                    time=0,
                )
            )

            timed_messages: List[Tuple[int, Message]] = []
            for note in getattr(track, "_note_list", []):
                if note.start < starting_beat:
                    continue

                rebased_note = Note(
                    pitch=note.pitch,
                    start=note.start - starting_beat,
                    duration=note.duration,
                    velocity=note.velocity,
                )
                timed_messages.extend(self.note_to_message(rebased_note, channel))

            timed_messages.sort(
                key=lambda item: (
                    item[0],
                    0 if item[1].type == "note_off" else 1,
                )
            )

            previous_tick = 0
            for absolute_time, message in timed_messages:
                absolute_tick = self.steps_to_ticks(
                    absolute_time,
                    mid.ticks_per_beat,
                )
                message.time = max(0, absolute_tick - previous_tick)
                mid_track.append(message)
                previous_tick = absolute_tick

            mid.tracks.append(mid_track)

        return mid

    @staticmethod
    def _normalize_midifile_path(path: str) -> str:
        """Ensure exported MIDI files use a MIDI extension."""
        if path.lower().endswith((".mid", ".midi")):
            return path
        return f"{path}.mid"

    # def choose_midifile_path(
    #     self,
    #     initial_filename: str = "song.mid",
    #     initial_dir: Optional[str] = None,
    #     title: str = "Save MIDI File",
    # ) -> Optional[str]:
    #     """Open a native save dialog and return the selected MIDI path.

    #     Returns ``None`` when the user cancels the dialog.
    #     """
    #     if tk is None or filedialog is None:
    #         raise RuntimeError("tkinter is not available for MIDI export")

    #     root = None
    #     try:
    #         root = tk.Tk()
    #         root.withdraw()
    #         selected_path = filedialog.asksaveasfilename(
    #             title=title,
    #             defaultextension=".mid",
    #             filetypes=[
    #                 ("MIDI files", "*.mid *.midi"),
    #                 ("All files", "*.*"),
    #             ],
    #             initialfile=initial_filename,
    #             initialdir=initial_dir or os.getcwd(),
    #         )
    #     except tk.TclError as exc:
    #         raise RuntimeError(
    #             "Could not open the MIDI save dialog. "
    #             "Check that a desktop display is available."
    #         ) from exc
    #     finally:
    #         if root is not None:
    #             root.destroy()

    #     if not selected_path:
    #         return None

    #     normalized_path = self._normalize_midifile_path(selected_path)
    #     return os.path.abspath(normalized_path)

    # def export_to_midi(
    #     self,
    #     path: Optional[str] = None,
    #     initial_filename: str = "song.mid",
    #     initial_dir: Optional[str] = None,
    # ) -> Optional[str]:
    #     """Export the song to a MIDI file.

    #     When ``path`` is omitted, a native save dialog is shown so the user
    #     can choose where to save the file. Returns ``None`` if the dialog is
    #     cancelled.
    #     """
    #     destination = path
    #     if destination is None:
    #         destination = self.choose_midifile_path(
    #             initial_filename=initial_filename,
    #             initial_dir=initial_dir,
    #         )
    #         if destination is None:
    #             return None

    #     destination = self._normalize_midifile_path(destination)
    #     return self.create_midifile(destination)

    @classmethod
    def steps_to_ticks(cls, steps: int, ticks_per_beat: int) -> int:
        """Convert 16th-note steps into MIDI ticks."""
        return int(round((steps * ticks_per_beat) / cls.STEPS_PER_BEAT))

    @classmethod
    def ticks_to_steps(cls, ticks: int, ticks_per_beat: int) -> int:
        """Convert MIDI ticks into 16th-note steps."""
        if ticks_per_beat <= 0:
            raise ValueError("ticks_per_beat must be positive")
        return int(round((ticks * cls.STEPS_PER_BEAT) / ticks_per_beat))

    def note_to_message(self,
                        note: Note,
                        channel: int = 0) -> List[Tuple[int, Message]]:
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
        max_song_step = 0

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
                start_step = self.ticks_to_steps(
                    start_tick,
                    midifile.ticks_per_beat,
                )
                duration_step = max(
                    Note.MIN_DURATION,
                    self.ticks_to_steps(
                        absolute_tick - start_tick,
                        midifile.ticks_per_beat,
                    ),
                )
                notes.append(
                    Note(
                        pitch=message.note,
                        start=start_step,
                        duration=duration_step,
                        velocity=velocity,
                    )
                )
                max_song_step = max(max_song_step, start_step + duration_step)

            if notes or channel is not None or instrument != 0:
                notes.sort(key=lambda note: (note.start, note.pitch))
                if len(self.track_list) <= self.MAX_TRACKS:
                    self.add_track(
                        Track(
                            channel=channel or 0,
                            instrument=instrument,
                            note_list=notes,
                        )
                    )
                elif self._overflow_track is None:
                    # TRACK OVERFLOW CONDITION
                    self._overflow_track = Track(channel=channel,
                                                 instrument=instrument,
                                                 note_list=notes,
                                                 )
                else:
                    self._overflow_track.extend_notes(notes=notes)
                    self._overflow_track.note_list.sort(key=lambda note: (note.start, note.pitch))

        self.bpm = int(round(tempo2bpm(midi_tempo)))
        self.signature = (numerator, denominator)

        steps_per_bar = (
            numerator * ((self.STEPS_PER_BEAT * 4) / denominator)
            if denominator else 0
        )
        if steps_per_bar:
            self.length = max(1, int(max_song_step / steps_per_bar))

    def save_song(
        self,
        path: Optional[str] = None,
        initial_filename: str = "song.mid",
        initial_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Save the current song as a MIDI file.

        When ``path`` is omitted, a native save dialog is shown. Returns the
        saved absolute path, or ``None`` if the dialog is cancelled.
        """
        destination = path
        if destination is None:
            if tk is None or filedialog is None:
                raise RuntimeError("tkinter is not available for song saving")

            root = None
            try:
                root = tk.Tk()
                root.withdraw()
                destination = filedialog.asksaveasfilename(
                    title="Save As",
                    defaultextension=".mid",
                    filetypes=[
                        ("MIDI files", "*.mid *.midi"),
                        ("All files", "*.*"),
                    ],
                    initialfile=initial_filename,
                    initialdir=initial_dir or os.getcwd(),
                )
            except tk.TclError as exc:
                raise RuntimeError(
                    "Could not open the save dialog. "
                    "Check that a desktop display is available."
                ) from exc
            finally:
                if root is not None:
                    root.destroy()

            if not destination:
                return None

        destination = os.path.abspath(self._normalize_midifile_path(destination))
        midifile = self.create_midifile()
        midifile.save(destination)
        return destination

    def load_song(
        self,
        path: Optional[str] = None,
        initial_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Load a song from a MIDI file.

        When ``path`` is omitted, a native open dialog is shown. Returns the
        loaded absolute path, or ``None`` if the dialog is cancelled.

        Raises:
            ValueError: The selected file is not a MIDI file or could not be
                parsed as one.
        """
        destination = path
        if destination is None:
            if tk is None or filedialog is None:
                raise RuntimeError("tkinter is not available for song loading")

            root = None
            try:
                root = tk.Tk()
                root.withdraw()
                destination = filedialog.askopenfilename(
                    title="Open Song",
                    filetypes=[
                        ("MIDI files", "*.mid *.midi"),
                        ("All files", "*.*"),
                    ],
                    initialdir=initial_dir or os.getcwd(),
                )
            except tk.TclError as exc:
                raise RuntimeError(
                    "Could not open the load dialog. "
                    "Check that a desktop display is available."
                ) from exc
            finally:
                if root is not None:
                    root.destroy()

            if not destination:
                return None

        destination = os.path.abspath(destination)
        if not destination.lower().endswith((".mid", ".midi")):
            raise ValueError("Selected file must be a MIDI file")

        try:
            midifile = MidiFile(destination)
        except (OSError, EOFError, ValueError, TypeError) as exc:
            raise ValueError(
                f"Selected file is not a valid MIDI file: {destination}"
            ) from exc

        self.build_tracks_from_midifile(midifile)
        return destination
