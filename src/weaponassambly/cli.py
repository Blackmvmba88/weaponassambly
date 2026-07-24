from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .assembly import plan_build
from .io import load_build
from .manifest import build_manifest
from .registry import PLATFORMS
from .validator import validate_build


def cmd_validate(path: str) -> int:
    try:
        build = load_build(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = validate_build(build)
    if not result.ok:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {build.display_name or build.platform}")
    return 0


def cmd_inspect(platform: str) -> int:
    slots = PLATFORMS.get(platform)
    if slots is None:
        print(f"ERROR: unknown platform: {platform}", file=sys.stderr)
        return 1

    print(platform)
    for slot, modules in slots.items():
        print(f"  {slot}:")
        for module in sorted(modules):
            print(f"    - {module}")
    return 0


def _load_validated(path: str):
    try:
        build = load_build(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return None, 2

    result = validate_build(build)
    if not result.ok:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return None, 1

    return build, 0


def cmd_plan(path: str) -> int:
    build, code = _load_validated(path)
    if build is None:
        return code

    plan = plan_build(build)
    print(f"{plan.display_name} [{plan.platform}]")
    for step in plan.steps:
        print(
            f"{step.order:02d}  {step.stage.name.lower():<8}  "
            f"{step.slot:<7}  {step.module:<20} -> {step.socket}"
        )
    return 0


def cmd_manifest(path: str, output: str | None) -> int:
    build, code = _load_validated(path)
    if build is None:
        return code

    payload = json.dumps(build_manifest(build), indent=2, sort_keys=True) + "\n"
    if output is None:
        print(payload, end="")
        return 0

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    print(f"WROTE: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bmwa", description="BlackMamba assembly runtime")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a build JSON file")
    validate.add_argument("path")

    inspect = subparsers.add_parser("inspect", help="inspect registered modules for a platform")
    inspect.add_argument("platform")

    plan = subparsers.add_parser("plan", help="print deterministic assembly steps")
    plan.add_argument("path")

    manifest = subparsers.add_parser("manifest", help="emit engine-neutral build manifest JSON")
    manifest.add_argument("path")
    manifest.add_argument("-o", "--output")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "validate":
        return cmd_validate(args.path)
    if args.command == "inspect":
        return cmd_inspect(args.platform)
    if args.command == "plan":
        return cmd_plan(args.path)
    if args.command == "manifest":
        return cmd_manifest(args.path, args.output)

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
