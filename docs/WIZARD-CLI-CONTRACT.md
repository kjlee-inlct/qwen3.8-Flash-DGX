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

## 2026-11-07 — Read-only ordinary model switch (post-P3-C)

The P3 A/B/C one-off transitions **actually passed on DGX** and finished with NVIDIA 27B active. The source-only ordinary switch preview is now available:

~~~bash
./wizard.sh switch flash-next-27b operational --target flash-next --plan --json
./wizard.sh switch flash-next-27b operational --target 27b --plan --json
~~~

This preview checks fresh service/API, strict P3 historical receipt provenance, exact preserved Docker models/images, port 8000 bindings, exclusivity and independent unresolved-journal blockers. A SHA256 candidate is **NOT an executable approval**. Any \`--execute\`, \`--approve-plan\`, \`--ack-downtime\` request is rejected. A separate guarded ordinary executor source exists (\`scripts/manager/operational_executor.py\`) but **is not exposed through CLI/TTY** and has not been qualified on DGX. P3-A/B/C stage commands must not be replayed for ordinary switching. Read-only \`./wizard.sh roadmap --json\` now separates historical local evidence, current API identity, generic switch readiness and UX acceptance. Do not stop the current NVIDIA 27B service or imply actual switch permission from CPU CI.

---

## 2026-11-06 — P3 new operator-defined sequence (read-only); old roundtrip retired

P2 27B bounded benchmark remains its own separately approved step. A P2 benchmark PASS **must NOT automatically enter P3**. After P2 returns to verified Flash-Next, stop and await the operator's new P3 authorization.

The **only current P3-specific sequence interface** is read-only:

```bash
./wizard.sh switch flash-next-27b sequence --plan --json
```

It always returns `status=BLOCKED`, `plan_id=null`, `executed=false`, `operations_enabled=false` until a separately qualified persistent switching executor is implemented and approved. Even with a valid P2 benchmark receipt, it shows `P3_SEPARATE_OPERATOR_ENTRY_REQUIRED`; no automatic P3 transition. Phase order: **explicit P3 entry → establish active 27B → switch 27B→Flash-Next → resolve P1 gaps and rebenchmark Flash-Next → switch Flash-Next→27B, final 27B API verified**. Each operational step requires a separate fresh approval, verified API model ID and recovery.

The former P3 two-roundtrip `roundtrip --plan`/`roundtrip --execute` commands are **RETIRED/BLOCKED**, including direct Python legacy entry points. Do not follow historical P3 instructions in old documents. See [binding P3 sequence](P3-MANUAL-TRANSITION-SEQUENCE-20261106.md).

---

## 2026-11-06 — Read-only installed model inventory, including protected legacy Orcarouter

An earlier example `./wizard.sh model list --installed --json` was suggested **before implementation** and gave `{"status":"BLOCKED","error":"choose a valid submenu item for model"}` when the operator tried it. That error was a **missing Wizard route**, NOT evidence that any model was deleted.

This command is now implemented and tested:
```bash
./wizard.sh model list --installed --json
```

Canonical config `runtimes/model-discovery.json` lists known Hugging Face caches (`~/.cache/huggingface`, `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`, and `HF_CACHE`/`HF_HOME` overrides). It maps registered service models to their source repo identifiers **without changing `runtimes/service-policy.json` or granting launch permission**. Includes protected original Orcarouter source `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4`, revision `3a3b63161c0745390e5270179af42e46efc70799` and original BF16/MTP recipe view `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2`. The previous project originally reported ~180GB `hf-cache`, ~5GB `recipe-views`; this was historical storage evidence and has **not been rechecked today**.

Read-only inventory validates selected snapshot's bounded weight index and existence of every indexed nonempty shard (following HF symlinks), tokenizer and config. It reports exact cache/revision and source state. A recipe view alone yields `RECIPE_VIEW_ONLY_SOURCE_UNVERIFIED`; missing weights yield `SNAPSHOT_INCOMPLETE_OR_UNVERIFIED`; found complete indexed weights yield `SOURCE_FILES_PRESENT_UNQUALIFIED`. Unknown caches beyond configured roots are **not** conclusively absent; limited other cached repos are reported as `UNREGISTERED_CACHE_SNAPSHOT_OBSERVED`. Active API identity comes from the manifest-led live service inspector. All these are observational; no model is moved, deleted, downloaded, registered as ready, started, restored, or switched.

The new command has **not yet run on the real DGX**. After clean Git fast-forward, operator executes one read-only Wizard command and provides JSON. Any Orcarouter result must be reconciled with current disk evidence before asserting continued asset availability or runtime compatibility. Original service `qwen38-flash` remains untouched. Existing P2 first GPU trial `PASS_RESTORED` and `LIVE_SERVICE_VERIFIED` are separate, already reported facts.

---

## 2026-11-06 — Manifest-driven unified read-only service status

Canonical operator command for live model/service verification after GPU trial, model switch or restore:

```bash
./wizard.sh service manager status --json
```

This is a **read-only** composite of a fresh Docker/socket observation (actual runtime truth), `runtimes/service-policy.json` (desired model/port invariants), and bounded localhost `GET /health` + `GET /v1/models` (exact served-model identity). It uses the same Manifest observation when assessing HTTP identity, rather than observing a second independently moving Docker state. `status=LIVE_SERVICE_VERIFIED` requires a single running managed model, the expected container/published :8000 mapping, HTTP health success, and exact expected served ID. Otherwise `status=BLOCKED` and `issues` report the missing checks. Useful fields: `observed_model`, `expected_served_id`, `observed_model_ids`, `active_container`, `manifest_status`, `api_health_status`, `checks`. It never restarts, stops, launches, downloads or infers.

Separate diagnostics remain `./wizard.sh service manager inventory --json`, `./wizard.sh service manager health --json`, `./wizard.sh service manager logs --json`. `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false` and `previous_trial_provenance_verified=false` indicate claims not proven by the bounded status query. A historical `PASS_RESTORED` trial journal is separate from actual current-model identity. The new Wizard status implementation requires its own real DGX read-only acceptance after source CI.

---

> **CURRENT, 2026-11-06 (D-021):** Full P1–P7 TTY Wizard implemented as one **model-first console**; see `wizard/console.py`, `wizard/workflow.py`, and `wizard/roadmap.py`. Older domain-based PRIMARY menu text below is preserved as historical contract. The old model/switch/storage/operations/legacy P1–P7 CLI handlers **remain supported**. Source UI complete does **not** mean P2–P7 execution is approved or DGX qualified. `nvidia/Qwen3.8-27B-NVFP4` download was operator-reported STARTED, completion unknown.

### Current operator menu (source)

```text
Blazux Wizard — one GPU model / port 8000
1. Select / run model
   1. NVIDIA Flash-Next
   2. NVIDIA 27B
   3. Orcarouter Flash-Next
   After selection: 1 Continue recommended step / 2 All model actions / 3 Refresh
   Model actions: inspect, download, prepare, start, wait, verify,
                  benchmark, switch, rollback, recipe
