# Pytone
minimal Digital audio workstation built in python following OOP principles

## Setup before running

run `bash ./setup.sh` to setup venv

in the terminal run the following command to start the venv: `source .venv/bin/activate`

## Notes on running project.
Use `docker-compose up -d` to start the container.
`docker exec -it course-container zsh` to open a terminal in the container.

Unfortunately, it does not appear to be possible to run the UI through docker as interracting with the GPU is quite difficult. If intending to use the UI, just use WSL.

Use `make run`