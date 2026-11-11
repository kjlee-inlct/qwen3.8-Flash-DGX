## 2026-11-07 — REAL DGX canonical Native Tools migration 1st attempt FAIL_RESTORED; BENCHMARK diagnostic and reconciliation fix

**Most recent actual DGX operator output:** TTY-approved `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --execute` consumed fresh plan `01702fa1b0901a0dce7517ccbaee133fc253058a1c07abe63bc00c42bec52a15`. JSON returned `status=FAIL_RESTORED`, `executed=true`, `native_tools_pass=true`, `benchmark_pass=false`, `benchmark_promoted=false`, `backup_container_deleted=false`, `original_restored=true`, `issues=["MIGRATION_ERROR_NEW_CANONICAL_BENCHMARK_NOT_QUALIFIED"]`. **Actual service independently checked AFTER this failure: NOT YET provided.** This is a real DGX Native Tools pass followed by an unsuccessful new 3-sample performance acceptance test and attempted original restore, **NOT a successful canonical migration**. Do not delete containers/cache/benchmark receipts or re-run the used SHA.

**Root-cause evidence boundary:** In the initial migration code, `p2_27b_benchmark.measure()` returned a structured measurement dictionary, then the caller rejected its acceptance criteria. The caller discarded `samples` and `metrics` before writing the immutable failure report. Therefore the actual failed sample or reason **cannot be reconstructed from the provided output**; not evidence of GPU/model inference failure. The benchmark also used legacy `/no_think` prompt text rather than explicit `chat_template_kwargs={"enable_thinking":False}` which the **successful Native Tools probe uses**. This is a plausible cause but NOT established. Avoid falsely claiming actual latency/TPS.

**Source remediation:** `scripts/manager/p2_27b_benchmark.py` now accepts opt-in pinned nonthinking kwargs while preserving historical defaults and captures per-sample `usage_reported`, `content_observed`, `reasoning_observed`, `stream_finish_reason`, exact failure reason codes, TTFT, tokens and sampled metrics (no generated text). `scripts/manager/p2_27b_recipe_migration.py` opts in to explicit `enable_thinking=false` and writes private immutable `benchmark-observed-<NEW SHA>.json` plus a `BENCHMARK_MEASURED` journal event **before** checking pass/rolling back. Result now includes `benchmark_diagnostics` even on `FAIL_RESTORED`. A `finish_reason=length` at the intended 64-token benchmark cap is recorded, **not automatically deemed a failure**. Do not loosen actual benchmark eligibility for missing usage, TTFT, SSE completion or generated tokens.

**Safe subsequent run protection:** Existing `attempt-<oldSHA>.json` remains immutable; source does NOT silently bypass it. Added `--audit-failure` read-only verification of exact one prior failed result, seven-event hash chain ending RESTORED, original P3 container ID running+API ready, stopped/owned failed candidate, Flash/variant stopped, original ordinary journal clean and no promoted benchmark. If and ONLY IF audit returns `PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY` / issues empty, operator may separately run interactive `--reconcile` and type exact prior used SHA plus `I_REVIEWED_27B_BENCHMARK_FAILURE_AND_RESTORED_SERVICE`; this writes **only a private reconciliation receipt**, never touches Docker. Then `--plan` issues **new distinct SHA** bound to prior reconciliation (also checks fresh current identity, recipe, cache and P3 lineage), and `--execute` STILL requires new TTY SHA, downtime and backup-deletion consent for any second attempt. Previously failed new container is **preserved**; new failed-container name is unique per NEW plan. Two unverified failures or state/evidence drift remain BLOCKED. **No next DGX attempt has been observed.**

