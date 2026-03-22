import importlib.util
import sys
from pathlib import Path


MODELS_DIR = Path(__file__).resolve().parents[1] / "src" / "Pytone" / "models"


def load_model_module(module_name: str):
    """Load a module directly from src/Pytone/models by filename."""
    module_path = MODELS_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
