import pygame
import pygame.freetype 
from models.note import Note
from typing import List, Callable
from ui.widget import Widget
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PIXEL_SCALE
from ui.cursor import Cursor
from models.audioEngine import Engine
from models.track import Track
from models.song import Song

BPM: int = 120
MAX_SONG_DURATION: int = 16 / (BPM / 60) * 60 * 3  # beats = beatspermeasure / beatspersecond * secondsperminute * minutes
MIN_BEAT_DURATION: int = 4
BEAT_WIDTH: int = 4 * PIXEL_SCALE
STEP_HEIGHT: int = 8 * PIXEL_SCALE
KEYS_PER_OCTAVE: int = 12
NUM_OCTAVES: int = 8

# colors
NOTE_COLOR: tuple[int, int, int] = (81, 152, 179)
GRID_COLOR: tuple[int, int, int] = (74, 101, 108)
ALT_GRID_COLOR: tuple[int, int, int] = (58, 82, 88)
GHOST_NOTE_COLOR: tuple[int, int, int] = (125, 199, 227)
NATURAL_KEY_COLOR: tuple[int, int, int] = (226, 226, 226)
ACCIDENTAL_KEY_COLOR: tuple[int, int, int] = (29, 29, 29)
KEY_COLORS: list[tuple[int, int, int]] = [
    NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR, NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR, ACCIDENTAL_KEY_COLOR, NATURAL_KEY_COLOR
]
MEASURE_COLOR: tuple[int, int, int] = (24, 34, 36)
PLAY_HEAD_COLOR: tuple[int, int, int] = (255, 255, 153)


