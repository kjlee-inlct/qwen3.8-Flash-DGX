# Unified Model-first Wizard — accepted design and implementation plan

> Decision date: 2026-11-05. Target: DGX Spark, Blazux vLLM 0.32, one active GPU model on host port 8000. This document governs the consolidated Wizard UX. It does not authorize GPU or service mutation.

## 1. Operator goal

The operator should do **model selection → only necessary preparation (download/transition) → approved start → verification** with as few prompts as practical. They should **not** have to understand P1–P7, call a collection of scripts, or separately choose `download`, `prepare`, `stop`, `wait`, and `verify` for ordinary operation.

Root interactive `./wizard.sh` presents only:

```text
Blazux Wizard                         API: :8000/v1
  Active: flash-next                   Runtime: OBSERVED / UNVERIFIED
  Download: NVIDIA 27B                 IN_PROGRESS (if observed)
  1. Select / run model
  2. Service / health / logs
  3. Advanced / recipes / storage
  0. Exit
```

Model selection shows:

```text
  1. NVIDIA Flash-Next (P1, existing validated backend)
  2. NVIDIA 27B        (P2, fixed revision)
  3. Orcarouter        (P5, adapter unqualified)
  0. Back
```

After selecting a model, the Wizard detects actual facts and prints one consolidated action plan: no operation if already running, download prompt if files are missing, transfer progress if downloading, or one scoped service transition proposal when ready. Advanced operations retain legacy CLI.

## 2. Ordered decision logic

1. Observe Docker/host port from the existing read-only inventory. Load desired, committed service policy. Do **not** trust a stale persisted manifest as the current service.
2. Inspect selected checkpoint and recipe qualification. **Source present** is not equivalent to runtime qualified. A pinned snapshot must be checked at the expected SHA even if `refs/main` was not updated.
3. If a transfer container named `qwen38-27b-dl` exists and is running, report `DOWNLOADING`, offer status only and **never re-launch download**.
4. If the selected model is the active model, request no download or restart. Verify actual API served ID separately before announcing `RUNNING_VERIFIED`.
5. If model is absent and an approved downloader exists, offer **one** download action using that model's **existing exact-plan approval backend**. Download may overlap Flash-Next inference; never stop it for acquisition.
6. If assets are present but recipe/runtime unqualified, show the blocking reasons. Do not begin prepare/start/switch just because source files exist.
7. If another GPU model is active and target is qualified, build **one atomic transition plan**: observe current API/GPU ownership → preserve old recipe/checkpoint/image → exact scoped approval → stop old → verify :8000 released → start new at :8000 → wait → verify served ID/probes → commit journal. On failure, restore old and report recovery outcome. **The executor is not implemented/approved yet.**
8. If no model is active and target is qualified, use the same guarded start/verify flow without a stop.
9. No destructive default, implicit cache deletion, model conversion, or hidden `./flash setup` inside the selector.

## 3. User-visible lifecycle states

`ABSENT`, `DOWNLOADING`, `SOURCE_PRESENT_UNQUALIFIED`, `PREPARED`, `READY_TO_START`, `STARTING`, `RUNNING_OBSERVED`, `RUNNING_VERIFIED`, `STOPPED`, `TRANSITIONING`, `ROLLING_BACK`, `RECOVERY_FAILED`, `UNKNOWN`. Also show scoped `BLOCKED` causes separately. Do not represent Docker `Up` as API identity or GPU readiness proof.

### Selected-model plan schema (version 1)

- `selected_model`, `source_stage`, `observed_model`, `api_host_port=8000`
- `checkpoint_state`, `download_state`, `runtime_qualified`, `api_identity_verified`
- `status`, `issues`, `steps` (each has action/reason/state/approval scope)
- `executed=false` by default, `operations_enabled=false` for unimplemented adapters
- `next_action`: `none`, `download`, `verify`, `start`, `switch`, `blocked`
- `service_manifest`: bounded, read-only observation, not a persisted claim of runtime correctness
- Plans print **no side-effectful action** unless user approves it through an existing guarded adapter.

## 4. Reuse and compatibility

| Existing module | Treatment |
| --- | --- |
| `scripts/manager/p1_wizard.py` and `wizard/menus/models/flash_next.py` | **KEEP** and delegate validated Flash-Next prepare/start/wait/verify/benchmark actions; do not rewrite or downgrade P1 gates |
| `scripts/manager/p2_27b_download.py` | **KEEP**, use exact pinned revision, capacity/revision/image gates, single download container/lock, evidence |
| `scripts/manager/p2_27b_inventory.py` | **KEEP**, reuse read-only checkpoint scan |
| `wizard/menus/models/orcarouter_flash_next.py` | **KEEP** unqualified adapter; no new runtime command yet |
| `scripts/manager/service_manifest.py` | Extend observed state with model registry and transfer awareness; actual Docker/API remain the authority |
| `scripts/manager/service_journal.py` | **KEEP** append-only generation guarded state transitions; do not confuse events with live state |
| `wizard/main.py` | Replace **only interactive top-level navigation**; preserve legacy `model/switch/storage/operations/service`, `p1..p7` and JSON route compatibility |
| `runtimes/service-policy.json` | Desired single-model/port policy; runtime qualification and immutable execution settings belong to verified recipes |

