PYTHON ?= python3

.PHONY: setup test lint check validate catalog-validate scene-validate resolve blender-bootstrap

setup:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check .

catalog-validate:
	bmwa catalog-validate

validate:
	bmwa validate configs/bm-s7.example.json

scene-validate:
	bmwa scene-validate examples/bm-s7.scene.json

resolve:
	bmwa resolve configs/bm-s7.example.json examples/bm-s7.scene.json -o /tmp/bm-s7.resolved.json

check: lint test catalog-validate validate scene-validate resolve

blender-bootstrap:
	blender --background --python scripts/bootstrap_scene.py
