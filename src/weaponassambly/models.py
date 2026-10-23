from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Slot(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    FRONT = "front"
    MAG = "mag"


@dataclass(frozen=True, slots=True)
class BuildConfig:
    schema_version: int
    platform: str
    display_name: str | None = None
    modules: dict[str, str | None] = field(default_factory=dict)
    cosmetics: dict[str, str | None] = field(default_factory=dict)
    assembly: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> BuildConfig:
        sv = data.get("schema_version", 1)
        pf = data.get("platform", "")
        modules = data.get("modules")
        cosmetics = data.get("cosmetics")
        assembly = data.get("assembly")
        # Avoid eager empty dict default evaluation and dict({}) calls for missing fields.
        # Fast-path exact type checks to avoid redundant int() and str() type constructor calls.
        return cls(
            schema_version=sv if type(sv) is int else int(sv),
            platform=pf if type(pf) is str else str(pf),
            display_name=data.get("display_name"),
            modules=dict(modules) if modules else {},
            cosmetics=dict(cosmetics) if cosmetics else {},
            assembly=dict(assembly) if assembly else {},
        )
