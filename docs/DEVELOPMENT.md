# Development

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
make setup
make check
```

## Runtime CLI

Validate a build:

```bash
bmwa validate configs/bm-s7.example.json
```

Inspect a platform registry:

```bash
bmwa inspect BM-S7
```

## Blender bootstrap

With Blender available on `PATH`:

```bash
make blender-bootstrap
```

This creates the canonical scene organization, root object and socket empties. Geometry remains a separate visual-authoring step.

## Architecture boundary

```text
Blender assets
    ↓
canonical sockets
    ↓
JSON build config
    ↓
Python validator / game adapter
```

The runtime never infers gameplay behavior from mesh dimensions. Asset geometry remains visual; module identity and compatibility are explicit data.

## CI contract

Every pull request to `main` must pass:

```text
ruff
pytest
bmwa validate configs/bm-s7.example.json
```

CI runs on Python 3.11 and 3.12.
