import sys
import types
from unittest.mock import Mock

from tests.conftest import load_model_module


class _DummySynth:
    def __init__(self, *args, **kwargs):
        pass


sys.modules.setdefault("fluidsynth", types.SimpleNamespace(Synth=_DummySynth))

audio_engine_module = load_model_module("audioEngine")
Engine = audio_engine_module.Engine


def test_engine_pause_delegates_to_stop():
    engine = Engine()
    engine.stop = Mock()

    engine.pause()

    engine.stop.assert_called_once_with()
