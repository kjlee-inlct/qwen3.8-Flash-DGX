## 2026-11-07 — SOURCE CI VERIFIED, NEXT DGX ACTION STILL READ-ONLY

`67ff9cc2e4ece0c89c911513673f7d5d55c98fa4` passed GitHub Actions [run 42310408411](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42310408411), **501/501 CPU PASS in 23 groups**. Draft PR #1 reviewed and not merged. New read-only `bash scripts/temporary/p1-post-b-audit.sh` has **not yet run on real DGX**; P1 POST-B Verify/Benchmark and P3-C are not authorized. After clean fast-forward pull, this one script is the next operator step; no GPU inference, service mutations or auto approvals.

---

## 2026-11-07 — POST-B P1 operator audit (read-only, D-016, P3-A/B already ACTUAL PASS)

**Observed upstream DGX outcome:** canonical `stage-b.json` PASS and `P3_B_PASS_FLASH_NEXT_ACTIVE`; original Flash-Next `qwen3.8-flash-next` restored to :8000. User's post-B P1 inspect-only `20261106T224010Z-d2095867/result.json` PASS/Verify+Benchmark plans READY; it did **not** execute Verify or Benchmark. Old B wrapper evidence filename is incorrectly `p3-a-operator-20261106T223124Z-14861d75.json` and must be preserved; source naming and approval field fixes affect only newly generated reports.

**After latest CPU CI SUCCESS and clean DGX fast-forward pull**:
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p1-post-b-audit.sh
```

The only operator inspection command is the final tracked `bash scripts/temporary/p1-post-b-audit.sh`; it exposes **no --execute/auto-gpu/approval options**. It checks immutable P3-B receipt, current Flash service/API on :8000 and original image, branch/clean/plan readiness, cached original/Hybrid checkpoint revision, and **both RAW JSON** launch preflight outputs for exactly own Flash container/port collision when rc=3. Calls existing `p1_post_download.session(inspect_only=True)`; no completion/chat/vision/tool generation, benchmark or Docker lifecycle mutation. Creates unique private 0600 `~/.local/state/blazux-wizard/p3/p1-diagnostics-YYYYMMDDTHHMMSSZ-<nonce>.json` on every attempt; never overwrites `p1-diagnostics.json` or old receipts.

Expected clean preflight: `status=PASS`, `issues=[]`, `doctor_exit_code=3`, `inventory_plan_exit_code=3`, `post_b_verify=NOT_RUN`, `post_b_benchmark=NOT_RUN`, `p3_c_authorized=false`, `executed=false`. Fail or BLOCKED: stop and send compact JSON with `evidence_file`, no retest/mutation. PASS validates diagnostics and read-only readiness **only**. Actual P1 Verify and numeric Benchmark need new individually approved action-specific SHA plans; P3-C additionally needs independently scoped explicit downtime consent and all source/revision/image/timestamp/numeric evidence gate PASS. PR #1 stays Draft.

---

## 2026-11-06 — Actual B inspection READY, new stage-B-specific exact approvals (SOURCE ONLY)

User ran the tracked read-only B inspector on actual DGX after successful P3-A: `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`; live `qwen3.8-27b`, original Flash container `90f39...` and running 27B `6d9ede...` preserved. Receipt `~/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. A shared Docker runtime IMAGE digest for these models is expected; only exact model ID/containers and pinned resources prove which runs.

**Critical correction before any B execute:** P3 canonical core used the A/C `I_ACCEPT_FLASH_NEXT_DOWNTIME` even for B, where the ACTIVE 27B is stopped. The correct **new B-only** manual strings are now `I_ACCEPT_27B_DOWNTIME` and independent `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`, plus a newly generated full 64-character `stage-b` plan SHA. Existing A/C approval strings and actions unchanged. This change is source/CPU only; B service interruption has NOT been authorized.

Tracked D-016 `scripts/temporary/p3-stage-b-operator.sh` wraps canonical stage-B with default safe `--plan` (no service changes), `--execute` (actual live 27B shutdown and original preserved Flash restart) protected by exact **three freshly typed operator inputs**, an independent real stage-B user decision, fresh live Manifest/API and original A receipt/27B+Flash image and container identity, minimum 120s input window, a read-only replan after inputs and core's final preflight. Exact actual SHA and both literal ACKs printed beside prompts. After B, wrapper rechecks `qwen3.8-flash-next` API, writes private 0600 `~/blazux-p3-reports/p3-b-operator-*.json` and stops; NO automatic P1 or stage C. If core returns `RECOVERY_FAILED` or live API fails, stop and inspect before any further action. Host failures can defeat rollback.

