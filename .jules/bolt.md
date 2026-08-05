# Bolt's Performance Journal

This journal logs critical learning experiences, insights, and lessons discovered during performance engineering across the BlackMamba weapon assembly platform.

## 2025-02-18 - Static Resource Queries Optimization
**Learning:** Functions that query platform static assets (such as JSON catalog metadata) are safe to cache globally using `@lru_cache` since catalogs are immutable during runtime. Rebuilding `frozenset` objects and performing dictionary lookups inside validation loops introduces significant overhead. Adding `@lru_cache(maxsize=128)` avoids constructing new containers and reduces lookup times dramatically.
**Action:** Always identify read-only/static data pipelines that are repeatedly queried in hot-paths (like build validators), and utilize `functools.lru_cache` or similar caching techniques to bypass object allocation and processing overhead.
