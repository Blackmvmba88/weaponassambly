# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2025-02-18 - Caching Registry Cosmetic Queries
**Learning:** Functions in `registry.py` such as `cosmetic_kinds` and `cosmetic_allowed` resolve lookups on static catalogs. Without caching, validating cosmetics on every build triggers redundant dictionary iterations and set generation, introducing performance degradation. By caching these functions with immutable return types (like `frozenset` and `bool`), we can drastically speed up validation routines.
**Action:** Cache static registry cosmetic functions using `@lru_cache` and ensure their caches are explicitly cleared during testing setup/teardown.
