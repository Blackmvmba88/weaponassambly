# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-06-26 - Scene Validation Hot-Path Optimization
**Learning:** Python generator expressions inside `all()` or `any()`, as well as list comprehensions converted to sets, introduce non-trivial overhead due to generator frame creation and temporary memory allocations in hot-path validation loops. Replacing them with direct, readable index/loop-based iteration can yield dramatic validation speedups.
**Action:** Replace generator expressions with clean, early-exit loops, and replace implicit set conversions with direct frozenset `.difference()` operations on pre-existing frozensets.
