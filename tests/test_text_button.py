"""Tests for the TextButton widget."""
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


fake_fluidsynth = types.ModuleType("fluidsynth")
setattr(fake_fluidsynth, "Synth", _DummySynth)
sys.modules.setdefault("fluidsynth", fake_fluidsynth)

UI_ROOT = Path(__file__).resolve().parents[1] / "src" / "Pytone"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from ui.button import Button
from ui.constants import TEXT_COLOR
from ui.cursor import Cursor
from ui.text_button import TextButton


pygame.init()


class TestTextButton(unittest.TestCase):
    def setUp(self):
        Cursor._instance = None
        self.screen = pygame.Surface((200, 200))
        Cursor().init(self.screen, (255, 255, 255), 4)
        self.font = Mock()
        self.callback = Mock()
        self.text_button = TextButton(
            self.screen,
            self.font,
            pygame.Rect(0, 0, 80, 80),
            "Go",
            self.callback,
        )

    def tearDown(self):
        Cursor._instance = None

    def test_text_button_is_a_button_with_text_and_font(self):
        self.assertIsInstance(self.text_button, Button)
        self.assertEqual(self.text_button.text, "Go")
        self.assertIs(self.text_button.font, self.font)

    def test_text_button_inherits_click_behavior(self):
        with patch.object(pygame.mouse, "get_pos", return_value=(20, 20)):
            self.text_button.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        self.callback.assert_called_once()

    def test_draw_renders_button_text_via_font(self):
        self.text_button.draw()

        self.font.render_to.assert_called_once()
        args, _ = self.font.render_to.call_args
        screen_arg, _, text_arg, color_arg = args

        self.assertIs(screen_arg, self.screen)
        self.assertEqual(text_arg, "Go")
        self.assertEqual(color_arg, TEXT_COLOR)

    def test_draw_renders_updated_text(self):
        self.text_button.text = "Pause"

        self.text_button.draw()

        self.font.render_to.assert_called_once()
        _, text_arg, _ = self.font.render_to.call_args.args[1:]
        self.assertEqual(text_arg, "Pause")
