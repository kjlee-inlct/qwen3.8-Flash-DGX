> **Source/CPU acceptance for new pre-A wrapper, 2026-11-06:** tested code SHA `75d22ce4303736ee84563a0f388a978379e4f228`, [push CI 42173798547](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173798547) and [PR CI 42173805888](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) **SUCCESS — 435/435 CPU tests, 19 groups**. This includes exact original P1 Wizard identity receipt contract (`identity.health=PASS`, `identity.models` contains the served ID), not a fictitious `identity.status`. Wrapper actual DGX execution **NOT_RUN**; CI never inspected private operator report bytes.

## 2026-11-06 — P1 pre-P3-A evidence reconciliation: tracked wrapper after user workflow correction

**Mandatory D-016 reinforced:** agent writes and pushes the temporary operator script, CPU fake-backend tests and handoff first. DGX operator uses `git pull --ff-only origin feature/recipe-wizard-handoff` and **one tracked command**; do not paste ad hoc multi-step Python/curl snippets or edit the DGX workspace to add temporary logic. Script NEVER performs `git pull`, Docker/GPU/HTTP inference, lifecycle actions, stage A execution or cleanup.

**New temporary wrapper:** `scripts/temporary/p1-pre-a-readiness.sh` (Python module `p1_pre_a_readiness.py`). It examines the latest **already saved** `~/blazux-p1-reports/20*/result.json` inspect-only report and the older P1 acceptance report `20261105T113110Z-fdc179fa/result.json`; validates private P1 Wizard verify/benchmark receipts `20261105T113119Z-eca4ec724ede.json` and `20261105T113125Z-586b2b46d93e.json` with actual numerical TTFT/latency/tokens/sec and each sample; then performs **one fresh read-only** `./wizard.sh service manager status --json` plus `git` branch/HEAD/clean checks. It parses complete **both** raw doctor and inventory-plan JSON for both inspection dates. rc=3 is recognized only when expected `qwen38-flash` is Up, exact same immutable image and published :8000, `status=PASS`, `errors=[]`, and launch-preview collision facts match. No P1 inference, no service mutation, no automatic P3-A plan or approval.

