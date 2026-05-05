from pathlib import Path
import os
from typing import Callable
import tkinter as tk
from tkinter import filedialog
import pygame
import pygame.freetype
from ui.widget import Widget
from ui.constants import PIXEL_SCALE, BUMPER_COLOR, TEXT_COLOR
from ui.piano_roll import MAX_SONG_DURATION
from ui.spin_box import SpinBox
from ui.button import Button
from ui.text_button import TextButton
from ui.slider import Slider
from ui.dropdown import DropDown
from models.song import Song
from models.audioEngine import Engine
from mido import bpm2tempo


class SongRibbon(Widget):
    """A class for managing the playback of the song visually
    and interactively allows the user to play, pause, stop,
    or restart the song.

    Properties:
     - size: how tall the song ribbon should be
     - font: the freetype font object for drawing text to the screen.
     - play_button: a ui.text_button object that allows the user to toggle play back
     - stop_button: a ui.button object that allows the user to stop play back
     - song_length: an int that determines how long the song can go.
     - progress_bar: a pygame.Rect that is used for drawing how far into the
        song the play head is.
     - playing: a bool that tracks if the song is playing or not
     - tempo: a ui.spinbox object that sets the bpm of the song
     - elapsed_time: an int that tracks the number of milliseconds that have
        passed since the song started.
    """
    def __init__(self,
                 screen: pygame.Surface,
                 font: pygame.freetype.Font,
                 size: int) -> None:
        super().__init__(screen)
        self.font: pygame.freetype.Font = font
        self.size: int = size
        self.play_button: TextButton = TextButton(screen,
                                                  font, pygame.Rect(32*PIXEL_SCALE,
                                                                    2*PIXEL_SCALE,
                                                                    8*PIXEL_SCALE,
                                                                    8*PIXEL_SCALE),
                                                  ">",
                                                  self.toggle_playback)
        self.stop_button: Button = Button(screen,
                                          pygame.Rect(42*PIXEL_SCALE,
                                                      2*PIXEL_SCALE,
                                                      8*PIXEL_SCALE,
                                                      8*PIXEL_SCALE),
                                          self.stop)
        self.save_button: TextButton = TextButton(screen,
                                                  font,
                                                  pygame.Rect(52*PIXEL_SCALE,
                                                              2*PIXEL_SCALE,
                                                              16*PIXEL_SCALE,
                                                              8*PIXEL_SCALE),
                                                  'Sv',
                                                  Song().save_song)
        self.load_button: TextButton = TextButton(screen,
                                                  font,
                                                  pygame.Rect(70*PIXEL_SCALE,
                                                              2*PIXEL_SCALE,
                                                              16*PIXEL_SCALE,
                                                              8*PIXEL_SCALE),
                                                  'Ld',
                                                  Song().load_song)
        self.song_length: int = MAX_SONG_DURATION
        self.progress_bar: Slider = Slider(screen,
                                           (32*PIXEL_SCALE,
                                            12*PIXEL_SCALE),
                                           128*PIXEL_SCALE,
                                           lambda: self.current_beat / self.song_length,
                                           self.set_beat_from_percentage)
        self.playing: bool = False
        self.tempo: SpinBox = SpinBox(screen,
                                      font,
                                      (552, 8),
                                      Song().bpm,
                                      5,
                                      999,
                                      on_change=lambda old: self.reset_beat(old))
        self.track: DropDown = DropDown(screen,
                                        font,
                                        (37*PIXEL_SCALE,
                                         16*PIXEL_SCALE),
                                        [("1", 0),
                                         ("2", 1),
                                         ("3", 2),
                                         ("4", 3)],
                                        on_change=self.update_track)
        self.instrument: DropDown = DropDown(screen,
                                             font,
                                             (53*PIXEL_SCALE,
                                              16*PIXEL_SCALE),
                                             [
                                                ("Acoustic Grand Piano", 1),
                                                ("Electric Piano", 5),
                                                ("Celesta", 9),
                                                ("Drawbar Organ", 17),
                                                ("Acoustic Guitar (nylon)", 25),
                                                ("Acoustic Guitar (steel)", 26),
                                                ("Electric Guitar (jazz)", 27),
                                                ("Electric Guitar (muted)", 29),
                                                ("Distortion Guitar", 31),
                                                ("Acoustic Bass", 33),
                                                ("Electric Bass", 34),
                                                ("Violin", 41),
                                                ("Cello", 43),
                                                ("String Ensemble", 49),
                                                ("Trumpet", 57),
                                                ("French Horn", 61),
                                                ("Soprano Sax", 65),
                                                ("Flute", 73),
                                                ("Square Wave", 81),
                                                ("Taiko Drum", 117)],
                                             on_change=self.update_instrument)
        self.elapsed_time: int = 0
        self.on_track_change: Callable[[int], None] = lambda: None

    def draw(self, dt: int):
        if self.playing:
            self.elapsed_time += dt
        pygame.draw.rect(self.screen, BUMPER_COLOR, (0,
                                                     0,
                                                     self.screen.get_size()[0],
                                                     self.size))

        # draw play button
        self.play_button.text = "||" if self.playing else ">"
        self.play_button.draw()

        # draw stop button
        self.stop_button.draw()
        spacing: int = 2*PIXEL_SCALE
        pygame.draw.rect(self.screen,
                         TEXT_COLOR,
                         pygame.Rect(self.stop_button.rect.x + spacing,
                                     self.stop_button.rect.y + spacing,
                                     self.stop_button.rect.width - spacing*2,
                                     self.stop_button.rect.height - spacing*2))

        # draw save button
        self.save_button.draw()

        # draw load button
        self.load_button.draw()

        # draw progress bar
        self.progress_bar.draw()
        self.tempo.draw()
        self.instrument.draw()
        self.track.draw()

        # add overflow track to track dropdown if not none
        if Song()._overflow_track is not None:
            self.track.options.append(("5", 4))

    @staticmethod
    def beat_from_time(time: int, tempo: int) -> int:
        """Convert the time elapsesed since start to the number of beats which
            would have occurred"""
        return int(time / (bpm2tempo(tempo) / 1000 / 4))

    @property
    def current_beat(self) -> int:
        """Get the current beat based the time that has passed and the BPM"""
        return SongRibbon.beat_from_time(self.elapsed_time, self.tempo.value)

    @current_beat.setter
    def current_beat(self, value: int) -> None:
        """Set the elapsed time based on the new number of beats to have passed"""
        self.elapsed_time = value * (bpm2tempo(self.tempo.value) / 1000 / 4)

    def set_beat_from_percentage(self, percent: float) -> None:
        """Set the current beat based on percentage of the song that has played"""
        self.pause()
        self.current_beat = int(percent * self.song_length)

    def reset_beat(self, tempo: int):
        """Adjust time_elapsed to keep current_beat consistent when tempo changes"""
        self.current_beat = SongRibbon.beat_from_time(self.elapsed_time, tempo)

    def update_instrument(self, new_instrument: int):
        Song().track_list[self.track.get_value()].instrument = new_instrument
        Engine().send_program_change(self.track.get_value(), new_instrument)

    def update_track(self, new_track: int):
        self.instrument.set_value(Song().track_list[new_track].instrument)
        Engine().send_program_change(self.track.get_value(),
                                     Song().track_list[new_track].instrument)
        self.on_track_change(new_track)

    def save_song(self):
        """Open a tkinter filedialog to choose where to save the song"""
        root = tk.Tk()
        root.withdraw()
        root.update()

        try:
            root = tk.Tk()
            root.withdraw()
            root.update()
            file_name = filedialog.asksaveasfilename(
                title="Save As",
                defaultextension=".mid",
                filetypes=[
                    ("MIDI files", "*.mid *.midi")
                ],
                initialfile="song.mid",
                initialdir=str(Path.home()),
                confirmoverwrite=True
                )
        except tk.TclError as exc:
            raise RuntimeError(
                "Could not open the save dialog. "
                "Check that a desktop display is available."
            ) from exc
        finally:
            if root is not None:
                root.destroy()

        if not file_name:
            return None

        destination = os.path.abspath(Song()._normalize_midifile_path(file_name))
        midifile = Song().create_midifile()
        midifile.save(destination)
        return destination

    def load_song(self):
        pass

    def toggle_playback(self):
        """Pause or play the song"""
        if self.playing:
            self.pause()
        else:
            self.resume()

    def pause(self):
        """Stop the song from playing but do not forget the position"""
        self.playing = False
        Engine().stop()

    def resume(self):
        """Play the song from the last position"""
        self.playing = True
        Song().bpm = self.tempo.value

        if self.current_beat == 0:
            Engine().play_midi_async(Song().create_midifile())
        else:
            Engine().play_midi_async(
                Song().create_midifile_from(self.current_beat)
            )

    def stop(self):
        """Stop playing the song and forget how far we were before"""
        self.pause()
        self.current_beat = 0

    def restart(self):
        """Play the song from the start"""
        self.elapsed_time = 0
        self.playing = True
        Song().bpm = self.tempo.value
        Engine().play_midi_async(Song().create_midifile())

    def process(self, event):
        if not self.playing:
            self.tempo.process(event)
        self.play_button.process(event)
        self.stop_button.process(event)
        self.progress_bar.process(event)
        self.instrument.process(event)
        self.track.process(event)
        self.save_button.process(event)
        self.load_button.process(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self.restart()
                else:
                    self.toggle_playback()
