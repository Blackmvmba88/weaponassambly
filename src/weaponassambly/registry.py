from __future__ import annotations

from .catalog import cosmetic_values, load_catalogs, slot_modules, socket_for_slot

_CATALOGS = load_catalogs()

PLATFORMS: dict[str, dict[str, set[str]]] = {
    platform: {
        slot: set(spec["modules"])
        for slot, spec in catalog["slots"].items()
    }
    for platform, catalog in _CATALOGS.items()
}

COSMETICS: dict[str, set[str]] = {}
for catalog in _CATALOGS.values():
    for kind, values in catalog["cosmetics"].items():
        COSMETICS.setdefault(kind, set()).update(values)


def platform_exists(platform: str) -> bool:
    return platform in PLATFORMS


def module_allowed(platform: str, slot: str, module: str) -> bool:
    return module in slot_modules(platform, slot)


def cosmetic_allowed(kind: str, value: str, platform: str | None = None) -> bool:
    if platform is None:
        return value in COSMETICS.get(kind, set())
    return value in cosmetic_values(platform, kind)


def canonical_socket(platform: str, slot: str) -> str | None:
    return socket_for_slot(platform, slot)
