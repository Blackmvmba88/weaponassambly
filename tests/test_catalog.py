from __future__ import annotations

from weaponassambly.catalog import (
    get_catalog,
    load_catalogs,
    slot_modules,
    socket_for_slot,
    validate_catalog,
)


def test_packaged_catalog_loads():
    catalogs = load_catalogs()

    assert "BM-S7" in catalogs
    assert catalogs["BM-S7"]["root"] == "BM_SIDEARM_ROOT"


def test_catalog_drives_modules_and_sockets():
    assert "MAMBA_RD01" in slot_modules("BM-S7", "top")
    assert socket_for_slot("BM-S7", "top") == "SOCKET_TOP"
    assert socket_for_slot("BM-S7", "mag") == "SOCKET_MAG"


def test_catalog_has_no_duplicate_module_ids():
    catalog = get_catalog("BM-S7")
    assert catalog is not None

    module_ids = [module for spec in catalog["slots"].values() for module in spec["modules"]]
    assert len(module_ids) == len(set(module_ids))


def test_catalog_validator_rejects_missing_slot():
    catalog = get_catalog("BM-S7")
    assert catalog is not None
    payload = {
        **catalog,
        "slots": dict(catalog["slots"]),
    }
    del payload["slots"]["top"]

    result = validate_catalog(payload)

    assert not result.ok
    assert "missing slot in catalog: top" in result.errors


def test_cosmetic_allowed_without_platform_and_cosmetic_kind_values():
    from weaponassambly.catalog import cosmetic_kind_values
    from weaponassambly.registry import cosmetic_allowed

    # Test cosmetic_kind_values returns correct frozenset
    finish_values = cosmetic_kind_values("finish")
    assert "polished_black" in finish_values
    assert "chrome" in finish_values
    assert "gunmetal" in finish_values
    assert "nonexistent" not in finish_values

    # Test cosmetic_allowed when platform is None
    assert cosmetic_allowed("finish", "polished_black", None) is True
    assert cosmetic_allowed("finish", "nonexistent", None) is False


def test_platform_modules():
    from weaponassambly.registry import platform_modules

    modules = platform_modules("BM-S7")
    assert modules is not None
    assert "top" in modules
    assert isinstance(modules["top"], frozenset)
    assert "MAMBA_RD01" in modules["top"]

    assert platform_modules("NONEXISTENT_PLATFORM") is None
