from __future__ import annotations

import pytest

from weaponassambly.parametric import (
    ObjectDescriptor,
    axial_body_recipe,
    box_body_recipe,
    validate_descriptor,
)


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


def test_box_body_descriptor_validates() -> None:
    descriptor = ObjectDescriptor.from_mapping(
        {
            "id": "OBJ_CRATE_001",
            "family": "box_body",
            "semantic": "crate",
            "parameters": {
                "width": 1.2,
                "height": 0.8,
                "depth": 1.0,
                "wall": 0.05,
                "chamfer": 0.02,
                "hollow": True,
                "cap_top": False,
                "cap_bottom": True,
            },
        }
    )

    result = validate_descriptor(descriptor)
    assert result.ok is True
    assert result.errors == ()

    recipe = box_body_recipe(descriptor)
    assert recipe["generator"] == "box_body"
    assert recipe["object_id"] == "OBJ_CRATE_001"
    assert recipe["dimensions"] == {
        "width": 1.2,
        "height": 0.8,
        "depth": 1.0,
        "wall": 0.05,
    }
    assert recipe["mesh"] == {
        "chamfer": 0.02,
        "hollow": True,
        "cap_top": False,
        "cap_bottom": True,
    }


def test_box_body_rejects_impossible_dimensions() -> None:
    descriptor = ObjectDescriptor.from_mapping(
        {
            "id": "OBJ_BAD_BOX",
            "family": "box_body",
            "parameters": {
                "width": -0.1,
                "height": 1.0,
                "depth": 1.0,
            },
        }
    )
    result = validate_descriptor(descriptor)
    assert not result.ok
    assert "width must be > 0" in result.errors


def test_box_body_rejects_impossible_wall_and_chamfer() -> None:
    descriptor = ObjectDescriptor.from_mapping(
        {
            "id": "OBJ_BAD_BOX",
            "family": "box_body",
            "parameters": {
                "width": 2.0,
                "height": 1.0,
                "depth": 2.0,
                "wall": 0.5,
                "chamfer": 0.1,
            },
        }
    )
    result = validate_descriptor(descriptor)
    assert not result.ok
    assert "wall must be smaller than half of the smallest dimension" in result.errors

    descriptor2 = ObjectDescriptor.from_mapping(
        {
            "id": "OBJ_BAD_BOX",
            "family": "box_body",
            "parameters": {
                "width": 2.0,
                "height": 1.0,
                "depth": 2.0,
                "wall": 0.1,
                "chamfer": 0.5,
            },
        }
    )
    result2 = validate_descriptor(descriptor2)
    assert not result2.ok
    assert "chamfer must be smaller than half of the smallest dimension" in result2.errors


def test_box_body_recipe_refuses_invalid_descriptor() -> None:
    descriptor = ObjectDescriptor.from_mapping(
        {
            "id": "OBJ_INVALID",
            "family": "box_body",
            "parameters": {
                "width": 1.0,
                "height": -0.5,
                "depth": 1.0,
            },
        }
    )
    with pytest.raises(ValueError, match="invalid descriptor"):
        box_body_recipe(descriptor)


def test_cmd_parametric_validate_cli(tmp_path) -> None:
    import json

    from weaponassambly.cli import cmd_parametric_validate

    valid_file = tmp_path / "valid.json"
    valid_file.write_text(
        json.dumps(
            {
                "id": "OBJ_CRATE_001",
                "family": "box_body",
                "parameters": {
                    "width": 1.2,
                    "height": 0.8,
                    "depth": 1.0,
                },
            }
        ),
        encoding="utf-8",
    )

    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text(
        json.dumps(
            {
                "id": "OBJ_CRATE_001",
                "family": "box_body",
                "parameters": {
                    "width": -1.2,
                    "height": 0.8,
                    "depth": 1.0,
                },
            }
        ),
        encoding="utf-8",
    )

    assert cmd_parametric_validate(str(valid_file)) == 0
    assert cmd_parametric_validate(str(invalid_file)) == 1
    assert cmd_parametric_validate("non_existent_file.json") == 2
