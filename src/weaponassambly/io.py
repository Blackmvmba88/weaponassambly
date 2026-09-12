from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import BuildConfig


def load_json(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    with file_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("build config root must be a JSON object")
    return data


REQUIRED_KEYS = ("schema_version", "platform", "modules", "cosmetics")


def load_build(path: str | Path) -> BuildConfig:
    data = load_json(path)
    # Fast path: check for required keys directly using short-circuiting boolean operations.
    # For valid configs (the vast majority of calls), this avoids temporary list creation
    # and string formatting overhead.
    if not (
        "schema_version" in data
        and "platform" in data
        and "modules" in data
        and "cosmetics" in data
    ):
        missing = [key for key in REQUIRED_KEYS if key not in data]
        raise ValueError(f"missing required keys: {', '.join(missing)}")
    if not isinstance(data.get("modules"), dict):
        raise ValueError("modules must be a JSON object")
    if not isinstance(data.get("cosmetics"), dict):
        raise ValueError("cosmetics must be a JSON object")
    return BuildConfig.from_mapping(data)
