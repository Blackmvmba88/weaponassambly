"""Bootstrap the canonical BM-S7 Blender scene structure.

Run from Blender's Scripting workspace or with:
    blender --background --python scripts/bootstrap_scene.py

This script creates scene organization, root objects, and canonical sockets only.
It intentionally does not create weapon geometry or functional mechanisms.
"""

from __future__ import annotations

import bpy

ROOT_NAME = "BM_SIDEARM_ROOT"
PLATFORM_COLLECTION = "BM_S7"

COLLECTIONS = (
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

SOCKETS = (
    "SOCKET_TOP",
    "SOCKET_BOTTOM",
    "SOCKET_FRONT",
    "SOCKET_MAG",
    "SOCKET_GRIP",
)


def get_or_create_collection(name: str, parent: bpy.types.Collection) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)

    if collection.name not in {child.name for child in parent.children}:
        parent.children.link(collection)

    return collection


def ensure_empty(name: str, collection: bpy.types.Collection, parent=None) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if obj is None:
        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = "PLAIN_AXES"
        obj.empty_display_size = 0.05

    for linked_collection in list(obj.users_collection):
        linked_collection.objects.unlink(obj)

    collection.objects.link(obj)
    obj.parent = parent
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    return obj


def bootstrap() -> None:
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    root_collection = scene.collection
    platform = get_or_create_collection(PLATFORM_COLLECTION, root_collection)

    subcollections = {
        name: get_or_create_collection(name, platform)
        for name in COLLECTIONS
    }

    root = ensure_empty(ROOT_NAME, subcollections["00_ROOT"])
    root.empty_display_type = "CUBE"
    root.empty_display_size = 0.08

    for socket_name in SOCKETS:
        ensure_empty(socket_name, subcollections["70_SOCKETS"], parent=root)

    bpy.context.view_layer.objects.active = root
    root.select_set(True)

    print("[BLACKMAMBA] BM-S7 scene bootstrap complete")
    print(f"[BLACKMAMBA] root={ROOT_NAME}")
    print(f"[BLACKMAMBA] sockets={', '.join(SOCKETS)}")


if __name__ == "__main__":
    bootstrap()
