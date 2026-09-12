from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCENE_SCHEMA_VERSION = 1
REQUIRED_ROOT = "BM_SIDEARM_ROOT"
REQUIRED_SOCKETS_ORDERED = (
    "SOCKET_BOTTOM",
    "SOCKET_FRONT",
    "SOCKET_GRIP",
    "SOCKET_MAG",
    "SOCKET_TOP",
)
REQUIRED_SOCKETS = frozenset(REQUIRED_SOCKETS_ORDERED)
TRANSFORM_FIELDS = ("location", "rotation_euler", "scale")


@dataclass(frozen=True, slots=True)
class SceneValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_scene_manifest(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    with file_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("scene manifest root must be a JSON object")
    return data


def validate_scene_manifest(data: dict[str, Any]) -> SceneValidationResult:
    errors: list[str] = []

    scene_schema_version = data.get("scene_schema_version")
    if scene_schema_version != SCENE_SCHEMA_VERSION:
        errors.append(f"unsupported scene_schema_version: {scene_schema_version!r}")

    platform = data.get("platform")
    if platform != "BM-S7":
        errors.append(f"unsupported platform: {platform!r}")

    root = data.get("root")
    if root != REQUIRED_ROOT:
        errors.append(f"root must be {REQUIRED_ROOT}")

    sockets = data.get("sockets")
    if not isinstance(sockets, dict):
        errors.append("sockets must be an object")
        sockets = {}

    # Iterate pre-sorted tuple directly to avoid allocating temporary missing sockets list.
    for socket in REQUIRED_SOCKETS_ORDERED:
        if socket not in sockets:
            errors.append(f"missing socket: {socket}")

    for socket_name, transform in sockets.items():
        if socket_name not in REQUIRED_SOCKETS:
            errors.append(f"unknown socket: {socket_name}")
            continue
        if not isinstance(transform, dict):
            errors.append(f"socket {socket_name} transform must be an object")
            continue
        for field in TRANSFORM_FIELDS:
            value = transform.get(field)
            if not isinstance(value, list) or len(value) != 3:
                errors.append(f"socket {socket_name}.{field} must contain 3 numbers")
                continue

            # Combine scale validation with type checking to avoid secondary component loops.
            has_non_number = False
            scale_invalid = False
            is_scale = field == "scale"

            for component in value:
                component_type = type(component)
                if component_type is int or component_type is float:
                    if is_scale and abs(component - 1.0) > 1e-6:
                        scale_invalid = True
                elif isinstance(component, bool) or not isinstance(component, (int, float)):
                    has_non_number = True
                    break
                elif is_scale:
                    try:
                        if abs(float(component) - 1.0) > 1e-6:
                            scale_invalid = True
                    except (TypeError, ValueError):
                        scale_invalid = True

            if has_non_number:
                errors.append(f"socket {socket_name}.{field} must contain only numbers")
                if is_scale:
                    for component in value:
                        try:
                            if abs(float(component) - 1.0) > 1e-6:
                                errors.append(f"socket {socket_name} scale must be 1,1,1")
                                break
                        except (TypeError, ValueError):
                            errors.append(f"socket {socket_name} scale must be 1,1,1")
                            break
            elif scale_invalid:
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
