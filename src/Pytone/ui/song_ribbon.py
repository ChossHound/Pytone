import pygame
import pygame.freetype 
import math
from typing import List
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE
from ui.cursor import Cursor
from ui.piano_roll import BEAT_WIDTH, MAX_SONG_DURATION
from models.song import Song
from models.audioEngine import Engine

BUMPER_COLOR: tuple[int, int, int] = (68, 68, 68)
DARK_ACCENT: tuple[int, int, int] = (34, 34, 34)
BUTTON_COLOR: tuple[int, int, int] = (102, 119, 170)
TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)

class SpinBox:
    def __init__(self, screen, position: tuple[int, int], value, _min, _max, get_next = lambda x: x + 1, get_previous = lambda x: x - 1):
        self.screen: pygame.Surface = screen
        self.FONT = pygame.freetype.Font("src/Pytone/assets/Tiny5.ttf", 1, resolution=PIXEL_SCALE*5*128)
        self.position = position
        self.value = value
        self.min = _min
        self.max = _max
        self.get_next = get_next
        self.width = 16 * (int(math.log10(_max)) + 1) + 16
        self.get_previous = get_previous

        x, y = self.position
        self.plus_rect = pygame.Rect(x + self.width + 4, y, 20, 16)
        self.minus_rect = pygame.Rect(x + self.width + 4, y + 20, 20, 12)

    def increment(self) -> None:
        self.value = self.get_next(self.value)
        if self.value > self.max:
            self.value = self.max

    def decrement(self) -> None:
        self.value = self.get_previous(self.value)
        if self.value < self.min:
            self.value = self.min

    def draw(self):
        x, y = self.position

        # text
        pygame.draw.rect(self.screen, DARK_ACCENT, pygame.Rect(x, y, self.width, 32))
        self.FONT.render_to(self.screen, (x + 8, y + 4), str(self.value), TEXT_COLOR)

        # buttons
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.plus_rect)
        x, y, w, h = self.plus_rect
        pygame.draw.rect(self.screen, TEXT_COLOR, (x + 8, y, 4, 12))
        pygame.draw.rect(self.screen, TEXT_COLOR, (x + 4, y + 4, 12, 4))

        pygame.draw.rect(self.screen, BUTTON_COLOR, self.minus_rect)
        x, y, w, h = self.minus_rect
        pygame.draw.rect(self.screen, TEXT_COLOR, (x + 4, y + 4, 12, 4))

    def process(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if Cursor().is_overlapping(self.plus_rect):
                    self.increment()
                elif Cursor().is_overlapping (self.minus_rect):
                    self.decrement()

class SongRibbon:
    def __init__(self,
                 screen,
                 size: int,
                 song: Song | None = None,
                 engine: Engine | None = None) -> None:
        self.screen: pygame.Surface = screen
        self.size: int = size
        self.song: Song = Song() if song is None else song
        self.engine: Engine = Engine() if engine is None else engine
        self.FONT = pygame.freetype.Font("src/Pytone/assets/Tiny5.ttf", 1, resolution=PIXEL_SCALE*5*128)
        self.play_button: pygame.Rect = pygame.Rect(128, 8, 32, 32)
        self.stop_button: pygame.Rect = pygame.Rect(128 + 32 + 8, 8, 32, 32)
        self.progress_bar: pygame.Rect = pygame.Rect(128, 48, 512, 8)
        self.song_length = MAX_SONG_DURATION
        self.current_beat = 0
        self.playing: bool = False
        self.scrubbing: bool = False
        self.tempo = SpinBox(screen, (552, 8), self.song.bpm, 1, 999)
        # self.time_signature_numerator = SpinBox(screen, (476, 8), 4, 1, 64)
        # self.time_signature_denomerator = SpinBox(screen, (568, 8), 4, 1, 64, lambda x: x * 2, lambda x: x // 2)

    def draw(self):
        if self.playing and self.current_beat < self.song_length:
            self.current_beat += 1

        pygame.draw.rect(self.screen, BUMPER_COLOR, (0, 0, SCREEN_WIDTH, self.size))

        # draw play button
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.play_button)
        button_text: str = "||" if self.playing else ">"
        self.FONT.render_to(self.screen, (self.play_button.x + 8, self.play_button.y + 4), button_text, TEXT_COLOR)

        # draw stop button
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.stop_button)
        spacing: int = 8
        pygame.draw.rect(self.screen, TEXT_COLOR, pygame.Rect(self.stop_button.x + spacing, self.stop_button.y + spacing, self.stop_button.width - spacing*2, self.stop_button.height - spacing*2))

        # draw progress bar
        pygame.draw.rect(self.screen, DARK_ACCENT, self.progress_bar)
        progress: int = (self.current_beat * self.progress_bar.width) // self.song_length
        progress = (progress // PIXEL_SCALE) * PIXEL_SCALE
        pygame.draw.rect(self.screen, BUTTON_COLOR, pygame.Rect(self.progress_bar.x, self.progress_bar.y, progress, self.progress_bar.height))

        # tempo
        # self.FONT.render_to(self.screen, (324, 12), "T", TEXT_COLOR)
        self.tempo.draw()

        # time signature
        # self.FONT.render_to(self.screen, (452, 12), "S", TEXT_COLOR)
        # self.time_signature_numerator.draw()
        # self.FONT.render_to(self.screen, (554, 12), "/", TEXT_COLOR)
        # self.time_signature_denomerator.draw()

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
        self.engine.play_midi_async(self.song.create_midifile(path=None))

    def process(self, event):
        self.tempo.process(event)
        # self.time_signature_numerator.process(event)
        # self.time_signature_denomerator.process(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if Cursor().is_overlapping((0, 0, SCREEN_WIDTH, self.size)):
                    if Cursor().is_overlapping(self.play_button):
                        self.toggle_playback()
                    if Cursor().is_overlapping(self.stop_button):
                        self.stop()
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

                    
