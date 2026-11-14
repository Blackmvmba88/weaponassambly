"""Run the repository's validation gates locally, without GitHub Actions.

Usage: python scripts/verify_local.py
       python scripts/verify_local.py --only pytest resolve
       python scripts/verify_local.py --output-dir .verification/my-run
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    "ruff", "pytest", "catalog", "build", "scene", "resolve",
)


def command_for(name: str, output: Path) -> list[str]:
    python = sys.executable
    commands = {
        "ruff": [python, "-m", "ruff", "check", "."],
        "pytest": [python, "-m", "pytest", "-q", "--junitxml", str(output / "pytest.xml")],
        "catalog": [python, "-m", "weaponassambly.cli", "catalog-validate"],
        "build": [python, "-m", "weaponassambly.cli", "validate", "configs/bm-s7.example.json"],
        "scene": [
            python, "-m", "weaponassambly.cli", "scene-validate",
            "examples/bm-s7.scene.json",
        ],
        "resolve": [
            python, "-m", "weaponassambly.cli", "resolve",
            "configs/bm-s7.example.json", "examples/bm-s7.scene.json",
            "--adapter", "generic-json", "--output", str(output / "resolved.json"),
        ],
    }
    return commands[name]


def run_check(name: str, root: Path, output: Path, timeout: int) -> dict[str, object]:
    command = command_for(name, output)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(root / "src"), env.get("PYTHONPATH", "")) if part
    )
    started = time.monotonic()
    exit_code: int | None = None
    try:
        result = subprocess.run(
            command, cwd=root, env=env, capture_output=True, text=True,
            errors="replace", timeout=timeout, check=False,
        )
        exit_code = result.returncode
        log = result.stdout + result.stderr
        status = "passed" if exit_code == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        log = stdout + stderr + f"\nTIMEOUT after {timeout}s\n"
    except OSError as exc:
        status = "failed"
        log = f"EXECUTION ERROR: {exc}\n"

    if name == "resolve" and status == "passed":
        target = output / "resolved.json"
        if not target.is_file() or target.stat().st_size == 0:
            status = "failed"
            log += "\nERROR: resolve exited 0 but output file is missing or empty\n"
        else:
            try:
                payload = json.loads(target.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("JSON root must be an object")
            except (OSError, ValueError) as exc:
                status = "failed"
                log += f"\nERROR: resolve output is invalid JSON: {exc}\n"
    log_path = output / f"{name}.log"
    log_path.write_text(log, encoding="utf-8")
    return {
        "name": name, "status": status, "exit_code": exit_code,
        "duration_seconds": round(time.monotonic() - started, 3),
        "command": command, "log": log_path.name,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument(
        "--output-dir", type=Path, default=Path(".verification/local"),
        help="run archive directory (relative to --root unless absolute)",
    )
    parser.add_argument("--only", nargs="+", choices=CHECKS, help="run selected gates")
    parser.add_argument("--timeout", type=int, default=300, help="seconds per gate")
    args = parser.parse_args(argv)
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    root = args.root.resolve()
    if not (root / "pyproject.toml").is_file():
        parser.error(f"not a project root: {root}")
    output = args.output_dir
    if not output.is_absolute():
        output = root / output
    output = output.resolve()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    output = output / run_id
    output.mkdir(parents=True, exist_ok=False)
    selected = args.only or list(CHECKS)
    results = []
    for name in selected:
        result = run_check(name, root, output, args.timeout)
        results.append(result)
        print(f"{name}: {result['status']} (log: {output / str(result['log'])})")
    report = {
        "schema_version": 1,
        "run_id": run_id,
        "python": sys.version.split()[0],
        "root": str(root),
        "overall": "passed" if all(r["status"] == "passed" for r in results) else "failed",
        "checks": results,
    }
    (output / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Evidence: {output / 'report.json'}")
    return 0 if report["overall"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
