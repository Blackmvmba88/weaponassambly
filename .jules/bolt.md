# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-11-04 - Hot Path Generator Expression Overhead
**Learning:** Generator expressions with `all()` or `any()` inside loops over small, fixed-size structures (e.g., verifying exactly 3 components in transform lists) introduce significant overhead compared to direct index-based comparisons. Similarly, explicit set conversion (e.g. `set(dict_keys)`) is redundant when operating against a `frozenset` which already implements `difference()` on any iterable.
**Action:** Avoid generator expressions and temporary set conversions in validation loops of hot paths. Use direct indexing and built-in collection methods instead.
