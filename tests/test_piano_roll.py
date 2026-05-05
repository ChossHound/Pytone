import os
import sys
import types
import unittest
from unittest.mock import Mock, patch
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class _DummySynth:
    def __init__(self, *args, **kwargs):
        pass


fake_fluidsynth = types.ModuleType("fluidsynth")
setattr(fake_fluidsynth, "Synth", _DummySynth)
sys.modules.setdefault("fluidsynth", fake_fluidsynth)

import pygame
from hypothesis import assume, given, settings, strategies as st

from models.note import Note
from models.song import Song
from models.track import Track
from ui.constants import PIXEL_SCALE
from ui.cursor import Cursor
from ui.piano_roll import BEAT_WIDTH, MIN_BEAT_DURATION, PianoRoll


class TestPianoRoll(unittest.TestCase):
    def setUp(self) -> None:
        Song.reset_instance()
        self.song = Song()
        self.track = Track()
        self.song.add_track(self.track)

        self.screen = pygame.Surface((200 * PIXEL_SCALE, 200 * PIXEL_SCALE))
        Cursor().init(self.screen, (255, 255, 255), 2)

        self.engine = Mock()
        self.engine_patcher = patch("ui.piano_roll.Engine", return_value=self.engine)
        self.engine_patcher.start()

        self.get_current_beat = Mock(return_value=0)
        self.piano_roll = PianoRoll(
            self.screen,
            Mock(),
            16 * PIXEL_SCALE,
            16 * PIXEL_SCALE,
            self.get_current_beat,
            0,
        )

    def tearDown(self) -> None:
        self.engine_patcher.stop()
        Song.reset_instance()

    def _build_visible_note_case(
        self,
        pitch: int,
        start: int,
        duration: int,
    ) -> tuple[Note, pygame.Rect]:
        viewport = pygame.Rect(
            self.piano_roll.piano_size,
            self.piano_roll.ribbon_size,
            self.screen.get_width() - self.piano_roll.piano_size,
            self.screen.get_height() - self.piano_roll.ribbon_size,
        )
        note = Note(pitch=pitch, start=start, duration=duration, velocity=100)
        note_rect = self.piano_roll.get_rect(note)
        assume(viewport.colliderect(note_rect))
        return note, note_rect

    def _screen_position_for_note(self, pitch: int, start: int) -> tuple[int, int]:
        return (
            self.piano_roll.dimension.x + start * BEAT_WIDTH,
            self.piano_roll.dimension.y + self.piano_roll.position_from_pitch(pitch),
        )

    def test_start_and_end_ghost_note_uses_engine_and_adds_note(self) -> None:
        position = self._screen_position_for_note(pitch=60, start=4)

        self.piano_roll.start_ghost_note(position)

        self.assertEqual(
            self.piano_roll.ghost_note,
            Note(pitch=60, start=4, duration=MIN_BEAT_DURATION, velocity=100),
        )
        self.engine.send_note_on.assert_called_once_with(self.track.channel, 60, 100)

        self.piano_roll.end_ghost_note()

        self.assertEqual(
            self.track.note_list,
            [Note(pitch=60, start=4, duration=MIN_BEAT_DURATION, velocity=100)],
        )
        self.engine.send_note_off.assert_called_once_with(self.track.channel, 60)

    @settings(deadline=None, max_examples=25)
    @given(
        # Pitches outside this range scroll out of the default viewport.
        pitch=st.integers(min_value=51, max_value=68),
        start=st.integers(min_value=0, max_value=32),
        duration=st.integers(min_value=1, max_value=8),
        x_offset_steps=st.integers(min_value=0, max_value=6),
    )
    def test_right_click_removes_note_under_cursor(
        self,
        pitch: int,
        start: int,
        duration: int,
        x_offset_steps: int,
    ) -> None:
        note, note_rect = self._build_visible_note_case(pitch, start, duration)
        self.piano_roll.add_note(note)

        max_x_offset = max(0, note_rect.width - Cursor().size - 1)
        x_offset = min(x_offset_steps * 4, max_x_offset)
        cursor_position = (note_rect.x + x_offset, note_rect.y)

        with patch.object(pygame.mouse, "get_pos", return_value=cursor_position):
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3)
            self.piano_roll.process(event)

        self.assertEqual(self.track.note_list, [])

    @settings(deadline=None, max_examples=25)
    @given(
        pitch=st.integers(min_value=51, max_value=68),
        start=st.integers(min_value=0, max_value=32),
        duration=st.integers(min_value=1, max_value=8),
        x_offset_steps=st.integers(min_value=0, max_value=6),
    )
    def test_right_drag_delete_removes_note_under_cursor(
        self,
        pitch: int,
        start: int,
        duration: int,
        x_offset_steps: int,
    ) -> None:
        note, note_rect = self._build_visible_note_case(pitch, start, duration)
        self.piano_roll.add_note(note)

        max_x_offset = max(0, note_rect.width - Cursor().size - 1)
        x_offset = min(x_offset_steps * 4, max_x_offset)
        cursor_position = (note_rect.x + x_offset, note_rect.y)

        with patch.object(pygame.mouse, "get_pos", return_value=cursor_position):
            Cursor().holding_right = True
            try:
                event = pygame.event.Event(pygame.MOUSEMOTION)
                self.piano_roll.process(event)
            finally:
                Cursor().holding_right = False

        self.assertEqual(self.track.note_list, [])
