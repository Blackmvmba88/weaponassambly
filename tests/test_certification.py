from __future__ import annotations

import pytest

from weaponassambly.certification import (
    canonical_json_bytes,
    certification_as_dict,
    certify_resolved_build,
    sha256_digest,
)
from weaponassambly.resolver import ResolvedBuild, ResolvedModule, Transform


def make_resolved() -> ResolvedBuild:
    transform = Transform(
        location=(0.0, 0.15, 0.08),
        rotation_euler=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
    )
    return ResolvedBuild(
        resolver_version=1,
        platform="BM-S7",
        display_name="BM-S7 Phantom",
        root="BM_SIDEARM_ROOT",
        modules=(
            ResolvedModule(
                order=1,
                stage="top",
                slot="top",
                module="MAMBA_RD01",
                socket="SOCKET_TOP",
                transform=transform,
            ),
        ),
        cosmetics={"finish": "polished_black"},
        assembly={"animation": "assemble_default"},
    )


def test_canonical_json_is_order_independent() -> None:
    left = {"b": 2, "a": {"y": 2, "x": 1}}
    right = {"a": {"x": 1, "y": 2}, "b": 2}

    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert sha256_digest(left) == sha256_digest(right)


def test_canonical_json_normalizes_equivalent_numbers() -> None:
    integer_payload = {"assembly": {"count": 1, "offset": 0}}
    float_payload = {"assembly": {"count": 1.0, "offset": -0.0}}

    assert canonical_json_bytes(integer_payload) == canonical_json_bytes(float_payload)
    assert sha256_digest(integer_payload) == sha256_digest(float_payload)


def test_canonical_json_preserves_fractional_numbers_and_booleans() -> None:
    assert canonical_json_bytes({"value": 1.5}) != canonical_json_bytes({"value": 1})
    assert canonical_json_bytes({"value": True}) != canonical_json_bytes({"value": 1})


def test_canonical_json_rejects_non_finite_numbers() -> None:
    with pytest.raises(ValueError, match="NaN or Infinity"):
        canonical_json_bytes({"value": float("nan")})

    with pytest.raises(ValueError, match="NaN or Infinity"):
        canonical_json_bytes({"value": float("inf")})


def test_canonical_json_escapes_lone_surrogates() -> None:
    payload = {"display_name": "phantom\ud800"}

    canonical = canonical_json_bytes(payload)

    assert canonical == b'{"display_name":"phantom\\ud800"}'
    assert len(sha256_digest(payload)) == 64


def test_certification_is_deterministic() -> None:
    first = certify_resolved_build(make_resolved())
    second = certify_resolved_build(make_resolved())

    assert first == second
    assert len(first.digest_sha256) == 64
    assert first.module_count == 1


def test_certification_changes_when_resolved_payload_changes() -> None:
    baseline = make_resolved()
    changed = ResolvedBuild(
        resolver_version=baseline.resolver_version,
        platform=baseline.platform,
        display_name=baseline.display_name,
        root=baseline.root,
        modules=baseline.modules,
        cosmetics={"finish": "chrome"},
        assembly=baseline.assembly,
    )

    assert certify_resolved_build(baseline).digest_sha256 != certify_resolved_build(changed).digest_sha256


def test_certification_dict_has_stable_contract() -> None:
    payload = certification_as_dict(certify_resolved_build(make_resolved()))

    assert payload["certification_version"] == 1
    assert payload["resolver_version"] == 1
    assert payload["platform"] == "BM-S7"
    assert payload["root"] == "BM_SIDEARM_ROOT"
    assert payload["module_count"] == 1
    assert isinstance(payload["digest_sha256"], str)
