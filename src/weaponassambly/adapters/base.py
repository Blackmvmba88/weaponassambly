from __future__ import annotations

from typing import Any, Protocol

from ..resolver import ResolvedBuild


class EngineAdapter(Protocol):
    """Contract for converting a resolved build into engine-facing data."""

    name: str

    def emit(self, resolved: ResolvedBuild) -> dict[str, Any]:
        """Return a serializable engine-facing representation."""
        ...
