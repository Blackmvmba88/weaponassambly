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
TRANSFORM_FIELDS = ("location", "rotation_euler", "scale")


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

        for field in TRANSFORM_FIELDS:
            value = transform.get(field)
            if not isinstance(value, list) or len(value) != 3:
                errors.append(f"socket {socket_name}.{field} must contain 3 numbers")
                continue

            # Performance optimization: Unroll 3-element type checks to avoid inner loop iteration
            # overhead on fixed-length 3D vector lists.
            v0, v1, v2 = value[0], value[1], value[2]
            v0_type, v1_type, v2_type = type(v0), type(v1), type(v2)
            is_valid_type = (
                (v0_type is float or (v0_type is int and v0_type is not bool))
                and (v1_type is float or (v1_type is int and v1_type is not bool))
                and (v2_type is float or (v2_type is int and v2_type is not bool))
            )
            if not is_valid_type:
                errors.append(f"socket {socket_name}.{field} must contain only numbers")
                continue

            # Integrate unit scale check directly when processing 'scale' to eliminate
            # redundant transform.get("scale") dictionary lookups and re-iteration.
            if field == "scale":
                try:
                    if (
                        abs(float(v0) - 1.0) > 1e-6
                        or abs(float(v1) - 1.0) > 1e-6
                        or abs(float(v2) - 1.0) > 1e-6
                    ):
                        errors.append(f"socket {socket_name} scale must be 1,1,1")
                except (TypeError, ValueError):
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
