## Verified GitHub Actions follow-up — 2026-11-08

CI on original source commit `d68106a24c4c6071acff7a4d98d74e04c6ecbfe1`: [Run 42386939625](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42386939625), manifest job `128446200136`, **SUCCESS, 862/862 tests / 38 groups**. Actual run logs verified; no real DGX action. Acceptance/release gates remain locked.

---

# P3-E / P3-F source hardening checkpoint — 2026-11-08

Scope: **source-only** change on `feature/recipe-wizard-handoff`. No Docker, DGX GPU, :8000, HF cache, live API, or old receipts are changed by this commit. P3-A/B/C/G stay REAL PASS/CLOSED; P8 alone owns failure injection, automatic restoration trials and final release signoff.

## P3-E — Flash FP8-hybrid draft completeness

- Keep `recipes/qwen38-flash-next.runtime.draft.json` **non-executable** (`launch_allowed=false`, `register_as_runtime_recipe=false`). The pinned NVIDIA source revision plus `-fp8hybrid` prepared checkpoint view, Yarn, 500k context, MTP=2, native tool/reasoning parsers, /hf and read-only chat-template mount remain in the observed-field comparison.
- The comparison now rejects a template bind mount with a relative/unqualified source and emits `host_runtime_qualification_coverage`. The latter counts extra environment keys and mounts without leaking host paths/secret values, and explicitly records unqualified host-cache bytes, template bytes, registry digest, network/security config, and full reinstall readiness.
- Correct an obsolete draft blocker: **P3-G bidirectional live transfer has already passed**, but **P8 fault recovery and final operational acceptance remain not run**. Neither existing P3-G transfer nor field matching establishes Flash reinstall qualification.
- Missing for canonical installability: independent operator-supplied full Config/HostConfig and mount-source provenance, complete image/entrypoint/env/network/security normalization, host-cache and template-content validation, pinned prepared view reinstallation, approved test recreate with identity/chat/native-tools/benchmark and verified backup/restore, and an explicit production qualification decision. Never turn a historic writable /hf bind into an automatically approved desired deployment.

## P3-F — lifecycle failure truthfulness

- Set source/target stop intent **before** Docker mutation so a stop that completes but reports an error still enters reconciliation.
- During rollback, inspect the current running state before attempting to start an original container, avoiding duplicate start when the original never stopped.
- Failed first installation with no prior active service no longer claims `FAIL_RESTORED`. It returns `FAIL_NO_PRIOR_SERVICE_TO_RESTORE`, with `restored_original=false` and an explicit `NO_PRIOR_SERVICE_TO_RESTORE` journal phase; failed candidates remain available for diagnostics.
- Regression additions cover partial source/target stop, failure without any prior service, explicit host-coverage gaps, template source path and P3-G/P8 blocker scope.

**Release boundary:** `PRODUCTION_LIFECYCLE_RELEASED=False`; no execute path is enabled by these changes. Source tests and GitHub CI must be reported separately from DGX hardware verification. P8 retains deliberate fault injection, real auto-recovery, journal/release/UX final acceptance.

## Next approved work (read-only until separate operator authorization)

1. On DGX, use existing read-only Flash observation and source comparison to capture a redacted, complete Docker runtime inventory and validate host paths/file hashes against the pinned hybrid snapshot.
2. Add a distinct, versioned canonical Flash recipe and isolated Fake-DGX candidate launcher tests **without registering or executing it** while qualification is missing.
3. Extend lifecycle fake tests for partial journaling/restore, stale plan changes, unknown port owners and failed-candidate reconciliation. Verify source CI.
4. Separately propose bounded Flash reinstall DGX runbook with explicit downtime, exact SHA, intended rollback and P8 fault-test separation. Do not replay P3-A/B/C/G.
