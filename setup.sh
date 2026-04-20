#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
VENV_DIR="$SCRIPT_DIR/venv"
SOUNDFONT_DIR="$SCRIPT_DIR/src/Pytone/assets/soundfonts"
SOUNDFONT_PATH="$SOUNDFONT_DIR/FluidR3_GM.sf2"
SOUNDFONT_URL="https://github.com/pianobooster/fluid-soundfont/releases/download/v3.1/FluidR3_GM.sf2"

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

find_downloader() {
    if command -v curl >/dev/null 2>&1; then
        echo "curl"
        return 0
    fi

    if command -v wget >/dev/null 2>&1; then
        echo "wget"
        return 0
    fi

    return 1
}

install_soundfont() {
    local existing_path
    local downloader
    local temp_path

    mkdir -p "$SOUNDFONT_DIR"

    if [ -s "$SOUNDFONT_PATH" ]; then
        echo "SoundFont already present at '$SOUNDFONT_PATH'."
        return 0
    fi

    for existing_path in \
        "/usr/share/sounds/sf2/FluidR3_GM.sf2" \
        "/usr/share/soundfonts/FluidR3_GM.sf2"
    do
        if [ -r "$existing_path" ]; then
            echo "Copying FluidR3_GM.sf2 from '$existing_path'."
            cp "$existing_path" "$SOUNDFONT_PATH"
            return 0
        fi
    done

    if ! downloader=$(find_downloader); then
        echo "Neither curl nor wget was found, so FluidR3_GM.sf2 could not be downloaded."
        return 1
    fi

    temp_path="$SOUNDFONT_PATH.part"
    rm -f "$temp_path"

    echo "Downloading FluidR3_GM.sf2 into '$SOUNDFONT_PATH'."
    if [ "$downloader" = "curl" ]; then
        curl -L --fail --output "$temp_path" "$SOUNDFONT_URL"
    else
        wget -O "$temp_path" "$SOUNDFONT_URL"
    fi

    mv "$temp_path" "$SOUNDFONT_PATH"
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
install_soundfont

cat <<EOF

Virtual environment is ready and the default SoundFont is in place.

Python packages installed:
- requirements.txt
- pyfluidsynth

If you plan to use FluidSynth in Pytone, you still need to install:
- the native FluidSynth system library

SoundFont installed:
- $SOUNDFONT_PATH

To activate it later, run:
source venv/bin/activate
EOF
