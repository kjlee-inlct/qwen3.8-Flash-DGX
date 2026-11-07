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
