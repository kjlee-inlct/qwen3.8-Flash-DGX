## 2026-11-08 current P5 v2 supersession (document-wide audit)

The complete [document inventory and consistency audit](HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) and [current **P5 QSA+LM-head v2** DGX trial runbook](P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md) supersede earlier P5 source-only / GPU NOT_RUN descriptions and older QSA-only commands. Latest actual DGX **QSA-only** trial failed after 15/17 safetensors shards with missing `lm_head.weight_scale`; the candidate v2 source/CPU CI passed but **v2 GPU load is not proven**. Current v2 adapter is `qwen4exp-qsa62318-lmhead-v032-v2` and its **new** target is `qwen38-orcarouter-qsa62318-lmhead`. Actual current :8000 service state remains unobserved since that failed trial. Previous 27B and failed candidate images/containers are preserved. Never copy the earlier QSA-only `execute` commands without revalidation. vLLM=0.32.0, one active model, :8000; P6/P8 live operations and PR #1 merge remain out of scope. Older sections below remain historical.

---

## 2026-11-08 — Shared Wizard manifest registry and managed Orcarouter PLE

**Implemented (source/CPU):** `runtimes/manifest-registry.json` is the Wizard's canonical shared registry for service policy, model discovery, the canonical 27B recipe, the Orcarouter source-only recipe, YSLAB compatibility and a **new first-class PLE asset registry** `runtimes/ple-assets.json`. `scripts/manager/manifest_registry.py` centralizes bounded strict JSON loading, duplicate-key/non-finite/symlink rejection and all model/recipe/PLE/donor/service cross-reference checks; `./wizard.sh manifest status --json` and `./wizard.sh manifest validate --json` are read-only and do not check the GPU. PLE asset `orcarouter-bf16-ple` is now referenced by the P5 recipe, service policy and model discovery; canonical `scripts/manager/ple_assets.py` performs local pinned header/weight-map checks and reports metadata status independent of GPU. Wizard P5 status/doctor, model installed list, service status and model-first selector expose the asset appropriately. These interfaces **never authorize deletion/overlay, Docker mutation or runtime activation**.

