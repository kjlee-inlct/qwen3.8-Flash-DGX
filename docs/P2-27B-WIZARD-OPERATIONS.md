## LATEST 2026-11-07 — P2 GPU history PASSED, appended P2-FINAL Native Tool Calling NOT QUALIFIED

The P2 NVIDIA pinned 27B initial loader/trial/benchmark/Flash restore is **historical REAL DGX PASS**. The newly required P2-FINAL official `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3` is **not active** in the original preserved `qwen38-27b` Docker `Config.Cmd`, verified by an actual operator inspect. Source-only `scripts/serve_27b.sh --tools-profile` displays correct option candidate but no Docker change; bounded `--tools-probe` returns `BLOCKED/LOCAL_API_HTTP_ERROR_400`, no structured tool call. Meanwhile real 27B API remains `LIVE_SERVICE_VERIFIED` and the distinct ordinary switch journal `VERIFIED/COMMITTED/14` after both directions physically PASS. **P2-FINAL cannot be closed by ordinary chat/benchmark, config documentation or another historic P3-C replay.** The next source task is separate protected tool-enabled 27B recipe/profile, proven parser/stream/Open WebUI Native tool cycle, independently authorized cutover/rollback. Historic P3-C remains FINAL PASS and unchanged. See `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.

---

## 2026-11-06 — First Qwen3.8-27B GPU launch trial (one-shot and original service restoration)

Actual DGX restricted CPU import/registry audit completed **all nine checks true with `issues: []`**; vLLM resolves `modelopt_mixed` to ModelOpt's imported config class. The Qwen3.8 NVIDIA checkpoint internally advertises `model_type=qwen3_5` and `Qwen3_5ForConditionalGeneration` solely as the loader class. The served model **is Qwen3.8-27B**, `nvidia/Qwen3.8-27B-NVFP4` pinned SHA `482ca0f3832238542f8f5295dde86b5f22711d80`.

Community references were reviewed:
- MiaAI-Lab `https://github.com/MiaAI-Lab/Qwen3.8-27B-DGX-Spark-RTX-6000` deploys **Unsloth compressed-tensors**; its `--quantization compressed-tensors`, FP8 KV defaults and MTP **must not** be copied to this NVIDIA ModelOpt checkpoint unverified.
- NVIDIA forum `https://forums.developer.nvidia.com/t/qwen3-8-27b-nvfp4-on-a-single-dgx-spark-up-to-1m-context-vllm-mtp-measurements/380244/17` highlights GB10 NVFP4 kernel compatibility and separate tuned MTP results; future tuning only.
- eugr `https://github.com/eugr/spark-vllm-docker` explicitly has NVIDIA Qwen3.8-27B recipes and alternative Spark kernel images; consider if the current pinned local vLLM 0.32 image fails actual GPU loading.
- NVIDIA guidance `https://build.nvidia.com/spark/vllm/intermediate` includes the NVIDIA checkpoint and alternate tested images; not evidence that this particular local image works.

**Implementation:** `scripts/manager/p2_27b_gpu_trial.py` is a separate first-use experimental executor, called only through dedicated `scripts/serve_27b.sh --trial-*`. Its **read-only plan** checks the exact live original container ID, original API identity, immutable image, pinned source ModelOpt metadata, :8000 ownership, absence of another running GPU-enabled Docker container, and absence of a preexisting 27B container. Any unknown additional condition stays BLOCKED. A 64-hex plan ID binds these observed facts for a 10-minute window; no prior download/CPU approval authorizes it.

Start with a clean repo and inspect the plan **without changing the running service**:

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./scripts/serve_27b.sh --trial-plan
```

If `status=READY_TO_REQUEST_TRIAL_APPROVAL`, the operator may separately accept a **maintenance outage** and enter a full fresh plan ID (not literally `FULL_64_HEX_PLAN_ID`):

```bash
./scripts/serve_27b.sh --trial-execute \
  --approve-plan FULL_64_HEX_PLAN_ID \
  --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME
