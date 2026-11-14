# TOKYO — Local Verification

GitHub Actions can fail before the first step starts (issue #129). This local
verifier runs the repository gates without hosted runners, preserving separate
evidence for each execution. It is **not** a substitute for a successfully
executed CI job.

## Install

Run from the repository root using Python 3.11 or 3.12:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -e '.[dev]'

## Execute all local gates

    make verify-local

Equivalent direct command:

    python scripts/verify_local.py

It executes Ruff, pytest (with JUnit XML), catalog validation, build validation,
scene-manifest validation and generic JSON resolution. Each subprocess uses the
current Python interpreter and does not use a shell. All gates run even if one
fails, and the overall return code is nonzero on failure or timeout.

A resolve command counts as successful only if it returns zero and produces
a nonempty JSON object. The verifier cannot certify Blender scene geometry;
it checks the runtime and its JSON fixtures.

## Evidence and history

Every invocation creates a unique directory under:

    .verification/local/<UTC-time>-<random-suffix>/

The folder includes report.json, separate command logs, a JUnit XML report if
pytest generates one, and the resolved JSON if the resolve gate ran. Existing
runs are preserved. The directory is ignored by Git.

A focused run is supported:

    python scripts/verify_local.py --only pytest resolve --timeout 180

An alternate archive location can be specified:

    python scripts/verify_local.py --output-dir /tmp/bmwa-verification

## Release / merge gate

- All six local gates must pass with their recorded evidence.
- Run the full set on Python 3.11 and Python 3.12 before claiming compatibility.
- Hosted GitHub CI must be independently confirmed operational, with actual
  job steps, before claiming GitHub Actions is green.
- No PR should be merged based only on mocked tests of this verifier.

To share a failed-run diagnosis, attach report.json and the relevant log files
to the PR. Neither the local runner nor this documentation changes issue #129.
