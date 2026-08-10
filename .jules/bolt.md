# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-10-31 - Caching Global Cosmetic Kinds
**Learning:** Functions like `cosmetic_kinds()` that aggregate cosmetic metadata across all packaged catalogs build and return a new `frozenset` on every call. Because catalog data is static and cached, caching `cosmetic_kinds()` with `@lru_cache(maxsize=1)` yields a >10x speedup (from ~0.137s to ~0.013s for 100k calls) in build validations without risking cache mutation since a `frozenset` is completely immutable.
**Action:** Cache static collection aggregations returning immutable collections, and clear their caches in the test suite's global teardown.
