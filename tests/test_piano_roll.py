import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


UI_ROOT = Path(__file__).resolve().parents[1] / "src" / "Pytone"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from models.note import Note
from ui.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from ui.cursor import Cursor
from ui.piano_roll import PianoRoll


pygame.init()


def _make_piano_roll() -> PianoRoll:
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    Cursor().init(screen, (255, 255, 255), 2)
    return PianoRoll(
        screen,
        pygame.Rect(64, 64, SCREEN_WIDTH - 64, SCREEN_HEIGHT - 64),
    )


def test_right_click_removes_note_under_cursor(monkeypatch):
    piano_roll = _make_piano_roll()
    note = Note(pitch=10, start=2, duration=4, velocity=100)
    piano_roll.add_note(note)
    note_rect = piano_roll.get_rect(note)

    monkeypatch.setattr(
        pygame.mouse,
        "get_pos",
        lambda: (note_rect.x, note_rect.y),
    )

    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3)

    piano_roll.process(event)

    assert piano_roll.notes == []


def test_right_drag_delete_removes_note_under_cursor(monkeypatch):
    piano_roll = _make_piano_roll()
    note = Note(pitch=12, start=3, duration=2, velocity=100)
    piano_roll.add_note(note)
    note_rect = piano_roll.get_rect(note)

    monkeypatch.setattr(
        pygame.mouse,
        "get_pos",
        lambda: (note_rect.x, note_rect.y),
    )
    Cursor().holding_right = True

    event = pygame.event.Event(pygame.MOUSEMOTION)

    piano_roll.process(event)

    assert piano_roll.notes == []
