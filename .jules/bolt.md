# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2026-08-07 - LRU Caching for cosmetic_kinds()
**Learning:** Functions that aggregate global catalog info into immutable collections (like `frozenset[str]` from `cosmetic_kinds()`) should be cached using `@lru_cache` to prevent rebuilding the set/frozenset on every single invocation in hot paths such as `validate_build`.
**Action:** Apply `@lru_cache(maxsize=1)` to `cosmetic_kinds()` in `registry.py` and clear its cache in the test autouse fixture `clear_caches` within `tests/conftest.py`.
