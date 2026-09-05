from __future__ import annotations

from typing import Any

from .assembly import STAGE_NAMES, plan_build
from .models import BuildConfig

MANIFEST_VERSION = 1


def _sort_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Sort dictionary by keys, short-circuiting for 0 or 1 item (~3x faster)."""
    if len(d) <= 1:
        return dict(d)
    return dict(sorted(d.items()))


def build_manifest(build: BuildConfig) -> dict[str, Any]:
    """Produce a game-engine-neutral manifest for a validated build."""
    plan = plan_build(build)

    return {
        "manifest_version": MANIFEST_VERSION,
        "schema_version": build.schema_version,
        "platform": build.platform,
        "display_name": plan.display_name,
        "root": "BM_SIDEARM_ROOT",
        "modules": [
            {
                "order": step.order,
                "stage": STAGE_NAMES[step.stage],
                "slot": step.slot,
                "module": step.module,
                "socket": step.socket,
            }
            for step in plan.steps
        ],
        "cosmetics": _sort_dict(build.cosmetics),
        "assembly": _sort_dict(build.assembly),
    }


def plan_as_dict(build: BuildConfig) -> dict[str, Any]:
    plan = plan_build(build)
    # Construct dict directly to avoid dataclasses.asdict reflection
    # and copy overhead (~1.8x speedup).
    return {
        "platform": plan.platform,
        "display_name": plan.display_name,
        "steps": [
            {
                "order": step.order,
                "stage": STAGE_NAMES[step.stage],
                "slot": step.slot,
                "module": step.module,
                "socket": step.socket,
            }
            for step in plan.steps
        ],
    }
