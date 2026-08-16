# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2025-02-14 - Unrolling Loops and Caching Immutable Lookups in Hot Paths
**Learning:** In hot-path validation routines like `validate_scene_manifest` and `validate_build`, Python generator expressions coupled with `all()` or `any()` create significant overhead due to iterator creation and function call stack allocation. Unrolling fixed-size iterable checks using direct indexing (`value[0]`, `value[1]`, `value[2]`) or explicit `for` loops yields immense throughput gains (~3x speedup). Additionally, calling global schema queries like `cosmetic_kinds()` repeatedly on every build validation creates redundant collection updates which can be cached globally using `@lru_cache` if they return immutable frozensets.
**Action:** Replace generator-based `all()` or `any()` checks with direct index comparisons or standard for-loops in hot validation paths, and ensure global schema collection queries are cached via `@lru_cache` while cleaning their caches in pytest fixtures.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2025-02-15 - Replacing dataclasses.asdict Reflection in Hot Paths
**Learning:** Python's standard `dataclasses.asdict()` uses heavy reflection, type inspection, and recursive copying, making it prohibitively slow (~47µs per call) for serializing dataclasses in hot paths or API endpoints. Replacing `asdict()` calls with explicit direct dict construction yields a ~14x speedup (~3.3µs per call) while maintaining identical schema structures.
**Action:** In serialization hot paths, construct dictionaries explicitly from dataclass fields instead of using `dataclasses.asdict()`.

## 2024-06-26 - IntEnum Comparison Overhead
**Learning:** Calling `int()` explicitly on `IntEnum` subclass members (e.g. `AssemblyStage`) inside hot-path sort keys or comparison loops introduces unnecessary function call overhead. Python's `IntEnum` members are already subclasses of `int` and directly comparable to integer values.
**Action:** Avoid explicit casting of `IntEnum` subclass members to `int` in sorting keys and comparison paths.
