from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .adapters.registry import adapter_names, get_adapter
from .assembly import STAGE_NAMES, plan_build
from .catalog import registered_platforms
from .io import load_build
from .manifest import build_manifest
from .parametric import ObjectDescriptor, validate_descriptor
from .registry import platform_modules
from .resolver import resolve_build
from .scene import load_scene_manifest, validate_scene_manifest
from .validator import validate_build


def cmd_parametric_validate(path: str) -> int:
    try:
        with Path(path).open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print("ERROR: descriptor root must be a JSON object", file=sys.stderr)
            return 2
        descriptor = ObjectDescriptor.from_mapping(data)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = validate_descriptor(descriptor)
    if not result.ok:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {descriptor.id or 'unnamed'} [{descriptor.family}]")
    return 0


def cmd_validate(path: str) -> int:
    try:
        build = load_build(path)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = validate_build(build)
    if not result.ok:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {build.display_name or build.platform}")
    return 0


def cmd_catalog_validate() -> int:
    try:
        platforms = registered_platforms()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"OK: {len(platforms)} platform catalog(s): {', '.join(platforms)}")
    return 0


def cmd_inspect(platform: str) -> int:
    try:
        slots = platform_modules(platform)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

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
    except (OSError, ValueError) as exc:
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
            f"{step.order:02d}  {STAGE_NAMES[step.stage]:<8}  "
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


def cmd_scene_validate(path: str) -> int:
    try:
        manifest = load_scene_manifest(path)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = validate_scene_manifest(manifest)
    if not result.ok:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: scene {manifest['platform']} / {manifest['root']}")
    return 0


def cmd_resolve(
    build_path: str,
    scene_path: str,
    adapter_name: str,
    output: str | None,
) -> int:
    build, code = _load_validated(build_path)
    if build is None:
        return code

    try:
        scene_manifest = load_scene_manifest(scene_path)
        resolved = resolve_build(build, scene_manifest)
        adapter = get_adapter(adapter_name)
        data = adapter.emit(resolved)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
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

    subparsers.add_parser("catalog-validate", help="validate all packaged platform catalogs")

    parametric_validate = subparsers.add_parser(
        "parametric-validate", help="validate a parametric object descriptor JSON file"
    )
    parametric_validate.add_argument("path")

    validate = subparsers.add_parser("validate", help="validate a build JSON file")
    validate.add_argument("path")

    inspect = subparsers.add_parser("inspect", help="inspect registered modules for a platform")
    inspect.add_argument("platform")

    plan = subparsers.add_parser("plan", help="print deterministic assembly steps")
    plan.add_argument("path")

    manifest = subparsers.add_parser("manifest", help="emit engine-neutral build manifest JSON")
    manifest.add_argument("path")
    manifest.add_argument("-o", "--output")

    scene_validate = subparsers.add_parser(
        "scene-validate", help="validate a Blender-exported scene manifest"
    )
    scene_validate.add_argument("path")

    resolve = subparsers.add_parser(
        "resolve", help="resolve a build against Blender socket transforms"
    )
    resolve.add_argument("build")
    resolve.add_argument("scene")
    resolve.add_argument("--adapter", choices=adapter_names(), default="generic-json")
    resolve.add_argument("-o", "--output")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "catalog-validate":
        return cmd_catalog_validate()
    if args.command == "parametric-validate":
        return cmd_parametric_validate(args.path)
    if args.command == "validate":
        return cmd_validate(args.path)
    if args.command == "inspect":
        return cmd_inspect(args.platform)
    if args.command == "plan":
        return cmd_plan(args.path)
    if args.command == "manifest":
        return cmd_manifest(args.path, args.output)
    if args.command == "scene-validate":
        return cmd_scene_validate(args.path)
    if args.command == "resolve":
        return cmd_resolve(args.build, args.scene, args.adapter, args.output)

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
