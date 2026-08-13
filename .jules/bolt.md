# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-10-24 - LRU Caching for Registry Cosmetic Lookups
**Learning:** Registry functions query static catalogs and return immutable data structures (frozenset, bool), which can be cached globally using `@lru_cache` for instant responses.
**Action:** Always verify cached functions return immutable types and register cache clearance in `tests/conftest.py` to prevent state leakage.
