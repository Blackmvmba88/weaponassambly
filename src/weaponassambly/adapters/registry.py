from __future__ import annotations

from .base import EngineAdapter
from .generic_json import GenericJsonAdapter


_ADAPTERS: dict[str, EngineAdapter] = {
    GenericJsonAdapter.name: GenericJsonAdapter(),
}


def adapter_names() -> tuple[str, ...]:
    return tuple(sorted(_ADAPTERS))


def get_adapter(name: str) -> EngineAdapter:
    try:
        return _ADAPTERS[name]
    except KeyError as exc:
        available = ", ".join(adapter_names())
        raise ValueError(f"unknown adapter: {name}; available: {available}") from exc
