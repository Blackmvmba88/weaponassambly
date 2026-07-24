"""Validate the canonical BM-S7 Blender scene contract.

Usage:
    blender BM_Sidearm_MASTER.blend --background --python scripts/validate_scene.py

Exit code 0 means the scene satisfies the minimum authoring contract.
This validator checks organization and transforms only; it does not inspect or
create any functional weapon mechanism.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

import bpy


ROOT_NAME = "BM_SIDEARM_ROOT"
PLATFORM_COLLECTION = "BM_S7"
REQUIRED_COLLECTIONS = (
    "00_ROOT",
    "10_CORE",
    "20_TOP",
    "30_FRONT",
    "40_BOTTOM",
    "50_MAG",
    "60_COSMETICS",
    "70_SOCKETS",
    "80_RIG",
    "90_GUIDES",
)
REQUIRED_SOCKETS = (
    "SOCKET_TOP",
    "SOCKET_BOTTOM",
    "SOCKET_FRONT",
    "SOCKET_MAG",
    "SOCKET_GRIP",
)
EPSILON = 1e-6


@dataclass(frozen=True, slots=True)
class SceneError:
    code: str
    message: str


def is_unit_scale(obj: bpy.types.Object) -> bool:
    return all(abs(component - 1.0) <= EPSILON for component in obj.scale)


def is_origin_transform(obj: bpy.types.Object) -> bool:
    return all(abs(component) <= EPSILON for component in obj.location)


def validate() -> list[SceneError]:
    errors: list[SceneError] = []

    platform = bpy.data.collections.get(PLATFORM_COLLECTION)
    if platform is None:
        errors.append(SceneError("missing_collection", f"missing {PLATFORM_COLLECTION}"))
        return errors

    child_names = {collection.name for collection in platform.children}
    for name in REQUIRED_COLLECTIONS:
        if name not in child_names:
            errors.append(SceneError("missing_collection", f"missing collection {name}"))

    root = bpy.data.objects.get(ROOT_NAME)
    if root is None:
        errors.append(SceneError("missing_root", f"missing object {ROOT_NAME}"))
    else:
        if not is_unit_scale(root):
            errors.append(SceneError("root_scale", f"{ROOT_NAME} scale must be 1,1,1"))
        if not is_origin_transform(root):
            errors.append(SceneError("root_location", f"{ROOT_NAME} must be at world origin"))

    for name in REQUIRED_SOCKETS:
        socket = bpy.data.objects.get(name)
        if socket is None:
            errors.append(SceneError("missing_socket", f"missing socket {name}"))
            continue
        if root is not None and socket.parent != root:
            errors.append(SceneError("socket_parent", f"{name} must be parented to {ROOT_NAME}"))
        if not is_unit_scale(socket):
            errors.append(SceneError("socket_scale", f"{name} scale must be 1,1,1"))

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(f"[BLACKMAMBA] scene validation failed: {len(errors)} error(s)")
        for error in errors:
            print(f"[BLACKMAMBA] {error.code}: {error.message}")
        return 1

    print("[BLACKMAMBA] scene validation OK")
    print(f"[BLACKMAMBA] root={ROOT_NAME}")
    print(f"[BLACKMAMBA] sockets={len(REQUIRED_SOCKETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