2. Service health / status / logs
   status, health, logs (read-only); start, stop, restart, rollback,
   proxy, gateway (guarded and blocked until executor qualified)
3. Advanced / recipes / storage
   P3 switch pair selection, P4 selective cleanup, P6 switch pair,
   P7 proxy/gateway/acceptance plan, legacy stage tools, readiness dashboard
0. Exit
```

CLI entrypoints:
```bash
./wizard.sh
./wizard.sh select 27b --json
./wizard.sh workflow 27b --json
./wizard.sh workflow 27b --for-action start --json
./wizard.sh roadmap --json
./wizard.sh service manager status --json
./wizard.sh service manager health --json
./wizard.sh service manager logs --json
./wizard.sh model 27b status --inspect-cache --json
./wizard.sh model 27b download --guided    # only after no transfer running
./wizard.sh p1 plan --for-action verify --json
./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json
```

**Approval and execution:** P1 individual guarded actions call the existing P1 backend; a P2 missing-checkpoint download calls the existing exact revision/plan approval backend. The source UI does not synthesize approvals or pass `--execute`; P2–P7 runtime actions remain `BLOCKED`. Current service status is derived from live Docker/socket, while API model identity uses bounded `GET /health` + `GET /v1/models`; service logs use an opt-in bounded `docker logs --tail 40` only for the observed managed container. Running containers are not GPU verification. All reports are read-only and release `PASS` requires actual DGX/benchmark/recovery evidence.

# Blazux P1–P7 Wizard — CLI and menu contract

**2026-11-05.** Single operator-facing entrypoint: `./wizard.sh` or `python3 -m wizard`. **Execution engine: vLLM 0.32 only; SGLang excluded.** All stages have separate modules in `wizard/menus/models/flash_next.py` … `p7.py`. They share the central router in `wizard/main.py`, common fail-closed contract in `wizard/menus/common.py`, and external `:8000/v1` target.

## Primary domain-based navigation (current)

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

```bash
./wizard.sh                                   # four primary menus, then submenu choice
./wizard.sh list --json                       # grouped catalog + P1–P7 stage metadata
./wizard.sh model flash-next status --json
./wizard.sh model 27b status --json
./wizard.sh model orcarouter-flash-next status --json
./wizard.sh switch flash-next-27b plan --for-action switch --from-model flash-next --to-model 27b --json
./wizard.sh switch orcarouter-27b plan --for-action switch --from-model orcarouter --to-model 27b --json
./wizard.sh storage flash-next status --json
./wizard.sh operations system status --json
# Equivalent automation syntax:
./wizard.sh --group model --item flash-next --action status --json
# Backward compatibility:
./wizard.sh p1 status --json
./wizard.sh --stage p3 --action switch --from-model flash-next --to-model 27b --json
```

The catalog reports both `groups` and a flat `stages` list. P-stage IDs remain stable for evidence/handoff and existing scripts. **P2–P7 actions still return BLOCKED**; a direct CLI interface is not authorization to execute unvalidated work.

## Supported entry modes

| Mode | Example | Behavior |
|---|---|---|
| Interactive | `./wizard.sh` | Choose P1–P7. P1 opens existing per-step confirmation menu. Others expose safe inspection/plan choices only |
| List | `./wizard.sh list --json` | Returns all seven modules and implementation states |
| Status | `./wizard.sh p1 status --json` | P1 current local inventory/model check; may report blockers without failing the inspection |
| Direct stage/action | `./wizard.sh --stage p1 --action plan --for-action verify --json` | Same P1 handler as interactive UI |
| P2 plan | `./wizard.sh p2 plan --for-action prepare --json` | Structured BLOCKED response until 27B compatibility and adapter acceptance |
| P3 switch plan | `./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json` | Structured BLOCKED; never changes live services |
| P4 storage plan | `./wizard.sh p4 plan --for-action retire --target flash-next --json` | Structured BLOCKED; no deletion |
| P5/P6/P7 | `./wizard.sh p5 status --json` | Stage-specific read-only inspection/plan interface |

**Do not equate a menu's presence with an implemented operation.** The router is implemented for P1–P7 in SOURCE/CI. Only P1 delegates to the previous guarded P1 engine. P2–P7 are **INTERFACE_ONLY**, with `operations_enabled=false`, `executed=false`, `plan_id=null` and a nonempty blocker list on any action plan.

## Machine interface conventions

- Preferred syntax: `./wizard.sh <p1..p7> <status|plan|action> [options] --json`. Alternative: `./wizard.sh --stage p3 --action switch [options] --json`.
- Every P2–P7 object contains `schema_version=1`, stage ID, state, implementation, prerequisites, blocker reasons and `executed=false`. P1 has its original JSON shape from `p1_wizard.py`; harmonizing detailed P1 schemas is later implementation work, not an undocumented guarantee.
- Exit 0: an inspection or supported plan succeeded; inspect the **status field** because `status` can still display BLOCKED readiness.
- Exit 2: syntax/unknown stage errors (P1's own action failures may also use 2).
- Exit 3: operation blocked, unimplemented or approval/plan not valid. Other nonzero codes are errors and must not be interpreted as PASS.
- `--json` never requests user input; `guided` with `--json` is rejected. A non-TTY invocation with no arguments prints stage inventory rather than prompting. `--dry-run` with `--execute` is refused.
- `--execute` has **no effect** on unimplemented P2–P7 except a BLOCKED response, even if a fake `--approve-plan` value is supplied. The common router does not perform any Docker/GPU/network/deletion operation.
- The P1 backend is **different**: it may really prepare/start/verify/benchmark after a current, full matching SHA-256 `plan_id`, a second preflight, and an operator's explicit decision. It refuses incomplete checkpoint, active download/setup, insufficient Hybrid preparation, wrong image, occupied port or container name.

## P1 operator workflow after existing setup finishes

The uploaded DGX terminal log showed a successful vLLM 0.32 Docker build, model download **9/25 files (36%) at last visible line**, and a user shell with `./flash setup default`, then `./flash serve default`, `./flash wait`, `./flash test` queued. **Do not interrupt that shell, change the active worktree, duplicate setup or launch another service.** Once all have exited, inspect (read-only):

```bash
git status --short --branch
git pull --ff-only
./wizard.sh list --json
./wizard.sh p1 status --json
./wizard.sh p1 plan --for-action verify --json
```

If `qwen38-flash` is already running, **skip** P1 `prepare` and `start` and use the current exact per-action plan to approve `verify` then `benchmark`, when separately scoped. Example P1 commands:

```bash
./wizard.sh p1 plan --for-action verify --json
./wizard.sh p1 verify --execute --approve-plan FULL_CURRENT_VERIFY_PLAN_ID --json

