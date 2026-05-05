"""Tests for the Cursor singleton."""
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from hypothesis import given, settings, strategies as st


class _DummySynth:
    def __init__(self, *args, **kwargs):
        pass


sys.modules.setdefault("fluidsynth", types.SimpleNamespace(Synth=_DummySynth))

UI_ROOT = Path(__file__).resolve().parents[1] / "src" / "Pytone"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from ui.constants import PIXEL_SCALE
from ui.cursor import Cursor


pygame.init()


class TestCursor(unittest.TestCase):
    def setUp(self):
        Cursor._instance = None
        self.screen = pygame.Surface((100, 100))
        Cursor().init(self.screen, (10, 20, 30), 4)

    def tearDown(self):
        Cursor._instance = None

    def test_cursor_is_a_singleton(self):
        self.assertIs(Cursor(), Cursor())

    def test_init_sets_color_size_and_initial_state(self):
        cursor = Cursor()

        self.assertEqual(cursor.color, (10, 20, 30))
        self.assertEqual(cursor.size, 4)
        self.assertFalse(cursor.is_holding_left())
        self.assertFalse(cursor.is_holding_right())
        self.assertIsNone(cursor.focus)

    def test_left_mousedown_sets_holding_left_only(self):
        Cursor().process(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1))

        self.assertTrue(Cursor().is_holding_left())
        self.assertFalse(Cursor().is_holding_right())

    def test_right_mousedown_sets_holding_right_only(self):
        Cursor().process(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3))

        self.assertTrue(Cursor().is_holding_right())
        self.assertFalse(Cursor().is_holding_left())

    def test_mouseup_clears_only_corresponding_button(self):
        Cursor().holding_left = True
        Cursor().holding_right = True

        Cursor().process(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1))

        self.assertFalse(Cursor().is_holding_left())
        self.assertTrue(Cursor().is_holding_right())

        Cursor().process(pygame.event.Event(pygame.MOUSEBUTTONUP, button=3))

        self.assertFalse(Cursor().is_holding_right())

    def test_middle_button_events_are_ignored(self):
        Cursor().process(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=2))

        self.assertFalse(Cursor().is_holding_left())
        self.assertFalse(Cursor().is_holding_right())

    @settings(deadline=None, max_examples=25)
    @given(
        x=st.integers(min_value=0, max_value=999),
        y=st.integers(min_value=0, max_value=999),
    )
    def test_get_position_snaps_to_pixel_scale_multiples(self, x, y):
        with patch.object(pygame.mouse, "get_pos", return_value=(x, y)):
            px, py = Cursor().get_position()

        self.assertEqual(px % PIXEL_SCALE, 0)
        self.assertEqual(py % PIXEL_SCALE, 0)
        self.assertEqual(px, (x // PIXEL_SCALE) * PIXEL_SCALE)
        self.assertEqual(py, (y // PIXEL_SCALE) * PIXEL_SCALE)

    def test_get_rect_uses_position_and_size(self):
        with patch.object(pygame.mouse, "get_pos", return_value=(20, 32)):
            rect = Cursor().get_rect()

        self.assertEqual(rect.x, 20)
        self.assertEqual(rect.y, 32)
        self.assertEqual(rect.width, 4)
        self.assertEqual(rect.height, 4)

    def test_is_overlapping_returns_true_when_cursor_intersects_rect(self):
        target = pygame.Rect(0, 0, 50, 50)

        with patch.object(pygame.mouse, "get_pos", return_value=(20, 20)):
            self.assertTrue(Cursor().is_overlapping(target))

    def test_is_overlapping_returns_false_when_cursor_outside_rect(self):
        target = pygame.Rect(0, 0, 50, 50)

        with patch.object(pygame.mouse, "get_pos", return_value=(80, 80)):
            self.assertFalse(Cursor().is_overlapping(target))

    def test_obtain_focus_blocks_overlap_for_other_widgets(self):
        rect = pygame.Rect(0, 0, 100, 100)
        focus_holder = object()
        other = object()

        Cursor().obtain_focus(focus_holder)

        with patch.object(pygame.mouse, "get_pos", return_value=(10, 10)):
            self.assertFalse(Cursor().is_overlapping(rect, other))
            self.assertTrue(Cursor().is_overlapping(rect, focus_holder))

    def test_relinquish_focus_only_clears_when_called_by_focus_owner(self):
        focus_holder = object()
        other = object()
        Cursor().obtain_focus(focus_holder)

        Cursor().relinquish_focus(other)
        self.assertIs(Cursor().focus, focus_holder)

        Cursor().relinquish_focus(focus_holder)
        self.assertIsNone(Cursor().focus)

    def test_draw_paints_cursor_rect_with_configured_color(self):
        with patch.object(pygame.mouse, "get_pos", return_value=(20, 32)), \
                patch.object(pygame, "draw") as draw_mock:
            Cursor().draw()

        draw_mock.rect.assert_called_once()
        args, _ = draw_mock.rect.call_args
        screen_arg, color_arg, rect_arg = args

        self.assertIs(screen_arg, self.screen)
        self.assertEqual(color_arg, (10, 20, 30))
        self.assertEqual((rect_arg.x, rect_arg.y), (20, 32))
        self.assertEqual((rect_arg.width, rect_arg.height), (4, 4))
