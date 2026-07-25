from __future__ import annotations

import pytest

from weaponassambly.parametric import ObjectDescriptor, axial_body_recipe, validate_descriptor


def test_axial_body_descriptor_validates() -> None:
    descriptor = ObjectDescriptor.from_mapping(
        {
            "id": "OBJ_GLASS_001",
            "family": "axial_body",
            "semantic": "glass",
            "parameters": {
                "height": 0.65,
                "radius_top": 0.38,
                "radius_bottom": 0.32,
                "wall": 0.025,
                "segments": 32,
                "cap_top": False,
                "cap_bottom": True,
                "bevel": 0.01,
            },
        }
    )

    result = validate_descriptor(descriptor)

    assert result.ok is True
    assert result.errors == ()


def test_axial_body_rejects_impossible_wall() -> None:
    descriptor = ObjectDescriptor.from_mapping(
        {
            "id": "OBJ_BAD",
            "family": "axial_body",
            "semantic": "generic",
            "parameters": {
                "height": 1.0,
                "radius_top": 0.2,
                "radius_bottom": 0.2,
                "wall": 0.2,
            },
        }
    )

    result = validate_descriptor(descriptor)

    assert result.ok is False
    assert "wall must be smaller than both radii" in result.errors


def test_axial_body_recipe_is_semantic_agnostic() -> None:
    base = {
        "family": "axial_body",
        "parameters": {
            "height": 1.0,
            "radius_top": 0.25,
            "radius_bottom": 0.25,
            "wall": 0.03,
        },
    }

    glass = axial_body_recipe(
        ObjectDescriptor.from_mapping({"id": "A", "semantic": "glass", **base})
    )
    leg = axial_body_recipe(
        ObjectDescriptor.from_mapping({"id": "B", "semantic": "furniture_leg", **base})
    )

    assert glass["dimensions"] == leg["dimensions"]
    assert glass["semantic"] == "glass"
    assert leg["semantic"] == "furniture_leg"


def test_axial_body_recipe_refuses_invalid_descriptor() -> None:
    descriptor = ObjectDescriptor.from_mapping(
        {
            "id": "OBJ_INVALID",
            "family": "axial_body",
            "parameters": {
                "height": -1.0,
                "radius_top": 0.25,
                "radius_bottom": 0.25,
            },
        }
    )

    with pytest.raises(ValueError, match="invalid descriptor"):
        axial_body_recipe(descriptor)
