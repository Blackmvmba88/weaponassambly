from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCENE_SCHEMA_VERSION = 1
REQUIRED_ROOT = "BM_SIDEARM_ROOT"
REQUIRED_SOCKETS = frozenset(
    {
        "SOCKET_TOP",
        "SOCKET_BOTTOM",
        "SOCKET_FRONT",
        "SOCKET_MAG",
        "SOCKET_GRIP",
    }
)
REQUIRED_FIELDS = ("location", "rotation_euler", "scale")


@dataclass(frozen=True, slots=True)
class SceneValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_scene_manifest(path: str | Path) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("scene manifest root must be a JSON object")
    return data


def validate_scene_manifest(data: dict[str, Any]) -> SceneValidationResult:
    errors: list[str] = []

    if data.get("scene_schema_version") != SCENE_SCHEMA_VERSION:
        errors.append(f"unsupported scene_schema_version: {data.get('scene_schema_version')!r}")

    if data.get("platform") != "BM-S7":
        errors.append(f"unsupported platform: {data.get('platform')!r}")

    if data.get("root") != REQUIRED_ROOT:
        errors.append(f"root must be {REQUIRED_ROOT}")

    sockets = data.get("sockets")
    if not isinstance(sockets, dict):
        errors.append("sockets must be an object")
        sockets = {}

    # Optimized set difference: sorted list of REQUIRED_SOCKETS difference with sockets.
    # set.difference() is cleaner and faster than converting sockets to a set.
    missing = sorted(REQUIRED_SOCKETS.difference(sockets))
    for socket in missing:
        errors.append(f"missing socket: {socket}")

    for socket_name, transform in sockets.items():
        if socket_name not in REQUIRED_SOCKETS:
            errors.append(f"unknown socket: {socket_name}")
            continue
        if not isinstance(transform, dict):
            errors.append(f"socket {socket_name} transform must be an object")
            continue
        for field in REQUIRED_FIELDS:
            value = transform.get(field)
            if not isinstance(value, list) or len(value) != 3:
                errors.append(f"socket {socket_name}.{field} must contain 3 numbers")
                continue

            # Check components using loop to maintain readability while avoiding generator overhead
            has_non_number = False
            for component in value:
                if not isinstance(component, (int, float)) or isinstance(component, bool):
                    has_non_number = True
                    break
            if has_non_number:
                errors.append(f"socket {socket_name}.{field} must contain only numbers")
            elif field == "scale":
                # Scale check consolidated directly inside field loop to avoid redundant dict
                # lookup and re-iteration
                if (
                    abs(float(value[0]) - 1.0) > 1e-6
                    or abs(float(value[1]) - 1.0) > 1e-6
                    or abs(float(value[2]) - 1.0) > 1e-6
                ):
                    errors.append(f"socket {socket_name} scale must be 1,1,1")

    collections = data.get("collections")
    if not isinstance(collections, list):
        errors.append("collections must be a list of strings")
    else:
        # Avoid `all(isinstance(item, str) ...)` generator overhead, using clean loop
        for item in collections:
            if not isinstance(item, str):
                errors.append("collections must be a list of strings")
                break

    return SceneValidationResult(ok=not errors, errors=tuple(errors))
