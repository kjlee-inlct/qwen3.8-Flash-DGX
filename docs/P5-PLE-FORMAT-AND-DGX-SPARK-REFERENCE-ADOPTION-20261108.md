# P5 PLE format-independence, safe model switching, and DGX Spark research — 2026-11-08

## New operator authorization and boundary

The operator confirmed on 2026-11-08 that this is a **development DGX, not a currently required production service**. Stopping the running 27B service and using the GPU for P5 tests is acceptable. This authorization changes the P5 test scheduling constraint; it does **not** mean a candidate ABI/image has been qualified, nor does it permit deletion of any source model, HF cache, old image, receipt or recipe, or merging PR #1. Revalidation of an exact current service identity and a rollback plan still precedes an actual one-model transition. This source-only commit **does not** stop or start any DGX container.

## First-class PLE asset format vs model-body quantization

`runtimes/ple-assets.json` is now **schema v2**. It declares per-asset `format.storage_dtype`, `scale_mode`, `scale_dtype`, `scale_block_shape`, `packing`, `placement.table_memory`, `offload_backend`, `tp1_executor_requirement` and `validated_on_gpu`. Its storage format is explicitly independent from the inference model's compressed-tensors/NVFP4/MXFP8 quantization, MTP donor format and KV-cache dtype.

`scripts/manager/ple_format.py` validates supported *declarative* formats, size arithmetic and scale structures without assuming BF16. Registered encodings: BF16, F16, F32, F8_E4M3, F8_E4M3FN, F8_E5M2, I8 and U8, with ELEMENT_ALIGNED packing only; int4/variable bitpacking and other formats require a later explicit schema/loader adapter. Supported scale mode declarations: NONE, PER_TABLE, PER_TENSOR, PER_ROW, PER_BLOCK. In PER_TABLE the single scale can be BF16/F16/F32; no per-shard scale count must be invented. PER_ROW and PER_BLOCK scale memory is **unknown without a verified header and actual block layout**. A valid declaration does **not** constitute a working loader.

The currently pinned Orcarouter source is unchanged and still **BF16 with no scale**: 128 tensors × width160, 320001536 rows, 102400491520 payload bytes, original revision `3a3b63161c0745390e5270179af42e46efc70799`. `orcarouter-bf16-ple` remains `metadata PASS` on the provided DGX observations, GPU mmap NOT_RUN. The independent PLE controller can register additional assets and reports their dtype/scale/placement; unqualified future formats can never show false metadata PASS.

## Independent engine/ABI loader capability matrix

`runtimes/ple-loader-profiles.json` is registered through the Wizard's shared `runtimes/manifest-registry.json`. It binds the current Orcarouter BF16 PLE asset to a candidate vLLM **0.32.0**, `linux/arm64`, `NVIDIA_GB10_SM121A` loader profile with an **unset** runtime image digest, unverified CUDA load, TP=1 worker, mmap, API identity, tools, benchmarking, and rollback. Autostart stays disabled. `recipes/qwen38-orcarouter.runtime.json` references exactly this profile. The matrix also records external reference examples for alternate FP8 and disk-backed PLE encodings, explicitly non-executable and not qualified on Blazux 0.32.

A target model can have no PLE, a new BF16 PLE, or another independently registered FP8/etc PLE. The model-discovery/service-policy entries bind the model to its PLE `asset_id`; not all model choices require a PLE. Exact runtime identity includes **engine version/image digest, model checkpoint revision, PLE asset/source revision, PLE dtype and scales, placement backend, profile/MTP configuration, port and tool parser**. Any mismatch prevents silent container reuse or automatic aliasing.

## Model and PLE transition contract

`scripts/manager/ple_format.transition_contract()` and `service_transition_preview.preview_transition()` expose the change types `NO_PLE`, `LOAD_PLE`, `UNLOAD_PLE`, `CHANGE_PLE_DTYPE`, `REPLACE_PLE_ASSET`, `RELOAD_PROFILE`, `SAME_ASSET`. There is **no unverified in-process hot swap**. The intended transaction order is:

