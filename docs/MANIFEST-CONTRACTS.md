## 2026-11-08 current P5 v2 supersession (document-wide audit)

The complete [document inventory and consistency audit](HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) and [current **P5 QSA+LM-head v2** DGX trial runbook](P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md) supersede earlier P5 source-only / GPU NOT_RUN descriptions and older QSA-only commands. Latest actual DGX **QSA-only** trial failed after 15/17 safetensors shards with missing `lm_head.weight_scale`; the candidate v2 source/CPU CI passed but **v2 GPU load is not proven**. Current v2 adapter is `qwen4exp-qsa62318-lmhead-v032-v2` and its **new** target is `qwen38-orcarouter-qsa62318-lmhead`. Actual current :8000 service state remains unobserved since that failed trial. Previous 27B and failed candidate images/containers are preserved. Never copy the earlier QSA-only `execute` commands without revalidation. vLLM=0.32.0, one active model, :8000; P6/P8 live operations and PR #1 merge remain out of scope. Older sections below remain historical.

---

## 2026-11-08 — PLE schema v2; format independence and DGX Spark reference adoption

Superseding update: `runtimes/ple-assets.json` is **schema v2**, independent PLE storage dtype, scale mode, scale dtype, packing and placement; the fixed Orcarouter BF16 asset remains untouched. `runtimes/ple-loader-profiles.json` is now included in the **seven-document** common Wizard registry and separately records target vLLM **0.32.0** ABI/GB10 capabilities as **UNQUALIFIED**. Other models may register FP8 etc PLE separately; BF16 is not a global assumption. `scripts/manager/ple_format.py` and `service_transition_preview.py` enforce unmap/release/reload/no-unverified-hot-swap for PLE model/profile/dtype changes, preserve rollback sources, GPU allocations and port 8000.

