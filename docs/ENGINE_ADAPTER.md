# Asset Resolver and Engine Adapter

## Purpose

The resolver is the boundary between authored Blender data and engine-facing runtime data.

It consumes two independently validated inputs:

```text
BuildConfig JSON
+
Blender scene manifest JSON
        ↓
scene-aware resolver
        ↓
ResolvedBuild
        ↓
engine adapter
        ↓
engine-facing payload
```

The resolver does not infer gameplay behavior from geometry. It only materializes canonical module/socket bindings and scene transforms.

## Inputs

### Build configuration

```bash
bmwa validate configs/bm-s7.example.json
```

The build chooses module IDs and cosmetics.

### Scene manifest

```bash
bmwa scene-validate examples/bm-s7.scene.json
```

The scene manifest exposes canonical socket transforms exported from Blender.

## Resolve

```bash
bmwa resolve \
  configs/bm-s7.example.json \
  examples/bm-s7.scene.json \
  --adapter generic-json \
  --output exports/bm-s7.resolved.json
```

The resolver validates both inputs, verifies platform/root identity, resolves deterministic assembly order and binds every selected module to the transform of its canonical socket.

## Generic JSON adapter

The first adapter is intentionally engine-neutral:

```text
generic-json
```

It emits a serializable node list such as:

```json
{
  "adapter": "generic-json",
  "root": "BM_SIDEARM_ROOT",
  "nodes": [
    {
      "name": "MAMBA_RD01",
      "parent": "BM_SIDEARM_ROOT",
      "slot": "top",
      "socket": "SOCKET_TOP",
      "transform": {
        "location": [0.0, 0.15, 0.08],
        "rotation_euler": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0]
      }
    }
  ]
}
```

## Adapter contract

New game-engine integrations implement `EngineAdapter`:

```python
class EngineAdapter(Protocol):
    name: str

    def emit(self, resolved: ResolvedBuild) -> dict[str, Any]: ...
```

This keeps the canonical resolver independent from Unity, Unreal, Godot or a custom engine.

## Invariants

1. A build and scene must target the same platform.
2. The scene root must match the platform catalog root.
3. Every selected module resolves to exactly one canonical socket.
4. Socket transforms come only from the validated scene manifest.
5. Adapters cannot redefine compatibility or assembly order.
6. Engine-specific serialization happens after canonical resolution.

## Next adapters

The recommended sequence is:

```text
generic-json
→ Godot scene importer
→ Unreal data/import adapter
→ workshop preview runtime
```

The generic adapter remains the reference contract used by tests and CI.
