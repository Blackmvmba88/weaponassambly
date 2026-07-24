from __future__ import annotations

PLATFORMS: dict[str, dict[str, set[str]]] = {
    "BM-S7": {
        "top": {"MAMBA_RD01", "THERMAL_MK1"},
        "bottom": {"X_TAC", "LIGHT_MK1"},
        "front": {"COSMETIC_FRONT_A"},
        "mag": {"STANDARD", "DUAL"},
    }
}

COSMETICS: dict[str, set[str]] = {
    "finish": {"polished_black", "chrome", "gunmetal"},
    "grip": {"serpent_scale", "smooth", "hex"},
    "engraving": {"BLACKMAMBA", "BM_S7", "NONE"},
}


def platform_exists(platform: str) -> bool:
    return platform in PLATFORMS


def module_allowed(platform: str, slot: str, module: str) -> bool:
    return module in PLATFORMS.get(platform, {}).get(slot, set())


def cosmetic_allowed(kind: str, value: str) -> bool:
    return value in COSMETICS.get(kind, set())
