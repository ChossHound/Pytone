import importlib
import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def load_model_module(module_name: str):
    """Load a model module using its package name."""
    return importlib.import_module(f"Pytone.models.{module_name}")