1. Re-observe Docker, actual API served ID, GPU occupancy and :8000 process owner. Pin original image digest, recipe, source snapshots, PLE mapping and rollback evidence.
2. Resolve target checkpoint's declared PLE asset, dtype, scale mode, memory placement and qualified **engine-specific loader**. Validate filesystem capacity and mapped/offloaded table size; do not assume disk mmap always works on TP=1.
3. Execute an exact, separately guarded trial/plan when an audited vLLM0.32 candidate image/ABI is present. Existing model is stopped before target starts on :8000. GPU memory and old PLE mmap/IPC workers must be released.
4. Start one target, verify worker/PLE mmap handshake, exact API served ID, chat/stream/native tools, bounded MTP0 then MTP2, real numerical and throughput/TTFT. Never treat a successful header audit as a GPU load.
5. On failure, stop only the failed target, unmap PLE, restore the original model/image/recipe/service on :8000, confirm served ID and journal the final observed state. On success, keep source assets/images/receipts; deletion is a separate scoped action.

`read_only` now accepts an observed healthy 27B **or** a genuinely idle/port-free DGX as a service preflight PASS, but neither case proves exclusive GPU residency. An unknown :8000 listener or unexpected active model still blocks.

## Research inputs and integration lessons (not runtime dependencies)

1. [dolf3131/dgx-spark-llm-serving, pinned commit 45e3d47771577dabab0998e9013e85dd0915ae4f](https://github.com/dolf3131/dgx-spark-llm-serving/tree/45e3d47771577dabab0998e9013e85dd0915ae4f) documents separate inference **lanes** and their actual test state. [vLLM NVFP4 lane](https://github.com/dolf3131/dgx-spark-llm-serving/blob/45e3d47771577dabab0998e9013e85dd0915ae4f/lanes/vllm-nvfp4/README.md) describes NVIDIA NVFP4's F8_E4M3 PLE table shards with **one BF16 per-table scalar** even while the body uses MIXED_PRECISION; its vLLM patch corrects the mistaken quantization-config class gate. That external lane also describes a TP=1 PLE-offload hang with a uniproc executor and forcing `--distributed-executor-backend mp` in its version, plus a checkpoint-specific MTP `k` sweep. Use these as **audits and negative tests**, not patches to copy into vLLM0.32 blindly.
2. [NVIDIA forum thread, 2026-10-16](https://forums.developer.nvidia.com/t/nvidia-official-qwen3-8-flash-next-checkpoint-for-single-dgx-spark/385994) describes a different new [`nvidia/Qwen3.8-Flash-Next-FP4-Local`](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local) checkpoint/recipe. The model card's suggested container is a B12X derivative, **not this project's pinned vLLM0.32**. It uses `VLLM_PLE_TABLE_MEMORY=disk` and an io_uring backend, plus FP8 KV and model-specific MTP. It warns about compressed scales requiring that environment. Its benchmark figures and launcher flags are **not evidence of Blazux 0.32 compatibility**, and this checkpoint is not interchangeable with the previously pinned `nvidia/Qwen3.8-Flash-Next-NVFP4` or Orcarouter.
3. The references strengthen the requirements for engine/version-specific PLE worker startup, independent per-tensor format handling, strict no-implicit-conversion, checkpoint-specific MTP tuning, and isolated rollback evidence. No model or script from either reference is copied or automatically installed.

## Reproduction and acceptance

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh manifest validate --json
./wizard.sh model list --installed --json
./wizard.sh select orcarouter --json
./wizard.sh p5 status --json
./wizard.sh p5 doctor --read-only --json
./wizard.sh service manager status --json
bash scripts/temporary/p5-one-shot-acceptance.sh --cpu-only --json
```

CPU/Fake-DGX tests `tests/test_p5_ple_format_transition_cpu.py` cover non-BF16 format arithmetic, NVIDIA-style single BF16 per-table scale, invalid scale/packing/loader declarations, BF16→FP8 and MTP profile transitions, and read-only safe P5 preview. `tests/test_manifest_registry_cpu.py` exercises the shared v2 registry, new model with FP8 PLE, external reference non-import, and loader release prevention. **CI PASS is CPU acceptance, never an actual GPU pass**.

**Still NOT_RUN:** pinned vLLM0.32 GB10 image built and ABI-tested with PLE/MTP; actual runtime load of Orcarouter, MTP0/MTP2, Native Tools, measured benchmarks and rollback. A separate GPU executor must not be enabled simply because this machine is available for downtime. The user authorizes its use once the plan is safe and the actual shell is accessible; this GitHub-only session cannot claim DGX hardware was driven.
