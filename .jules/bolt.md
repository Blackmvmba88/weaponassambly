# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2025-03-06 - Hoisting Enum collections as module-level constants
**Learning:** Re-evaluating list/set comprehensions of Enum member values (like `{slot.value for slot in Slot}`) within hot-path validator functions creates a redundant allocation of sets on every single call. Converting these collections to module-level constants (like `frozenset`) eliminates allocation overhead completely and results in significant performance improvements.
**Action:** Always identify Enum lookups and comprehensions in critical-path/validation functions, and hoist them into global constants using `frozenset` or `tuple` to avoid recreation overhead.
