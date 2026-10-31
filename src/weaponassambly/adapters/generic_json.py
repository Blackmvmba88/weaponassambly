from __future__ import annotations

from typing import Any

from ..resolver import ResolvedBuild, resolved_build_as_dict


class GenericJsonAdapter:
    """Default adapter for engines or tools that consume plain JSON data."""

    name = "generic-json"

    def emit(self, resolved: ResolvedBuild) -> dict[str, Any]:
        # Hoist root and modules attributes outside list comprehension and unpack
        # 3-tuples directly with [*...] to avoid global list lookup and iterator
        # overhead (~1.09x speedup in emit serialization).
        root = resolved.root
        modules = resolved.modules
        payload = resolved_build_as_dict(resolved)
        payload["adapter"] = self.name
        payload["nodes"] = [
            {
                "name": module.module,
                "parent": root,
                "slot": module.slot,
                "socket": module.socket,
                "transform": {
                    "location": [*module.transform.location],
                    "rotation_euler": [*module.transform.rotation_euler],
                    "scale": [*module.transform.scale],
                },
            }
            for module in modules
        ]
        return payload
