from __future__ import annotations

import pytest

from weaponassambly.assembly import AssemblyStage, plan_build
from weaponassambly.manifest import build_manifest
from weaponassambly.models import BuildConfig


def make_build(**overrides):
    data = {
        "schema_version": 1,
        "platform": "BM-S7",
        "display_name": "BM-S7 Test",
        "modules": {
            "top": "MAMBA_RD01",
            "bottom": "X_TAC",
            "front": "COSMETIC_FRONT_A",
            "mag": "DUAL",
        },
        "cosmetics": {
            "finish": "polished_black",
            "grip": "serpent_scale",
            "engraving": "BLACKMAMBA",
        },
        "assembly": {"animation": "assemble_default", "explode_view": True},
    }
    data.update(overrides)
    return BuildConfig.from_mapping(data)


def test_plan_is_deterministic_and_stage_ordered():
    build = make_build()
    plan = plan_build(build)

    assert [step.slot for step in plan.steps] == ["front", "bottom", "top", "mag"]
    assert [step.stage for step in plan.steps] == [
        AssemblyStage.FRONT,
        AssemblyStage.BOTTOM,
        AssemblyStage.TOP,
        AssemblyStage.MAG,
    ]
    assert [step.order for step in plan.steps] == [1, 2, 3, 4]


def test_plan_maps_slots_to_canonical_sockets():
    plan = plan_build(make_build())
    sockets = {step.slot: step.socket for step in plan.steps}

    assert sockets == {
        "front": "SOCKET_FRONT",
        "bottom": "SOCKET_BOTTOM",
        "top": "SOCKET_TOP",
        "mag": "SOCKET_MAG",
    }


def test_plan_skips_empty_optional_module():
    build = make_build(
        modules={
            "top": "MAMBA_RD01",
            "bottom": None,
            "front": None,
            "mag": "STANDARD",
        }
    )
    plan = plan_build(build)

    assert [step.slot for step in plan.steps] == ["top", "mag"]


def test_plan_rejects_invalid_build():
    build = make_build(modules={"top": "NOT_REGISTERED"})

    with pytest.raises(ValueError, match="invalid build"):
        plan_build(build)


def test_manifest_is_engine_neutral_contract():
    manifest = build_manifest(make_build())

    assert manifest["manifest_version"] == 1
    assert manifest["platform"] == "BM-S7"
    assert manifest["root"] == "BM_SIDEARM_ROOT"
    assert manifest["modules"][0] == {
        "order": 1,
        "stage": "front",
        "slot": "front",
        "module": "COSMETIC_FRONT_A",
        "socket": "SOCKET_FRONT",
    }
