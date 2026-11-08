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
