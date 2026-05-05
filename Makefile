PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
FLAKE8 ?= flake8 --max-line-length=100
MYPY ?= mypy
DOCS = docs

SRC_DIR := src
PACKAGE_DIR := $(SRC_DIR)/Pytone
TEST_DIR := tests
PYTHONPATH := $(SRC_DIR)

export PYTHONPATH

.PHONY: all check style types test clean help venv install

all: check

run: 
	${PYTHON} src/Pytone/main.py
venv:
	python -m venv venv

install:
	pip install -r requirements.txt

check: style types test test-coverage clean
	@echo "All checks passed."

style:
	$(FLAKE8) $(PACKAGE_DIR)

types:
	mypy --ignore-missing-imports $(PACKAGE_DIR)

test:
	pytest -v $(TEST_DIR)

test-coverage:
	pytest --color=yes --cov --cov-report term-missing --cov-report=html:$(DOCS)/htmlcov tests/
clean:
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .hypothesis \) -prune -exec rm -rf {} +
	find . -name ".coverage" -delete

help:
	@echo "Available targets:"
	@echo "  make style  - Run flake8 on source and tests"
	@echo "  make types  - Run mypy on source and tests"
	@echo "  make test   - Run pytest"
	@echo "  make test-coverage   - documents test coverage"
	@echo "  make check  - Run style, type, and test checks"
	@echo "  make clean  - Remove tool caches"
