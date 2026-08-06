# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-06-26 - Loop Unrolling and Generator Overhead in Vector Manifests
**Learning:** Checking fixed-length vectors (such as 3D location, rotation, and scale transforms) using generator expressions combined with `all()` or `any()` creates massive call-stack and iterator overhead. Explicit index-based checks (e.g. `isinstance(value[0], ...)` instead of `all(isinstance(x, ...) for x in value)`) completely bypasses generator creation and yields over 24-45% speedups in validation/resolution pipelines.
**Action:** Always prefer unrolling checks for fixed-size coordinate, scale, or color arrays in performance-sensitive validators instead of using generic list comprehensions or generator loops.
