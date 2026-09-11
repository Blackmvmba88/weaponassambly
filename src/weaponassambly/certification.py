from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .resolver import ResolvedBuild, resolved_build_as_dict

CERTIFICATION_VERSION = 1


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize JSON-compatible data deterministically for hashing.

    The representation is intentionally compact and independent of pretty-printing
    so the same resolved build produces the same digest across CLI invocations.
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


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
