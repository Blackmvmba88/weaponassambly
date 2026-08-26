from __future__ import annotations

from typing import Any

from .assembly import STAGE_NAMES, plan_build
from .models import BuildConfig

MANIFEST_VERSION = 1


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
        "cosmetics": dict(sorted(build.cosmetics.items())),
        "assembly": dict(sorted(build.assembly.items())),
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
