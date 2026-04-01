from pathlib import Path
from typing import Optional
from importlib.resources import files
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
        self.synth = fluidsynth.Synth(channels=16)

        self.sound_font = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "soundfonts"
            / "FluidR3_GM.sf2"
            )

        self.synth.start(driver="pulseaudio")
        sfid = self.synth.sfload(str(self.sound_font))
        self.synth.program_select(0, sfid, 0, 0)

        self._test_audio()

        # self._test_audio()

    def play_midi(self, song: MidiFile, loop: bool = False) -> None:
        """_summary_

        Args:
            song (MidiFile): _description_

        Returns:
            Npne: _description_
        """
        while True:
            self.play_midi_once(song=song)
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

    def play_midi_once(self, song: MidiFile) -> None:
        """Sends a given Midifile to the soundcard to be played
        """
        if not isinstance(song, MidiFile):
            raise TypeError("song must be a MidiFile")

        for message in song.play(meta_messages=True):
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

        for channel in range(16):
            self.synth.cc(chan=channel, ctrl=123, val=0)

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


test = Engine()
