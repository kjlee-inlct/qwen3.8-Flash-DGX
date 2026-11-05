# Next actions — ordered work queue

> Updated 2026-11-05 KST. **Draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) open; zero CI checks on the initial documentation commit; verify current checks after N1 commit.** Status terms are scoped. Tasks are not achieved merely because listed in a plan.

## NOW — P0, read-only/source-safe

**CI regression note:** First N2+port commit `7e8f4a1` had four launch FAIL due to permission `100644` (exit 126), despite 15 schema and 10 inventory tests PASS. Script executable bits repaired in follow-up commit; check actual new HEAD CI before claiming all PASS.

**2026-11-05 priority revision (user request):** legacy services reported deleted; restore external `:8000/v1` with Blazux *NVIDIA Flash-Next* `default` profile, not Orcarouter. SOURCE changes to `flash`, `scripts/serve.sh`, `profiles/default.env` and manifest rules; N2 read-only inventory and deterministic plan implemented. **DGX state unobserved**. No setup, serve, GPU, download or cleanup done.


**N1 completed SOURCE/CPU only (2026-11-04):** JSON Schema Draft 2020-12, safe YAML loader, bounded guards and 15 isolated CPU tests PASS. 27B candidate intentionally FAIL (exit 2); synthetic valid fixture is not deployable. New PR CI requires GitHub readback at the actual commit SHA. No DGX/GPU/API execution.


- [x] **N1 — Make manifest schema machine-checkable.** Add `recipes/` and `schemas/` proposals implemented with validated, explicit repo revision, digest and immutable targets; a sample 27B placeholder must fail closed. CPU tests cover malformed manifest and unsupported engine.
- [x] **N2 — Implement read-only storage/Docker inventory.** Gather capacity and model references without changing caches, engines or services. Detect protected live service name/image/mount/port and disallow unsafe paths/names. Add `--dry-run` and deterministic plan output.
- [ ] **N3 — Implement wizard orchestration skeleton. (**PARTIAL**: `wizard/00-doctor.sh` and `10-plan.sh` read-only wrappers implemented; no interactive/execute service manager.)** Shared Python manager plus small interactive/noninteractive shell wrappers; confirm no default launch, download, restart or deletion. Add error-path tests.
- [ ] **N4 — vLLM 0.32 27B source feasibility audit.** Determine exact architecture mapping, NVFP4 quantized output head, vision input, GDN, kernel/sm_121 constraints, context, MTP OFF baseline and DFlash2 scope. Record precise pinning and file/line evidence; **do not copy SGLang launcher**.
- [ ] **N5 — Integrate existing Orcarouter feature deliberately.** Review `feature/orcarouter-bf16-adapter` docs/commits, resolve against manifest contract, then merge/cherry-pick only after explicit integration/test plan. Preserve PLE/MTP count/dtype guards.

## THEN — P1 to P3, requires GPU window approval

- [ ] P1 Flash-Next vLLM baseline: pinned startup, API/bench, memory, quality, evidence.
- [ ] P2 27B vLLM baseline: compatibility/source/CPU GO first; pinned GPU run, functional/bench.
- [ ] P3 Flash-Next ↔ 27B repeated two-way switch, rollback and failure injection.

## AFTER — independently gated

- [ ] P4 Flash-Next removal *only* by per-plan approved path list after P3 verified and fallback guaranteed.
- [ ] P5 Orcarouter direct BF16 PLE MTP OFF then 31/31 BF16 overlay MTP2; benchmark.
- [ ] P6 Orcarouter ↔ 27B switch with gateway route/model alias checks.
- [ ] P7 qualification: operational guide, retention, CI, numerics/reproducibility, rollout and rollback.

## Required action output format

Each completed N-step must report: file+commit SHA, `PASS/FAIL/NOT_RUN` with source/CPU/CI/GPU scope, exact commands, side effects, relevant evidence path and next blocker. Update `CURRENT-STATE.md`, `CHANGELOG.md`, and tests ledger. If blocked, retain task unchecked and add precise reason.

## Current exclusions

Current **source-only development**: no operational GPU usage; no `./flash setup` or `./flash serve` run on DGX; no image pull/build/download; no Docker stop/rm; no deletion; no SGLang. User-requested source default now targets :8000; actual port occupancy and service deployment remain unverified and require separate preflight.
