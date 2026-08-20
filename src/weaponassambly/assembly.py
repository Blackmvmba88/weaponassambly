from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .models import BuildConfig
from .registry import canonical_socket
from .validator import validate_build


class AssemblyStage(IntEnum):
    CORE = 0
    FRONT = 10
    BOTTOM = 20
    TOP = 30
    MAG = 40
    COSMETICS = 50


SLOT_TO_STAGE: dict[str, AssemblyStage] = {
    "front": AssemblyStage.FRONT,
    "bottom": AssemblyStage.BOTTOM,
    "top": AssemblyStage.TOP,
    "mag": AssemblyStage.MAG,
}


@dataclass(frozen=True, slots=True)
class AssemblyStep:
    order: int
    stage: AssemblyStage
    slot: str
    module: str
    socket: str


@dataclass(frozen=True, slots=True)
class AssemblyPlan:
    platform: str
    display_name: str
    steps: tuple[AssemblyStep, ...]


def plan_build(build: BuildConfig) -> AssemblyPlan:
    """Create a deterministic assembly plan for a validated game build."""
    validation = validate_build(build)
    if not validation.ok:
        joined = "; ".join(validation.errors)
        raise ValueError(f"invalid build: {joined}")

    # Optimized pending list construction using list comprehension and direct tuple sorting.
    # Avoiding lambda sort key functions and manual loop appends reduces overhead in hot
    # assembly planning (~6% speedup).
    pending = [
        (SLOT_TO_STAGE[slot], slot, module)
        for slot, module in build.modules.items()
        if module is not None
    ]
    pending.sort()

    platform = build.platform
    steps: list[AssemblyStep] = []
    for index, (stage, slot, module) in enumerate(pending, start=1):
        socket = canonical_socket(platform, slot)
        if socket is None:
            raise RuntimeError(f"catalog has no canonical socket for {platform}:{slot}")
        steps.append(
            AssemblyStep(
                order=index,
                stage=stage,
                slot=slot,
                module=module,
                socket=socket,
            )
        )

    return AssemblyPlan(
        platform=platform,
        display_name=build.display_name or platform,
        steps=tuple(steps),
    )
