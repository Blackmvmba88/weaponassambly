# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-06-26 - Eliminate Redundant Casts in Sort Keys
**Learning:** `AssemblyStage` inherits from `IntEnum`, meaning its members are directly comparable to integers and each other without any manual cast. Using `int(item[0])` inside a lambda sort key adds unnecessary function call and casting overhead (causing up to ~27% slowdown for the sorting operation itself).
**Action:** Avoid explicit casting of `IntEnum` objects in sorting keys and comparisons.
