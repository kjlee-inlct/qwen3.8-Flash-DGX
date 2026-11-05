## 2026-11-06 — Exact pinned ModelOpt layer configuration inspection

The real DGX result earlier confirmed `model_type=qwen3_5`, `quant_method=modelopt`, host/image ARM64, pinned checkpoint and existing Flash-Next API. Current SOURCE adds a second step: the existing read-only Wizard command

```bash
./wizard.sh model 27b status --inspect-runtime --json
```

now includes a `quantization_audit` object. It parses only the exact pinned snapshot's `hf_quant_config.json` (maximum 2MiB, at most 20,000 layer entries) and reports `quant_algo`, ModelOpt producer, total layers, counts by `NVFP4` and `FP8`, and a separate non-executable `mixed_fp8_nvfp4_metadata` boolean. Invalid/missing/unexpected values remain BLOCKED. It never copies weights, starts Docker, probes GPU or modifies Flash-Next.

NVIDIA's published main file shows `quantization.quant_algo=MIXED_PRECISION` and per-layer `FP8` and `NVFP4` entries (https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/blob/main/hf_quant_config.json), but the exact immutable DGX snapshot is the source of truth. Do not infer GPU compatibility from this metadata shape. Run the separately documented CPU-only installed-image source audit if desired; actual ModelOpt kernels and vLLM 0.32 startup remain unverified.

---

## 2026-11-06 — Installed vLLM image source audit (after operator runtime-preflight PASS metadata)

Actual DGX runtime preflight shows correct NVIDIA 27B checkpoint and Qwen3.5/ModelOpt config, host aarch64, existing Linux/ARM64 `qwen38-flash-dgx:v0.32` image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; Flash-Next occupies `:8000` and `repo_digests=[]`. This is metadata only; image ID is an immutable **local** artifact ID, not a canonical registry digest. The public **vLLM v0.32.0** docs register `Qwen3_5ForConditionalGeneration` and document ModelOpt NVFP4/FP8 mixed precision, but the exact installed patched image needs local verification.

After clean fast-forward update, run the safe plan first:

```bash
./scripts/temporary/p2-27b-image-audit.sh --plan
```

Explicit opt-in to the static image source audit (CPU only):

```bash
./scripts/temporary/p2-27b-image-audit.sh --execute-cpu-only
```

The second command temporarily creates and removes a **non-inference runc container** (no `--gpus`, no port binding or network, read-only filesystem, no model cache mount). The self-contained audit script reads installed Python source with AST only and emits 4 checks: Qwen3.5 architecture registration, class declaration, ModelOpt mixed/NVFP4 config classes and NVFP4+FP8+MIXED_PRECISION algorithm literals. A `SOURCE_SURFACES_PRESENT_UNQUALIFIED` result means static code surfaces exist, **not** runnable GPU compatibility. A `BLOCKED` result means inspect returned issues and do not start GPU; do not suppress guards or rebuild automatically.

The actual 27B vLLM loader, mixed NVFP4/FP8 GPU kernels, memory/context budget, isolated start/wait/verify/benchmark and Flash-Next rollback remain unverified. `./wizard.sh model 27b status --inspect-runtime --json` remains the default safe Wizard preflight. This image-source probe is an explicit temporary diagnostic, **not** automatic model selection, download, GPU start, service transition or permanent Wizard execution logic.

Sources: https://docs.vllm.ai/en/v0.32.0/models/supported_models/ and https://docs.vllm.ai/en/v0.32.0/api/vllm/model_executor/layers/quantization/modelopt/ .

---

> **2026-11-06 superseding P2 receipt:** The user completed NVIDIA `nvidia/Qwen3.8-27B-NVFP4` at full immutable revision `482ca0f3832238542f8f5295dde86b5f22711d80` (19/19, exit code 0). Exact pinned *source* was found, with `gpu_verified=false`, `runtime=NOT_RUN`; see `handoff/EVIDENCE-LEDGER.md`. Do **not** restart acquisition. For new read-only audit run `./wizard.sh model 27b status --inspect-runtime --json`. This checks only local checkpoint facts, Docker image metadata and current service state; it cannot start the GPU model. Existing `scripts/serve.sh` uses Flash-Next-specific PLE/hybrid/MTP and snapshot-selection semantics and is **not** a qualified 27B launcher. Current public NVIDIA checkpoint config declares `Qwen3_5ForConditionalGeneration`, `qwen3_5`, ModelOpt `modelopt` mixed NVFP4/FP8 (https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/blob/main/config.json); public metadata does not prove pinned GB10/vLLM 0.32 load. Need actual pinned file audit, vLLM registry/loader and validated image digest plus reversible runtime before GPU approval.

