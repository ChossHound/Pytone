import pygame
import pygame.freetype
from ui.widget import Widget
from ui.constants import SCREEN_WIDTH, PIXEL_SCALE, BUMPER_COLOR, DARK_ACCENT, BUTTON_COLOR, TEXT_COLOR
from ui.cursor import Cursor
from ui.piano_roll import MAX_SONG_DURATION
from ui.spin_box import SpinBox
from ui.button import Button
from ui.text_button import TextButton
from models.song import Song
from models.audioEngine import Engine
from mido import bpm2tempo

class SongRibbon(Widget):
    """A class for managing the playback of the song visually and interactively.
    Allows the user to play, pause, stop, or restart the song.

    Properties:
     - size: how tall the song ribbon should be
     - play_button: a ui.text_button object that allows the user to toggle play back
     - stop_button: a ui.button object that allows the user to stop play back
     - progress_bar: a pygame.Rect that is used for drawing how far into the song the play head is.
     - song_length: an int that determines how long the song can go.
     - current_beat: an int based on where in the song the play head is.
     - ? Come back after merge

    """
    def __init__(self, screen: pygame.Surface, font: pygame.freetype.Font, size: int, song: Song | None = None, engine: Engine | None = None) -> None:
        super().__init__(screen)
        self.font: pygame.freetype.Font = font
        self.size: int = size
        self.song: Song = Song() if song is None else song
        self.engine: Engine = Engine() if engine is None else engine
        self.play_button: TextButton = TextButton(screen, font, pygame.Rect(32*PIXEL_SCALE, 2*PIXEL_SCALE, 8*PIXEL_SCALE, 8*PIXEL_SCALE), ">", self.toggle_playback)
        self.stop_button: Button = Button(screen, pygame.Rect(42*PIXEL_SCALE, 2*PIXEL_SCALE, 8*PIXEL_SCALE, 8*PIXEL_SCALE), self.stop)
        self.progress_bar: pygame.Rect = pygame.Rect(32*PIXEL_SCALE, 12*PIXEL_SCALE, 128*PIXEL_SCALE, 2*PIXEL_SCALE)
        self.song_length: int = MAX_SONG_DURATION
        self.current_beat: int = 0
        self.playing: bool = False
        self.scrubbing: bool = False
        self.tempo = SpinBox(screen, font, (552, 8), self.song.bpm, 5, 999)
        self.elapsed_time: int = 0

    def draw(self, dt: int):
        if self.playing:
            self.elapsed_time += dt
        pygame.draw.rect(self.screen, BUMPER_COLOR, (0, 0, SCREEN_WIDTH, self.size))

        # draw play button
        self.play_button.text = "||" if self.playing else ">"
        self.play_button.draw()

        # draw stop button
        self.stop_button.draw()
        spacing: int = 2*PIXEL_SCALE
        pygame.draw.rect(self.screen, TEXT_COLOR, pygame.Rect(self.stop_button.rect.x + spacing, self.stop_button.rect.y + spacing, self.stop_button.rect.width - spacing*2, self.stop_button.rect.height - spacing*2))

        # draw progress bar
        pygame.draw.rect(self.screen, DARK_ACCENT, self.progress_bar)
        progress: int = (self.get_current_beat() * self.progress_bar.width) // self.song_length
        progress = (progress // PIXEL_SCALE) * PIXEL_SCALE
        pygame.draw.rect(self.screen, BUTTON_COLOR, pygame.Rect(self.progress_bar.x, self.progress_bar.y, progress, self.progress_bar.height))

        # tempo
        self.tempo.draw()

    def get_current_beat(self) -> int:
        return int(self.elapsed_time / (bpm2tempo(self.tempo.value) / 1000 / 4))

    def toggle_playback(self):
        self.playing = not self.playing

        # TEMPORARY CHANGES !
        if self.playing:
            self.restart()
        else:
            self.stop()

    def stop(self):
        self.playing = False
        self.current_beat = 0
        self.engine.stop()

    def restart(self):
        self.song.bpm = self.tempo.value
        self.playing = True
        self.current_beat = 0
        self.elapsed_time = 0
        self.engine.play_midi_async(self.song.create_midifile(path=None))

    def process(self, event):
        self.tempo.process(event)
        self.play_button.process(event)
        self.stop_button.process(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if Cursor().is_overlapping((0, 0, SCREEN_WIDTH, self.size)):
                    if Cursor().is_overlapping(self.progress_bar):
                        x, y = Cursor().get_position()
                        progress: int = x - self.progress_bar.x
                        progress = (progress * self.song_length) // self.progress_bar.width
                        self.current_beat = min(self.song_length, max(0, progress))
                        self.scrubbing = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.scrubbing = False
        if event.type == pygame.MOUSEMOTION and self.scrubbing:
            x, y = Cursor().get_position()
            progress: int = x - self.progress_bar.x
            progress = (progress * self.song_length) // self.progress_bar.width
            self.current_beat = min(self.song_length, max(0, progress))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self.restart()
                else:
                    self.toggle_playback()