class PianoRoll(Widget):
    """Class for drawing and managing notes.
    Allows the user to draw, move, and crop notes on the piano roll using the cursor.
    Also creates and handles the piano on the right side of the screen for playing notes without drawing them.
    Notes are maintained by models.track.

    Properties:
     - track: The models.track object that keeps track notes.
     - ghost_note: A note that is used for displaying where a not is going to be added or where a note will be moved to.
                   Set to None when not in use.
     - cropping_note: a boolean for determining if the user is moving, or cropping an existing note. 
                      If this is true, the ghost_note's duration (instead of its position) will be set based on the cursor position.
     - current_pitch: an int (or None) that keeps track of the pitch of the currently playing note. This information is used to send on and off messages to the engine to preview notes.
     - self.piano_size: an int that determines how large the piano should be on the left side of the screen.
     - self.ribbon_size: an int that determines how large the song_ribbon is on the screen. Because song_ribbon is handled by ui.song_rubbon, this is used just to determine how far the piano roll can scroll without overlapping.
     - dimension: a pygame.rect that holds the position of notes. .x and .y are offset by the user panning around the piano roll.
    """
    def __init__(self, screen: pygame.Surface, font: pygame.freetype.Font, piano_size: int, ribbon_size: int, get_current_beat: Callable[[None], int], song: Song, track_index: int):
        super().__init__(screen)
        self.font: pygame.freetype.Font = font
        self.song: Song = song
        self.track_index: int = track_index
        self.get_current_beat = get_current_beat
        self.track: Track = self._resolve_track()
        self.ghost_note: Note | None = None
        self.cropping_note: bool = False
        self.current_pitch: int | None = None
        self.piano_size: int = piano_size
        self.ribbon_size: int = ribbon_size
        self.dimension: pygame.Rect = pygame.Rect(self.piano_size, -STEP_HEIGHT*12*PIXEL_SCALE, MAX_SONG_DURATION*BEAT_WIDTH, NUM_OCTAVES*STEP_HEIGHT*KEYS_PER_OCTAVE)

    def _resolve_track(self) -> Track:
        if self.song is None:
            return Track(instrument=0)

        while len(self.song.track_list) <= self.track_index:
            self.song.add_track(Track(instrument=0))

        return self.song.track_list[self.track_index]

    def add_note(self, note: Note):
        self.track.add_note(note)

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

    def pitch_from_position(self, y: int) -> int:
        y = y // STEP_HEIGHT
        y = (108 + 11 - y)
        return y

    def position_from_pitch(self, pitch: int) -> int:
        y: int = 119 - pitch
        y *= STEP_HEIGHT
        return y 

    def start_ghost_note(self, position: tuple[int, int]):
        # Extract pitch and beat from the position
        x, y = self.apply_dimension(position)
        x = x // BEAT_WIDTH
        y = self.pitch_from_position(y)
        self.cropping_note = False
        self.ghost_note = Note(y, x, duration=MIN_BEAT_DURATION)

    def update_ghost_note(self, position: tuple[int, int]):
        if self.ghost_note is not None:
            # make position start at left side of the screen
            x, y = self.apply_dimension(position)
            x = x // BEAT_WIDTH
            y = self.pitch_from_position(y)
            if self.cropping_note:
                n: note = self.get_note_at_position(self.ghost_note.start, self.ghost_note.pitch, x - self.ghost_note.start)
                if n is not None:
                    x = n.start
                self.ghost_note.duration = x - self.ghost_note.start
            else:
                n: note = self.get_note_at_position(x, y, self.ghost_note.duration)
                if n is None:
                    if self.ghost_note.pitch != y:
                        Engine().send_note_off(self.track.channel, self.ghost_note.pitch)          
                        Engine().send_note_on(self.track.channel, y, 100)
                    self.ghost_note.pitch = y
                    self.ghost_note.start = x

    def end_ghost_note(self):
        if self.ghost_note is not None:
            if self.ghost_note.duration > 0:
                self.add_note(self.ghost_note)
            self.ghost_note = None
            self.cropping_note = False

    def get_rect(self, note: Note) -> pygame.Rect:
        # Convert note properties to a pygame.Rect
        x = note.start * BEAT_WIDTH + self.dimension.x
        y = self.position_from_pitch(note.pitch) + self.dimension.y
        width = note.duration * BEAT_WIDTH
        height = STEP_HEIGHT
        r: pygame.Rect = pygame.Rect(x, y, width, height)
        return r

    def get_note_at_position(self, beat: int, pitch: int, width: int) -> Note | None:
        found_notes: List[Note] = []
        for n in self.track.note_list:
            if n.pitch == pitch and n.start < beat + width and n.start + n.duration > beat:
                found_notes.append(n)
        if len(found_notes) > 0:
            found_notes.sort(key=lambda x: x.start)
            return found_notes[0]
        return None

    def get_note_at_cursor(self) -> Note | None:
        #check if over piano or screen
        if Cursor().is_overlapping((self.piano_size, self.ribbon_size, SCREEN_WIDTH, SCREEN_HEIGHT)):
            #check if any notes are hovered
            for n in self.track.note_list:
                note_rect: pygame.Rect = self.get_rect(n)
                if Cursor().is_overlapping(note_rect):
                    return n
        return None

    def process(self, event):
        if event.type == pygame.MOUSEMOTION:
            # if we were already drawing a note: continue
            self.update_ghost_note(Cursor().get_position())
            # if we are not drawing a note and over the piano: make a sound
            if self.ghost_note is None and Cursor().is_overlapping((0, self.ribbon_size, self.piano_size, SCREEN_HEIGHT)) and Cursor().is_holding_left():
                pitch: int = self.pitch_from_position(self.apply_dimension(Cursor().get_position())[1])
                if self.current_pitch != pitch or self.current_pitch is None:
                    if self.current_pitch is not None:
                        Engine().send_note_off(self.track.channel, self.current_pitch)
                    self.current_pitch = pitch
                    Engine().send_note_on(self.track.channel, pitch, 100)
            # if we are deleting notes: delete this one too
            if Cursor().is_holding_right():
                n: Note = self.get_note_at_cursor()
                if n is not None:
                    self.track.remove_note(n.pitch, n.start)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # if hovering over piano roll
                if Cursor().is_overlapping((self.piano_size, self.ribbon_size, SCREEN_WIDTH, SCREEN_HEIGHT)):
                    n: Note = self.get_note_at_cursor()
                    if n is not None:
                        note_rect: pygame.Rect = self.get_rect(n)
                        distance_to_left: int = abs(note_rect.x - Cursor().get_position()[0])
                        distance_to_right: int = abs(note_rect.x + note_rect.width - Cursor().get_position()[0] + Cursor().size)
                        
                        # if more on the left side
                        if distance_to_left < distance_to_right:
                            #begin moving note
                            self.cropping_note = False                       
                        else:
                            self.cropping_note = True
                        self.ghost_note = n
                        self.track.remove_note(n.pitch, n.start)
                        
                    #if no notes are hovered: make a new note
                    elif self.ghost_note is None:
                        self.start_ghost_note(Cursor().get_position())
                #if hovering over piano
                elif Cursor().is_overlapping((0, self.ribbon_size, self.piano_size, SCREEN_HEIGHT)):
                    #play note on piano
                    pitch: int = self.pitch_from_position(self.apply_dimension(Cursor().get_position())[1])
                    if self.current_pitch != pitch or self.current_pitch is not None:
                        Engine().send_note_off(self.track.channel, self.current_pitch)
                    self.current_pitch = pitch
                    Engine().send_note_on(self.track.channel, pitch, 100)

            if event.button == 3: #right click
                n: Note = self.get_note_at_cursor()
                if n is not None:
                    self.track.remove_note(n.pitch, n.start)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                self.end_ghost_note()
                if self.current_pitch is not None:
                    Engine().send_note_off(self.track.channel, self.current_pitch)
                    self.current_pitch = None

        elif event.type == pygame.MOUSEWHEEL:
            self.dimension.y += event.y * PIXEL_SCALE * 4
            self.dimension.y = min(self.ribbon_size, max(self.dimension.y, SCREEN_HEIGHT - KEYS_PER_OCTAVE*NUM_OCTAVES*STEP_HEIGHT))

            self.dimension.x -= event.x * PIXEL_SCALE * 4
            self.dimension.x = min(self.piano_size, max(self.dimension.x, SCREEN_WIDTH - self.dimension.width))

    def draw(self):
        for i in range(0, KEYS_PER_OCTAVE * NUM_OCTAVES, 1):
            # draw grid
            color: tuple[int, int, int] = GRID_COLOR if i % 2 == 0 else ALT_GRID_COLOR
            pygame.draw.rect(self.screen, color,
                             (self.dimension.x,
                              self.dimension.y + i*STEP_HEIGHT,
                              self.dimension.width,
                              STEP_HEIGHT))

            # draw piano keys
            color_index: int = i % KEYS_PER_OCTAVE
            pygame.draw.rect(self.screen, KEY_COLORS[color_index], (0, i*STEP_HEIGHT + self.dimension.y, self.dimension.x, STEP_HEIGHT))
        
        # draw beat markers
        for i in range(0, 120, 16):
            start: int = i*BEAT_WIDTH + self.dimension.x
            pygame.draw.rect(self.screen, MEASURE_COLOR, (start, 0, PIXEL_SCALE, SCREEN_HEIGHT))

        # draw octave numbers
        for i in range(1, NUM_OCTAVES + 1, 1):
            self.font.render_to(self.screen, (self.dimension.x - 5*PIXEL_SCALE, i*STEP_HEIGHT*KEYS_PER_OCTAVE + self.dimension.y - 7*PIXEL_SCALE), str(NUM_OCTAVES + 1 - i), ACCIDENTAL_KEY_COLOR)

        # draw notes
        for note in self.track.note_list:
            pygame.draw.rect(self.screen, NOTE_COLOR, self.get_rect(note))
        if self.ghost_note is not None:
            pygame.draw.rect(self.screen, GHOST_NOTE_COLOR,
                             self.get_rect(self.ghost_note))

        # draw play head
        pygame.draw.rect(self.screen, PLAY_HEAD_COLOR, pygame.Rect(self.get_current_beat() * BEAT_WIDTH + self.dimension.x, 64, PIXEL_SCALE, SCREEN_HEIGHT))
