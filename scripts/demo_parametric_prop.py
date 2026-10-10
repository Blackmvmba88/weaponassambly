"""Generate a harmless modular sci-fi prop demo in Blender.

Run: blender --background --python scripts/demo_parametric_prop.py
Produces /tmp/blackmamba_parametric_demo.blend unless BM_DEMO_OUTPUT is set.
Uses Blender primitives; no functional mechanisms are modeled.
"""
from __future__ import annotations

import os
from pathlib import Path

import bpy

OUTPUT = Path(os.environ.get("BM_DEMO_OUTPUT", "/tmp/blackmamba_parametric_demo.blend"))
PALETTE = {
    "obsidian": (0.019, 0.025, 0.038, 1),
    "gold": (0.63, 0.37, 0.09, 1),
    "ruby": (0.5, 0.012, 0.04, 1),
    "glass": (0.018, 0.32, 0.38, 1),
}
SOCKETS = {
    "SOCKET_TOP": (0, 0, 0.5),
    "SOCKET_BOTTOM": (0, 0, -0.5),
    "SOCKET_FRONT": (0, -0.95, 0),
    "SOCKET_MAG": (0, 0.95, -0.12),
    "SOCKET_GRIP": (0, 0.75, -0.3),
}


def material(name, rgba, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = 0.24
    return mat


def cube(name, location, dimensions, mat, bevel=0.06):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft machined edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Corner normals", "WEIGHTED_NORMAL")
    return obj


def generate():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    dark = material("BM_OBSIDIAN", PALETTE["obsidian"], 0.65)
    gold = material("BM_GOLD", PALETTE["gold"], 0.8)
    red = material("BM_RUBY", PALETTE["ruby"], 0.25)
    glass = material("BM_GLASS", PALETTE["glass"], 0.35)
    root = bpy.data.objects.new("BM_DEMO_ROOT", None)
    bpy.context.scene.collection.objects.link(root)
    cube("CORE_monolith", (0, 0, 0), (1.4, 1.8, 0.8), dark).parent = root
    cube("CORE_gold_band", (0, 0, 0.05), (1.45, 0.22, 0.83), gold, 0.02).parent = root
    for name, position in SOCKETS.items():
        empty = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(empty)
        empty.parent = root
        empty.location = position
        empty.empty_display_type = "SPHERE"
        empty.empty_display_size = 0.13
    modules = [
        cube("TOP_crystal", (0, 0, 0.66), (0.65, 0.75, 0.30), glass),
        cube("BOTTOM_base", (0, 0, -0.63), (0.85, 0.85, 0.24), gold),
        cube("FRONT_badge", (0, -1.03, 0), (0.6, 0.16, 0.43), red),
        cube("REAR_badge", (0, 1.03, 0), (0.62, 0.16, 0.43), gold),
    ]
    # Preserve assembled transforms via parented world-space coordinates.
    for obj in modules:
        obj.parent = root
        assembled = obj.location.copy()
        exploded = assembled * 1.65
        obj.location = exploded
        obj.keyframe_insert(data_path="location", frame=1)
        obj.keyframe_insert(data_path="location", frame=12)
        obj.location = assembled
        obj.keyframe_insert(data_path="location", frame=34)
        obj.keyframe_insert(data_path="location", frame=40)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 40
    scene.frame_set(40)
    scene.render.engine = "BLENDER_EEVEE"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    print(f"[BLACKMAMBA] demo saved: {OUTPUT}; sockets={len(SOCKETS)}; modules={len(modules)}")


if __name__ == "__main__":
    generate()
