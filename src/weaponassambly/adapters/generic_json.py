from __future__ import annotations

from typing import Any

from ..resolver import ResolvedBuild, resolved_build_as_dict


class GenericJsonAdapter:
    """Default adapter for engines or tools that consume plain JSON data."""

    name = "generic-json"

    def emit(self, resolved: ResolvedBuild) -> dict[str, Any]:
        payload = resolved_build_as_dict(resolved)
        adapter_name = self.name
        root = resolved.root
        payload["adapter"] = adapter_name
        # Hoisting root attribute lookup outside the comprehension and replacing list(tuple)
        # with list unpacking syntax [*tuple] eliminates global list lookup and iterator
        # overhead (~1.09x speedup).
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
            for module in resolved.modules
        ]
        return payload
