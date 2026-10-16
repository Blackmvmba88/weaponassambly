from __future__ import annotations

from typing import Any


def sorted_dict_copy(value: dict[str, Any]) -> dict[str, Any]:
    """Copy a dict in deterministic key order, skipping sorting when it is unnecessary."""
    # Fast path: returning {} for empty mappings and using value.copy() for 1-item mappings
    # avoids dict() constructor call frame allocation and iteration overhead.
    if not value:
        return {}
    if len(value) == 1:
        return value.copy()
    return dict(sorted(value.items()))
