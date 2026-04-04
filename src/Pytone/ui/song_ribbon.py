import pygame
import pygame.freetype 
from typing import List
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE
from ui.cursor import Cursor
from ui.piano_roll import BEAT_WIDTH, MAX_SONG_DURATION

BUMPER_COLOR: tuple[int, int, int] = (68, 68, 68)
DARK_ACCENT: tuple[int, int, int] = (34, 34, 34)
BUTTON_COLOR: tuple[int, int, int] = (102, 119, 170)
TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)

class SongRibbon:
    def __init__(self, screen, size: int) -> None:
        self.screen: pygame.Surface = screen
        self.size: int = size
        self.FONT = pygame.freetype.Font("src/Pytone/assets/Tiny5.ttf", 1, resolution=PIXEL_SCALE*5*128)
        self.play_button: pygame.Rect = pygame.Rect(128, 8, 32, 32)
        self.stop_button: pygame.Rect = pygame.Rect(128 + 32 + 8, 8, 32, 32)
        self.progress_bar: pygame.Rect = pygame.Rect(128, 48, 512, 8)
        self.song_length = MAX_SONG_DURATION
        self.current_beat = 0
        self.playing: bool = False
        self.scrubbing: bool = False

    def draw(self):
        if self.playing:
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

    def process(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if Cursor().is_overlapping((0, 0, SCREEN_WIDTH, self.size)):
                    if Cursor().is_overlapping(self.play_button):
                        self.playing = not self.playing
                    if Cursor().is_overlapping(self.stop_button):
                        self.playing = False
                        self.current_beat = 0
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

                    