[Source commit a17b3618](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/a17b3618fab98aa5b849359d464c0d7698fae4a0) passed [Actions #42433160630](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42433160630), including 996 executed CPU test cases across 44 unittest invocations (duplicates included), manifest registry contract/drift and new PLE asset mocks. Final model-first selector/documentation follow-up requires independent CI. Read detailed decisions and commands in `docs/WIZARD-MANIFEST-REGISTRY-AND-PLE-ASSETS-20261108.md`.

**Actual DGX evidence:** the operator's supplied previous-HEAD console output showed `qwen38-27b` serving `qwen3.8-27b` on :8000, Orcarouter pinned BF16 PLE 128/128 header/shape PASS, MTP 31/31 donor tensors and all 3 donor SHA256 PASS; GPU Orcarouter not started. This observation predates the manifest code and does not verify its new DGX integration. The P5 GPU loader/overlay/bench/rollback and P8 release remain NOT_RUN. Preserve 27B, :8000/ONE_ACTIVE_MODEL_ONLY, all HF assets and historical receipts; P3 replay/P4 delete/P6 switch/P8 fault/PR merge remain unauthorized.

---

## 2026-11-08 — P5 vLLM 0.32 source patch candidate; image not built

Verified the official `vllm-project/vllm@v0.32.0` Qwen4Exp `model.py` and `mtp.py` static anchors (one occurrence each). v0.32 `CompressedTensorsConfig.ignore` is separate from `ignored_layers` and `exclude_modules`, requiring a scoped remap for donor MTP BF16 bypass.

`src/p5_patch_qwen4exp_v032.py` is the **P5-only optional source patch** for quantized LM head, compressed-tensors ignore remap, and strict 31/31 native BF16 MTP name/dtype guard. Other models are unaffected when `VLLM_P5_ORCAROUTER` is unset. The source candidate requires exactly installed vLLM 0.32.0 and fail-closed anchor matching. `Dockerfile.p5.candidate` has no fixed base; its required `P5_QUALIFIED_BASE_IMAGE` must be provided only after independently verified Blazux v0.32 image pin and explicit image-build permission. `P5_EXPLICIT_IMAGE_BUILD=1` permits source patching *inside that isolated candidate image build only*; **no image has been built or loaded**. `tests/test_p5_vllm032_patch_cpu.py` validates pure-source patch behavior without Docker/GPU. Actual ARM64 ABI, GPU model load, MTP0/MTP2 API, OpenWebUI and benchmark remain **NOT_RUN**.

This is not permission to run `docker build`, generate a multi-GB BF16 MTP overlay, interrupt the active 27B on :8000 or merge Draft PR #1. Existing standalone source-only one-shot `--gpu-trial` stays BLOCKED. Await final CI for this addition before reporting test PASS.

---

# P5 — Orcarouter BF16PLE: source implementation, CI and DGX read-only runbook

Date: 2026-11-08. Runtime authority: **Blazux vLLM 0.32.0**, port **8000**, policy **ONE_ACTIVE_MODEL_ONLY**. Existing branch `feature/recipe-wizard-handoff` / PR #1 Draft, not merged.

## Source and evidence

Pinned YSLAB reference: `YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark@9492b78c6bc04638587b42f2ffeb0680b0fcb3ef`. Pinned Orcarouter source: `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799`; gated HF token requirements apply, secrets must not be logged. Donor: `RadixArk/Qwen3.8-Flash-Next-NVFP4@7b719225242aacd3dbd3f9407468c2ee9a9d2594`.

The YSLAB manifest, safetensors header auditor, checkpoint auditor and deterministic BF16 MTP overlay creator were imported as pinned Apache-2.0 **source** under `scripts/p5_vendor/`. LICENSE/NOTICE are preserved. The YSLAB vLLM development container, its Dockerfile, and its independent port 18300 were **not deployed**. Existing Blazux `src/vllm_ple_mmap.py` already has BF16 table support, but static hook/syntax inspection cannot establish installed vLLM0.32/ARM64 compatibility.

Source commit [33adec1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/33adec182e97a8eac0d5584bdf73f1448bdd84f2) passed [Actions 42429745463](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463) including 20/20 new CPU/Fake-DGX tests and one-shot `--cpu-only --json` PASS. Later per-case JSON enhancement and this documentation update require their own CI. The current source recipe `recipes/qwen38-orcarouter.runtime.json` remains `launch_allowed=false`, `register_as_runtime_recipe=false`, `runtime.image_id=null` and is deliberately not the qualified 27B production launch recipe.

## Acceptance matrix

| Gate | Code readiness | Measured DGX evidence |
| --- | --- | --- |
| PLE direct BF16 | 128 tensors, 320001536 rows, width 160, exactly 102400491520 BF16 bytes, no scale, index/header audit imported | NOT_RUN in this session; no pinned local checkpoint accessed |
| MTP donor | 31 exact tensor names, 3 donor shards each pinned by size and SHA256, source overlay creator imported | NOT_RUN; full 3-shard SHA/shape and on-GPU load-count not demonstrated |
| MTP OFF | Opt-in candidate profile, distinct served ID, PLE mmap candidate in Blazux | GPU/API/BENCHMARK NOT_RUN |
| MTP=2 | Separate candidate profile, donor/overlay fingerprint and source guard metadata | Overlay construction, quantized lm_head/MTP loader/CUDA graph ABI, GPU/API/BENCHMARK NOT_RUN |
| Numerical parity | strict first-token logprob absolute threshold 1e-4 retained | NOT_RUN / not waived |
| Service safety | GPU executor disabled, no approval plan, :8000 single-model policy | Historical 27B active evidence only; no fresh DGX read-only run |
| Release | source CI PASS | NOT_RELEASED; P6/P8 separate |

The vendor `build_mtp_overlay` is intentionally **not invoked** by the Wizard or one-shot, because it creates large immutable derived files that require separate asset-write approval. Do not manually treat source presence as permission to generate an overlay. MTP0 and MTP2 model IDs are proposed and separate from NVIDIA Flash/27B; the actual Orcarouter served identity remains null in live service policy until verified.

## Commands permitted on an operator-managed DGX (read-only)

Before inspecting, check the repository state; a dirty worktree must be reconciled by the operator instead of overwriting:

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
git rev-parse HEAD
./wizard.sh service manager status --json

bash scripts/temporary/p5-one-shot-acceptance.sh --plan --json
bash scripts/temporary/p5-one-shot-acceptance.sh --cpu-only --json
bash scripts/temporary/p5-one-shot-acceptance.sh --read-only --json

./wizard.sh p5 recipe --profile mtp0 --json
./wizard.sh p5 recipe --profile mtp2 --json
```

`--read-only` uses configured pinned cache roots, strict PLE header/weight-map inspection and complete SHA256 of the three donor shards **if present**. This may create significant read I/O and should be scheduled accordingly, but it does not write HF assets or touch GPUs. Source-only `--cpu-only` reports case-by-case PASS/FAIL and retains GPU stage as NOT_RUN. `--plan` outputs a review fingerprint, never a consent token. Exit code 0 means **only** the requested CPU/read-only scope PASS, never a live model qualification. A blocked request uses exit code 3, with issues and individual gate statuses.

The `--gpu-trial` mode and even `--approve-plan`/downtime ACK combinations return BLOCKED because `GPU_EXECUTION_RELEASED=False` and the backend is absent. Do not copy the YSLAB Dockerfile into the DGX or bypass this gate. A future separately approved runtime trial requires pin-verified Blazux vLLM0.32 image digest and ABI, pinned origin/donor audit, asset-write consent and immutable derived overlay (for MTP2), exact active 27B API/container proof, rollback and fresh expiring TTY authorization. Test MTP0 then MTP2 independently, including model IDs, reasoning/tools/SSE/Open WebUI compatibility and real TTFT/throughput/latency/concurrency/long context/VRAM; publish measured results only after actual execution. Preserve strict 1e-4 numerical release criterion until comparable evidence exists.

No Docker stop/start/rm/recreate/prune, image replacement, 27B downtime, original checkpoint edit, P3 replay, P4 actual deletion, P6 switching, P8 faults or PR merge is authorized by P5 source work.
