from __future__ import annotations

from functools import lru_cache

from .catalog import (
    cosmetic_values,
    get_catalog,
    load_catalogs,
    slot_modules,
    socket_for_slot,
)


# ⚡ OPTIMIZATION: Cache platform existence queries to avoid repeated get_catalog lookup calls.
@lru_cache(maxsize=32)
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


# ⚡ OPTIMIZATION: Cache module allowed lookups to avoid set membership check overhead.
@lru_cache(maxsize=512)
def module_allowed(platform: str, slot: str, module: str) -> bool:
    return module in slot_modules(platform, slot)


# ⚡ OPTIMIZATION: Cache cosmetic kinds set once since the catalog contents are static.
# Avoids repeated iteration over all catalog cosmetics dictionaries and recreating a frozenset.
@lru_cache(maxsize=1)
def cosmetic_kinds() -> frozenset[str]:
    kinds: set[str] = set()
    for catalog in load_catalogs().values():
        kinds.update(catalog["cosmetics"])
    return frozenset(kinds)


# ⚡ OPTIMIZATION: Cache cosmetic allowed checks (up to 512 entries) to avoid repeated
# dictionary and values scanning.
@lru_cache(maxsize=512)
def cosmetic_allowed(kind: str, value: str, platform: str | None = None) -> bool:
    if platform is not None:
        return value in cosmetic_values(platform, kind)

    return any(
        value in catalog["cosmetics"].get(kind, [])
        for catalog in load_catalogs().values()
    )


# ⚡ OPTIMIZATION: Cache canonical socket retrieval.
@lru_cache(maxsize=128)
def canonical_socket(platform: str, slot: str) -> str | None:
    return socket_for_slot(platform, slot)
