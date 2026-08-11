# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-11-04 - Hot Path Validation Optimization
**Learning:** Generator expressions inside `all()` and `any()` introduce non-trivial overhead in hot path validation loops. Replacing them with direct, index-based checks or early-break `for` loops yields massive speed improvements. Additionally, recreating enum value sets on every call of a validator function is highly inefficient; hoisting them to module-level cached `frozenset` constants saves significant overhead, as does using `.difference()` on a `frozenset` to avoid converting dictionaries to sets.
**Action:** Always hoist static enum collections to module-level `frozenset` constants, use `.difference()` directly, and avoid generator expressions inside functions called repeatedly in high-throughput routines.
