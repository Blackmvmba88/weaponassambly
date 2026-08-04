# Bolt's Journal - weaponassambly

## 2026-08-04 - Static Catalog Cache and Generator Overhead in Hot Paths
**Learning:** In the weapon assembly runtime, configuration validation (`validate_build`) and scene resolution (`resolve_build`) are hot paths executed frequently. Repeatedly looking up, parsing, and rebuilding frozensets from static package JSON catalogs on every validation call degrades performance significantly. Furthermore, using generator expressions inside `all()` or `any()` for coordinate validation (e.g., checking socket transforms and collections) creates substantial Python interpreter/stack frame overhead compared to direct component unpacking and check loops.
**Action:** Always cache static packaged asset properties using `@lru_cache` to ensure O(1) query speeds, and unpack list elements/use direct loops instead of generator expressions in performance-critical validation routines.
