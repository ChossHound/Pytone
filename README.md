# Pytone
minimal Digital audio workstation built in python following OOP principles

## Setup before running

run `bash ./setup.sh` to setup venv

in the terminal run the following command to start the venv: `source venv/bin/activate`

## FluidSynth setup

Pytone installs the Python package `pyfluidsynth` into the virtual environment,
downloads `FluidR3_GM.sf2` into `src/Pytone/assets/soundfonts/`, but FluidSynth
still requires a native system library on the host machine.

The virtual environment setup will install the Python binding automatically:

`pip install -r requirements.txt`

You must still install FluidSynth on the host machine:

- Ubuntu/Debian: `sudo apt install fluidsynth libfluidsynth-dev`
- macOS with Homebrew: `brew install fluid-synth`
- Windows: install a FluidSynth binary/package and make sure the library is on
  your PATH

The default audio engine path already points at:

`src/Pytone/assets/soundfonts/FluidR3_GM.sf2`

<!-- 
run the following commands:
sudo apt update
sudo apt install fluidsynth libfluidsynth-dev
sudo apt install fluid-soundont-gm

did this for WSL
 -->
in the terminal run the following command to start the venv: `source .venv/bin/activate`

## Notes on running project.
Use `docker-compose up -d` to start the container.
`docker exec -it course-container zsh` to open a terminal in the container.

Unfortunately, it does not appear to be possible to run the UI through docker as interracting with the GPU is quite difficult. If intending to use the UI, just use WSL.

Use `make run`
