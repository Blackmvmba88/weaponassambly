"""Regression tests for strict parametric validation and the documented fixture."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from weaponassambly.cli import cmd_parametric_validate
from weaponassambly.parametric import (
    ObjectDescriptor,
    axial_body_recipe,
    box_body_recipe,
    validate_descriptor,
)

ROOT = Path(__file__).resolve().parents[1]

BASES = {
    "axial_body": {"height": 1.0, "radius_top": 0.25, "radius_bottom": 0.25},
    "box_body": {"width": 1.2, "height": 0.8, "depth": 0.4},
}


@pytest.mark.parametrize(
    ("family", "field"),
    [
        ("axial_body", "height"),
        ("axial_body", "radius_top"),
        ("axial_body", "radius_bottom"),
        ("axial_body", "wall"),
        ("axial_body", "bevel"),
        ("box_body", "width"),
        ("box_body", "height"),
        ("box_body", "depth"),
        ("box_body", "wall"),
        ("box_body", "chamfer"),
    ],
)
@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf"), 10**500])
def test_nonfinite_numbers_are_rejected(family: str, field: str, bad_value: float | int) -> None:
    params = {**BASES[family], field: bad_value}
    descriptor = ObjectDescriptor(id="OBJ_TEST", family=family, semantic="prop", parameters=params)
    result = validate_descriptor(descriptor)
    assert not result.ok
    assert f"{field} must be a number" in result.errors


@pytest.mark.parametrize(
    ("family", "flag"),
    [
        ("axial_body", "cap_top"),
        ("axial_body", "cap_bottom"),
        ("box_body", "hollow"),
        ("box_body", "cap_top"),
        ("box_body", "cap_bottom"),
    ],
)
@pytest.mark.parametrize("bad_value", ["false", 0, 1, None])
def test_flags_must_be_boolean(family: str, flag: str, bad_value: object) -> None:
    descriptor = ObjectDescriptor(
        id="OBJ_FLAG", family=family, semantic="prop",
        parameters={**BASES[family], flag: bad_value},
    )
    assert f"{flag} must be a boolean" in validate_descriptor(descriptor).errors


@pytest.mark.parametrize("family", ["axial_body", "box_body"])
def test_false_flags_remain_valid_and_preserved(family: str) -> None:
    params = {**BASES[family], "cap_top": False, "cap_bottom": False}
    if family == "box_body":
        params["hollow"] = False
    descriptor = ObjectDescriptor(
        id="OBJ_VALID", family=family, semantic="prop", parameters=params
    )
    assert validate_descriptor(descriptor).ok
    recipe = axial_body_recipe(descriptor) if family == "axial_body" else box_body_recipe(descriptor)
    assert recipe["mesh"]["cap_top"] is False
    assert recipe["mesh"]["cap_bottom"] is False
    if family == "box_body":
        assert recipe["mesh"]["hollow"] is False


def test_invalid_numbers_are_rejected_before_recipe_generation() -> None:
    descriptor = ObjectDescriptor(
        id="OBJ_INVALID", family="box_body", semantic="prop",
        parameters={**BASES["box_body"], "width": float("inf")},
    )
    with pytest.raises(ValueError, match="invalid descriptor"):
        box_body_recipe(descriptor)


def test_documented_parametric_example_validates() -> None:
    example = ROOT / "examples/parametric_box_body.json"
    assert "examples/parametric_box_body.json" in (ROOT / "README.md").read_text()
    assert cmd_parametric_validate(str(example)) == 0


def test_cli_rejects_nonfinite_json_number(tmp_path: Path) -> None:
    fixture = tmp_path / "bad.json"
    fixture.write_text(
        json.dumps({
            "id": "OBJ_INVALID",
            "family": "box_body",
            "parameters": {**BASES["box_body"], "width": float("nan")},
        }),
        encoding="utf-8",
    )
    assert cmd_parametric_validate(str(fixture)) == 1
