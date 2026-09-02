from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from typing import Any

from .models import Slot

CATALOG_VERSION = 1

EXPECTED_SLOTS = frozenset(slot.value for slot in Slot)


@dataclass(frozen=True, slots=True)
class CatalogValidationResult:
    ok: bool
    errors: tuple[str, ...]


def validate_catalog(data: dict[str, Any]) -> CatalogValidationResult:
    errors: list[str] = []

    if data.get("catalog_version") != CATALOG_VERSION:
        errors.append(f"unsupported catalog_version: {data.get('catalog_version')!r}")

    platform = data.get("platform")
    if not isinstance(platform, str) or not platform:
        errors.append("platform must be a non-empty string")

    display_name = data.get("display_name")
    if not isinstance(display_name, str) or not display_name:
        errors.append("display_name must be a non-empty string")

    root = data.get("root")
    if not isinstance(root, str) or not root:
        errors.append("root must be a non-empty string")

    slots = data.get("slots")
    if not isinstance(slots, dict):
        errors.append("slots must be an object")
        slots = {}

    slots_keys = set(slots)
    unknown_slots = sorted(slots_keys - EXPECTED_SLOTS)
    missing_slots = sorted(EXPECTED_SLOTS - slots_keys)
    for slot in unknown_slots:
        errors.append(f"unknown slot in catalog: {slot}")
    for slot in missing_slots:
        errors.append(f"missing slot in catalog: {slot}")

    module_ids: set[str] = set()
    for slot, spec in slots.items():
        if slot not in EXPECTED_SLOTS:
            continue
        if not isinstance(spec, dict):
            errors.append(f"slot {slot} must be an object")
            continue

        socket = spec.get("socket")
        if not isinstance(socket, str) or not socket.startswith("SOCKET_"):
            errors.append(f"slot {slot}.socket must be a canonical SOCKET_* name")

        modules = spec.get("modules")
        if not isinstance(modules, list):
            errors.append(f"slot {slot}.modules must be a list")
            continue
        # Avoid all(...) generator allocation overhead by checking elements with a loop
        has_non_string_module = False
        for module in modules:
            if not isinstance(module, str) or not module:
                has_non_string_module = True
                break
        if has_non_string_module:
            errors.append(f"slot {slot}.modules must contain non-empty strings")
            continue
        if len(modules) != len(set(modules)):
            errors.append(f"slot {slot}.modules contains duplicate IDs")

        for module in modules:
            if module in module_ids:
                errors.append(f"module ID registered more than once: {module}")
            module_ids.add(module)

    cosmetics = data.get("cosmetics")
    if not isinstance(cosmetics, dict):
        errors.append("cosmetics must be an object")
        cosmetics = {}

    for kind, values in cosmetics.items():
        if not isinstance(kind, str) or not kind:
            errors.append("cosmetic kind must be a non-empty string")
            continue
        if not isinstance(values, list):
            errors.append(f"cosmetic {kind} must be a list")
            continue
        # Avoid all(...) generator allocation overhead by checking elements with a loop
        has_non_string_value = False
        for value in values:
            if not isinstance(value, str) or not value:
                has_non_string_value = True
                break
        if has_non_string_value:
            errors.append(f"cosmetic {kind} must contain non-empty strings")
            continue
        if len(values) != len(set(values)):
            errors.append(f"cosmetic {kind} contains duplicate values")

    return CatalogValidationResult(ok=not errors, errors=tuple(errors))


def _catalog_resources():
    directory = files("weaponassambly").joinpath("data").joinpath("catalog")
    return sorted(
        (resource for resource in directory.iterdir() if resource.name.endswith(".json")),
        key=lambda resource: resource.name,
    )


@lru_cache(maxsize=1)
def load_catalogs() -> dict[str, dict[str, Any]]:
    catalogs: dict[str, dict[str, Any]] = {}

    for resource in _catalog_resources():
        data = json.loads(resource.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"catalog {resource.name} root must be a JSON object")

        result = validate_catalog(data)
        if not result.ok:
            joined = "; ".join(result.errors)
            raise ValueError(f"invalid catalog {resource.name}: {joined}")

        platform = data["platform"]
        if platform in catalogs:
            raise ValueError(f"duplicate platform catalog: {platform}")
        catalogs[platform] = data

    if not catalogs:
        raise ValueError("no platform catalogs packaged")

    return catalogs


def get_catalog(platform: str) -> dict[str, Any] | None:
    return load_catalogs().get(platform)


@lru_cache(maxsize=128)
def registered_platforms() -> tuple[str, ...]:
    return tuple(sorted(load_catalogs()))


@lru_cache(maxsize=256)
def slot_modules(platform: str, slot: str) -> frozenset[str]:
    catalog = get_catalog(platform)
    if catalog is None:
        return frozenset()
    spec = catalog["slots"].get(slot)
    if spec is None:
        return frozenset()
    return frozenset(spec["modules"])


@lru_cache(maxsize=256)
def socket_for_slot(platform: str, slot: str) -> str | None:
    catalog = get_catalog(platform)
    if catalog is None:
        return None
    spec = catalog["slots"].get(slot)
    if spec is None:
        return None
    return str(spec["socket"])


@lru_cache(maxsize=256)
def cosmetic_values(platform: str, kind: str) -> frozenset[str]:
    catalog = get_catalog(platform)
    if catalog is None:
        return frozenset()
    values = catalog["cosmetics"].get(kind, [])
    return frozenset(values)


@lru_cache(maxsize=256)
def cosmetic_kind_values(kind: str) -> frozenset[str]:
    values: set[str] = set()
    for catalog in load_catalogs().values():
        values.update(catalog["cosmetics"].get(kind, []))
    return frozenset(values)
