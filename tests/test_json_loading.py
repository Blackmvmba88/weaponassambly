from __future__ import annotations

import json

import pytest

from weaponassambly.cli import cmd_parametric_validate
from weaponassambly.io import load_build
from weaponassambly.scene import load_scene_manifest


def test_load_scene_manifest_reads_json_object(tmp_path) -> None:
    payload = {"scene_schema_version": 1, "platform": "BM-S7"}
    path = tmp_path / "scene.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert load_scene_manifest(path) == payload


def test_load_scene_manifest_rejects_non_object_root(tmp_path) -> None:
    path = tmp_path / "scene-list.json"
    path.write_text('["not", "an", "object"]', encoding="utf-8")

    with pytest.raises(ValueError, match="scene manifest root must be a JSON object"):
        load_scene_manifest(path)


def test_parametric_cli_rejects_non_object_root(tmp_path) -> None:
    path = tmp_path / "descriptor-list.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")

    assert cmd_parametric_validate(str(path)) == 2


def test_parametric_cli_rejects_invalid_json(tmp_path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{invalid_json", encoding="utf-8")

    assert cmd_parametric_validate(str(path)) == 2


def test_load_build_valid(tmp_path) -> None:

    payload = {
        "schema_version": 1,
        "platform": "BM-S7",
        "modules": {"top": "MAMBA_RD01"},
        "cosmetics": {"finish": "polished_black"},
    }
    path = tmp_path / "build.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    build = load_build(path)
    assert build.schema_version == 1
    assert build.platform == "BM-S7"
    assert build.modules == {"top": "MAMBA_RD01"}
    assert build.cosmetics == {"finish": "polished_black"}


def test_load_build_missing_keys(tmp_path) -> None:

    payload = {"schema_version": 1, "platform": "BM-S7"}
    path = tmp_path / "incomplete_build.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="missing required keys: modules, cosmetics"):
        load_build(path)


def test_load_build_non_object_root(tmp_path) -> None:

    path = tmp_path / "list_build.json"
    path.write_text('["not", "a", "dict"]', encoding="utf-8")

    with pytest.raises(ValueError, match="build config root must be a JSON object"):
        load_build(path)


def test_load_build_invalid_modules_or_cosmetics(tmp_path) -> None:

    payload = {
        "schema_version": 1,
        "platform": "BM-S7",
        "modules": "not_a_dict",
        "cosmetics": {},
    }
    path = tmp_path / "bad_modules.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="modules must be a JSON object"):
        load_build(path)