**NO B APPROVAL IN USER LOG:** Do not ask operator to invoke `--execute` until they explicitly authorize 27B downtime and transition 27B→Flash. To review source safely after GitHub CI: `bash scripts/temporary/p3-stage-b-operator.sh --plan` (read-only) after `git pull --ff-only origin feature/recipe-wizard-handoff`. B inspector earlier plan SHA `7af40f...` expired 17:50 KST and may not be reused. Do not modify DGX workspace with ad hoc scripts, restart/stop 27B automatically, clean caches or merge Draft PR. After separate approval the same D-016 wrapper may use `--execute`; no new source required.

**CPU source evidence:** [PR GitHub Actions 42190159738](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) SUCCESS 489/489 tests across 22 groups on source `59046c4e17a5094f2c80a84025a763c2a767edcb`. DGX has NOT run this updated wrapper and B is NOT_RUN.

---

## 2026-11-06 — P3-A real DGX PASS; P3-B preparation is strictly READ-ONLY

Actual DGX operator `scripts/temporary/p3-stage-a-operator.sh --execute` at `20261106T074306Z` succeeded: `P3_A_PASS_27B_ACTIVE`, `issues=[]`, canonical Wizard stage-A `status=PASS`, `executed=true`, `live_verified=true`, independent API/Manifest `LIVE_SERVICE_VERIFIED` with `observed_model=27b`. Real receipts: `~/.local/state/blazux-wizard/p3/stage-a.json` and `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. The active target is **27B**, not Flash; keep running. P3-B has **not** been approved, and P3-C and post-B P1 are pending.

New D-016 tracked inspector: `scripts/temporary/p3-stage-b-inspect.sh` / `p3_stage_b_inspect.py`. It has **NO `--execute` option** and only invokes `./wizard.sh service manager status --json` plus `./wizard.sh switch flash-next-27b stage-b --plan --json`, both read-only. It compares the local immutable stage-A success receipt, observed active 27B ID and image, original Flash ID/image, 27B target ID, immutable P2 receipt and the 10-minute fresh B planning record; writes a 0600 local `~/blazux-p3-reports/p3-b-inspect-*.json`, reporting `READY_FOR_SEPARATE_P3_B_APPROVAL` or `BLOCKED`. READY proves B preflight, not permission for B interruption, rollback fault resilience, or P1 GPU performance after B.

**DGX after GitHub source/CI:**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p3-stage-b-inspect.sh
```
No background work, no automatic transition, no raw Docker or ad hoc Python. Report concise JSON `status`, `issues`, observed ID, original Flash container and P2 hash. If a plan expires, re-run read-only check when appropriate; do not reuse its plan SHA for any approved live action. Stage B if approved later will get a NEW stage-specific plan and explicitly typed downtime ACK. Existing P3-A triple-ACK is not B consent.

---

## 2026-11-06 — Display actual approval literals at EVERY P3-A prompt, block stale ten-minute IDs

Operator real DGX stage-A attempt after `git pull`: all three requested values typed **correctly**, but `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT` with `executed=false`. No live transition. Old plan SHA `94b4dedae21eb72b12443029257931e123e33404c32898d9ae2bad52954c064f` expired at **16:30:00 KST**; evidence `~/blazux-p3-reports/p3-a-operator-20261106T073049Z-4dc8be1b.json` written at 16:30:49 KST. This is a plan expiry or fresh preflight mismatch, **not an incorrect operator-typed string**.

**New D-016 wrapper behavior:** `bash scripts/temporary/p3-stage-a-operator.sh --execute` prints the **current live SHA** directly in step 1/3; prints `I_ACCEPT_FLASH_NEXT_DOWNTIME` beside step 2/3; prints `I_SEPARATELY_AUTHORIZE_P3_ENTRY` beside step 3/3; shows plan expires `YYYY-MM-DD HH:MM:SS KST` and seconds remaining. The operator still has to type each independently; no implicit consent. If less than 120 seconds left at initial execution prompt, return `BLOCKED/P3_A_NOT_ENOUGH_TIME_FOR_MANUAL_CONFIRMATIONS` with no input and no stop. After all typed strings, call read-only Wizard plan again and refuse a new/different/expired SHA before executing. Canonical Wizard final preflight remains mandatory. If Wizard returns `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT`, `executed=false`, operator report now `BLOCKED`, not ambiguous recovery warning. This does not auto-retry, auto-replace plan, start 27B or chain B/C.

