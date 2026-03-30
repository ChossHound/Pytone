#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
VENV_DIR="$SCRIPT_DIR/venv"

find_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
        return 0
    fi

    if command -v python >/dev/null 2>&1; then
        echo "python"
        return 0
    fi

    return 1
}

check_python_version() {
    local python_cmd=$1

    "$python_cmd" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'
}

if ! PYTHON_CMD=$(find_python); then
    echo "Python was not found in PATH. Please install Python 3.10 or newer."
    exit 1
fi

if ! check_python_version "$PYTHON_CMD"; then
    echo "Python 3.10 or newer is required. Found: $($PYTHON_CMD --version 2>&1)"
    exit 1
fi

if ! "$PYTHON_CMD" -m venv "$VENV_DIR"; then
    echo "Failed to create the virtual environment in '$VENV_DIR'."
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "requirements.txt was not found in '$SCRIPT_DIR'."
    exit 1
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

cat <<EOF

Virtual environment is ready.

Python packages installed:
- requirements.txt
- pyfluidsynth

If you plan to use FluidSynth in Pytone, you still need to install:
- the native FluidSynth system library
- a SoundFont file such as FluidR3_GM.sf2

To activate it later, run:
source venv/bin/activate
EOF
