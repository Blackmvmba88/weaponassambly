from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ObjectDescriptor:
    id: str
    family: str
    semantic: str
    parameters: dict[str, float | int | bool | str | None] = field(default_factory=dict)
    connectors: tuple[dict[str, Any], ...] = ()
    materials: tuple[dict[str, Any], ...] = ()
    modifiers: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> ObjectDescriptor:
        return cls(
            id=str(data.get("id", "")),
            family=str(data.get("family", "")),
            semantic=str(data.get("semantic", "generic")),
            parameters=dict(data.get("parameters", {})),
            connectors=tuple(data.get("connectors", ())),
            materials=tuple(data.get("materials", ())),
            modifiers=tuple(data.get("modifiers", ())),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True, slots=True)
class ParametricValidationResult:
    ok: bool
    errors: tuple[str, ...]


def _number(value: object) -> bool:
    # Direct exact type checking (`t is float or t is int`) is ~1.9x faster than
    # `isinstance(value, (int, float)) and not isinstance(value, bool)` in CPython hot paths
    # because it avoids tuple unpacking and class hierarchy traversal while naturally
    # excluding `bool` (since `type(True)` is `bool`, not `int` or `float`).
    t = type(value)
    return t is float or t is int


def validate_descriptor(descriptor: ObjectDescriptor) -> ParametricValidationResult:
    errors: list[str] = []

    if not descriptor.id:
        errors.append("id is required")
    if not descriptor.family:
        errors.append("family is required")

    if descriptor.family == "axial_body":
        errors.extend(_validate_axial_body(descriptor.parameters))
    elif descriptor.family == "box_body":
        errors.extend(_validate_box_body(descriptor.parameters))
    else:
        errors.append(f"unsupported family: {descriptor.family}")

    return ParametricValidationResult(ok=not errors, errors=tuple(errors))


def _validate_axial_body(parameters: dict[str, object]) -> list[str]:
    errors: list[str] = []

    height = parameters.get("height")
    radius_top = parameters.get("radius_top")
    radius_bottom = parameters.get("radius_bottom")
    wall = parameters.get("wall", 0.0)
    bevel = parameters.get("bevel", 0.0)
    segments = parameters.get("segments", 32)

    for name, value in (
        ("height", height),
        ("radius_top", radius_top),
        ("radius_bottom", radius_bottom),
        ("wall", wall),
        ("bevel", bevel),
    ):
        if not _number(value):
            errors.append(f"{name} must be a number")

    if errors:
        return errors

    assert isinstance(height, (int, float))
    assert isinstance(radius_top, (int, float))
    assert isinstance(radius_bottom, (int, float))
    assert isinstance(wall, (int, float))
    assert isinstance(bevel, (int, float))

    if height <= 0:
        errors.append("height must be > 0")
    if radius_top <= 0:
        errors.append("radius_top must be > 0")
    if radius_bottom <= 0:
        errors.append("radius_bottom must be > 0")
    if wall < 0:
        errors.append("wall must be >= 0")
    if wall >= min(radius_top, radius_bottom):
        errors.append("wall must be smaller than both radii")
    if bevel < 0:
        errors.append("bevel must be >= 0")
    if type(segments) is not int:
        errors.append("segments must be an integer")
    elif segments < 3:
        errors.append("segments must be >= 3")

    return errors


def _validate_box_body(parameters: dict[str, object]) -> list[str]:
    errors: list[str] = []

    width = parameters.get("width")
    height = parameters.get("height")
    depth = parameters.get("depth")
    wall = parameters.get("wall", 0.0)
    chamfer = parameters.get("chamfer", 0.0)

    for name, value in (
        ("width", width),
        ("height", height),
        ("depth", depth),
        ("wall", wall),
        ("chamfer", chamfer),
    ):
        if value is None:
            errors.append(f"{name} is required")
        elif not _number(value):
            errors.append(f"{name} must be a number")

    if errors:
        return errors

    assert isinstance(width, (int, float))
    assert isinstance(height, (int, float))
    assert isinstance(depth, (int, float))
    assert isinstance(wall, (int, float))
    assert isinstance(chamfer, (int, float))

    if width <= 0:
        errors.append("width must be > 0")
    if height <= 0:
        errors.append("height must be > 0")
    if depth <= 0:
        errors.append("depth must be > 0")
    if wall < 0:
        errors.append("wall must be >= 0")

    limit = min(width, height, depth) / 2.0
    if wall >= limit:
        errors.append("wall must be smaller than half of the smallest dimension")
    if chamfer < 0:
        errors.append("chamfer must be >= 0")
    if chamfer >= limit:
        errors.append("chamfer must be smaller than half of the smallest dimension")

    return errors


def axial_body_recipe(descriptor: ObjectDescriptor) -> dict[str, Any]:
    result = validate_descriptor(descriptor)
    if not result.ok:
        raise ValueError(f"invalid descriptor: {'; '.join(result.errors)}")

    p = descriptor.parameters
    height = float(p["height"])
    radius_top = float(p["radius_top"])
    radius_bottom = float(p["radius_bottom"])
    wall = float(p.get("wall", 0.0))
    bevel = float(p.get("bevel", 0.0))
    segments = int(p.get("segments", 32))
    cap_top = bool(p.get("cap_top", True))
    cap_bottom = bool(p.get("cap_bottom", True))

    return {
        "generator": "axial_body",
        "object_id": descriptor.id,
        "semantic": descriptor.semantic,
        "dimensions": {
            "height": height,
            "radius_top": radius_top,
            "radius_bottom": radius_bottom,
            "wall": wall,
        },
        "mesh": {
            "segments": segments,
            "cap_top": cap_top,
            "cap_bottom": cap_bottom,
            "bevel": bevel,
        },
        "connectors": list(descriptor.connectors),
        "materials": list(descriptor.materials),
        "modifiers": list(descriptor.modifiers),
        "metadata": dict(descriptor.metadata),
    }


def box_body_recipe(descriptor: ObjectDescriptor) -> dict[str, Any]:
    result = validate_descriptor(descriptor)
    if not result.ok:
        raise ValueError(f"invalid descriptor: {'; '.join(result.errors)}")

    p = descriptor.parameters
    width = float(p["width"])
    height = float(p["height"])
    depth = float(p["depth"])
    wall = float(p.get("wall", 0.0))
    chamfer = float(p.get("chamfer", 0.0))
    hollow = bool(p.get("hollow", False))
    cap_top = bool(p.get("cap_top", True))
    cap_bottom = bool(p.get("cap_bottom", True))

    return {
        "generator": "box_body",
        "object_id": descriptor.id,
        "semantic": descriptor.semantic,
        "dimensions": {
            "width": width,
            "height": height,
            "depth": depth,
            "wall": wall,
        },
        "mesh": {
            "chamfer": chamfer,
            "hollow": hollow,
            "cap_top": cap_top,
            "cap_bottom": cap_bottom,
        },
        "connectors": list(descriptor.connectors),
        "materials": list(descriptor.materials),
        "modifiers": list(descriptor.modifiers),
        "metadata": dict(descriptor.metadata),
    }
