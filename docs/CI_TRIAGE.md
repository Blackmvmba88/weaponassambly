# TOKYO — CI incident triage and merge gates

This document is operational guidance for the **fictional 3D asset pipeline**. It does not change runtime or game behavior.

## Evidence snapshot (2026-11-20)

- GitHub issue [#129](https://github.com/Blackmvmba88/weaponassambly/issues/129) describes hosted jobs failing before checkout with **zero steps**.
- PRs [#205](https://github.com/Blackmvmba88/weaponassambly/pull/205), [#206](https://github.com/Blackmvmba88/weaponassambly/pull/206), and [#207](https://github.com/Blackmvmba88/weaponassambly/pull/207) remain open in the retrieved PR list.
- The latest five workflow runs returned by GitHub on this date included run [#43598858809](https://github.com/Blackmvmba88/weaponassambly/actions/runs/43598858809), failed on 2026-11-14. A failed check with zero executed steps is **not** proof of a Ruff, pytest, or application failure.
- The `.github/workflows/ci.yml` matrix requests Python 3.11 and 3.12 on `ubuntu-latest`.

Re-check the run history and checks before using this snapshot for a merge decision.

## Triage decision tree

1. Open the failed workflow run and inspect **each matrix job**.
2. If the job has **zero steps**, record it as *runner/provisioning unavailable*, not *tests failed*. Check GitHub Actions service status, repository Actions settings, runner provisioning and account-level billing/usage notices. Do not change billing or repository security settings during triage.
3. If checkout or setup steps ran, inspect the earliest failing step, its logs, Python version, dependency installation and exit code.
4. If tests ran, attach their actual output to the PR. A red check alone does not identify a test failure.
5. Re-run only after the underlying blockage is understood; preserve the original run URL and note the new run URL.

## Reproducible local verification

On a clean checkout of each PR head, with Python **3.11 and 3.12 separately**:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
ruff check .
python -m pytest -q
bmwa catalog-validate
bmwa validate configs/bm-s7.example.json
bmwa scene-validate examples/bm-s7.scene.json
bmwa resolve configs/bm-s7.example.json examples/bm-s7.scene.json --adapter generic-json --output resolved.json
python -m json.tool resolved.json > /dev/null
```

Use separate clean virtual environments per interpreter. Preserve the exact commit SHA, version, commands, terminal exit codes and output. The `resolved.json` file is a **game-asset manifest**, not a physical construction specification.

PR #207 proposes a `make verify-local` wrapper and structured evidence; validate that wrapper **on its own branch**, not on `main`, before adopting it.

## Independent PR review gates

| PR | Required before merge |
| --- | --- |
| #205 | Confirm MIT LICENSE text, README links and complete tests on the PR head |
| #206 | Confirm invalid-number/flag cases and all regression tests on the PR head |
| #207 | Confirm the verification runner preserves evidence and propagates failures; execute real repo checks rather than only its simulated fixtures |
| #203 / #204 | Compare diffs and benchmark with identical inputs; avoid merging duplicate implementations |

Do not merge solely because an isolated mock test passed. Do not interpret missing CI steps as validation. Record a passing, reproducible test result for each affected branch before integration.

## Verification record template

```text
UTC timestamp:
PR / branch / commit SHA:
Python version:
Environment:
Command:
Exit code:
Result / log URL or saved path:
Open blockers:
Decision (ready / blocked):
```

## Scope boundary

This effort is limited to CI diagnosis, software quality and fictional game-asset data. No guidance on physical weapon construction, parts compatibility or operational performance belongs in this checklist.

## Diff review: PR #203 versus #204 (2026-11-20)

**Confirmed overlap:** both PRs modify only `.jules/bolt.md` and `src/weaponassambly/_mapping.py`. In the executable code, both replace `dict(sorted(value.items()))` with exactly `{k: value[k] for k in sorted(value)}` inside `sorted_dict_copy`. They differ only in explanatory comments and journal wording. Both PRs report GitHub `mergeable: true` against the current base, but that is **not** a test result.

**Integration recommendation:** select **one** PR after checking its source and tests; do **not** merge both independently. If one lands, close the redundant PR with a reference to the merged commit. Retain `tests/test_mapping.py` regression coverage; check the empty, singleton, unordered and fresh-copy behaviors.

The current assistant execution container cannot resolve `github.com` for a real clone, so no full-source pytest or Ruff result can be claimed here. Connector API inspection of the branch diffs and repository files **did** complete.