API namespace for new selection: `./wizard.sh select 27b --json` = read-only model selection plan. The interactive root uses the **same** planner. No `--execute` bypass is added. New APIs remain read-only until actual executor is qualified.

## 5. Approval boundaries and live-service protection

- **One GPU model, one external port** `:8000/v1`. Switching requires stop-before-start and rollback, not an alternate port.
- Download authorization is scoped to checkpoint bytes and **does not** authorize Flash-Next stop, 27B start, service restart or API cutover.
- While `qwen38-27b-dl` downloads, never change the pinned download container, cache, active Flash-Next service, Docker image or repository worktree on the DGX. GitHub-only source work and CPU CI are allowed.
- User-supplied console evidence on 2026-11-05: 27B `download --guided` accepted pinned plan, terminal displayed `Fetching 19 files: 84%`. **Download has started, but successful completion is NOT YET VERIFIED.** The percentage is files, not total bytes.
- Separate truth values: source/CPU CI, actual DGX file verification, actual GPU/API verification, benchmarks and transition recovery.

## 6. Implementation batches and acceptance

**Batch A — now, while 27B downloads:** commit this design; implement root three-choice menu, read-only model `select` plan, live manifest/repo status classification and minimal prompts. Add CPU test matrix: active Flash-Next, downloading 27B, missing files, source present but runtime blocked, active target, manifest unavailable, selection alias/invalid option. Keep P1 CLI/runner unchanged. Record CI evidence.

**Batch B — next:** unify recipe qualification and model-specific action registry, add exact present/ready evidence schema; plan start/switch and reproducible rollback. Implement read-only service health/logs with safe bounds. Validate P2 image/architecture/vLLM-0.32 on arm64 **before enabling 27B GPU start**.

**Batch C — separately authorized live window:** implement gated service handover and rollback, verify on real DGX after download completion; measure model switching, P2 bounded API/bench, P3 two-way cycles.

**Batch D — Orcarouter:** pull reviewed adapter from `feature/orcarouter-bf16-adapter` only after source audit; qualify runtime/PLE/MTP and integrate as another model target without rewriting common Wizard.

**Batch E — release:** advanced storage, backups, gateway/proxy, failure recovery, P7 acceptance, docs and scripts cleanup.

### Acceptance criteria for Batch A
1. Root TTY menu exposes only Select model, Service, Advanced, Exit.
2. `./wizard.sh select <model> --json` is machine-readable, read-only and fail-closed on uncertainty.
3. During 27B download the planner reports `DOWNLOADING`, cannot initiate a second transfer and leaves Flash-Next untouched.
4. Existing CLI aliases and P1 guarded implementation still pass prior CPU suites.
5. GitHub PR and CPU CI pass; real service/download/GPU state is not modified by this batch.


## 7. Batch B source-only progress (2026-11-05)

- Added `scripts/manager/service_health.py`: bounded, **GET-only**, fixed loopback `127.0.0.1:8000` `/health` and `/v1/models` with capped responses/timeouts, matching expected served model ID. This is proof of **API identity only**, not GPU exclusivity or full runtime qualification. The Service root choice now runs this explicit read-only health check. Logs remain unimplemented/guarded.
- Added `scripts/manager/service_transition_preview.py`: **non-executable** read-only preview of `OBSERVED → PLANNED → OLD_STOPPING → OLD_STOPPED(port free) → NEW_STARTING → NEW_VERIFYING → COMMITTED`, with explicit rollback `ROLLBACK_STARTING → RESTORED/RECOVERY_FAILED`. It requires target asset/runtime qualification, actual API and GPU identity, source recovery proof and exact separate approval before any future executor may act. The preview currently always includes `SERVICE_TRANSITION_EXECUTOR_NOT_IMPLEMENTED` and `plan_id=null`.
- Model selection includes a `transition_preview` only if an **other** managed inference model is observed. The preview is information, not an operation. No download, service or GPU mutation was executed during this development.
- Added CPU mocked tests and GitHub workflow coverage for health/identity mismatch, malformed/oversized HTTP, source+target gating, stop-before-start, rollback and no execution.

### Deferred runtime gates

Before a future launch can be enabled: pin target model-compatible vLLM 0.32 ARM64 image/loader; validate actual GPU memory constraints and served ID; verify the current API model independently; test Flash-Next recovery from deliberate failed target start; allow rollback only with a fresh scoped operator approval. Until then, `select 27b` after completed download reports `SOURCE_PRESENT_UNQUALIFIED`.
