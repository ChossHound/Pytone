import pygame
from note import Note
from typing import List
from pygame import Rect
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE
from cursor import Cursor

MIN_BEAT_DURATION: int = 16
BEAT_WIDTH: int = 2 * PIXEL_SCALE
STEP_HEIGHT: int = 8 * PIXEL_SCALE
NOTE_COLOR: tuple[int, int, int] = (81, 152, 179)
GRID_COLOR: tuple[int, int, int] = (74, 101, 108)
ALT_GRID_COLOR: tuple[int, int, int] = (58, 82, 88)
GHOST_NOTE_COLOR: tuple[int, int, int] = (125, 199, 227)

class PianoRoll:
    def __init__(self, screen, dimension: pygame.Rect):
        self.screen: pygame.Surface = screen
        self.notes: list[Note] = []
        self.ghost_note: Note | None = None
        self.dimension = dimension

    def add_note(self, note: Note):
        self.notes.append(note)

    def start_ghost_note(self, position: tuple[int, int]):
        # Extract pitch and beat from the position
        pitch = position[1] // STEP_HEIGHT
        beat = position[0] // BEAT_WIDTH
        self.ghost_note = Note(pitch, beat, duration=MIN_BEAT_DURATION)

    def update_ghost_note(self, position: tuple[int, int]):
        if self.ghost_note is not None:
            pitch = position[1] // STEP_HEIGHT
            beat = position[0] // BEAT_WIDTH
            self.ghost_note.pitch = pitch
            self.ghost_note.beat = beat

    def end_ghost_note(self):
        if self.ghost_note is not None:
            self.add_note(self.ghost_note)
            self.ghost_note = None

    def get_rect(self, note: Note) -> Rect:
        # Convert note properties to a pygame.Rect
        x = note.beat * BEAT_WIDTH
        y = note.pitch * STEP_HEIGHT
        width = note.duration * BEAT_WIDTH
        height = STEP_HEIGHT
        return Rect(x, y, width, height)

    def process(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.start_ghost_note(Cursor().get_position())
        if event.type == pygame.MOUSEMOTION:
            self.update_ghost_note(Cursor().get_position())
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                self.end_ghost_note()


    def draw(self):
        #draw scale
        for i in range(0, self.dimension.height, STEP_HEIGHT*2):
            pygame.draw.rect(self.screen, GRID_COLOR, (self.dimension.x, self.dimension.y + i, self.dimension.width, STEP_HEIGHT))
        for i in range(STEP_HEIGHT, self.dimension.height, STEP_HEIGHT*2):
            pygame.draw.rect(self.screen, ALT_GRID_COLOR, (self.dimension.x, self.dimension.y + i, self.dimension.width, STEP_HEIGHT))

        #draw notes
        for note in self.notes:
            pygame.draw.rect(self.screen, NOTE_COLOR, self.get_rect(note))
        if self.ghost_note is not None:
            pygame.draw.rect(self.screen, GHOST_NOTE_COLOR, self.get_rect(self.ghost_note))

        #draw piano