```

**WARNING:** This command actually STOPS `qwen38-flash` and interrupts all existing clients at :8000. It starts the separate official NVIDIA 27B snapshot with `--quantization modelopt_mixed`, `--max-model-len 8192`, `--max-num-seqs 1`, `--gpu-memory-utilization 0.70`, `--enforce-eager`, with PLE/MTP/YaRN disabled. It waits up to 600 seconds for exact Qwen3.8-27B API readiness and makes one max-24-token inference. Whether success or failure, it tries to stop/remove **only the labeled trial-created 27B container**, restart the **same preserved original Flash-Next** container, and verify `/health` plus served ID `qwen3.8-flash-next` within 240 seconds. The response distinguishes `PASS_RESTORED`, `FAIL_RESTORED`, `RECOVERY_FAILED`; local append-only JSON and bounded private `target.log` provide error diagnostics. **Do not run trial in the background.** Failure of Docker, host OOM/power, SIGKILL, broken original restart, or interrupted recovery may leave an outage; auto-recovery is attempted, not guaranteed.

If `RECOVERY_FAILED`: inspect `docker ps -a`, the `qwen38-27b` trial ID/label, port :8000, GPU use, and `qwen38-flash` **before** manually restarting old service; never start two GPU inference containers together. No automatic image or model cache deletion, no permanent service switch, no PR merge. A GPU trial only becomes evidence when **actually run on DGX** and its original API return separately verified.

Source CPU CI `ea28b0c0`: **354/354 PASS, 16 suites**. **GPU trial has NOT been executed as of this document update.**

---

## 2026-11-06 — CPU import audit correction for vLLM ModelOpt mixed name

The first actual DGX `--execute-cpu-only` invocation proved Python imports of Qwen3.5 and ModelOpt modules/classes (five checks passed). The lone `modelopt_mixed_cli_name=false` was a **probe implementation error**: `ModelOptMixedPrecisionConfig.get_name(self)` is an instance method and cannot be called without an instance. The import tool now checks the public vLLM factory `get_quantization_config("modelopt_mixed")` returns the same class as `ModelOptMixedPrecisionConfig`. The tool does not instantiate a config or start a vLLM engine. `schema_version=2` results add `quant_registry_module_imported`, `quant_registry_factory_present`, `modelopt_mixed_registry_class_matches`, and `quantization_name_verification=public_registry_factory_class_identity`; the original `modelopt_mixed_cli_name` field is retained with corrected semantics.

New source CPU CI `0a14f189` run `42121160545`: **336/336 PASS**. New implementation **not yet run on DGX**.

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only
```

This bounded runc test allocates **no GPU**, loads no model weights and leaves original Flash-Next untouched. `vllm._C` / CUDA runtime warnings in a CPU sandbox do not alone establish actual serving compatibility or incompatibility. Even all-true CPU registry evidence must retain `runtime_qualified=false` and `launch_authorized=false`. Do **not** run previewed Docker GPU command.

---

## 2026-11-06 — Post-serve-split DGX receipt and CPU-only import diagnostics

Actual DGX after update through `99dde4c`: `./scripts/serve_27b.sh --status` succeeded as a read-only audit of immutable revision `482ca0f3832238542f8f5295dde86b5f22711d80` (ModelOpt FP8 208 + NVFP4 193, 401 total). `./scripts/serve_27b.sh --plan` returned `api_identity_confirmed=true` for current Flash-Next `:8000`, original `qwen38-flash` local image ID equal to target 27B candidate ID, and a **blocked non-executable** `modelopt_mixed` 8192/seqs1/0.70/eager argv. No Docker run for 27B or service stop/change occurred.

