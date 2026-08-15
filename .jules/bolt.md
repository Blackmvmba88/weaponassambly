# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-06-26 - Static Set Hoisting and IntEnum Comparisons
**Learning:** In hot paths such as build validation and assembly plan sorting, iterating/re-creating sets from Enum values (`{slot.value for slot in Slot}`) and explicitly casting `IntEnum` members (`int(item[0])`) introduces measurable object creation and function call overhead.
**Action:** Hoist static Enum sets to module-level `frozenset` constants and leverage native integer comparison on `IntEnum` members.
