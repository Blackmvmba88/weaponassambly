from weaponassambly.models import BuildConfig
from weaponassambly.validator import validate_build


def test_valid_bm_s7_build() -> None:
    build = BuildConfig.from_mapping(
        {
            "schema_version": 1,
            "platform": "BM-S7",
            "display_name": "BM-S7 Phantom",
            "modules": {
                "top": "MAMBA_RD01",
                "bottom": "X_TAC",
                "front": None,
                "mag": "DUAL",
            },
            "cosmetics": {
                "finish": "polished_black",
                "grip": "serpent_scale",
                "engraving": "BLACKMAMBA",
            },
        }
    )

    result = validate_build(build)

    assert result.ok is True
    assert result.errors == ()


def test_unknown_platform_is_rejected() -> None:
    build = BuildConfig.from_mapping({"schema_version": 1, "platform": "NOPE"})

    result = validate_build(build)

    assert result.ok is False
    assert "unknown platform: NOPE" in result.errors


def test_unknown_slot_is_rejected() -> None:
    build = BuildConfig.from_mapping(
        {
            "schema_version": 1,
            "platform": "BM-S7",
            "modules": {"left_wing": "WHATEVER"},
        }
    )

    result = validate_build(build)

    assert result.ok is False
    assert "unknown module slot: left_wing" in result.errors


def test_unregistered_module_is_rejected() -> None:
    build = BuildConfig.from_mapping(
        {
            "schema_version": 1,
            "platform": "BM-S7",
            "modules": {"top": "UNKNOWN_OPTIC"},
        }
    )

    result = validate_build(build)

    assert result.ok is False
    assert "module 'UNKNOWN_OPTIC' is not registered for BM-S7:top" in result.errors


def test_non_string_module_value_is_rejected() -> None:
    build = BuildConfig.from_mapping(
        {"schema_version": 1, "platform": "BM-S7", "modules": {"top": []}}
    )

    result = validate_build(build)

    assert result.ok is False
    assert "module value for top must be a string or null" in result.errors


def test_non_string_cosmetic_value_is_rejected() -> None:
    build = BuildConfig.from_mapping(
        {"schema_version": 1, "platform": "BM-S7", "cosmetics": {"finish": {}}}
    )

    result = validate_build(build)

    assert result.ok is False
    assert "cosmetic finish value must be a string or null" in result.errors
