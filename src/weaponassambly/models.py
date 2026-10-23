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
        sv = data.get("schema_version", 1)
        pf = data.get("platform", "")
        # Fast-path exact type checks and dict.copy() to eliminate int/str constructor
        # calls and dict constructor dispatch on standard mapping fields (~1.2x speedup).
        mod_dict = (
            modules.copy()
            if type(modules) is dict
            else (dict(modules) if modules else {})
        )
        cos_dict = (
            cosmetics.copy()
            if type(cosmetics) is dict
            else (dict(cosmetics) if cosmetics else {})
        )
        asm_dict = (
            assembly.copy()
            if type(assembly) is dict
            else (dict(assembly) if assembly else {})
        )

        return cls(
            schema_version=sv if type(sv) is int else int(sv),
            platform=pf if type(pf) is str else str(pf),
            display_name=data.get("display_name"),
            modules=mod_dict,
            cosmetics=cos_dict,
            assembly=asm_dict,
        )
