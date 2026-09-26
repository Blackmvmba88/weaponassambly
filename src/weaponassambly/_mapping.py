from __future__ import annotations

from typing import Any


def sorted_dict_copy(value: dict[str, Any]) -> dict[str, Any]:
    """Copy a dict in deterministic key order, skipping sorting when it is unnecessary."""
    if len(value) <= 1:
        return dict(value)
    return dict(sorted(value.items()))