**GitHub testing:** [push CI 42181851452](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181851452), [PR CI 42181858236](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236), **459/459 CPU PASS**, source `fb34ce0ce985824cecd9c63159bf6f1eed408279`. Real DGX fresh plan rerun NOT_RUN. Original Flash/27B images, containers, model cache and :8000 unchanged by GitHub updates.

---

## 2026-11-06 — P3-A conditional operator approval now eligible; one GitHub-tracked exact-gated wrapper

Operator provided **actual** tracked P1 pre-A receipt `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json` with `PRE_A_P1_REVIEW_READY`, `issues=[]`, both historical/current `doctor/inventory-plan` rc3 confirmed as own active Flash collisions, P1 Verify PASS and 3-sample numerical benchmark PASS. This closes the earlier pre-A P1 diagnostic gaps. The operator's previous "**if no P1 work remains, approve 27B transition**" is eligible as **P3-A only**, not B/C and not an automatic service stop. Local pre-A receipt `p3_a_execution_authorized=false` is expected for read-only evidence.

**D-016 tracked operator script:** `scripts/temporary/p3-stage-a-operator.sh` backed by `p3_stage_a_operator.py` (tested with fake-DGX). Default **read-only** plan `bash scripts/temporary/p3-stage-a-operator.sh --plan`; actual explicitly chosen service interruption `bash scripts/temporary/p3-stage-a-operator.sh --execute` requires a real TTY and three independent prompt responses: **full current stage-A `plan_id`** printed from real DGX, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, then `I_SEPARATELY_AUTHORIZE_P3_ENTRY`. No automatic approval, no plan ID supplied by assistant; 10-min plan expiry rechecked by Wizard. The wrapper verifies private pre-A PASS receipt freshness, live Flash API/image and P2 hash/target image/source container, branches and clean worktree before prompting. If any issue => BLOCKED, no Docker mutation. It invokes only canonical Wizard `switch flash-next-27b stage-a --execute` *after* all three confirmations. Successful A **leaves 27B active** and independently re-verifies served ID and image; no B/C. Failure displays recovery result and stops without retry; host/Docker crash may defeat rollback. Read-only/report mode only writes private `~/blazux-p3-reports/p3-a-operator-*.json` (0600), never Git/cache.

**DGX operator after GitHub push + CI:**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p3-stage-a-operator.sh --execute
```

Use `--plan` instead of `--execute` for read-only preview. This is a real first P3-A service interruption: :8000 becomes temporarily unavailable and return to Flash on failure is best effort. The model target must be verified via fresh API `qwen3.8-27b`, never inferred from same Docker image. A PASS in Python/CPU CI does **not** certify arbitrary host-GPU-process exclusivity or production recoverability. The operator must observe the outputs and stop on any unexpected GPU user, Docker error or unavailable rollback. Original Flash model checkpoint and container remain protected.

---

## 2026-11-06 — Correct persisted P1 cache diagnosis schema in pre-A wrapper

Real operator `bash scripts/temporary/p1-pre-a-readiness.sh` at prior HEAD `3a594193` reported P1 Verify PASS, benchmark PASS with real 3-sample numerical metrics, and historic/current expected Flash collision on :8000. It nevertheless returned `P1_ASSET_AUDIT_NOT_READY` and `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. **Source bug:** the stored `p1-post-download.sh --inspect-only` `result.json` contains `checks.cache_diagnosis.stdout` (full JSON as captured command output), **not** the ephemeral console-summary field `cache_diagnosis`. `p1-pre-a-readiness.py` read the latter and treated the absent revision as actual drift.

Fixed to use canonical `cache_diagnosis_summary(current["checks"])`; missing or corrupt diagnosis now returns `P1_CURRENT_CHECKPOINT_REVISION_UNAVAILABLE` + asset audit not ready, **without inventing drift**. Genuine mismatch of sourced snapshot revision vs P1 Wizard receipt still blocks. Real-schema CPU tests plus missing/corrupt and true-drift cases: [push CI 42176219970](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176219970) / [PR CI 42176224898](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898) **439/439 PASS** on code commit `9adc9ab282a91c02e959dcb5c62f98527b556391`. Actual DGX validation still needed. D-016 remains unchanged: GitHub commit/CI first, operator pulls `feature/recipe-wizard-handoff`, then runs **one** tracked wrapper; no pasted Python and no automatic model switching.

---

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
