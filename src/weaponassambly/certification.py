from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any

from .resolver import ResolvedBuild, resolved_build_as_dict

CERTIFICATION_VERSION = 1


def _normalize_json_value(value: Any) -> Any:
    """Normalize JSON values so semantically equivalent numbers hash identically.

    JSON has a single number type, while Python distinguishes ``int`` and ``float``.
    Resolved payloads that compare equal (for example ``1`` and ``1.0`` or ``0``
    and ``-0.0``) therefore need one canonical representation before serialization.
    """
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("canonical JSON does not support NaN or Infinity")
        if value == 0.0:
            return 0
        if value.is_integer():
            return int(value)
        return value
    if isinstance(value, dict):
        return {key: _normalize_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_json_value(item) for item in value]
    return value


def _escape_surrogate_code_units(text: str) -> str:
    """Escape raw UTF-16 surrogate code units without rewriting real astral scalars."""
    return "".join(
        f"\\u{ord(character):04x}"
        if 0xD800 <= ord(character) <= 0xDFFF
        else character
        for character in text
    )


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize JSON-compatible data deterministically for hashing.

    The representation is intentionally compact and independent of pretty-printing,
    dictionary insertion order, equivalent Python numeric spellings, and host Unicode
    encoding behavior. Raw surrogate code units are escaped after JSON serialization,
    keeping the byte stream valid UTF-8 while preserving the distinction between an
    astral Unicode scalar and an explicitly supplied surrogate pair.
    """
    normalized = _normalize_json_value(payload)
    serialized = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return _escape_surrogate_code_units(serialized).encode("utf-8")


def sha256_digest(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


@dataclass(frozen=True, slots=True)
class BuildCertification:
    certification_version: int
    resolver_version: int
    platform: str
    display_name: str
    root: str
    module_count: int
    digest_sha256: str


def certify_resolved_build(resolved: ResolvedBuild) -> BuildCertification:
    """Create a deterministic certificate for an engine-neutral resolved build."""
    payload = resolved_build_as_dict(resolved)
    return BuildCertification(
        certification_version=CERTIFICATION_VERSION,
        resolver_version=resolved.resolver_version,
        platform=resolved.platform,
        display_name=resolved.display_name,
        root=resolved.root,
        module_count=len(resolved.modules),
        digest_sha256=sha256_digest(payload),
    )


def certification_as_dict(certification: BuildCertification) -> dict[str, Any]:
    return {
        "certification_version": certification.certification_version,
        "resolver_version": certification.resolver_version,
        "platform": certification.platform,
        "display_name": certification.display_name,
        "root": certification.root,
        "module_count": certification.module_count,
        "digest_sha256": certification.digest_sha256,
    }
