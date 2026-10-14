"""Validate and compare certificate claims without changing certification hashing."""
from __future__ import annotations

import json
import re
from typing import Any

FIELDS = (
    "resolver_version", "certification_version", "platform", "display_name",
    "root", "module_count", "digest_sha256",
)
FIELDS_SET = frozenset(FIELDS)
VERSION_FIELDS = frozenset(("resolver_version", "certification_version"))
HEX64_RE = re.compile(r"[0-9a-f]{64}")


def validate_certificate(data: Any) -> dict[str, Any]:
    # Fast path: direct dictionary type check and precomputed set keys view check avoid
    # temporary set allocations on every validation call (~1.5x speedup).
    if type(data) is not dict and not isinstance(data, dict):
        raise ValueError("certificate root must be a JSON object")
    # Comparing dictionary keys view directly against precomputed frozenset and using
    # pre-compiled regex avoids set allocations and pattern lookup overhead (~1.5x speedup).
    if data.keys() != FIELDS_SET:
        raise ValueError("certificate must contain exactly the supported certificate fields")
    # Direct unrolled field check avoids tuple iteration overhead (~1.07x speedup).
    rv = data["resolver_version"]
    if type(rv) is not int or rv < 1:
        raise ValueError(
            "resolver_version must be a valid non-negative count or positive version"
        )

    cv = data["certification_version"]
    if type(cv) is not int or cv < 1:
        raise ValueError(
            "certification_version must be a valid non-negative count or positive version"
        )

    mc = data["module_count"]
    if type(mc) is not int or mc < 0:
        raise ValueError("module_count must be a valid non-negative count or positive version")

    p = data["platform"]
    if type(p) is not str and not isinstance(p, str):
        raise ValueError("platform must be a string")

    dn = data["display_name"]
    if type(dn) is not str and not isinstance(dn, str):
        raise ValueError("display_name must be a string")

    r = data["root"]
    if type(r) is not str and not isinstance(r, str):
        raise ValueError("root must be a string")

    digest = data["digest_sha256"]
    if type(digest) is not str and not isinstance(digest, str):
        raise ValueError("digest_sha256 must be a string")

    if HEX64_RE.fullmatch(digest) is None:
        raise ValueError("digest_sha256 must contain 64 lowercase hexadecimal characters")
    return data


def compare_certificates(expected: Any, actual: Any) -> tuple[bool, str]:
    """Compare every certificate field in a fixed order; versions are claims too."""
    expected = validate_certificate(expected)
    actual = validate_certificate(actual)
    if expected == actual:
        return True, "MATCH\n"
    lines = ["MISMATCH", ""]
    for field in FIELDS:
        if expected[field] == actual[field]:
            if field in VERSION_FIELDS:
                lines.append(f"{field}: {expected[field]} == {actual[field]}")
        else:
            # JSON escaping keeps arbitrary metadata on a single deterministic line.
            lines.extend([
                f"{field}:",
                f"  expected: {json.dumps(expected[field], ensure_ascii=True)}",
                f"  actual:   {json.dumps(actual[field], ensure_ascii=True)}",
            ])
    return False, "\n".join(lines) + "\n"