References were reviewed, NOT installed: [dolf3131 pinned vLLM NVFP4 lane](https://github.com/dolf3131/dgx-spark-llm-serving/blob/45e3d47771577dabab0998e9013e85dd0915ae4f/lanes/vllm-nvfp4/README.md) and [NVIDIA DGX Spark forum](https://forums.developer.nvidia.com/t/nvidia-official-qwen3-8-flash-next-checkpoint-for-single-dgx-spark/385994). The former records FP8 PLE with one BF16 per-table scale, mixed-quantizer bypass and TP1 offload worker hang; the latter discusses a different NVIDIA FP4-Local checkpoint requiring B12X-specific runtime flags. No automatic reuse of these images/settings in pinned Blazux 0.32.

The operator clarified the DGX is a development machine with **service downtime/GPU testing permitted**; preserve one active GPU model, :8000, caches, images, receipts, and recoverable transition. Permission is **not** proof that an Orcarouter vLLM0.32 image/ABI/PLE loader was qualified; P5 `--gpu-trial` remains blocked until such executor and rollback are ready. Latest code `d395368` passed [CI #42436269922](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42436269922). No DGX runtime commands executed in this GitHub session. See [detailed engineering note](../docs/P5-PLE-FORMAT-AND-DGX-SPARK-REFERENCE-ADOPTION-20261108.md).

---

## 2026-11-08 — Shared Wizard manifest registry and managed Orcarouter PLE

**Implemented (source/CPU):** `runtimes/manifest-registry.json` is the Wizard's canonical shared registry for service policy, model discovery, the canonical 27B recipe, the Orcarouter source-only recipe, YSLAB compatibility and a **new first-class PLE asset registry** `runtimes/ple-assets.json`. `scripts/manager/manifest_registry.py` centralizes bounded strict JSON loading, duplicate-key/non-finite/symlink rejection and all model/recipe/PLE/donor/service cross-reference checks; `./wizard.sh manifest status --json` and `./wizard.sh manifest validate --json` are read-only and do not check the GPU. PLE asset `orcarouter-bf16-ple` is now referenced by the P5 recipe, service policy and model discovery; canonical `scripts/manager/ple_assets.py` performs local pinned header/weight-map checks and reports metadata status independent of GPU. Wizard P5 status/doctor, model installed list, service status and model-first selector expose the asset appropriately. These interfaces **never authorize deletion/overlay, Docker mutation or runtime activation**.

[Source commit a17b3618](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/a17b3618fab98aa5b849359d464c0d7698fae4a0) passed [Actions #42433160630](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42433160630), including 996 executed CPU test cases across 44 unittest invocations (duplicates included), manifest registry contract/drift and new PLE asset mocks. Final model-first selector/documentation follow-up requires independent CI. Read detailed decisions and commands in `docs/WIZARD-MANIFEST-REGISTRY-AND-PLE-ASSETS-20261108.md`.

**Actual DGX evidence:** the operator's supplied previous-HEAD console output showed `qwen38-27b` serving `qwen3.8-27b` on :8000, Orcarouter pinned BF16 PLE 128/128 header/shape PASS, MTP 31/31 donor tensors and all 3 donor SHA256 PASS; GPU Orcarouter not started. This observation predates the manifest code and does not verify its new DGX integration. The P5 GPU loader/overlay/bench/rollback and P8 release remain NOT_RUN. Preserve 27B, :8000/ONE_ACTIVE_MODEL_ONLY, all HF assets and historical receipts; P3 replay/P4 delete/P6 switch/P8 fault/PR merge remain unauthorized.

---

## SUPERSEDING VERIFIED STATE — 2026-11-07, AFTER DGX REAL ACCEPTANCE

**LATEST FACTS override older diagnostic/HTTP-400/source-only text further down.** The initial NVIDIA 27B API HTTP 400 and absent native parser flags were RESOLVED via a user-approved RECREATION of the canonical `qwen38-27b` from pinned `recipes/qwen38-27b.runtime.json` (vLLM 0.32.0, modelopt_mixed, port 8000, `qwen3_coder` / `qwen3` / exact NVIDIA Jinja). Actual DGX native `tool_calls`, tool result continuation, streaming, normal chat, benchmark v2 **PASS** (3/3, mean client E2E 10.957 tok/s, p50 TTFT 0.165412 s), and Open WebUI Native **user-confirmed PASS**. Original old container's verified stopped backup was deleted after full success; new canonical `qwen38-27b` is operational. P3-C one-off already REAL PASS/CLOSED; old P3 Docker IDs are historical, not current execution identity.

Wizard manifest cleanup then actually removed the two *stopped historical test containers*, `qwen38-27b-failed-6d9ede0904c2` and `qwen38-27b-native-tools-v1`. Live `cleanup --execute` and independent `cleanup --status` returned `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, both absent, active canonical 27B preserved; `service manager status --json` returned `LIVE_SERVICE_VERIFIED` with API `qwen3.8-27b` at :8000. The recorded cleanup was completed, NOT a pending removal. `qwen38-flash` remains stopped; Open WebUI and Portainer remain running.

**Next work is NOT P2 native-tool HTTP-400 troubleshooting.** It is general Wizard model lifecycle / recipe diff-aware install, removal, reinstallation and same-name recreation, current-Docker-ID-aware model switching and independent production release acceptance. Canonical 27B and Flash are removable/reinstallable upon independently approved actions; no global deletion ban. Such generic lifecycle functionality and the post-container-ID-change operating switch are **NOT YET RELEASED OR REAL-DGX QUALIFIED**. Keep `PRODUCTION_EXECUTION_RELEASED=False`; one active GPU model and port 8000; preserve historical journal/receipts/images/model files unless explicitly scoped.

Details: [27B real PASS](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-LIVE-PASS-20261107.md), [actual cleanup PASS](../docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md), [new Wizard lifecycle scope](../docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md). Do NOT edit the canonical recipe JSON cosmetically without a versioned/requalified migration: its exact SHA is bound into the current latest benchmark pointer.

---

# Manifest contracts, service orchestration and storage safety

**Current state (2026-11-05):** N1 recipe schema, P1 guarded Wizard backend, P2 source downloader, model-first selection plan, read-only service manifest and service transition journal primitives are implemented. P2 runtime image/loader and actual stop/start/switch remain **NOT_QUALIFIED/NOT_RUN**; do not infer operational readiness from model selection or download.

## Unified model-first contract (2026-11-05)

The accepted UX is `./wizard.sh` → **Select model / Service / Advanced**. Headless `./wizard.sh select 27b --json` returns a read-only lifecycle decision; the old `model/switch/storage/operations/p1..p7` CLI remains compatible. Full rules, classification table, safety contracts and phased acceptance live in [UNIFIED-MODEL-WIZARD-DESIGN.md](UNIFIED-MODEL-WIZARD-DESIGN.md).

Service state has three separate truths: desired Git policy `runtimes/service-policy.json`; observed, bounded Docker/socket inventory `scripts/manager/service_manifest.py`; append-only local transition journal `scripts/manager/service_journal.py`. **Observed container != served API model or exclusive GPU claim**; both require active qualification. Downloader `qwen38-27b-dl` is disk/network-only and can coexist with one active GPU inference container. A running downloader is `DOWNLOADING`, not `DOWNLOADED` or `READY`.

## A. Five concerns with different ownership

| Type | Source of truth | Key fields | Version policy |
|---|---|---|---|
| Recipe | Git `recipes/*.yaml` | `recipe_id`, model repo/revision, tokenizer, architecture, quantization, PLE, MTP, stage dependencies, compatible runtime IDs, checks | Versioned, reviewed, no tokens |
| Runtime | Git `runtimes/*.yaml` or bounded recipe reference | vLLM version, Docker image **digest**, architecture `linux/arm64`, host/GPU/env/CLI flags, mounts, limits | Versioned; no floating `latest` for qualified release |
| Service | Git desired state + local runtime state | served name vs model repo, container identity, port, API compatibility, gateway routing, health and rollback policy | Desired config versioned; actual process state read from DGX |
| Storage inventory | Local, generated, timestamped | checkpoint snapshot SHA, canonical path, inode/symlink/blobs, bytes, ownership, consumers, protection flags | Regenerate before stateful action; never assume Git knows free space |
| Benchmark/evidence | Immutable measured artifact + Git pointers | source/recipe/weights/image digests, host specs, exact commands, seeds, request hashes, results, logs, status | Append-only, link to `handoff/EVIDENCE-LEDGER.md` |

Secrets, HF read tokens, API keys and host-private raw paths are **never** committed.

## B. N1 recipe source contract — implemented subset

The source-only schema lives at [schemas/recipe.schema.json](../schemas/recipe.schema.json), validator at [scripts/manager/manifest.py](../scripts/manager/manifest.py), and intentionally **invalid** 27B example at [recipes/qwen38-27b.candidate.yaml](../recipes/qwen38-27b.candidate.yaml). JSON Schema Draft 2020-12 requires vLLM 0.32.0/linux-arm64, explicit model and runtime full commit SHAs, digest-pinned Docker image matching a separate SHA256 field, stated architecture/quantization/PLE/MTP, bounded service name/port and hardcoded no-bypass approval fields. The YAML parser rejects unsafe tags, anchors/aliases and duplicate keys.

Run (isolated CPU, no Docker/GPU):
- python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -v
- python3 -m scripts.manager.manifest validate recipes/qwen38-27b.candidate.yaml

27B example MUST fail (exit 2), because actual repo revision, image digest, source SHA, architecture and PLE are unknown. Only the **synthetic** test fixture is schema-valid; its SHA values are not real pins. Schema success NEVER means image/checkpoint existence or permission to serve, download, stop or delete. Historical hard-coded block for port 8000 and the former Orcarouter name was removed 2026-11-05 after user reported service retirement. N2 now performs fresh read-only Docker, socket, mount and cache observations. Port 8000 is allowed **at source schema level only**; if occupied, deployment MUST be blocked. No runtime authority follows from source schema PASS.

## C. Safety-first commands and state machine (proposed)

```text
inventory / plan / doctor / verify-source       READ_ONLY
prepare --dry-run                               READ_ONLY
prepare --execute --approval-id ...             RESOURCE_MUTATION
serve --dry-run                                 READ_ONLY
switch --dry-run --to RECIPE                    READ_ONLY
switch --execute --approval-id ...              GPU_SERVICE_MUTATION
retire --dry-run --recipe RECIPE                READ_ONLY
retire --execute --approval-id ...              DESTRUCTIVE_MUTATION
rollback --dry-run                              READ_ONLY
rollback --execute --approval-id ...            GPU_SERVICE_MUTATION
```

Use unique `plan_id`, `approval_id`, snapshot generation, expected active model/port/image, expected candidates and lock; approval binds to **exact plan digest and resource IDs**, expires after state changes. A source conversation saying “do the roadmap” is not an unconditional approval for any of those mutations.

```text
IDLE -> PLAN -> PRECHECK -> APPROVAL -> QUIESCE -> STOP_OLD
-> START_NEW -> READY_CHECK -> API_SMOKE -> COMMIT
                             \-> FAILED -> ROLLBACK -> VERIFY_OLD
```

Before `STOP_OLD`, guarantee the source recipe, rollback image, checkpoint, port and snapshot remain intact. A rollback that depends on deleted files is invalid. For a single GPU box, the gateway must queue/reject requests with a clear 503/Retry-After during cutover rather than silently misrouting; avoid misleading `/v1/models` listing if the model is not actually active.

At every transition write an append-only local transition log (no credentials). Restart after interruption must reconcile actual Docker/port state, **never** trust an outdated state.json alone. Prevent two overlapping switches with a lock.

## D. Disk deletion policy and required inventory

1. Snapshot existing protected live Docker container, image digest, mounts and current HF cache. Collect `df`, `du`, `docker system df` and resolved paths **read-only**.
2. Build a concrete candidate list with resolved parent/canonical paths and content hashes where feasible, expected reclaimed bytes **conservatively** estimated. Different snapshots may share blobs.
3. Deny deletion if a path is under a protected root, referenced by a runtime/recipe/rollback/donor overlay, bound into a running container, not owned by the manager, or has unresolved symlink/shared-blob references.
4. Show **exact file list**, checkpoint revision, byte count, consequences, redownload/recovery method. Explicit approval must identify the specific deletion plan; default is dry-run.
5. Remove only audited targets in bounded batches; log before/after free space, digests for surviving manifests, and rollback metadata. Never automatically run `docker system prune -a`, `docker image prune` or entire HF cache deletion.
6. Preserve recipe, original validation records, manifests, error traces (redacted), benchmark data and Git history even if model weights are removed.

**Space bottleneck before P2:** do not skip P3 to remove P1 checkpoint. Ask for targeted storage expansion, alternative download staging, or user-approved deletion plan with a still-recoverable fallback; otherwise mark `BLOCKED_CAPACITY`.

## E. Acceptance protocol

- CPU/CI: parse schema, select recipe, error-path guards, path canonicalization, symlink/refgraph logic, safe container name/port rules, dry-run idempotence, state-machine/recovery fault injection; no Docker/GPU for unit tests.
- GPU window: memory guard, one active model, startup, 27B architecture viability, PLE, MTP OFF then on, API routes, repeated switching, failover, and measured latency/throughput/quality. Pin benchmark seeds and prompts; redact secrets.
- Release: `PASS` requires reproducible artifacts and gate matrix, not only an API 200. A status is one of `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE` with explicit scope.

See [master plan](MODEL-RECIPE-WIZARD-PLAN.md) and [current handoff](../handoff/CURRENT-STATE.md).

## Read-only API/transition qualification additions (2026-11-05)

`scripts/manager/service_health.py` performs bounded GET-only local :8000 health plus served model identity; it does **not** prove GPU exclusivity. `scripts/manager/service_transition_preview.py` assembles a source-only, fail-closed stop-before-start and rollback preview. There is no executable service transition adapter or accepted plan ID yet. The interactive Service choice performs the read-only API health inspection; `./wizard.sh service manager health --json` is the corresponding existing nested CLI. No logs or service restart code has been enabled.


## Full Wizard model/service/release source contract (2026-11-06)

`wizard/workflow.py` catalogs all three models with the same ten named actions (`inspect/download/prepare/start/wait/verify/benchmark/switch/rollback/recipe`). Its statuses explicitly distinguish `READ_ONLY`, `GUARDED_P1`, `APPROVAL_REQUIRED`, `IN_PROGRESS`, `BLOCKED`. A plan can be displayed before an execution adapter is qualified but does not supply an authorization or runnable command. Service inventory is actual Docker/socket observation; bounded local HTTP health is separate; bounded opt-in log tail exposes only locally observed managed container logs, never uploads private log contents. `wizard/roadmap.py` summarizes all P1–P7 gates as **NOT_RELEASE_QUALIFIED** until actual scoped evidence.

Operator console `wizard/console.py` presents all P1–P7 actions: model lifecycle; service status/health/logs/start/stop/restart/rollback/proxy/gateway; advanced bidirectional P3/P6, P4 conditional storage, P7 acceptance and readiness report. Existing P1 and pinned P2 downloader are delegated without bypassing approvals. Model switching requires stop-old → free port 8000 → start-new → verify exact model → restore-old on failure; the actual executor is not yet qualified and remains blocked.

