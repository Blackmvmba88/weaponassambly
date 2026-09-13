"""Validate and compare certificate claims without changing certification hashing."""
from __future__ import annotations

import json
import re
from typing import Any

FIELDS = (
    "resolver_version", "certification_version", "platform", "display_name",
    "root", "module_count", "digest_sha256",
)


def validate_certificate(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("certificate root must be a JSON object")
    if set(data) != set(FIELDS):
        raise ValueError("certificate must contain exactly the supported certificate fields")
    for field in ("resolver_version", "certification_version", "module_count"):
        if type(data[field]) is not int or data[field] < (0 if field == "module_count" else 1):
            raise ValueError(f"{field} must be a valid non-negative count or positive version")
    for field in ("platform", "display_name", "root", "digest_sha256"):
        if not isinstance(data[field], str):
            raise ValueError(f"{field} must be a string")
    if re.fullmatch(r"[0-9a-f]{64}", data["digest_sha256"]) is None:
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
            if field in ("resolver_version", "certification_version"):
                lines.append(f"{field}: {expected[field]} == {actual[field]}")
        else:
            # JSON escaping keeps arbitrary metadata on a single deterministic line.
            lines.extend([
                f"{field}:",
                f"  expected: {json.dumps(expected[field], ensure_ascii=True)}",
                f"  actual:   {json.dumps(actual[field], ensure_ascii=True)}",
            ])
    return False, "\n".join(lines) + "\n"
