PYTHON ?= python3

.PHONY: setup test lint check validate blender-bootstrap

setup:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check .

validate:
	bmwa validate configs/bm-s7.example.json

check: lint test validate

blender-bootstrap:
	blender --background --python scripts/bootstrap_scene.py
