# P7 — Duplicate probe IDs and untrusted component evidence (2026-11-20 KST)

## Scope and identified gap
The pre-existing `scripts/manager/integration_contract.py` checked the presence of `probe_id` separately for `service`, `proxy`, `gateway`, and `storage`, but accepted the same ID reused by multiple components as `SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED` when other fields matched. This weakens a source-level claim that the records are separate observations.

## Source-only fix
- Collect nonempty string `probe_id` values from the four component entries and apply `strip()` to compare for duplicates. Missing/non-string/blank IDs retain the existing `PROBE_ID_MISSING` rejection.
- Mark **every** component that shares a repeated normalized ID as `NOT_OBSERVED`, with `<COMPONENT>_PROBE_ID_REUSED_ACROSS_COMPONENTS`; set overall `status=BLOCKED`.
- Keep all prior checks: model registry/canonical container and served ID, fixed port 8000, one-active-model list, checkpoint/recipe path/assets flags, and 120-second inter-component window.
- Leave `executed=false`, `real_dgx_verified=false`, `proxy_gateway_verified=false`, `operations_enabled=false` and `production_released=false`. Unique labels cannot authenticate who generated the evidence.
- This is a generic P7 policy for registered models, **not** an Orcarouter-specific execution adapter.

## Regression evidence and limits
- Exact unmodified Git source blob `fe78ec7751112c7d7b2082dc6ff71bc3bbd27f3a` and original test blob `a484d1581a126bb520095adce24edff9dc45916c` were reconstructed in an isolated local Python environment and confirmed by `git hash-object`.
- Patched code blob: `84c8032f5bf2a957fc2cdeb913879d948888c26f`; patched repository test blob: `78f22792f288cc8e567f68b60457f7bbcaf31700`. Both locally hashed blobs matched GitHub-created blobs before branch update.
- Targeted isolated synthetic CPU harness: **8/8 PASS** (positive unique IDs; exact/trimmed duplicates; blank ID; time window; port 8000; single-model; unknown model).
- A **7/7 PASS** run of the modified repository's `test_integration_contract_cpu.py` methods used a **stubbed model catalog/service manifest**; the real Wizard CLI test was excluded because the complete repository/runtime was not mounted. These results are explicitly **ISOLATED/STUBBED**, not a full real-tree test run.
- New negative test methods added to the actual repository file: `test_duplicate_probe_id_blocks_both_components` and `test_whitespace_normalized_duplicate_probe_id_fails_closed`. The full repository suite, genuine Wizard CLI and GitHub Actions for the new commit are **NOT_RUN/UNVERIFIED**.

## Acceptance and operations
This change **does not** attest independently authenticated P7 service/Proxy/Gateway/Storage observations. P5-D live PLE RSS/PSS/inode↔PID and kernel NAT ownership remain BLOCKED/UNVERIFIED, with known no-sudo UID/procfs restrictions. Real P6-E durable operating Journal/nonce replay fence remains BLOCKED, and P8 fault/recovery as well as Production Release remain BLOCKED. Do not repeat no-sudo host audits, start GPU inference, switch/restart a service, write operating journals, change permissions, dispatch Actions manually, modify `main` or merge PR #1.

## Follow-up
1. On a clean full source checkout at an exact Git SHA, run `python3 -B -m unittest discover -s tests -p 'test_integration_contract_cpu.py' -v` including its real Wizard CLI method, then report shell RC and the exact SHA.
2. Obtain independent P7 component evidence and operator approval before running any real live checks; avoid accepting untrusted JSON as proof.
3. Record exact-SHA CI run ID only if GitHub Actions actually executes. Keep Actions no-run root cause UNVERIFIED; do not trigger or change settings just to satisfy a gate.
