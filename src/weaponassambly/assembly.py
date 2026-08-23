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


# Precomputed lowercased stage names to avoid dynamic `.name.lower()` calls in hot paths
STAGE_NAMES: dict[AssemblyStage, str] = {stage: stage.name.lower() for stage in AssemblyStage}


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

    pending: list[tuple[AssemblyStage, str, str]] = []
    for slot, module in build.modules.items():
        if module is None:
            continue
        pending.append((SLOT_TO_STAGE[slot], slot, module))

    # Direct C-level tuple comparison avoids lambda function overhead and key allocation
    pending.sort()

    steps: list[AssemblyStep] = []
    for index, (stage, slot, module) in enumerate(pending, start=1):
        socket = canonical_socket(build.platform, slot)
        if socket is None:
            raise RuntimeError(f"catalog has no canonical socket for {build.platform}:{slot}")
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
        platform=build.platform,
        display_name=build.display_name or build.platform,
        steps=tuple(steps),
    )