> **2026-11-05 model-selection override:** P2 now targets `nvidia/Qwen3.8-27B-NVFP4`, not RadixArk. NVIDIA publishes a ModelOpt mixed NVFP4/FP8 checkpoint with a vLLM example on GB300/TP4, which does **not** prove vLLM 0.32 on one GB10. NVIDIA immutable SHA, model availability in the local cache, image digest and runtime compatibility remain unverified. The previously inspected RadixArk revision `52d1adc5f38aa5ebf099c29ed7025ba34cfbb854` is historical inventory only; it must not be reused as NVIDIA provenance. No transfer/delete/launch was authorized. Source: https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4

# P2 — Qwen 27B Wizard source readiness (2026-11-05)

## State and evidence boundaries

P1 NVIDIA Flash-Next now has real DGX `verify=PASS` including basic
Completions/Chat and optional Tools/Vision, and a bounded `benchmark=PASS`
reported by the operator. Original P1 model and `:8000` stay protected.

P2 is **not** yet runnable. The draft 27B candidate is
`nvidia/Qwen3.8-27B-NVFP4`, an NVIDIA published ~22 GB mixed NVFP4/FP8 file
set (public metadata only). The NVIDIA model card shows vLLM on multi-GPU GB300;
that does **not** prove our pinned vLLM 0.32 image on single GB10.
Our project is explicitly vLLM-only, no SGLang and no hidden fallbacks.

Existing `recipes/qwen38-27b.candidate.yaml` is intentionally invalid.
Immutable revision, architecture compatibility, image ref/digest,
memory fit, tokenizer and vision/tool calling support still require evidence.

