# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2025-02-14 - Enum Overhead and Caching Global Registry Queries
**Learning:** Python's `Enum` class introduces non-trivial runtime overhead during iteration and member attribute lookup in frequently invoked validator/hot-path functions. In addition, iterating over loaded static catalogs repeatedly in global query functions (like `cosmetic_kinds`) wastes computation.
**Action:** Hoist dynamic enum value lookups to module-level immutable constants (e.g., `frozenset`) and cache global static registry/catalog queries with `@lru_cache`. Remember to clear these caches in `conftest.py` to keep tests isolated.
