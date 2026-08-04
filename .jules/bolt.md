# Bolt's Performance Journal

This journal tracks critical performance learnings, bottlenecks, and optimizations identified in the `weaponassambly` codebase.

## 2025-02-18 - Caching Catalog Metadata Queries
**Learning:** Frequent queries to the weapon catalogs (e.g. `slot_modules`, `cosmetic_values`, `cosmetic_kinds`) performed repeated dictionary lookups and built new `frozenset` objects on every single validation or build execution. Caching these static calls with `@lru_cache` yields a dramatic performance improvement and completely eliminates this overhead.
**Action:** Apply `@lru_cache(maxsize=128)` to static query helper functions in `weaponassambly/catalog.py` to prevent redundant `frozenset` creation and parsing.
