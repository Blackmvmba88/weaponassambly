from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .io import load_build
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bmwa", description="BlackMamba assembly runtime")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a build JSON file")
    validate.add_argument("path")

    inspect = subparsers.add_parser("inspect", help="inspect registered modules for a platform")
    inspect.add_argument("platform")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "validate":
        return cmd_validate(args.path)
    if args.command == "inspect":
        return cmd_inspect(args.platform)

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
