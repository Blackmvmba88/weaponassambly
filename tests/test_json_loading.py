from __future__ import annotations

import json

import pytest

from weaponassambly.cli import cmd_parametric_validate
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
