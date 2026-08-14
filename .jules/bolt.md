# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2025-02-15 - Caching registry cosmetic functions
**Learning:** `cosmetic_kinds()` and `cosmetic_allowed()` inside `registry.py` fetch from static raw catalogs, and their dynamic results are stable/immutable. Caching them avoids repetitive `load_catalogs()` traversals during intensive builds or loops.
**Action:** Add `@lru_cache` on registry-level cosmetic query functions, and register their `.cache_clear()` inside `conftest.py`'s autouse fixture to prevent cross-test leakage.
