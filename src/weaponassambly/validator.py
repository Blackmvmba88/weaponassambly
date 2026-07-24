from __future__ import annotations

from dataclasses import dataclass

from .models import BuildConfig, Slot
from .registry import COSMETICS, cosmetic_allowed, module_allowed, platform_exists


@dataclass(frozen=True, slots=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def validate_build(build: BuildConfig) -> ValidationResult:
    errors: list[str] = []

    if build.schema_version != 1:
        errors.append(f"unsupported schema_version: {build.schema_version}")

    if not build.platform:
        errors.append("platform is required")
    elif not platform_exists(build.platform):
        errors.append(f"unknown platform: {build.platform}")

    valid_slots = {slot.value for slot in Slot}
    for slot, module in build.modules.items():
        if slot not in valid_slots:
            errors.append(f"unknown module slot: {slot}")
            continue
        if module is None:
            continue
        if build.platform and platform_exists(build.platform):
            if not module_allowed(build.platform, slot, module):
                errors.append(
                    f"module {module!r} is not registered for {build.platform}:{slot}"
                )

    for kind, value in build.cosmetics.items():
        if kind not in COSMETICS:
            errors.append(f"unknown cosmetic kind: {kind}")
            continue
        if value is None:
            continue
        if build.platform and platform_exists(build.platform):
            if not cosmetic_allowed(kind, value, build.platform):
                errors.append(
                    f"cosmetic {kind}={value!r} is not registered for {build.platform}"
                )

    return ValidationResult(ok=not errors, errors=tuple(errors))
