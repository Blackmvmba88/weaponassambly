# Bolt's Optimization Journal

This is Bolt's journal for tracking critical learnings about performance optimizations in the `weaponassambly` project.

## 2025-02-14 - Direct Dictionary Construction vs dataclasses.asdict
**Learning:** Python's `dataclasses.asdict()` relies on recursive `copy.deepcopy()` and dynamic field introspection. In hot paths and high-frequency serialization functions (e.g. `resolved_build_as_dict`), replacing `asdict()` with direct dictionary construction yields massive throughput gains (~14x speedup, reducing execution time from ~2.30s to ~0.16s for 50,000 iterations) without affecting output structure or safety.
**Action:** Use direct dictionary literal construction instead of `dataclasses.asdict()` in performance-critical serialization methods.

## 2025-02-14 - Unrolling Loops and Caching Immutable Lookups in Hot Paths
**Learning:** In hot-path validation routines like `validate_scene_manifest` and `validate_build`, Python generator expressions coupled with `all()` or `any()` create significant overhead due to iterator creation and function call stack allocation. Unrolling fixed-size iterable checks using direct indexing (`value[0]`, `value[1]`, `value[2]`) or explicit `for` loops yields immense throughput gains (~3x speedup). Additionally, calling global schema queries like `cosmetic_kinds()` repeatedly on every build validation creates redundant collection updates which can be cached globally using `@lru_cache` if they return immutable frozensets.
**Action:** Replace generator-based `all()` or `any()` checks with direct index comparisons or standard for-loops in hot validation paths, and ensure global schema collection queries are cached via `@lru_cache` while cleaning their caches in pytest fixtures.

## 2024-06-25 - LRU Caching for Global Catalog Queries
**Learning:** The weapon catalog data in `catalog.py` is read from static JSON resources, making queries about slots, cosmetics, and platform metadata safe to cache globally using `@lru_cache`, provided they return immutable structures (e.g. `frozenset`, `tuple`, `str`) to avoid cache mutation vulnerability.
**Action:** Use `@lru_cache` on catalog functions returning immutable structures, and clear caches in tests to avoid state leakage.

## 2024-06-26 - IntEnum Comparison Overhead
**Learning:** Calling `int()` explicitly on `IntEnum` subclass members (e.g. `AssemblyStage`) inside hot-path sort keys or comparison loops introduces unnecessary function call overhead. Python's `IntEnum` members are already subclasses of `int` and directly comparable to integer values.
**Action:** Avoid explicit casting of `IntEnum` subclass members to `int` in sorting keys and comparison paths.

## 2025-02-14 - Direct Dictionary Construction vs. dataclasses.asdict()
**Learning:** Python's `dataclasses.asdict()` relies heavily on dynamic reflection and `copy.deepcopy` internally to convert dataclass trees to dictionaries. In high-frequency dictionary serialization hot paths (such as `resolved_build_as_dict` and `plan_as_dict`), replacing `asdict()` with explicit direct dictionary construction avoids reflection and deep copy overhead, yielding a ~14x speedup for nested dataclass conversions.
**Action:** Use direct dictionary construction instead of `dataclasses.asdict()` for high-volume serialization of known dataclass schemas in performance-sensitive functions.

## 2025-02-14 - Precomputed Enum String Names and Native Tuple Sorting
**Learning:** Accessing Enum `.name` and calling `.lower()` repeatedly in serialization loops incurs function call and reflection overhead. Precomputing a dictionary mapping Enum members to lowercased string names (`STAGE_NAMES`) eliminates dynamic reflection. Additionally, passing `key=lambda item: (item[0], item[1], item[2])` to `list.sort()` when elements are already 3-tuples introduces unnecessary lambda call overhead; relying on Python's native element-by-element tuple sorting (`list.sort()`) achieves pure C-level comparison speed.
**Action:** Precompute Enum string lookup dicts for fixed Enums and prefer direct list sorting over redundant lambda key functions for tuple elements.

## 2025-05-20 - Unrolling Fixed Vectors vs Code Readability & Maintainability
**Learning:** Unrolling vector component indexing and replacing `isinstance` check loops with explicit manual element variables (`c0, c1, c2`, `type(c) is float`) yields micro-benchmark gains in Python validation loops, but significantly reduces code readability, increases brittleness, and violates Bolt's principle against sacrificing code readability for micro-optimizations. When existing optimizations have already eliminated major bottlenecks in a module, micro-optimizing clean validation code at the cost of clarity is an anti-pattern.
**Action:** Do not sacrifice clean loop constructs or idiomatic type checks for unrolled variable micro-optimizations in validation routines unless there is a major bottleneck that cannot be solved cleanly.

## 2025-05-21 - Deferred Exception String Formatting in Hot Helpers
**Learning:** Constructing formatted f-strings eagerly before passing error labels to validation/transform helper functions (e.g. `_vec3(..., f"{socket}.location")`) creates unnecessary heap string allocations on happy-path execution. Passing static field name string constants and socket identifiers separately to defer string formatting until an exception is raised improves transform resolution throughput (~1.14x speedup) with zero impact on code clarity or safety.
**Action:** Defer f-string formatting inside hot-path helper functions until exception blocks when error messages are only needed upon failure.
