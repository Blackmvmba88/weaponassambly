"""Export the canonical BM-S7 Blender scene contract as JSON.

Usage:
    blender BM_Sidearm_MASTER.blend --background \
      --python scripts/export_scene_manifest.py -- \
      --output exports/bm-s7.scene.json

The exported file contains scene organization and socket transforms only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


PLATFORM = "BM-S7"
ROOT_NAME = "BM_SIDEARM_ROOT"
SOCKETS = (
    "SOCKET_TOP",
    "SOCKET_BOTTOM",
    "SOCKET_FRONT",
    "SOCKET_MAG",
    "SOCKET_GRIP",
)


def vec3(values) -> list[float]:
    return [round(float(component), 8) for component in values]


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    user_args = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args(user_args)


def export_manifest() -> dict[str, object]:
    root = bpy.data.objects.get(ROOT_NAME)
    if root is None:
        raise RuntimeError(f"missing required root: {ROOT_NAME}")

    sockets: dict[str, object] = {}
    for name in SOCKETS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError(f"missing required socket: {name}")
        sockets[name] = {
            "location": vec3(obj.location),
            "rotation_euler": vec3(obj.rotation_euler),
            "scale": vec3(obj.scale),
        }

    platform_collection = bpy.data.collections.get("BM_S7")
    collections = []
    if platform_collection is not None:
        collections = sorted(child.name for child in platform_collection.children)

    return {
        "scene_schema_version": 1,
        "platform": PLATFORM,
        "root": ROOT_NAME,
        "collections": collections,
        "sockets": sockets,
    }


def main() -> int:
    args = parse_args()
    payload = export_manifest()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[BLACKMAMBA] wrote scene manifest: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
