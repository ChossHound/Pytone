"""Tests for the SpinBox widget."""
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from hypothesis import given, settings, strategies as st


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
from ui.spin_box import SpinBox


pygame.init()


class TestSpinBox(unittest.TestCase):
    def setUp(self):
        Cursor._instance = None
        self.screen = pygame.Surface((200, 200))
        Cursor().init(self.screen, (255, 255, 255), 4)
        self.font = Mock()
        self.on_change = Mock()
        self.spin = SpinBox(
            self.screen,
            self.font,
            position=(0, 0),
            value=10,
            min_value=0,
            max_value=99,
            on_change=self.on_change,
        )

    def tearDown(self):
        Cursor._instance = None

    def test_increment_advances_value_and_notifies(self):
        self.spin.increment()

        self.assertEqual(self.spin.value, 11)
        self.on_change.assert_called_once_with(10)

    def test_decrement_reduces_value_and_notifies(self):
        self.spin.decrement()

        self.assertEqual(self.spin.value, 9)
        self.on_change.assert_called_once_with(10)

    def test_increment_caps_at_max_and_does_not_notify_on_no_change(self):
        self.spin.value = 99

        self.spin.increment()

        self.assertEqual(self.spin.value, 99)
        self.on_change.assert_not_called()

    def test_decrement_floors_at_min_and_does_not_notify_on_no_change(self):
        self.spin.value = 0

        self.spin.decrement()

        self.assertEqual(self.spin.value, 0)
        self.on_change.assert_not_called()

    def test_custom_get_next_and_get_previous_drive_value_changes(self):
        spin = SpinBox(
            self.screen,
            self.font,
            position=(0, 0),
            value=2,
            min_value=1,
            max_value=64,
            get_next=lambda v: v * 2,
            get_previous=lambda v: v // 2,
        )

        spin.increment()
        self.assertEqual(spin.value, 4)
        spin.increment()
        self.assertEqual(spin.value, 8)

        spin.decrement()
        self.assertEqual(spin.value, 4)

    def test_increment_clamps_when_get_next_returns_value_above_max(self):
        spin = SpinBox(
            self.screen,
            self.font,
            position=(0, 0),
            value=50,
            min_value=0,
            max_value=99,
            get_next=lambda v: v + 1000,
        )

        spin.increment()

        self.assertEqual(spin.value, 99)

    def test_decrement_clamps_when_get_previous_returns_value_below_min(self):
        spin = SpinBox(
            self.screen,
            self.font,
            position=(0, 0),
            value=50,
            min_value=10,
            max_value=99,
            get_previous=lambda v: v - 1000,
        )

        spin.decrement()

        self.assertEqual(spin.value, 10)

    def test_process_dispatches_event_to_inner_buttons(self):
        plus_process = Mock()
        minus_process = Mock()
        self.spin.plus.process = plus_process
        self.spin.minus.process = minus_process
        event = pygame.event.Event(pygame.MOUSEMOTION)

        self.spin.process(event)

        plus_process.assert_called_once_with(event)
        minus_process.assert_called_once_with(event)

    @settings(deadline=None, max_examples=25)
    @given(
        start=st.integers(min_value=0, max_value=99),
        steps=st.integers(min_value=1, max_value=20),
    )
    def test_repeated_increment_never_exceeds_max(self, start, steps):
        spin = SpinBox(self.screen, self.font, (0, 0), start, 0, 99)

        for _ in range(steps):
            spin.increment()

        self.assertLessEqual(spin.value, 99)
        self.assertGreaterEqual(spin.value, start)

    @settings(deadline=None, max_examples=25)
    @given(
        start=st.integers(min_value=0, max_value=99),
        steps=st.integers(min_value=1, max_value=20),
    )
    def test_repeated_decrement_never_goes_below_min(self, start, steps):
        spin = SpinBox(self.screen, self.font, (0, 0), start, 0, 99)

        for _ in range(steps):
            spin.decrement()

        self.assertGreaterEqual(spin.value, 0)
        self.assertLessEqual(spin.value, start)

    def test_draw_renders_value_and_delegates_to_inner_buttons(self):
        plus_draw = Mock()
        minus_draw = Mock()
        self.spin.plus.draw = plus_draw
        self.spin.minus.draw = minus_draw

        self.spin.draw()

        # Value is rendered as a string.
        self.font.render_to.assert_called_once()
        rendered_text = self.font.render_to.call_args.args[2]
        self.assertEqual(rendered_text, str(self.spin.value))
        plus_draw.assert_called_once()
        minus_draw.assert_called_once()

    def test_draw_invokes_plus_callback_while_held(self):
        self.spin.plus.is_held = Mock(return_value=True)
        self.spin.minus.is_held = Mock(return_value=False)
        self.spin.plus.draw = Mock()
        self.spin.minus.draw = Mock()
        starting_value = self.spin.value

        self.spin.draw()

        self.assertEqual(self.spin.value, starting_value + 1)
        self.on_change.assert_called_once_with(starting_value)

    def test_draw_invokes_minus_callback_while_held(self):
        self.spin.plus.is_held = Mock(return_value=False)
        self.spin.minus.is_held = Mock(return_value=True)
        self.spin.plus.draw = Mock()
        self.spin.minus.draw = Mock()
        starting_value = self.spin.value

        self.spin.draw()

        self.assertEqual(self.spin.value, starting_value - 1)
        self.on_change.assert_called_once_with(starting_value)
