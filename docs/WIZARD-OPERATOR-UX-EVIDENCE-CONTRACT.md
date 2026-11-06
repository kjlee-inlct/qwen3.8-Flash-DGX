# Model-centered Wizard UX and local evidence layout (2026-11-07)

## Verified operator evidence, not source CI

The operator-supplied `blazux-wizard.zip` establishes these **actual DGX** receipts:

- P3-B canonical `~/.local/state/blazux-wizard/p3/stage-b.json`: PASS, executed and live-verified; 27B returned to NVIDIA Flash-Next on :8000, finished 2026-11-06T22:31:24Z.
- Two post-B read-only diagnostics (`p1-diagnostics-20261106T231959Z-8de8d9f283d8.json`, `p1-diagnostics-20261106T232509Z-42cd3f5e323f.json`): PASS. Both doctor and inventory rc=3 arise from the original running Flash container's own name and port 8000; they are not evidence of a foreign port owner.
- Post-B Flash Verify `20261106T232627Z-82b4aebbdd13.json`: PASS, baseline PASS, extended PASS (completions/chat/tools/vision); executed with its own exact SHA approval.
- Post-B Flash Benchmark `20261106T233031Z-66af25d31aab.json`: PASS, executed with **a different** exact SHA approval. Exactly 3 sequential requests, max tokens 64, seed 1234, 192 completion tokens, measured mean 37.9527 tokens/sec, TTFT p50 1.384594 sec, TTFT p95 1.779602 sec, latency p50 1.724560 sec, latency p95 1.813754 sec.
- Model source `nvidia/Qwen3.8-Flash-Next-NVFP4`, pinned revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, served API `qwen3.8-flash-next`.

These receipts are **historical immutable** facts; there was no new DGX run, no P3-C execution and no automatic authorization from this source change. Small bounded 3-request end-to-end token throughput is not a concurrency/stress test.

## Operator UX contract

The stable machine interfaces `./wizard.sh model flash-next ...` and `./wizard.sh p1 ...` continue to work for existing scripts. Rollout aliases such as P1 are not user-facing identities. The main interactive flow is **Select model → All model actions → Verify OR Benchmark → review plan → type exact current SHA**.

- Direct integrated selection uses `guided --for-action verify` or `guided --for-action benchmark` to avoid the old duplicate numeric P1 action menu.
- The confirmation prompt repeats the *actual* current SHA: `Type exactly [<current plan_id>] (Enter cancels):`. One approval authorizes one action only. No auto-generated approvals, inferred permission, or unexpected start/stop.
- The plan summary names NVIDIA Flash-Next and the served model ID, shows the benchmark workload and blockers; full JSON remains available through read-only CLI plans.
- After execution, present Verify baseline/extended and per-feature outcomes, or benchmark TTFT/latency p50/p95, mean throughput, token count, and per-request metrics; include the evidence path.
- The backend still creates a fresh preflight and checks the exact SHA immediately before performing the approved action. No change to ONE_ACTIVE_MODEL_ONLY, port 8000, vLLM 0.32, no SGLang.

## Append-only evidence paths

New P1 Flash execution JSON uses:

```text
<repo>/reports/
  models/
    qwen3.8-flash-next/
      <UTC>-<unique>.json
  # Future approved design only:
  # models/qwen3.8-27b/...
  # models/<served-model-id>/...
  # transitions/<source>--to--<target>/...
  # diagnostics/<model-id>/...
```

The repository's `.gitignore` excludes `/reports/` from Git. Each new P1 receipt uses an exclusive new filename and file mode 0600; parent evidence directory is created with mode 0700. The model-specific default can be overridden with the historical CLI `--evidence-dir` flag. Do not commit local receipts and do not mistake Git-ignored evidence for a synchronized backup.

**Backward compatibility is mandatory:** Existing `~/.local/state/blazux-wizard/p1/*.json` receipts must never be renamed, rewritten, copied over or deleted. The P3 final-27B prerequisite gate reads both the project-local served-model folder and the original P1 folder, validates private-file constraints, and selects latest action attempts by **UTC finished timestamp**, not pathname sorting. If a newer Verify/Benchmark failed, an older PASS must not authorize stage C. The P3 diagnostic/state records continue to live at their original paths for now, including stage-A/B immutable state, locks and journal. Altering those paths requires a separately reviewed migration of all state-machine readers, not an ad hoc copy.

## Remaining global evidence/UX audit

| Component | Current legacy location | Status |
| --- | --- | --- |
| Flash-Next Verify/Benchmark | `~/.local/state/blazux-wizard/p1/` | New writes project-local by model; old records dual-read |
| 27B download/trial/benchmark | `~/.local/state/blazux-wizard/p2/` | No migration in this change; preserve lock files and trial evidence |
| Flash ↔ 27B switching/state | `~/.local/state/blazux-wizard/p3/` | No migration: safety-critical state, lock and journal readers |
| P1 temporary reports | `~/blazux-p1-reports/` | Legacy reports retained; separate migration needed |
| P3 operator reports | `~/blazux-p3-reports/` | Legacy reports retained; separate migration needed |

Future model onboarding should use a model manifest's stable served ID and human label, not a phase number or hardcoded P1/P2/P3 folder. Migrate a subsystem only after inventorying its readers/writers, read-only compatibility tests, append-only semantics, startup/service recovery, and verified actual DGX deployment. Do not move P3 state files or active lock files merely to satisfy a folder naming preference.

## Verification

GitHub CI exercises exact approval input, cancellations, a single integrated action selection, benchmark metrics display, new project-local evidence path, and old/new P1 P3-gate compatibility. This source-only test evidence does not substitute for a separate actual DGX UX acceptance run. Draft PR #1 remains open/unmerged unless separately approved.
