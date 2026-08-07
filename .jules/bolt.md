# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.


## 2024-08-07 - Cached Sets for Multi-Catalog Membership Checks
**Learning:** Checking list membership inside a generator expression across all loaded catalogs in a hot loop is highly inefficient due to repeated O(n) list scans and generator allocation overhead. Since the catalogs are static, we can compute the union of all values for a given cosmetic kind across all platforms once, and cache it as a `frozenset`. Lookups then become a single O(1) set membership check.
**Action:** Implement a cached `@lru_cache(maxsize=256) def cosmetic_kind_values(kind: str)` returning a `frozenset[str]` and use it for global membership checks to avoid iterative generator evaluation.
