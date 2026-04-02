import pygame
from models.note import Note
from typing import List
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE
from ui.cursor import Cursor

MIN_BEAT_DURATION: int = 16
BEAT_WIDTH: int = 2 * PIXEL_SCALE
STEP_HEIGHT: int = 8 * PIXEL_SCALE
NOTE_COLOR: tuple[int, int, int] = (81, 152, 179)
GRID_COLOR: tuple[int, int, int] = (74, 101, 108)
ALT_GRID_COLOR: tuple[int, int, int] = (58, 82, 88)
GHOST_NOTE_COLOR: tuple[int, int, int] = (125, 199, 227)
NATURAL_KEY_COLOR: tuple[int, int, int] = (226, 226, 226)
ACCIDENTAL_KEY_COLOR: tuple[int, int, int] = (29, 29, 29)
KEY_COLORS: list[tuple[int, int, int]] = [
    NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR, NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR
]
KEYS_PER_OCTAVE: int = 12
NUM_OCTAVES: int = 8

class PianoRoll:
    def __init__(self, screen, dimension: pygame.Rect):
        self.screen: pygame.Surface = screen
        self.notes: list[Note] = []
        self.ghost_note: Note | None = None
        self.cropping_note: bool = False
        self.dimension = dimension

    def add_note(self, note: Note):
        self.notes.append(note)

    def apply_dimension(self, position: tuple[int, int]) -> tuple[int, int]:
        x: int = position[0]
        x -= self.dimension.x
        if x < 0:
            x = 0

        y: int = position[1]
        y -= self.dimension.y
        if y < 0:
            y = 0
        return (x, y)

    def start_ghost_note(self, position: tuple[int, int]):
        # Extract pitch and beat from the position
        x, y = self.apply_dimension(position)
        x = x // BEAT_WIDTH
        y = y // STEP_HEIGHT
        self.cropping_note = False
        self.ghost_note = Note(y, x, duration=MIN_BEAT_DURATION)

    def update_ghost_note(self, position: tuple[int, int]):
        if self.ghost_note is not None:
            # make position start at left side of the screen
            x, y = self.apply_dimension(position)
            x = x // BEAT_WIDTH
            y = y // STEP_HEIGHT
            if self.cropping_note:
                self.ghost_note.duration = x - self.ghost_note.start
            else:
                self.ghost_note.pitch = y
                self.ghost_note.start = x

    def end_ghost_note(self):
        if self.ghost_note is not None:
            self.add_note(self.ghost_note)
            self.ghost_note = None
            self.cropping_note = False

    def get_rect(self, note: Note) -> pygame.Rect:
        # Convert note properties to a pygame.Rect
        x = note.start * BEAT_WIDTH + self.dimension.x
        y = note.pitch * STEP_HEIGHT + self.dimension.y
        width = note.duration * BEAT_WIDTH
        height = STEP_HEIGHT
        r: pygame.Rect = pygame.Rect(x, y, width, height)
        return r

    def process(self, event):
        if event.type == pygame.MOUSEMOTION:
            # if we were already drawing a note: continue
            self.update_ghost_note(Cursor().get_position())
            # if we are not drawing a note and over the piano: make a sound
            if self.ghost_note is None and not Cursor().is_overlapping(self.dimension) and Cursor().is_holding():
                print(self.apply_dimension(Cursor().get_position())[1]//STEP_HEIGHT)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                #check if over piano or screen
                if Cursor().is_overlapping(self.dimension):
                    #check if any notes are hovered
                    for n in self.notes:
                        note_rect: pygame.Rect = self.get_rect(n)
                        if Cursor().is_overlapping(note_rect):
                            distance_to_left: int = abs(note_rect.x - Cursor().get_position()[0])
                            distance_to_right: int = abs(note_rect.x + note_rect.width - Cursor().get_position()[0] + Cursor().size)
                            
                            # if more on the left side
                            if distance_to_left < distance_to_right:
                                #begin moving note
                                self.cropping_note = False                       
                            else:
                                self.cropping_note = True
                            self.ghost_note = n
                            self.notes.remove(n)
                    
                    #if no notes are hovered: make a new note
                    if self.ghost_note is None:
                        self.start_ghost_note(Cursor().get_position())
                else:
                    print(self.apply_dimension(Cursor().get_position())[1]//STEP_HEIGHT)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                self.end_ghost_note()

        if event.type == pygame.MOUSEWHEEL:
            self.dimension.y += event.y

    def draw(self):
        # draw scale
        for i in range(0, STEP_HEIGHT * KEYS_PER_OCTAVE * NUM_OCTAVES, STEP_HEIGHT*2):
            pygame.draw.rect(self.screen, GRID_COLOR, (self.dimension.x,
                                                       self.dimension.y + i,
                                                       self.dimension.width,
                                                       STEP_HEIGHT))
        for i in range(STEP_HEIGHT, STEP_HEIGHT * KEYS_PER_OCTAVE * NUM_OCTAVES, STEP_HEIGHT*2):
            pygame.draw.rect(self.screen, ALT_GRID_COLOR,
                             (self.dimension.x,
                              self.dimension.y + i,
                              self.dimension.width,
                              STEP_HEIGHT))

        # draw notes
        for note in self.notes:
            pygame.draw.rect(self.screen, NOTE_COLOR, self.get_rect(note))
        if self.ghost_note is not None:
            pygame.draw.rect(self.screen, GHOST_NOTE_COLOR,
                             self.get_rect(self.ghost_note))

        # draw piano
        for i in range(0, self.dimension.height//STEP_HEIGHT, 1):
            color_index: int = i % KEYS_PER_OCTAVE
            pygame.draw.rect(self.screen, KEY_COLORS[color_index], (0, i*STEP_HEIGHT + self.dimension.y, self.dimension.x, STEP_HEIGHT))