from __future__ import annotations

import pytest

from weaponassambly.adapters.generic_json import GenericJsonAdapter
from weaponassambly.models import BuildConfig
from weaponassambly.resolver import resolve_build


def make_build() -> BuildConfig:
    return BuildConfig.from_mapping(
        {
            "schema_version": 1,
            "platform": "BM-S7",
            "display_name": "BM-S7 Phantom",
            "modules": {
                "top": "MAMBA_RD01",
                "bottom": "X_TAC",
                "front": None,
                "mag": "DUAL",
            },
            "cosmetics": {
                "finish": "polished_black",
                "grip": "serpent_scale",
                "engraving": "BLACKMAMBA",
            },
            "assembly": {"animation": "assemble_default", "explode_view": True},
        }
    )


def make_scene() -> dict:
    def transform(x: float, y: float, z: float) -> dict:
        return {
            "location": [x, y, z],
            "rotation_euler": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
        }

    return {
        "scene_schema_version": 1,
        "platform": "BM-S7",
        "root": "BM_SIDEARM_ROOT",
        "collections": [
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
        ],
        "sockets": {
            "SOCKET_TOP": transform(0.0, 0.15, 0.08),
            "SOCKET_BOTTOM": transform(0.0, 0.05, -0.05),
            "SOCKET_FRONT": transform(0.0, 0.25, 0.0),
            "SOCKET_MAG": transform(0.0, -0.05, -0.12),
            "SOCKET_GRIP": transform(0.0, -0.08, -0.08),
        },
    }


def test_resolver_binds_modules_to_scene_socket_transforms() -> None:
    resolved = resolve_build(make_build(), make_scene())

    assert resolved.platform == "BM-S7"
    assert [module.slot for module in resolved.modules] == ["bottom", "top", "mag"]

    top = next(module for module in resolved.modules if module.slot == "top")
    assert top.socket == "SOCKET_TOP"
    assert top.transform.location == (0.0, 0.15, 0.08)


def test_resolver_rejects_invalid_scene() -> None:
    scene = make_scene()
    del scene["sockets"]["SOCKET_TOP"]

    with pytest.raises(ValueError, match="invalid scene"):
        resolve_build(make_build(), scene)


def test_generic_adapter_emits_runtime_nodes() -> None:
    resolved = resolve_build(make_build(), make_scene())
    payload = GenericJsonAdapter().emit(resolved)

    assert payload["adapter"] == "generic-json"
    assert payload["root"] == "BM_SIDEARM_ROOT"
    assert [node["name"] for node in payload["nodes"]] == [
        "X_TAC",
        "MAMBA_RD01",
        "DUAL",
    ]
    assert payload["nodes"][1]["socket"] == "SOCKET_TOP"
