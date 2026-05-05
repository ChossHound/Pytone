"""Tests for the abstract Widget base class."""
import os
import sys
import types
import unittest
from pathlib import Path

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

from ui.widget import Widget


pygame.init()


class TestWidget(unittest.TestCase):
    def test_widget_is_abstract_and_cannot_be_instantiated_directly(self):
        with self.assertRaises(TypeError):
            Widget(pygame.Surface((10, 10)))

    def test_subclass_missing_abstract_methods_cannot_be_instantiated(self):
        class OnlyDraw(Widget):
            def draw(self):
                pass

        class OnlyProcess(Widget):
            def process(self, event):
                pass

        with self.assertRaises(TypeError):
            OnlyDraw(pygame.Surface((10, 10)))
        with self.assertRaises(TypeError):
            OnlyProcess(pygame.Surface((10, 10)))

    def test_concrete_subclass_holds_screen_reference(self):
        class Concrete(Widget):
            def process(self, event):
                pass

            def draw(self):
                pass

        screen = pygame.Surface((10, 10))
        widget = Concrete(screen)

        self.assertIs(widget.screen, screen)
