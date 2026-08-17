from __future__ import annotations

import pytest

from weaponassambly.catalog import (
    cosmetic_values,
    load_catalogs,
    registered_platforms,
    slot_modules,
    socket_for_slot,
)
from weaponassambly.registry import cosmetic_allowed, cosmetic_kinds


@pytest.fixture(autouse=True)
def clear_caches():
    """Autouse fixture to clear all LRU caches before and after every test."""
    _clear_all_caches()
    yield
    _clear_all_caches()


def _clear_all_caches():
    load_catalogs.cache_clear()
    registered_platforms.cache_clear()
    slot_modules.cache_clear()
    socket_for_slot.cache_clear()
    cosmetic_values.cache_clear()
    cosmetic_kinds.cache_clear()
    cosmetic_allowed.cache_clear()
