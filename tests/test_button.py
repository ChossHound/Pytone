"""Tests for the Button widget."""
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


class _DummySynth:
    def __init__(self, *args, **kwargs):
        pass


sys.modules.setdefault("fluidsynth", types.SimpleNamespace(Synth=_DummySynth))

UI_ROOT = Path(__file__).resolve().parents[1] / "src" / "Pytone"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from ui.button import Button
from ui.cursor import Cursor


pygame.init()


class TestButton(unittest.TestCase):
    def setUp(self):
        Cursor._instance = None
        self.screen = pygame.Surface((200, 200))
        Cursor().init(self.screen, (255, 255, 255), 4)
        self.callback = Mock()
        self.button = Button(self.screen, pygame.Rect(0, 0, 80, 80), self.callback)

    def tearDown(self):
        Cursor._instance = None

    def _send(self, position, event_type=pygame.MOUSEBUTTONDOWN, button=1):
        with patch.object(pygame.mouse, "get_pos", return_value=position):
            self.button.process(pygame.event.Event(event_type, button=button))

    def test_button_initializes_with_unpressed_state(self):
        self.assertFalse(self.button.pressed)
        self.assertEqual(self.button.last_called, 0)

    def test_left_click_inside_rect_calls_callback_and_marks_pressed(self):
        self._send((40, 40))

        self.callback.assert_called_once()
        self.assertTrue(self.button.pressed)
        self.assertGreater(self.button.last_called, 0)

    def test_left_click_outside_rect_does_not_call_callback(self):
        self._send((150, 150))

        self.callback.assert_not_called()
        self.assertFalse(self.button.pressed)

    def test_right_click_inside_rect_does_not_trigger_callback(self):
        self._send((40, 40), button=3)

        self.callback.assert_not_called()
        self.assertFalse(self.button.pressed)

    def test_left_mouseup_releases_pressed_state(self):
        self._send((40, 40))
        self.assertTrue(self.button.pressed)

        self._send((40, 40), event_type=pygame.MOUSEBUTTONUP)

        self.assertFalse(self.button.pressed)

    def test_pressed_resets_when_event_arrives_with_cursor_outside(self):
        self._send((40, 40))
        self.assertTrue(self.button.pressed)

        # Any event processed while cursor is outside the rect clears pressed.
        self._send((180, 180), event_type=pygame.MOUSEMOTION)

        self.assertFalse(self.button.pressed)

    def test_is_held_only_returns_true_after_hold_threshold(self):
        with patch.object(pygame.time, "get_ticks", return_value=1000), \
                patch.object(pygame.mouse, "get_pos", return_value=(40, 40)):
            self.button.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        with patch.object(pygame.time, "get_ticks", return_value=1300), \
                patch.object(pygame.mouse, "get_pos", return_value=(40, 40)):
            self.assertFalse(self.button.is_held())

        with patch.object(pygame.time, "get_ticks", return_value=2000), \
                patch.object(pygame.mouse, "get_pos", return_value=(40, 40)):
            self.assertTrue(self.button.is_held())

    def test_is_held_false_when_cursor_leaves_button(self):
        with patch.object(pygame.time, "get_ticks", return_value=1000), \
                patch.object(pygame.mouse, "get_pos", return_value=(40, 40)):
            self.button.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        with patch.object(pygame.time, "get_ticks", return_value=2000), \
                patch.object(pygame.mouse, "get_pos", return_value=(180, 180)):
            self.assertFalse(self.button.is_held())

    def test_draw_does_not_raise(self):
        # Smoke test that draw runs against a real Surface.
        self.button.draw()
