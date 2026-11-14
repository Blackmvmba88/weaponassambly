"""Tests for the local CI runner, without depending on any GitHub runner."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_local.py"
SPEC = importlib.util.spec_from_file_location("local_verifier", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def _report(root: Path) -> tuple[dict, Path]:
    matches = list((root / ".verification/local").glob("*/report.json"))
    assert len(matches) == 1
    return json.loads(matches[0].read_text()), matches[0].parent


def _root(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    return tmp_path


def test_success_writes_independent_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path)

    def fake_run(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        assert kwargs["cwd"] == root
        assert str(root / "src") in kwargs["env"]["PYTHONPATH"]
        return CompletedProcess(command, 0, stdout="OK\n", stderr="")

    monkeypatch.setattr(verifier.subprocess, "run", fake_run)
    assert verifier.main(["--root", str(root), "--only", "ruff", "catalog"]) == 0
    report, evidence = _report(root)
    assert report["overall"] == "passed"
    assert [r["name"] for r in report["checks"]] == ["ruff", "catalog"]
    assert (evidence / "ruff.log").read_text() == "OK\n"


def test_failure_does_not_skip_remaining_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path)
    calls = []

    def fake_run(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        calls.append(command)
        return CompletedProcess(command, 1 if "ruff" in command else 0, "output", "")

    monkeypatch.setattr(verifier.subprocess, "run", fake_run)
    assert verifier.main(["--root", str(root), "--only", "ruff", "pytest"]) == 1
    report, evidence = _report(root)
    assert [r["status"] for r in report["checks"]] == ["failed", "passed"]
    assert len(calls) == 2


def test_timeout_records_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _root(tmp_path)

    def fake_run(command: list[str], **kwargs: object) -> None:
        raise TimeoutExpired(command, 1, output=b"partial")

    monkeypatch.setattr(verifier.subprocess, "run", fake_run)
    assert verifier.main(["--root", str(root), "--only", "ruff", "--timeout", "1"]) == 1
    report, evidence = _report(root)
    assert "partial" in (evidence / "ruff.log").read_text()
    assert report["checks"][0]["status"] == "timeout"


def test_resolve_requires_nonempty_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path)

    def fake_run(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        return CompletedProcess(command, 0, "OK", "")

    monkeypatch.setattr(verifier.subprocess, "run", fake_run)
    assert verifier.main(["--root", str(root), "--only", "resolve"]) == 1
    report, evidence = _report(root)
    assert report["checks"][0]["status"] == "failed"


def test_resolve_nonempty_artifact_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _root(tmp_path)

    def fake_run(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        output = Path(command[-1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("{}")
        return CompletedProcess(command, 0, "OK", "")

    monkeypatch.setattr(verifier.subprocess, "run", fake_run)
    assert verifier.main(["--root", str(root), "--only", "resolve"]) == 0


def test_resolve_rejects_invalid_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _root(tmp_path)

    def fake_run(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        Path(command[-1]).write_text("not-json")
        return CompletedProcess(command, 0, "OK", "")

    monkeypatch.setattr(verifier.subprocess, "run", fake_run)
    assert verifier.main(["--root", str(root), "--only", "resolve"]) == 1
    report, evidence = _report(root)
    assert report["checks"][0]["status"] == "failed"
    assert "invalid JSON" in (evidence / "resolve.log").read_text()


def test_runs_preserve_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _root(tmp_path)

    def fake_run(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        return CompletedProcess(command, 0, "OK", "")

    monkeypatch.setattr(verifier.subprocess, "run", fake_run)
    assert verifier.main(["--root", str(root), "--only", "ruff"]) == 0
    assert verifier.main(["--root", str(root), "--only", "ruff"]) == 0
    reports = list((root / ".verification/local").glob("*/report.json"))
    assert len(reports) == 2
    assert reports[0].parent != reports[1].parent
