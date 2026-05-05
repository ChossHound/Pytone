"""Tests for the Slider widget."""
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
from ui.slider import Slider


pygame.init()


class TestSlider(unittest.TestCase):
    def setUp(self):
        Cursor._instance = None
        self.screen = pygame.Surface((400, 100))
        Cursor().init(self.screen, (255, 255, 255), 4)
        self.percent_holder = {"value": 0.0}
        self.slider = Slider(
            self.screen,
            position=(20, 20),
            width=100,
            get_percent=lambda: self.percent_holder["value"],
            set_percent=lambda v: self.percent_holder.update(value=v),
        )

    def tearDown(self):
        Cursor._instance = None

    def test_get_rect_uses_position_width_and_pixel_scaled_height(self):
        rect = self.slider.get_rect()

        self.assertEqual(rect.x, 20)
        self.assertEqual(rect.y, 20)
        self.assertEqual(rect.width, 100)
        self.assertEqual(rect.height, 2 * PIXEL_SCALE)

    def test_left_click_inside_starts_scrubbing_and_sets_percent(self):
        with patch.object(pygame.mouse, "get_pos", return_value=(60, 20)):
            self.slider.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        self.assertTrue(self.slider.scrubbing)
        self.assertAlmostEqual(self.percent_holder["value"], 0.4)

    def test_left_click_outside_does_not_scrub_or_set_percent(self):
        with patch.object(pygame.mouse, "get_pos", return_value=(300, 80)):
            self.slider.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
            )

        self.assertFalse(self.slider.scrubbing)
        self.assertEqual(self.percent_holder["value"], 0.0)

    def test_right_click_inside_does_not_start_scrubbing(self):
        with patch.object(pygame.mouse, "get_pos", return_value=(60, 20)):
            self.slider.process(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3)
            )

        self.assertFalse(self.slider.scrubbing)
        self.assertEqual(self.percent_holder["value"], 0.0)

    def test_left_mouseup_stops_scrubbing(self):
        self.slider.scrubbing = True

        self.slider.process(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1))

        self.assertFalse(self.slider.scrubbing)

    def test_motion_updates_percent_only_while_scrubbing(self):
        # Without scrubbing flag set, motion should not change the percent.
        with patch.object(pygame.mouse, "get_pos", return_value=(60, 20)):
            self.slider.process(pygame.event.Event(pygame.MOUSEMOTION))
        self.assertEqual(self.percent_holder["value"], 0.0)

        self.slider.scrubbing = True
        with patch.object(pygame.mouse, "get_pos", return_value=(80, 20)):
            self.slider.process(pygame.event.Event(pygame.MOUSEMOTION))

        self.assertAlmostEqual(self.percent_holder["value"], 0.6)

    def test_percent_clamps_to_zero_when_cursor_left_of_track(self):
        with patch.object(pygame.mouse, "get_pos", return_value=(0, 20)):
            self.assertEqual(self.slider.percent_from_position(), 0.0)

    def test_percent_clamps_to_one_when_cursor_right_of_track(self):
        with patch.object(pygame.mouse, "get_pos", return_value=(500, 20)):
            self.assertEqual(self.slider.percent_from_position(), 1.0)

    @settings(deadline=None, max_examples=30)
    @given(x=st.integers(min_value=0, max_value=400))
    def test_percent_from_position_is_within_unit_interval(self, x):
        with patch.object(pygame.mouse, "get_pos", return_value=(x, 20)):
            percent = self.slider.percent_from_position()

        self.assertGreaterEqual(percent, 0.0)
        self.assertLessEqual(percent, 1.0)

    def test_draw_runs_against_real_surface(self):
        # Smoke test: drawing should not raise even with extreme percents.
        self.percent_holder["value"] = 0.5
        self.slider.draw()
