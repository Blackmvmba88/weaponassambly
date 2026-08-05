from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def clear_caches():
    """Automatically clear all LRU caches before each test to prevent state leakage."""
    from weaponassambly.catalog import (
        cosmetic_values,
        load_catalogs,
        registered_platforms,
        slot_modules,
        socket_for_slot,
    )
    from weaponassambly.registry import cosmetic_kinds

    load_catalogs.cache_clear()
    registered_platforms.cache_clear()
    slot_modules.cache_clear()
    socket_for_slot.cache_clear()
    cosmetic_values.cache_clear()
    cosmetic_kinds.cache_clear()
    yield
    load_catalogs.cache_clear()
    registered_platforms.cache_clear()
    slot_modules.cache_clear()
    socket_for_slot.cache_clear()
    cosmetic_values.cache_clear()
    cosmetic_kinds.cache_clear()
