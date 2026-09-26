from __future__ import annotations

import json
from pathlib import Path

from weaponassambly.certification import certification_as_dict, certify_resolved_build
from weaponassambly.cli import cmd_certify
from weaponassambly.models import BuildConfig
from weaponassambly.resolver import resolve_build


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "tokyo_certification_golden.json"


def load_fixture() -> dict:
    with FIXTURE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_golden_certification_matches_expected_digest() -> None:
    fixture = load_fixture()
    build = BuildConfig.from_mapping(fixture["build"])
    resolved = resolve_build(build, fixture["scene"])

    assert certification_as_dict(certify_resolved_build(resolved)) == fixture["expected"]


def test_cmd_certify_emits_golden_certificate(tmp_path, capsys) -> None:
    fixture = load_fixture()
    build_path = tmp_path / "build.json"
    scene_path = tmp_path / "scene.json"
    build_path.write_text(json.dumps(fixture["build"]), encoding="utf-8")
    scene_path.write_text(json.dumps(fixture["scene"]), encoding="utf-8")

    assert cmd_certify(str(build_path), str(scene_path), None) == 0

    emitted = json.loads(capsys.readouterr().out)
    assert emitted == fixture["expected"]


def test_cmd_certify_writes_certificate_file(tmp_path) -> None:
    fixture = load_fixture()
    build_path = tmp_path / "build.json"
    scene_path = tmp_path / "scene.json"
    output_path = tmp_path / "certification.json"
    build_path.write_text(json.dumps(fixture["build"]), encoding="utf-8")
    scene_path.write_text(json.dumps(fixture["scene"]), encoding="utf-8")

    assert cmd_certify(str(build_path), str(scene_path), str(output_path)) == 0

    assert json.loads(output_path.read_text(encoding="utf-8")) == fixture["expected"]