**DGX use (after tracked script commit/CI):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p1-pre-a-readiness.sh
```

Optional `--report <path>`, `--historical-report <path>` to select exact reports if default source differs; use existing verified local records, never fabricate raw P1 evidence. Report writes `~/blazux-p1-reports/p1-pre-a-<UTC>-<id>.json` with 0600 permissions and prints a **small JSON summary**. `PRE_A_P1_REVIEW_READY` means historical initial P1 evidence is complete **for pre-A review only**, not approval for downtime or stage A, full production acceptance, independent GPU exclusivity, or post-B rebenchmark. `BLOCKED` includes explicit issues. The P3-C post-B P1 verify/rebenchmark and historical collision disposition remain separately required by D-034. Do not infer that an old `inspect_only` `actions.verify/benchmark.status=BLOCKED` erased the genuine November 5 P1 PASS receipts.

---

## First one-shot Qwen3.8-27B GPU trial (separate operator approval)

Actual DGX CPU-only module/registry audit PASS 9/9. An EXPERIMENTAL GPU trial is available through `./scripts/serve_27b.sh --trial-plan` (read-only) and `--trial-execute --approve-plan FULL_SHA64 --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME` (operator-initiated real service interruption). This is a **single-GPU stop→trial→restore** experiment, *not* production model switching. It keeps `qwen38-flash` intact and tries to restore it automatically with exact served ID verification even if 27B fails. No guarantee on host/Docker fault, manual inspection on `RECOVERY_FAILED`. See `docs/P2-27B-WIZARD-OPERATIONS.md`.

---

## 2026-11-06 — Corrected ModelOpt quantization-name registration proof

Initial real DGX restricted CPU probe imported Qwen3.5 and ModelOpt modules/classes successfully but incorrectly marked `modelopt_mixed` unavailable due to calling `ModelOptMixedPrecisionConfig.get_name()` as a classmethod; vLLM implements `get_name(self)`. The revised probe uses `vllm.model_executor.layers.quantization.get_quantization_config("modelopt_mixed")` and compares the returned class identity to the imported config type. No config/model instance is created. Run again after fast-forward; the old failed check does **not** disqualify 27B. All results remain CPU-only, `launch_authorized=false`; GPU transition requires scoped approval.

---

## P2 CPU-only vLLM Qwen3.5 / ModelOpt Python loader import probe

`./scripts/temporary/p2-27b-loader-import-audit.sh --plan` (default; only Docker image inspect) previews exact local image ID with no container. `--execute-cpu-only` explicitly opts into **one disposable read-only CPU runc container** with network disabled, no GPU, no HF model cache or host port, 2 GiB RAM limit, 2 CPUs and a Python module/class/name import check. The result reports individual checks and retains `runtime_qualified=false`, `gpu_verified=false`, `launch_authorized=false` even when all imports pass. An import failure may reflect the restricted sandbox rather than real GPU model incompatibility. **Do not treat this as approval** for 27B startup or switching. Implementation `scripts/manager/p2_27b_loader_import_audit.py`; unit tests `tests/test_p2_27b_loader_import_audit_cpu.py`.

---

## P2 static image source probe — no GPU or API mutation

For downloaded NVIDIA 27B, the installed-image source check is available as `./scripts/temporary/p2-27b-image-audit.sh --plan` (Docker image-inspect only), or operator-selected `./scripts/temporary/p2-27b-image-audit.sh --execute-cpu-only` (creates and removes a restricted runc container with network disabled, no GPU and no host port). It AST-parses the installed vLLM 0.32 image's model registry and ModelOpt code. `PASS`-like static output is **not** a model-load, GPU, API or recovery acceptance; do not use it as a model-lifecycle approval. See `docs/P2-27B-WIZARD-OPERATIONS.md`.

---

# Temporary operator scripts — maintained GitHub workflow

Temporary scripts here are **tracked, tested, and short-lived**. They replace large
pasted terminal command blocks for DGX Spark operations. This directory is **not**
a place for production services, permanent recipes, datasets, caches or GPU logs.

## Mandatory process (D-016)

1. Inspect the exact current GitHub branch/HEAD, existing DGX state and operator
   restrictions. Prepare one coherent temporary wrapper for a specific session or
   milestone. Use descriptive names, not `p1.py` or `test.sh`.
2. Commit wrapper, CPU fake-subprocess tests and docs to
   `feature/recipe-wizard-handoff`; inspect GitHub Actions, PR and HEAD. Never
   mark CPU CI as DGX GPU/API/BENCH success.
3. Operator **finishes existing running setup/serve/wait/test first**. Only then,
   with a clean worktree, operator runs `git fetch` / `git pull --ff-only` on
   the intended branch, then invokes **one** wrapper from this directory.
   The wrapper must **not** perform `git pull` or reset/clean the repo itself.
4. One wrapper orchestrates **(1) inspection/preflight → (2) individual
   approved Wizard actions → (3) evidence gathering/summary**. Default dry-run
   or interactive review. No silent approval; each live API/GPU/action needs a
   fresh, exact action-specific plan ID and a second Wizard preflight.
5. Write timestamped, unique, permission-restricted logs and JSON evidence
   **outside Git and HF cache**; print the folder/file path. Don't store secrets,
   copies of model weights, confidential prompts or access tokens. Don't upload
   host-only logs to GitHub automatically. User sends reviewed results back.
6. Record command, Git HEAD, check results, source/runtime distinction, blockers
   and evidence path into handoff; run CPU-only CI, commit PR review. Keep the
   temporary wrapper until the handoff has sufficient reproducible evidence.
   Retire/archive it by a separate documented, reviewed commit (no automatic
   deletion). Preserve permanent recipes, tests, logs and validated runbooks.

**Hard exclusions:** `git reset --hard`, `git clean -fd`, `docker rm`,
container stop/restart, `./flash setup`, downloading the checkpoint, deleting
HF cache, proxy/gateway cutover, model switching and any other destructive work
must never be automatically hidden inside a temporary wrapper. A temporary
script must call the existing Wizard for actual runtime operations and reuse
its explicit approval/rollback guards, not bypass them.

## Current temporary script

- **File:** `p1-post-download.sh` → `p1_post_download.py`
- **Purpose:** single-invocation Flash-Next post-download P1 inspection, bounded
  verified text/tool/vision probes and sequential 3-request SSE benchmark,
  ending in a consolidated JSON report.
- **Use:** AFTER the original operator-owned `./flash setup default` and queued
  `./flash serve default`, `./flash wait`, `./flash test` all exit.
- **Invoke (safe read-only):**
  ```bash
  git fetch origin
  git switch feature/recipe-wizard-handoff
  git pull --ff-only origin feature/recipe-wizard-handoff
  bash scripts/temporary/p1-post-download.sh --inspect-only
  ```
- **Invoke (single interactive wrapper for phases 1–3):**
  ```bash
  bash scripts/temporary/p1-post-download.sh
  ```
  When current plan is READY, the script requests the **full current
  `plan_id` separately** for verify and benchmark. Any missing/incorrect
  approval skips that action. Benchmark requires verify PASS **in that run**.
  Non-TTY defaults to inspection-only behavior unless both exact plans have
  been separately passed as `--approve-verify` and `--approve-benchmark`.
- **Output:** `~/blazux-p1-reports/<UTC>-<id>/result.json` (permissions 0600,
  directory 0700), includes all check exit codes, guarded plans and result
  references to the Wizard's own evidence files at
  `~/.local/state/blazux-wizard/p1/`.
- **Status:** SOURCE/CPU CI verified at `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b` (2/2 jobs SUCCESS, 131/131 CPU tests/job); **actual DGX runtime checks still NOT_RUN**. BLOCKED and PARTIAL are not GPU PASS.

## Troubleshooting: completed download but Wizard reports INCOMPLETE

The original `./flash` resolves `refs/main`, then `refs/master`, then the most
recent non-Hybrid snapshot; the P1 Wizard currently requires `refs/main`
and checks indexed shards, quantization metadata, Hybrid state and leftover
`*.incomplete` blob names. A completed transfer is **not** a P1 runtime PASS.

The temporary wrapper now includes a **read-only** `cache_diagnosis` result
with actual `refs/main` and `refs/master`, up to 16 snapshot revisions,
missing indexed shard/config names, Hybrid `.prepared` presence, and the
strict Wizard asset audit. It does not download, repair or delete anything.
After `git pull` run `bash scripts/temporary/p1-post-download.sh --inspect-only`
and share the `cache_diagnosis` part of its `result.json`, plus
`checks.models.stdout` (inspect locally for anything sensitive).
A successful `/health` or `/v1/models` HTTP request alone does not prove
which model is served. Do not rerun `setup`, reprepare Hybrid or change
a running container until the mismatch is diagnosed.

## 2026-11-05 — Corrected index-size check / read-only file-probe

An operator confirmed the download finished, yet the P1 Wizard reported
`model.safetensors.index.json` and `tokenizer.json` failures in the source
snapshot and `tokenizer.json` in the Hybrid snapshot. The official NVIDIA
index is ~31.3 MB; a strict 16 MiB cap in our new P1 auditor was independently
wrong and is fixed to 64 MiB at `66c6c44`. **The earlier two filename
failures are from an even earlier file-existence/symlink/size check, so the
index-size fix alone cannot be claimed as the root-cause solution.**

The read-only `cache_diagnosis` now includes `source_metadata` and
`hybrid_metadata` for the two affected files, distinguishing `MISSING`,
`DANGLING_SYMLINK`, `TARGET_OUTSIDE_REPOSITORY`, `ZERO_BYTES` and
`PRESENT_NONEMPTY`, and reports size plus old/current index cap comparisons.
The wrapper console summary includes `api_model_ids`, extracted from
`/v1/models` rather than just treating curl returncode zero as model proof.
All changes are source/CPU only; CI 2/2 PASS, 145 tests/job.

**Action:** `bash scripts/temporary/p1-post-download.sh --inspect-only`
after Git Pull. No automatic repair/download, Hybrid rewrite or service changes.

## D-017: Blazux metadata links and opt-in automatic GPU testing

Operator's actual report found source `model.safetensors.index.json` and
`tokenizer.json`, plus Hybrid `tokenizer.json`, resolve to existing symlink
targets outside their model-repository directory. P1's new strict checker
previously marked these missing, but upstream Blazux follows file symlinks.
We now accept these **two nonempty metadata link types only**; all indexed
weight shards still require in-repo targets and valid bounded JSON indexing.
`cache_diagnosis.*_metadata.*.p1_metadata_link_compatible` explains what
was accepted, without exposing target paths or copying files.

**GPU permission (operator granted 2026-11-05):** to use the currently
responding Flash-Next API for bounded, non-disruptive tests **without typing
plan IDs at prompts**, invoke after Git Pull:

```bash
bash scripts/temporary/p1-post-download.sh --auto-gpu
```

This flag only permits the existing Wizard's `verify` and `benchmark`
actions after the same current-pinned-plan checks, with fresh action-specific
plan IDs passed internally. P1 verify (text/tool/vision) must PASS before
a short SSE benchmark (default 3 requests, 64 max tokens, seed 1234).
It does **not** authorize `prepare`, `start`, `serve`, `stop`, `setup`,
download, Docker replacement, Hybrid repair, model deletion, switching or
gateway changes. No active GPU run is claimed until the operator supplies
real evidence. `--inspect-only` remains fully non-executing.


**CI verification:** `0063b0e004902408f980c155076c098d49d4569e`,
push and PR actions 2/2 SUCCESS with 155 unique CPU tests each. The
source/Hybrid external metadata compatibility is protected by regressions;
only the DGX operator's next run can establish actual model inference/benchmark.

## D-018 — Baseline acceptance vs extended feature diagnostics

The first **actual** operator `--auto-gpu` call after checkpoint/Hybrid
readiness returned `verify=FAIL`, `benchmark=BLOCKED`, but the prior
runner silently dropped the Wizard error JSON whenever the Wizard returned
nonzero (including rc=2 for FAIL/PARTIAL, even with evidence saved).
The saved raw report at
`~/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` is still
the best source for the *original* failure reason.

The corrected Wizard first probes native Blazux-shaped `/v1/completions`
and ordinary `/v1/chat/completions` (with `/no_think`).
Tool forcing and synthetic vision are **additional** checks. Any extra
failure is separately reported as `extended_status=FAIL`, with overall
`verify=PARTIAL`, while `baseline_status=PASS` enables the short
benchmark. A baseline failure still blocks benchmark. The wrapper now
prints each probe's status, sanitized error type/HTTP status and the
Wizard evidence path even when Wizard exits nonzero.

Commit `391a2844f4c8549e282eae3e266806c89801ad1a`: GitHub
CI 2/2 SUCCESS, 173/173 CPU tests per job. Real DGX result for the
new version remains unverified until the operator reruns the bundle.
