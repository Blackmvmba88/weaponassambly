from __future__ import annotations

from functools import cache

from .catalog import cosmetic_values, get_catalog, load_catalogs, slot_modules, socket_for_slot


@cache
def platform_exists(platform: str) -> bool:
    return get_catalog(platform) is not None


def platform_modules(platform: str) -> dict[str, set[str]] | None:
    catalog = get_catalog(platform)
    if catalog is None:
        return None
    return {
        slot: set(spec["modules"])
        for slot, spec in catalog["slots"].items()
    }


def module_allowed(platform: str, slot: str, module: str) -> bool:
    return module in slot_modules(platform, slot)


@cache
def cosmetic_kinds() -> frozenset[str]:
    kinds: set[str] = set()
    for catalog in load_catalogs().values():
        kinds.update(catalog["cosmetics"])
    return frozenset(kinds)


@cache
def _cosmetic_allowed_any_platform(kind: str, value: str) -> bool:
    return any(
        value in catalog["cosmetics"].get(kind, [])
        for catalog in load_catalogs().values()
    )


def cosmetic_allowed(kind: str, value: str, platform: str | None = None) -> bool:
    if platform is not None:
        return value in cosmetic_values(platform, kind)

    return _cosmetic_allowed_any_platform(kind, value)


def canonical_socket(platform: str, slot: str) -> str | None:
    return socket_for_slot(platform, slot)
