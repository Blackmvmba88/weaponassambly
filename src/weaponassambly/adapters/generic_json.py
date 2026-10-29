from __future__ import annotations

from typing import Any

from ..resolver import ResolvedBuild, resolved_build_as_dict


class GenericJsonAdapter:
    """Default adapter for engines or tools that consume plain JSON data."""

    name = "generic-json"

    def emit(self, resolved: ResolvedBuild) -> dict[str, Any]:
        payload = resolved_build_as_dict(resolved)
        payload["adapter"] = self.name
        payload["nodes"] = [
            {
                "name": module.module,
                "parent": resolved.root,
                "slot": module.slot,
                "socket": module.socket,
                "transform": {
                    "location": list(module.transform.location),
                    "rotation_euler": list(module.transform.rotation_euler),
                    "scale": list(module.transform.scale),
                },
            }
            for module in resolved.modules
        ]
        return payload
