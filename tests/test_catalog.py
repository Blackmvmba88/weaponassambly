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


def test_catalog_validator_preserves_slot_error_order():
    catalog = get_catalog("BM-S7")
    assert catalog is not None
    slots = dict(catalog["slots"])
    del slots["top"]
    slots["zzz"] = {"socket": "SOCKET_ZZZ", "modules": []}
    slots["aaa"] = {"socket": "SOCKET_AAA", "modules": []}

    result = validate_catalog({**catalog, "slots": slots})
    slot_errors = [
        error
        for error in result.errors
        if (
            error.startswith("unknown slot in catalog:")
            or error.startswith("missing slot in catalog:")
        )
    ]

    assert slot_errors == [
        "unknown slot in catalog: aaa",
        "unknown slot in catalog: zzz",
        "missing slot in catalog: top",
    ]


def test_catalog_validator_rejects_invalid_module_string():
    catalog = get_catalog("BM-S7")
    assert catalog is not None
    slots = {name: dict(spec) for name, spec in catalog["slots"].items()}
    slots["top"]["modules"] = ["MAMBA_RD01", ""]

    result = validate_catalog({**catalog, "slots": slots})

    assert not result.ok
    assert "slot top.modules must contain non-empty strings" in result.errors


def test_catalog_validator_rejects_invalid_cosmetic_string():
    catalog = get_catalog("BM-S7")
    assert catalog is not None
    cosmetics = {name: list(values) for name, values in catalog["cosmetics"].items()}
    cosmetics["finish"] = ["polished_black", ""]

    result = validate_catalog({**catalog, "cosmetics": cosmetics})

    assert not result.ok
    assert "cosmetic finish must contain non-empty strings" in result.errors


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