Next **separate and explicit CPU-only test** (does not request a GPU, weights or API port):

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./scripts/temporary/p2-27b-loader-import-audit.sh --plan
./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only
```

`--plan` is metadata-only (`docker image inspect`). `--execute-cpu-only` starts one transient `--rm --runtime runc --network none --read-only --memory 2g --cpus 2` container with no GPU/port/weights mount. It checks Python import of installed `vllm.model_executor.models.qwen3_5` and `...quantization.modelopt`, model/config classes and `ModelOptMixedPrecisionConfig.get_name()==modelopt_mixed`. This is **not a model load or actual GPU test**; restricted sandbox import failures do not alone prove GPU incompatibility. Do not execute `command_preview`; 27B start/switch/rollback are blocked pending separately scoped GPU transition approval. Source CI `834c750`: **333/333 PASS**.

---

## 2026-11-06 — Separate serving script layout

The model-specific server entrypoints are now:

```text
scripts/
  serve.sh                 # compatibility dispatcher; default REAL Flash-Next start
  serve_flash-next.sh      # original Flash-Next executable logic (PLE/MTP/QSA)
  serve_27b.sh             # NVIDIA pinned 27B (currently read-only plan/status only)
```

`./flash serve` continues to call the Flash-Next-specific implementation and should never be used as a 27B launcher. The direct old `scripts/serve.sh` CLI remains valid for existing Flash-Next deployments; `scripts/serve.sh 27b --plan` dispatches only to the guarded P2 preview.

After clean fast-forward in DGX (without interrupting original API), safe NVIDIA 27B commands:

```bash
./scripts/serve_27b.sh --status
./scripts/serve_27b.sh --plan
# equivalent:
./scripts/serve.sh --model 27b --plan
```

The first prints immutable P2 metadata/source status, the second inspects **read-only** 27B dedicated launch candidate and the current Flash-Next localhost API identity. Plan JSON must remain `status=BLOCKED`, `plan_id=null`, `operations_enabled=false`; it is **not** a valid approval to execute `command_preview`. `./scripts/serve_27b.sh --execute` is explicitly refused until a GPU-qualified P2 runner with per-action exact approvals and tested recovery exists. The 27B candidate retains pinned NVIDIA ModelOpt `MIXED_PRECISION` FP8/NVFP4, no Flash-Next PLE/MTP inheritance, and one GPU serving model at a time. No DGX 27B load/benchmark/rollback has yet been run.

---

## 2026-11-06 — DGX source evidence and dedicated 27B startup preview

DGX operator verified exactly pinned modelopt `MIXED_PRECISION`: **208 FP8 + 193 NVFP4 = 401** quantized layers, all metadata checks clear. The installed Docker image's registry/Qwen3.5 class/ModelOpt AST check reported **4/4 true**, static scope `SOURCE_SURFACES_PRESENT_UNQUALIFIED`. Neither result is a GPU kernel or model-loading verification. Existing Flash-Next remains the sole inference service at host port 8000.

New standalone P2 preview:

```bash
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh model 27b plan --for-action start --launch-preview --json
```

This audits currently running Flash-Next container identity and **only local** `http://127.0.0.1:8000/health` and `/v1/models` (no inference calls). Expected JSON always `status=BLOCKED`, `plan_id=null`, `operations_enabled=false`. A `command_preview` array describes the **27B-specific, untested** candidate: exact pinned snapshot, immutable local Docker image ID, ModelOpt `modelopt_mixed` (vLLM v0.32 docs), 8192 initial max context, one concurrent seq, 0.70 GPU memory utilization, eager, no PLE or MTP flags; no image rebuild or global CLI defaults. **Do not execute command_preview manually.** No GPU, Docker run/stop, model switch, port ownership changes or automatic recovery occurs.

There are two independent source/identity problems to solve before executable code may be enabled: locally registered source symbols do not prove Python module import/CUDA/FlashInfer kernels; the OCI **local image ID** is not a verified registry digest or source tree commit. Actual memory and context, startup, API identity, chat/tools/vision, benchmark, and protected original Flash-Next rollback remain unverified. These require an explicit approved transition plan with live revalidation and no simultaneous models.

Official vLLM v0.32 references: https://docs.vllm.ai/en/v0.32.0/api/vllm/model_executor/layers/quantization/modelopt/ and https://docs.vllm.ai/en/v0.32.0/features/quantization/ .

---

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

