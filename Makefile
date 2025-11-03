# Basic Makefile for local dev tasks.
# Notes:
# - This Makefile assumes you run targets from a POSIX-like shell. On Windows PowerShell use the venv activation commands shown below
# - Many targets assume the virtualenv is activated; use `make venv` then `.\.venv\Scripts\Activate.ps1` in PowerShell.

VENV := .venv

# Choose python executable inside venv depending on platform
ifeq ($(OS),Windows_NT)
PY := $(VENV)\\Scripts\\python.exe
else
PY := $(VENV)/bin/python
endif

.PHONY: help venv install test lint format isort run clean

help:
	@echo "Makefile targets:"
	@echo "  make venv      - create a virtual environment in $(VENV)"
	@echo "  make install   - install runtime requirements from requirements.txt"
	@echo "  make test      - run pytest"
	@echo "  make lint      - run pylint on src/"
	@echo "  make format    - run black on src/ and tests/"
	@echo "  make isort     - run isort to sort imports"
	@echo "  make run       - run the scraper entrypoint (python -m src.scraper.main)"
	@echo "  make clean     - remove Python cache and pytest cache"

venv:
	@echo "Creating virtualenv at $(VENV) ..."
	python -m venv $(VENV)
	@echo "Virtualenv created. Activate it with:\n  PowerShell: .\\$(VENV)\\Scripts\\Activate.ps1\n  Bash: source $(VENV)/bin/activate"

install: venv
	@echo "Installing requirements from requirements.txt into $(VENV)"
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

test:
	@echo "Running tests with pytest"
	$(PY) -m pytest -q


lint:
	@echo "Running pylint (may be noisy)."
	-$(PY) -m pylint src

format:
	@echo "Formatting code with black"
	$(PY) -m black src tests

isort:
	@echo "Sorting imports with isort"
	$(PY) -m isort .

run:
	@echo "Running scraper entrypoint"
	$(PY) -m src.scraper.main

clean:
	@echo "Removing Python cache and pytest cache"
	-find . -type d -name "__pycache__" -exec rm -rf {} + || true
	-rm -rf .pytest_cache || true
