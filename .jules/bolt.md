# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2026-08-07 - Avoid Redundant Set Creation in Catalog Validation
**Learning:** Instantiating new sets and parsing enum values inside hot-path validation loops (such as `validate_catalog`) adds significant CPU and memory allocation overhead. Since the set of expected slots is derived from a static Enum `Slot` definition, hoisting this to a module-level `frozenset` constant (`EXPECTED_SLOTS`) completely eliminates redundant runtime set creations and enum iterations, speeding up catalog validation.
**Action:** Always hoist static enum-derived collections or set literals to module-level constants (preferably as `frozenset`) in code that is frequently called or validated.