**DGX Pull/read-only instructions (NO service mutation):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
docker ps -a --filter name=qwen38-27b --format 'table {{.Names}}\t{{.Status}}'
bash scripts/temporary/p2-27b-native-recipe-migrate.sh --audit-failure
```
If audit is BLOCKED, inspect actual Docker and private `~/.local/state/blazux-wizard/27b-recipe-migration/` rather than clearing markers. Only after reviewing evidence can operator choose interactive `--reconcile`, then `--plan`, then separately authorized live `--execute`. Any new migration result must be grounded in real DGX output; GitHub source-only CI is not DGX acceptance. Preserve original 27B model, HF cache, vLLM image, original P3 A/B/C and 14-event ordinary journal. Main Wizard production flag remains OFF; Draft PR #1 not merged.

---

# P2-FINAL — Canonical 27B Native Tools recipe migration

## Decision (2026-11-07)

User explicitly chose the **simpler in-place 27B recipe upgrade**, **not** a permanent two-variant service switch. The previous DGX one-shot experiment was successful: structured `tool_calls`, tool-result continuation, streamed calls, preserved original restoration = `PASS_RESTORED`; stopped `qwen38-27b-native-tools-v1` and its private, chained nine events remain. The user further instructed: **after successful upgrade run a fresh benchmark, replace the active benchmark result, and delete the backed-up OLD Docker container**.

Use a **separate pinned runtime recipe** `recipes/qwen38-27b.runtime.json` registered by desired `runtimes/service-policy.json`. The existing schema-incomplete `recipes/qwen38-27b.candidate.yaml` and `recipes/qwen38-27b-native-tools-v1.candidate.yaml` are HISTORICAL candidate contracts and must not be mistaken for executable production recipes.

Upgrade objective:
1. Exact-read-only audit of original `qwen38-27b` on :8000, stopped successful 27B Native Tools V1 trial, exact vLLM image and pinned NVIDIA Jinja, original P3 lineage, ordinary journal, GPU ownership and HF mount.
2. **Fresh independent TTY downtime and container-deletion approvals.** This is a new request, not a reuse of the already-consumed one-shot SHA.
3. Stop only `qwen38-27b` → rename it to `qwen38-27b-pre-native-<old-container-id-prefix>` (rollback backup) → wait port/GPU release.
4. Create a **new** canonical `qwen38-27b` with same `sha256:9479fc92...` vLLM 0.32 image, same pinned NVIDIA NVFP4 revision `482ca0f...`, same 8000 port and readonly HF cache, plus `--chat-template` pinned NVIDIA Jinja, `--enable-auto-tool-choice`, `--tool-call-parser qwen3_coder`, `--reasoning-parser qwen3`.
5. Verify new Docker provenance, startup, localhost API model ID, ordinary chat, structured tool `get_probe_token` call+synthetic response continuation, SSE tool call, single GPU model.
6. **New** reproducible bounded 27B benchmark, three sequential SSE requests, 64-token limit, seed 1234, TTFT/latency/E2E throughput and client decode proxy. Requires `benchmark.status=PASS` and all individual samples successful with positive measured E2E throughput.
7. Save immutable private `benchmark-<new-sha>.json`, atomically replace **new active canonical latest benchmark pointer** `~/.local/state/blazux-wizard/27b-recipe-migration/latest-27b-benchmark.json`; save immutable migration commit proof. **Old benchmark receipts remain immutable** (no rewriting of old P2/P3 evidence).
8. **Only after all PASS and identity recheck:** `docker rm` the exact verified, stopped backup container. Never `docker rmi`, prune images, alter caches or delete stopped `qwen38-27b-native-tools-v1`. If deletion fails, report `COMMITTED_CLEANUP_PENDING`, do **not** undo an already promoted new active benchmark automatically.
9. On precommit errors, stop and rename only the migration-owned new container to an identifiable failed name, restore the backup's canonical name, restart and check original API. A host failure, OOM, SIGKILL or Docker outage may defeat rollback. Never blindly retry a consumed SHA. The private `attempt-<sha>.json` and event chain block another attempt until manual reconciliation.

**Important: original P3 A/B/C receipts reference the old Docker container ID.** They remain preserved historical evidence and **are not rewritten**. The existing ordinary `operational_switch` source currently checks those exact old IDs; its next Flash-Next ↔ 27B switch should **fail closed** until explicitly migrated to post-recipe lineage. The existing Wizard live service status identifies the same canonical container name and model ID but does not check Tool Calling flags; use the independent new `--status` read-only audit to verify actual new runtime and benchmark identity.

## DGX operator instructions (pull before execution; no Fake-DGX CI dependency)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
git log -1 --oneline
bash -n scripts/temporary/p2-27b-native-recipe-migrate.sh

# ALWAYS first: read-only, no service stop/start
bash scripts/temporary/p2-27b-native-recipe-migrate.sh --plan
```

Require `status=READY_FOR_CANONICAL_27B_NATIVE_RECIPE_MIGRATION`, `issues=[]`, matching preserved image/model, `backup_name`, `delete_backup_only_after_benchmark_pass=true`, `overwrite_latest_benchmark_pointer=true`. A `BLOCKED` plan is a hard stop: share the JSON and fix the concrete cause, never bypass with raw `docker stop/rm`.

**Only after reviewing that plan and accepting an actual temporary API outage and backup-container deletion:** run the next command interactively (not in CI, not in a pipe):

```bash
bash scripts/temporary/p2-27b-native-recipe-migrate.sh --execute
```

It prints a FRESH SHA and requests these exact inputs one-by-one:

- displayed full 64-hex SHA (not the old one-shot SHA);
- `I_ACCEPT_27B_RECIPE_MIGRATION_DOWNTIME`;
- `I_APPROVE_VERIFIED_OLD_27B_CONTAINER_DELETION_AFTER_BENCH_PASS`.

The expected success is `status=COMMITTED`, `native_tools_pass=true`, `benchmark_pass=true`, `benchmark_promoted=true`, `backup_container_deleted=true`, `issues=[]`. If `FAIL_RESTORED`, `RECOVERY_FAILED`, `COMMITTED_CLEANUP_PENDING`, or `EVIDENCE_WRITE_FAILED`, preserve state and investigate before any other command.

Post migration read-only verification:

```bash
bash scripts/temporary/p2-27b-native-recipe-migrate.sh --status
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
docker ps -a --filter name=qwen38-27b --format 'table {{.Names}}\t{{.Status}}'
```

**Evidence status before operator runs the above:** source committed to Git, **NO LIVE canonical recipe migration yet**. The earlier one-shot Native Tools inference PASS is REAL DGX; it does not prove this later canonical recreate or new benchmark has completed. No Fake-DGX CI gate was awaited at the user's express request. This increases execution risk; the `--plan` and actual post-execution report are mandatory acceptance evidence. All service state changes remain user TTY gated; mere Git pull changes only files, not Docker.
