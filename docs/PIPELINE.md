# Runtime Pipeline

## End-to-end contract

```text
Blender authoring
    ↓
scripts/validate_scene.py
    ↓
scripts/export_scene_manifest.py
    ↓
*.scene.json
    ↓
bmwa scene-validate
    ↓
BuildConfig JSON
    ↓
bmwa validate
    ↓
bmwa plan
    ↓
bmwa manifest
    ↓
engine-neutral runtime manifest
```

The scene manifest and build manifest solve different problems:

- **scene manifest** describes what the authored Blender scene exposes;
- **build config** describes which modules/cosmetics a game build requests;
- **runtime manifest** resolves the requested build into deterministic socket bindings.

## 1. Bootstrap Blender scene

```bash
blender --background --python scripts/bootstrap_scene.py
```

For an existing `.blend` file, run the script from Blender's scripting workspace or open the file first and run it in background mode.

## 2. Validate authoring contract

```bash
blender BM_Sidearm_MASTER.blend \
  --background \
  --python scripts/validate_scene.py
```

This checks the canonical root, collection layout, socket presence, parenting and unit scale.

## 3. Export scene manifest

```bash
blender BM_Sidearm_MASTER.blend \
  --background \
  --python scripts/export_scene_manifest.py \
  -- \
  --output exports/bm-s7.scene.json
```

## 4. Validate scene outside Blender

```bash
bmwa scene-validate exports/bm-s7.scene.json
```

This allows CI, asset processors or game-engine import tooling to verify the Blender contract without importing `bpy`.

## 5. Validate a requested build

```bash
bmwa validate configs/bm-s7.example.json
```

## 6. Resolve deterministic assembly order

```bash
bmwa plan configs/bm-s7.example.json
```

Expected order for the current BM-S7 contract:

```text
front → bottom → top → mag
```

Each active module resolves to exactly one canonical socket.

## 7. Emit game-engine-neutral manifest

```bash
bmwa manifest configs/bm-s7.example.json \
  --output exports/bm-s7.runtime.json
```

The runtime manifest is intentionally engine-neutral. A Unity, Unreal, Godot or custom importer can consume the same socket/module contract without changing Blender authoring rules.

## Failure model

Every boundary is independently testable:

```text
invalid .blend organization
        → validate_scene.py fails

invalid exported scene contract
        → bmwa scene-validate fails

invalid build request
        → bmwa validate fails

unregistered module/socket combination
        → bmwa plan fails
```

No downstream stage should silently repair an invalid upstream contract.
