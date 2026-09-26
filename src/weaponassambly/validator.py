from __future__ import annotations

from dataclasses import dataclass

from .models import BuildConfig, Slot
from .registry import cosmetic_allowed, cosmetic_kinds, module_allowed, platform_exists

VALID_SLOTS = frozenset(slot.value for slot in Slot)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...]


# Singleton instance for successful build validations avoids repeated dataclass
# instantiation and empty tuple allocation on every valid build check.
OK_BUILD_VALIDATION_RESULT = ValidationResult(ok=True, errors=())


def validate_build(build: BuildConfig) -> ValidationResult:
    errors: list[str] = []

    if build.schema_version != 1:
        errors.append(f"unsupported schema_version: {build.schema_version}")

    platform = build.platform
    platform_ok = bool(platform) and platform_exists(platform)
    if not platform:
        errors.append("platform is required")
    elif not platform_ok:
        errors.append(f"unknown platform: {platform}")

    if build.display_name is not None and not isinstance(build.display_name, str):
        errors.append("display_name must be a string or null")

    for slot, module in build.modules.items():
        if slot not in VALID_SLOTS:
            errors.append(f"unknown module slot: {slot}")
            continue
        if module is None:
            continue
        if not isinstance(module, str):
            errors.append(f"module value for {slot} must be a string or null")
            continue
        if platform_ok and not module_allowed(platform, slot, module):
            errors.append(f"module {module!r} is not registered for {platform}:{slot}")

    valid_cosmetic_kinds = cosmetic_kinds()
    for kind, value in build.cosmetics.items():
        if kind not in valid_cosmetic_kinds:
            errors.append(f"unknown cosmetic kind: {kind}")
            continue
        if value is None:
            continue
        if not isinstance(value, str):
            errors.append(f"cosmetic {kind} value must be a string or null")
            continue
        if platform_ok and not cosmetic_allowed(kind, value, platform):
            errors.append(f"cosmetic {kind}={value!r} is not registered for {platform}")

    if not errors:
        return OK_BUILD_VALIDATION_RESULT
    return ValidationResult(ok=False, errors=tuple(errors))
