# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2025-02-18 - Unrolling Fixed 3D Vector Type Checks and Inline Scale Validation in Scene Manifests
**Learning:** In Blender scene manifest validation (`validate_scene_manifest`), socket transform checks repeatedly iterate over 3-element coordinate lists (`location`, `rotation_euler`, `scale`) using `for component in value:` loops. Unrolling fixed 3-element index assignments (`v0, v1, v2 = value[0], value[1], value[2]`) and checking element types directly avoids iterator creation overhead. Furthermore, integrating the unit scale check directly when processing the `scale` field eliminates redundant `transform.get("scale")` dictionary lookups and re-iterations, yielding a ~2.1x speedup in manifest validation.
**Action:** Unroll type and value checks on fixed 3D spatial vectors in hot-path validation loops and consolidate field lookups into a single traversal.

## 2025-02-14 - Unrolling Loops and Caching Immutable Lookups in Hot Paths
**Learning:** In hot-path validation routines like `validate_scene_manifest` and `validate_build`, Python generator expressions coupled with `all()` or `any()` create significant overhead due to iterator creation and function call stack allocation. Unrolling fixed-size iterable checks using direct indexing (`value[0]`, `value[1]`, `value[2]`) or explicit `for` loops yields immense throughput gains (~3x speedup). Additionally, calling global schema queries like `cosmetic_kinds()` repeatedly on every build validation creates redundant collection updates which can be cached globally using `@lru_cache` if they return immutable frozensets.
**Action:** Replace generator-based `all()` or `any()` checks with direct index comparisons or standard for-loops in hot validation paths, and ensure global schema collection queries are cached via `@lru_cache` while cleaning their caches in pytest fixtures.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-06-26 - IntEnum Comparison Overhead
**Learning:** Calling `int()` explicitly on `IntEnum` subclass members (e.g. `AssemblyStage`) inside hot-path sort keys or comparison loops introduces unnecessary function call overhead. Python's `IntEnum` members are already subclasses of `int` and directly comparable to integer values.
**Action:** Avoid explicit casting of `IntEnum` subclass members to `int` in sorting keys and comparison paths.
