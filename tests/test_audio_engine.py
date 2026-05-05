import sys
import types
from unittest.mock import Mock

from tests.conftest import load_model_module


class _DummySynth:
    def __init__(self, *args, **kwargs):
        pass


fake_fluidsynth = types.ModuleType("fluidsynth")
setattr(fake_fluidsynth, "Synth", _DummySynth)
sys.modules.setdefault("fluidsynth", fake_fluidsynth)

audio_engine_module = load_model_module("audioEngine")
Engine = audio_engine_module.Engine


def test_engine_pause_delegates_to_stop():
    engine = Engine()
    engine.stop = Mock()

    engine.pause()

    engine.stop.assert_called_once_with()
