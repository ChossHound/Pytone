"""Tests for the DropDown widget."""
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

from ui.cursor import Cursor
from ui.dropdown import DropDown


pygame.init()


class TestDropDown(unittest.TestCase):
    def setUp(self):
        Cursor._instance = None
        self.screen = pygame.Surface((400, 400))
        Cursor().init(self.screen, (255, 255, 255), 4)
        self.font = Mock()
        self.font.origin = False
        self.on_change = Mock()
        self.options = [("One", 1), ("Two", 2), ("Three", 3)]
        self.dropdown = DropDown(
            self.screen,
            self.font,
            position=(0, 0),
            options=self.options,
            on_change=self.on_change,
        )

    def tearDown(self):
        Cursor._instance = None

    def test_initial_index_is_zero_and_get_value_returns_first_option_id(self):
        self.assertEqual(self.dropdown.index, 0)
        self.assertEqual(self.dropdown.get_value(), 1)

    def test_set_value_updates_index_when_option_id_already_present(self):
        self.dropdown.set_value(3)

        self.assertEqual(self.dropdown.index, 2)
        self.assertEqual(self.dropdown.get_value(), 3)

    def test_set_value_appends_new_option_when_id_unknown(self):
        original_count = len(self.dropdown.options)

        self.dropdown.set_value(99)

        self.assertEqual(len(self.dropdown.options), original_count + 1)
        self.assertEqual(self.dropdown.options[-1], ("99", 99))

    def test_get_rect_grows_taller_when_dropdown_is_open(self):
        closed_height = self.dropdown.get_rect().height

        self.dropdown.open = True
        opened_height = self.dropdown.get_rect().height

        self.assertGreater(opened_height, closed_height)

    def test_click_inside_closed_dropdown_opens_and_obtains_focus(self):
        rect = self.dropdown.get_rect()

        with patch.object(pygame.mouse, "get_pos",
                          return_value=(rect.x + 4, rect.y + 4)):
            self.dropdown.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        self.assertTrue(self.dropdown.open)
        self.assertIs(Cursor().focus, self.dropdown)

    def test_click_outside_open_dropdown_closes_and_releases_focus(self):
        self.dropdown.open = True
        Cursor().obtain_focus(self.dropdown)
        opened = self.dropdown.get_rect()
        outside = (opened.right + 8, opened.bottom + 16)

        with patch.object(pygame.mouse, "get_pos", return_value=outside):
            self.dropdown.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        self.assertFalse(self.dropdown.open)
        self.assertIsNone(Cursor().focus)

    def test_click_on_different_option_selects_it_and_calls_on_change(self):
        self.dropdown.open = True
        Cursor().obtain_focus(self.dropdown)
        rect = self.dropdown.get_rect()
        # Roughly the center of the third (index 2) option region.
        click_y = rect.y + int(rect.height * 5 / 6)

        with patch.object(pygame.mouse, "get_pos",
                          return_value=(rect.x + 4, click_y)):
            self.dropdown.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        self.assertEqual(self.dropdown.index, 2)
        self.assertFalse(self.dropdown.open)
        self.on_change.assert_called_once_with(3)

    def test_click_on_currently_selected_option_does_not_call_on_change(self):
        self.dropdown.open = True
        Cursor().obtain_focus(self.dropdown)
        rect = self.dropdown.get_rect()
        click_y = rect.y + int(rect.height * 1 / 6)

        with patch.object(pygame.mouse, "get_pos",
                          return_value=(rect.x + 4, click_y)):
            self.dropdown.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        self.assertEqual(self.dropdown.index, 0)
        self.assertFalse(self.dropdown.open)
        self.on_change.assert_not_called()

    def test_right_click_does_not_change_open_state(self):
        rect = self.dropdown.get_rect()

        with patch.object(pygame.mouse, "get_pos",
                          return_value=(rect.x + 4, rect.y + 4)):
            self.dropdown.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3)
            )

        self.assertFalse(self.dropdown.open)
        self.assertIsNone(Cursor().focus)

    def test_draw_when_closed_renders_selected_option_and_arrow(self):
        # Closed dropdown should render exactly two glyphs: the selected
        # option label and the down-arrow indicator.
        self.dropdown.open = False
        self.dropdown.index = 1

        self.dropdown.draw()

        rendered = [call.args[2] for call in self.font.render_to.call_args_list]
        self.assertEqual(rendered, ["Two", "v"])
        # draw() flips font.origin to True for rendering and back to False.
        self.assertFalse(self.font.origin)

    def test_draw_when_open_renders_one_glyph_per_option(self):
        self.dropdown.open = True

        self.dropdown.draw()

        rendered = [call.args[2] for call in self.font.render_to.call_args_list]
        self.assertEqual(rendered, ["One", "Two", "Three"])
        self.assertFalse(self.font.origin)

    def test_width_grows_with_longest_option_label(self):
        narrow = DropDown(
            self.screen, self.font, (0, 0), [("a", 0), ("b", 1)]
        )
        wide = DropDown(
            self.screen,
            self.font,
            (0, 0),
            [("a", 0), ("a-very-long-option", 1)],
        )

        self.assertGreater(wide.width, narrow.width)
