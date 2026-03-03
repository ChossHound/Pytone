#!/usr/bin/env bash

# Exit immediately if a command fails
set -e

VENV_DIR=".venv"
REQ_FILE="requirements.txt"

echo "Setting up Python virtual environment..."

# Check that python exists
if ! command -v python3 &> /dev/null
then
    echo "python3 not found. Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment in $VENV_DIR"
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies if requirements file exists
if [ -f "$REQ_FILE" ]; then
    echo "Installing dependencies from $REQ_FILE..."
    pip install -r $REQ_FILE
else
    echo "No requirements.txt found. Skipping dependency installation."
fi

echo "Setup complete!"
echo "To activate later, run: source .venv/bin/activate"