from __future__ import annotations

import pytest

from weaponassambly.registry import module_allowed, platform_modules


def test_platform_modules_reuses_cached_immutable_mapping():
    first = platform_modules("BM-S7")
    second = platform_modules("BM-S7")

    assert first is not None
    assert second is first
    assert platform_modules.cache_info().hits == 1
    assert all(isinstance(modules, frozenset) for modules in first.values())


def test_platform_modules_mapping_cannot_be_mutated():
    modules = platform_modules("BM-S7")

    assert modules is not None
    with pytest.raises(TypeError):
        modules["top"] = frozenset({"BROKEN"})  # type: ignore[index]


def test_platform_modules_unknown_platform_is_cached_as_none():
    assert platform_modules("UNKNOWN") is None
    assert platform_modules("UNKNOWN") is None
    assert platform_modules.cache_info().hits == 1


def test_module_allowed_caches_allowed_lookup():
    assert module_allowed("BM-S7", "top", "MAMBA_RD01") is True
    assert module_allowed("BM-S7", "top", "MAMBA_RD01") is True
    assert module_allowed.cache_info().hits == 1


def test_module_allowed_caches_rejected_lookup():
    assert module_allowed("BM-S7", "top", "NOT_REGISTERED") is False
    assert module_allowed("BM-S7", "top", "NOT_REGISTERED") is False
    assert module_allowed.cache_info().hits == 1
