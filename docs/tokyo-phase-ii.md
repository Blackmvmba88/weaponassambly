# TOKYO Phase II — Deterministic Certification Layer

TOKYO Phase II hardens the runtime around a simple invariant:

> A resolved build is not complete until it can be reproduced, hashed, compared, and certified.

The existing pipeline already separates build data, catalog validation, deterministic planning, scene manifests, resolution, and engine adapters. This phase adds a certification boundary after resolution without coupling the runtime to Blender or any game engine.

```text
Build JSON
  -> validate
  -> deterministic plan
  -> scene manifest
  -> scene validate
  -> resolve
  -> canonical serialization
  -> SHA-256 digest
  -> certification record
  -> adapter/export
```

## Why this layer exists

A successful execution only proves that the runtime completed. It does not prove that two runs resolved to the same output.

The certification layer gives the pipeline a stable comparison primitive that can be used by tests, CI, asset review, export jobs, or future workshop tooling.

## Contract

A certification record contains:

- certification schema version;
- resolver version;
- platform identifier;
- display name;
- canonical root;
- resolved module count;
- SHA-256 digest of the engine-neutral resolved build.

The digest is calculated from compact JSON with sorted keys and deterministic separators. Pretty-printing, dictionary insertion order, and CLI formatting therefore do not affect the result.

## TOKYO invariants

1. Same resolved payload -> same digest.
2. Any meaningful resolved payload change -> different digest.
3. Certification does not mutate the build or resolved output.
4. Certification is engine-neutral.
5. The canonical serialization rejects non-standard numeric values such as NaN/Infinity.
6. Certification versioning is independent from resolver versioning.

## Next increment

The next TOKYO slice should expose certification through the CLI and CI, then add a regression fixture that compares known build+scene inputs against an expected digest.

Target flow:

```text
READ -> VALIDATE -> PLAN -> RESOLVE -> CERTIFY -> COMPARE -> EXPORT
```

That creates a reproducible boundary before downstream adapters and makes regressions visible even when execution still succeeds.