## One safe next operator command

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh model 27b status --inspect-cache --json
```

The inspection is **read-only**: no network, no Docker/port changes, no GPU,
no downloads and no files altered. It only reads HF local paths, refs and
`model.safetensors.index.json` (bounded 64MiB) plus file metadata.
No weight bytes are copied/read. Even if local shards exist, no source-only
check is permission to start or replace the active model.

Expected `status=BLOCKED` for P2 runtime, `operations_enabled=false`,
`runtime=NOT_RUN`. `inspection.source_files_present` is independent and
can be true or false. Record exact local model revision and issue list for
next recipe pinning.

## Next implementation gates

1. Verify model repo/pinned full revision, config architecture and weight-map,
   quantization support and vLLM-0.32 loader compatibility on arm64/GB10.
2. Plan disk and memory headroom, names/ports/ownership, actual image digest,
   and a reversible change strategy protecting `:8000`.
3. Build safe `prepare → start → wait → default completions/chat → optional
   tools/vision → bounded benchmark` Wizard adapter (same Blazux-first
   criterion as P1). Keep source, CPU, CI distinct from DGX/GPU PASS.
4. Only after operator-approved runtime change perform an actual P2
   install/serve/benchmark. No stopping Flash-Next, no 27B download,
   no cleanup and no automatic model switching in this phase.

## Source references

- https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4
- `scripts/manager/p2_27b_inventory.py` and `wizard/menus/models/qwen_27b.py`
- `handoff/OPERATING-RULES.md`, `handoff/NEXT-ACTIONS.md`

## Public source cross-check (2026-11-05; NOT runtime qualification)

- Published `RadixArk/Qwen3.8-27B-NVFP4` listing reports ~21.9 GB weights and current displayed commit `319f741`. A third-party DGX Spark vLLM example pins the full revision `319f741cce68d7914884900c138a1fbb70a42f30`; verify it against the authoritative HF repository API and exact snapshot before using in a validated recipe.
- Public `config.json` identifies `Qwen3_5ForConditionalGeneration` and `model_type=qwen3_5` with a vision configuration. Quantization metadata uses ModelOpt NVFP4. These are checkpoint-format observations, not proof of Blazux's current vLLM-0.32 loader or working image/tool API.
- Third-party vLLM/DGX Spark deployment reports are useful comparative evidence, but do not prove this immutable image digest, GB10 headroom, PLE/MTP acceptance, or active port safety. No model download or runtime invocation has occurred in this source session.
- Sources: https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4/tree/main ; https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4/blame/main/config.json ; https://github.com/Tuxbull-Open-Source/vllm.qwen3.8-27b
- New Wizard cache inspector exposes local, bounded config facts as `inspection.configuration` and leaves `vllm032_qualified=false`. Malformed or >1 MiB config invalidates source readiness. A successful read is not a release gate.



## Wizard download and service-management design (2026-11-05)

DGX operator evidence: after updating to `3f4ef68`, `./wizard.sh model 27b status --inspect-cache --json` returned `model_repo=nvidia/Qwen3.8-27B-NVFP4`, `local_revision=null`, `indexed_shard_count=0`, `issues=[NO_PINNED_LOCAL_SNAPSHOT]`. NVIDIA checkpoint is **not present in the examined HF cache**, while the earlier RadixArk checkpoint inventory is historical and unrelated. This observation is not a failed GPU load or proof about caches outside the inspected root.

### Menu separation

- **Model management → 27B → download**: download planning belongs to the model lifecycle, *not* to service start. CLI: `./wizard.sh model 27b plan --for-action download --json`. At present this is intentionally `BLOCKED` and does not execute.
- **Service management → manager**: independent top-level menu/CLI, with `status`, `inventory`, `health`, `logs`, `start`, `stop`, `restart`, `rollback`, `proxy`, `gateway`. CLI: `./wizard.sh service manager status --json` or `./wizard.sh service manager plan --for-action restart --json`. Source-only; no Docker or API mutation.
- **System operations → system (P7)** remains the final integrated acceptance menu, distinct from everyday service controls. No P1–P7 milestones are renumbered.

### Download transaction contract — required before enabling execution

1. Inspect target's full immutable HF revision from authoritative repository metadata, exact file list and size estimate. Do not use `main` or a historical RadixArk revision in an executable plan. Preserve existing HF cache / shared blobs.
2. Read-only host inventory: free bytes/inodes under actual cache mount, running containers, `qwen38-dl` name use, Docker availability, existing transfer processes, disk protection and real Flash-Next API. No automatic source download for inventory.
3. Produce SHA-256 `plan_id` over model repo, revision, exact cache destination, expected files, disk state, download image identity, container collision and expiry. No download if revision, plan, available capacity or environment changed. Require separate explicit operator approval binding the exact plan; never accept a generic `--execute` alone.
4. Download through a validated restricted subprocess wrapper reusing `scripts/download-weights.sh` behavior (HF/Xet/resumability) **only after** correcting fixed-name collisions, exact revision support, cache and image pinning, command validation and lifecycle locking. Never call `flash setup` (which may touch the active service) for 27B acquisition.
5. Audit existing files, indexed shards, `.incomplete` state and full revision after download. Success means source checkpoint present, not vLLM readiness. Record bounded evidence with error category and resume/retry plan. No automatic restart, model switch, preparation or deletion.
6. If disk headroom is inadequate, return `BLOCKED_CAPACITY` and propose storage expansion or separately authorized exact-path cleanup (P4); never delete P1 or RadixArk weights to make room without approval.

### Service manager contract — required before enabling execution

`inventory/health/logs` should be live read-only snapshots, showing active Docker name/image ID, served model ID, host port binding and API response independently. `start/stop/restart/rollback` require ownership validation, fresh signed-off plan, lock, preservation of existing service and tested recovery. A service-name collision, occupied `:8000`, inability to inspect Docker, or missing known-good rollback blocks action. Proxy/gateway are configuration plans until implemented and verified. Keep external `:8000/v1` stable and avoid one-GPU double loading.

**SOURCE implementation in this change:** menu/router and fail-closed plans/CPU tests. Actual NVIDIA download, service operations, DGX/GPU and full P2 benchmark: **NOT_RUN**.

## 2026-11-05 — pinned downloader + single active GPU model policy (supersedes earlier source-only download note)

The operator confirms **one active GPU model per DGX**. Flash-Next and NVIDIA 27B use the **same external `:8000/v1`**; 27B start **requires** a separately approved Flash-Next stop and port release. A cache download is allowed concurrently with the current Flash-Next service because it does not request GPU devices, publish a host port or alter containers. Never infer runtime completion from a download.

**Verified public pin:** `nvidia/Qwen3.8-27B-NVFP4` at exact revision `482ca0f3832238542f8f5295dde86b5f22711d80`, published with 3 safetensors shards (~21.9GB). Source: https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/482ca0f3832238542f8f5295dde86b5f22711d80 . This source revision is verified; **single GB10 vLLM-0.32 runtime compatibility remains unverified**.

**Download operator flow** (safe by default, CPU source tested, actual DGX download NOT_RUN until operator execution):

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh model 27b plan --for-action download --json
# If status=READY_TO_REQUEST_APPROVAL and plan_id is non-null:
./wizard.sh model 27b download --guided
```

