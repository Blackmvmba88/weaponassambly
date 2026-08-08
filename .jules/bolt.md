# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-10-24 - Hoisting Static Collections and Caching Registry Scans
**Learning:** Functions like `cosmetic_kinds` perform costly file scan aggregations over all loaded platforms, and creating the `valid_slots` set repeatedly in every `validate_build` invocation introduces massive CPU overhead in high-frequency validation code paths.
**Action:** Use `@lru_cache` on static multi-catalog queries and hoist constant lists/sets of enum values to module-level constants. Remember to clear caches in tests using autouse fixtures.
