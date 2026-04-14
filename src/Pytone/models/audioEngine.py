"""_summary_

    Raises:
        FileNotFoundError: _description_
        TypeError: _description_

    Returns:
        _type_: _description_
    """
from pathlib import Path
from typing import Optional
import threading
# from importlib.resources import files
from mido import MidiFile
import fluidsynth
import time
# from note import Note


class Engine:
    """Simple program to pass of midi instructions to sound card to be played.

    Engine is designed to use fluidsynth so if you dont have fluidsynth 
    playback wont work. Midi editing features should still work regardless. 

    Returns:
        _type_: _description_
    """
    _instance: Optional["Engine"] = None

    def _test_audio(self) -> None:
        project_root = Path(__file__).resolve().parents[3]
        example_paths = [
            project_root / "examples" / "piano_c_octaves.mid",
            project_root / "examples" / "dual_track_instruments.mid",
        ]

        for path in example_paths:
            if not path.exists():
                raise FileNotFoundError(f"Missing MIDI example: {path}")

            self.play_midi_once(MidiFile(path))
            time.sleep(0.5)

    def __new__(cls) -> "Engine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
            
    def __init__(self,
                 sound_font: str = None) -> None:
        if getattr(self, "_initialized", False):
            return

        self.synth = fluidsynth.Synth(channels=16)
        if sound_font is not None:
            self.sound_font = sound_font
        else:
            self.sound_font = str(
                Path(__file__).resolve().parents[1]
                / "assets"
                / "soundfonts"
                / "FluidR3_GM.sf2"
                )

        self._started = False
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_playback = threading.Event()
        self._initialized = True

        # self._test_audio()

    def start(self) -> None:
        if self._started:
            return

        self.synth.start(driver="pulseaudio")
        sfid = self.synth.sfload(self.sound_font)
        self.synth.program_select(0, sfid, 0, 0)
        self._started = True

    def play_midi(self, song: MidiFile, loop: bool = False) -> None:
        """_summary_

        Args:
            song (MidiFile): _description_

        Returns:
            None: _description_
        """
        while True:
            self.play_midi_once(song=song, stop_event=self._stop_playback)
            if self._stop_playback.is_set():
                break
            if not loop:
                break

    def pause(self) -> None:
        """_summary_
        """
        pass

    def restart(self) -> None:
        """_summary_
        """
        pass

    def play_midi_async(self, song: MidiFile, loop: bool = False) -> None:
        """Play a MIDI file in a background thread so the UI stays responsive."""
        if not isinstance(song, MidiFile):
            raise TypeError("song must be a MidiFile")

        previous_thread = self._playback_thread
        self.stop()
        if previous_thread is not None and previous_thread.is_alive():
            previous_thread.join(timeout=0.1)

        self._stop_playback = threading.Event()
        self._playback_thread = threading.Thread(
            target=self.play_midi,
            kwargs={"song": song, "loop": loop},
            daemon=True,
        )
        self._playback_thread.start()

    def play_midi_once(self,
                       song: MidiFile,
                       stop_event: Optional[threading.Event] = None) -> None:
        """Sends a given Midifile to the soundcard to be played
        """
        if not isinstance(song, MidiFile):
            raise TypeError("song must be a MidiFile")

        stop_event = threading.Event() if stop_event is None else stop_event

        for message in song:
            if stop_event.wait(message.time):
                break

            if message.is_meta:
                continue

            if message.type == "note_on":
                if message.velocity == 0:
                    self.send_note_off(message.channel, message.note)
                else:
                    self.send_note_on(
                        message.channel,
                        message.note,
                        message.velocity,
                    )
                continue

            if message.type == "note_off":
                self.send_note_off(message.channel, message.note)
                continue

            if message.type == "program_change":
                self.send_program_change(message.channel, message.program)
                continue

            if message.type == "control_change":
                self.synth.cc(
                    chan=message.channel,
                    ctrl=message.control,
                    val=message.value,
                )
                continue

            # ----- Unimplemented in Pytone -----
            # if message.type == "pitchwheel":
            #     self.synth.pitch_bend(
            #         chan=message.channel,
            #         val=message.pitch,
            #     )
            #     continue

            # if message.type == "aftertouch":
            #     self.synth.channel_pressure(
            #         chan=message.channel,
            #         val=message.value,
            #     )
            #     continue

            # if message.type == "polytouch":
            #     self.synth.key_pressure(
            #         chan=message.channel,
            #         key=message.note,
            #         val=message.value,
            #     )

        self._all_notes_off()

    def play_wav(self, path: str) -> None:
        """Sends a .wav file to the audiocard to be played

        Args:
            path (str): path to the given .wav file.
        """
        pass

    def send_note_on(self, channel, pitch, velocity) -> None:
        """_summary_

        Args:
            channel (_type_): _description_
            pitch (_type_): _description_
            velocity (_type_): _description_
        """
        self.synth.noteon(chan=channel, key=pitch, vel=velocity)

    def send_note_off(self, channel, pitch) -> None:
        """_summary_

        Args:
            channel (_type_): _description_
            pitch (_type_): _description_
        """
        self.synth.noteoff(chan=channel, key=pitch)

    def send_program_change(self, channel, program) -> None:
        """_summary_

        Args:
            channel (_type_): _description_
            program (_type_): _description_
        """
        self.synth.program_change(chan=channel, prg=program)

    def stop(self) -> None:
        """Stop any active playback and silence all notes."""
        self._stop_playback.set()
        self._all_notes_off()

    def _all_notes_off(self) -> None:
        if not hasattr(self.synth, "cc"):
            return

        for channel in range(16):
            self.synth.cc(chan=channel, ctrl=123, val=0)