./wizard.sh p1 plan --for-action benchmark --requests 3 --max-tokens 64 --seed 1234 --json
./wizard.sh p1 benchmark --execute --approve-plan FULL_CURRENT_BENCH_PLAN_ID \
    --requests 3 --max-tokens 64 --seed 1234 --json
```

Those examples are **not authorizations to run them now**. They require a completed, healthy checkpoint/service, a new matching plan hash, and deliberate operator approval. Execution evidence goes to `~/.local/state/blazux-wizard/p1/` unless overridden. No automatic rollback exists yet; no action automatically deletes HF cache or Docker resources.

## Stage boundary table

| Stage | Menu module | Next integration required |
|---|---|---|
| P1 NVIDIA Flash-Next | `wizard/menus/models/flash_next.py` | Actual DGX P1 Wizard functional and benchmark acceptance, rollback proof |
| P2 27B | `wizard/menus/models/qwen_27b.py` | Pinned recipe, vLLM 0.32 source/CPU compatibility, model preparation/bench |
| P3 Flash-Next ↔ 27B | `wizard/menus/switching/flash_next_27b.py` | Transactional switch, readiness gate, repeat A→B→A and rollback |
| P4 optional Flash-Next cleanup | `wizard/menus/storage/flash_next_cleanup.py` | Capacity check, canonical exact candidates, shared refs, independently approved delete path; otherwise SKIP |
| P5 Orcarouter | `wizard/menus/models/orcarouter_flash_next.py` | BF16 PLE/MTP overlay adapter, numeric qualification and benchmark |
| P6 Orcarouter ↔ 27B | `wizard/menus/switching/orcarouter_27b.py` | Bidirectional switch/rollback, verified API model IDs |
| P7 integrated operations | `wizard/menus/operations/system.py` | Service/proxy/gateway/storage managers, audit, production rollout and rollback |

The accepted execution/acceptance order remains P1→P2→P3→conditional P4→P5→P6→P7. Source scaffolding for later stages does **not** authorize skipping earlier runtime gates.

## Next implementation tasks

1. Fix source/CI failures and make machine interface consistent across commands (including P1 payload versioning), while preserving legacy P1 scripts.
2. Complete DGX P1 verification/benchmark using **existing** downloaded/serving assets and record JSON evidence.
3. Implement P2-specific vLLM 0.32 pinned source adapter and CPU compatibility tests, then progress along the stage order; P3/P4/P5/P6/P7 adapters stay disabled until validated.