The `--guided` path prints the exact current plan and requires typing the complete `plan_id`, then regenerates and checks the plan under an exclusive lock before any download. Alternatively use the same Wizard CLI with `download --execute --approve-plan FULL_PLAN_ID`. It executes a **pinned-image, exact-revision HF CLI** in its own `qwen38-27b-dl` Docker container, with an existing host-mounted cache, no `--gpus`, no published port and no `flash setup`/service stop. It enforces cache availability, Docker inventory and image SHA256, at least 35GiB available disk headroom, inode headroom, no name conflict or competing transfer, and a ten-minute plan-fingerprint window. Conservative headroom is an operational guard, not a model-memory estimate. Every successful or failed transfer attempt writes local bounded JSON evidence under `~/.local/state/blazux-wizard/p2/evidence`, and re-audits the exact immutable snapshot.

Explicit revision downloads do not necessarily update HF `refs/main`; the P2 auditor now selects an existing pinned snapshot directly if `--expected-revision` is given. `SOURCE_FILES_PRESENT_PINNED_CANDIDATE` means files are visible and validated at the expected SHA, **not** P2 runtime readiness.

**Service/manifest source contract:** `runtimes/service-policy.json` defines model identities, one-model rule, host port and stop-before-start/restore constraints. `./wizard.sh service manager inventory --json` derives a read-only manifest from current Docker/port observations. `scripts/manager/service_journal.py` provides an append-only, generation-checked, atomic local state journal for future approved transitions; no active switching executor calls it yet. Docker inventory alone is not proof of actual GPU residency or served API model ID, so these fields remain explicitly unverified. Service stop/start/switch/rollback need a separately implemented and approved transaction with API/GPU identification.

**P1 protection:** preserve `qwen38-flash`, its checkpoint/image/cache, OpenWebUI clients and current host API. Download approval **cannot** authorize a GPU start or old service stop. No deletion as an implicit capacity remedy. If preflight is BLOCKED, return the JSON blocker for a code/host-specific remedy before any download.

## 2026-11-05 — Download approval false invalidation fixed

Operator confirmed a fully matching, 64-character `plan_id` was rejected with `PREFLIGHT_CHANGED_REPLAN_REQUIRED` and `executed=false`. **No download had started.** Reproducible source cause: the first plan hashed `free_inodes`, exact `free_gib_floor` and Docker's human `Up N hours` field. The approved-execution path then creates a state directory and `download.lock`, which changes free inodes before its mandatory second preflight. Uptime and disk telemetry can also drift independently of operational safety.

The new `_approval_facts` binds the exact checkpoint/revision, cache, download container, immutable image ID, current managed container names/image IDs, **running vs stopped**, port occupancy, transfer/checkpoint conditions and ten-minute time window; it excludes raw inode counts, disk capacity and human uptime from the fingerprint. **The second preflight still independently checks free space ≥35GiB, inode headroom, Docker/name collisions, transfer process presence, current checkpoint state and image identity.** A changed image or running/stopped state causes a different plan ID; insufficient live disk blocks execution outright. A ten-minute epoch boundary intentionally expires a plan, reported as `DOWNLOAD_PLAN_TIME_WINDOW_EXPIRED`.

Fix and CPU regression tests commit on `feature/recipe-wizard-handoff`. After Git pull, generate and approve a **new** plan ID; old IDs were computed with the previous algorithm and are not reusable. Do not manually disable the second preflight. DGX actual download remains `NOT_RUN` pending a successful operator run.

