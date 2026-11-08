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

## 2026-11-08 — P5 source implementation and acceptance update (not GPU released)

P5 source was committed to the existing feature branch and Draft PR #1 as [33adec1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/33adec182e97a8eac0d5584bdf73f1448bdd84f2), with [GitHub Actions 42429745463](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463) **SUCCESS** including the new 20/20 CPU/Fake-DGX tests and `--cpu-only --json` PASS. Additional detailed per-case JSON and profile inspection enhancements require independent follow-up CI.

Implemented source: `recipes/qwen38-orcarouter.runtime.json` (pinned, **unqualified**, launch forbidden), imported YSLAB safetensors/manifest/BF16 PLE audit and immutable MTP overlay code under `scripts/p5_vendor`, donor 3-shard SHA256 / 31 BF16 name audit when local files exist, distinct MTP0/MTP2 candidate recipes, Wizard `p5` and `model orcarouter-flash-next` routes, `scripts/temporary/p5-one-shot-acceptance.sh`. The vendor overlay builder is **not** executable via CLI and no HF asset changes were authorized. Prior Blazux BF16 PLE source markers pass static inspection only; compressed-tensors and MTP2 runtime ABI/quantized lm_head/CUDA graph compatibility in actual vLLM 0.32 remain unqualified.

No DGX command/active-state reread or GPU/API/benchmark/rollback was performed in this session. All live P5 stages are NOT_RUN, `--gpu-trial` permanently BLOCKED until a separate operator approval and verified image/rollback implementation. Preserve 27B and :8000/ONE_ACTIVE_MODEL_ONLY, other models/caches, P3 historical receipts, no P4 deletion/P6 switch/P8 tests or Draft PR merge. New source/runbook: `docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md`.

---

# P5 — Orcarouter BF16PLE on Blazux vLLM 0.32: implementation and one-shot acceptance contract

**Prepared on 2026-11-08 for the NEXT conversation. This document is a design/implementation contract; P5 has NOT been implemented or executed on DGX in this session.**

## Operator decision

P5 is the implementation of Orcarouter Flash-Next from [YSLAB-ai's BF16PLE DGX Spark reference](https://github.com/YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark) **inside the existing Blazux Wizard, service/recipe/manifest and vLLM 0.32.0 runtime**. Do **not** deploy the YSLAB standalone Docker image or retain its own server/port as production infrastructure. Implement as much of the adapter, preparation, lifecycle, tests, and source-only integrated automatic judge as practical in one coherent batch. GPU tests are separate from code and require operator-approved downtime. The user will start P5 in a NEW conversation; this handoff changes no running service.

## Pinned source comparison (must re-check in the next conversation)

- Current Blazux fork: `kjlee-inlct/qwen3.8-Flash-DGX`, `feature/recipe-wizard-handoff`, pre-handoff HEAD `ac88693196a8b2b5efc95f091dc88531d6951037`, existing PR #1 Draft/Open/Unmerged, CI [42405103774](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42405103774) SUCCESS (source CPU/Fake-DGX: 902/902, 41 groups). Re-query latest HEAD/PR/CI in the new conversation.
- YSLAB reference code: `YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark@9492b78c6bc04638587b42f2ffeb0680b0fcb3ef` (main; verify if updated). Source files: `compatibility.json`, `README.md`, `docs/COMPATIBILITY.md`, `docs/HOW-IT-WORKS.md`, `Dockerfile`, `src/recipe/{manifest,download,audit,hybrid,mtp,runtime,safetensors,cli}.py`, `src/vllm_ple_mmap.py`, five `src/patch_*.py`, tests and `results/orcarouter/*`.
- Parallel design branch **not merged**: `feature/orcarouter-bf16-adapter@620598c30cfe3521af99a935caf0baf5b83556d8`, important `docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md`. Review/reuse selectively, do not overwrite current branch, cherry-pick blindly or create a new PR.
- Blazux upstream `blazux/qwen3.8-Flash-DGX` and vLLM 0.32.0 are the runtime authority. YSLAB Dockerfile pins `vllm/vllm-openai:qwen38-flash-next@sha256:fc120ece...`, with `ai.yslab.vllm.version=0.1.dev20073+g8e685d198` and a different model layout; YSLAB runner defaults to port **18300**. These are NOT the current production runtime or API. Re-map imports, model class names and execution flags on **vLLM 0.32**, maintain host API **8000** and `ONE_ACTIVE_MODEL_ONLY`.

## Model/checkpoint and PLE constraints

- Base gated checkpoint: `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799`. HF browser-access terms/token may be required; never log auth secrets. Existing DGX Orcarouter cache was observed by P4; presence is **not** pinned/checksum/loader qualification, and does not authorize redundant download.
- Checkpoint uses `compressed-tensors` and direct **BF16 PLE**, distinct from Blazux NVIDIA/RadixArk ModelOpt hybrid. YSLAB expectations: 128 PLE tensors, 320001536 total rows, width 160, dtype BF16, layer 1, 128 split parts, 95.37 GiB file-backed. No blanket NVFP4-to-FP8 conversion or touching original safetensors/index.
- MTP OFF must have a valid vLLM-0.32 loader/PLE mmap baseline. In the same implementation batch, also provide opt-in 31/31 native BF16 MTP overlay and `MTP=2` recipe with isolated validation; the stages are tested independently (baseline fail does not silently promote MTP).
- MTP source pinned `RadixArk/Qwen3.8-Flash-Next-NVFP4@7b719225242aacd3dbd3f9407468c2ee9a9d2594`, exactly 31 native BF16 MTP tensors from three pinned donor shards, each subject to name, size, SHA-256, dtype/shape, config/arch compatibility and runtime load guard. Overlay is immutable/local derived view; preserve Orcarouter original, donor/source and other HF cache, and redact private paths in reports.
- YSLAB qualified runtime (reference, **not Blazux acceptance**): PIECEWISE capture, BF16 KV, MTP=2, 262144 context, 8 sequences, 0.8 GPU utilization, no PLE prewarm; its reported 44.23 tok/s MTP2 vs 27.26 tok/s MTP0 is a **YSLAB-specific measured observation**, not a P5 performance gate. Validate compatibility with vLLM 0.32 and DGX memory before adopting each value.
- Previous Orcarouter API compatible ID: `qwen3.8-flash-next-orca-uncensored-bf16-mtp`. Keep distinct from NVIDIA Flash `qwen3.8-flash-next` and 27B `qwen3.8-27b`; exact ID selection remains an explicit manifest decision, with MTP OFF baseline not falsely claiming MTP2 identity.
- The YSLAB `src/vllm_ple_mmap.py` and `patch_qwen4_exp_*` are **references**, not patches safe to append to the current image without ABI/import/graph path checks. Compare to Blazux `src/vllm_ple_mmap.py`, Qwen4Exp class/loader, compressed-tensors mapping, lm_head and QSA splitting, speculative decode.

## Work package to implement together in the new session

1. **Preflight/source map:** fetch latest HEAD, source trees and model manifest, identify exact ABI/patch differences; inspect local service-policy and existing Orcarouter cache metadata **read-only**. No stale P3 replay.
2. **Manifest/recipe/asset registry:** add `recipes/qwen38-orcarouter.runtime.json` (or exact qualified name) and schema/validation, frozen source revisions, image provenance, output model ID, protected cache and immutable derived view, `runtimes/service-policy.json` and discovery integration, per-model diff/replace idempotence.
3. **Loader/PLE adapter:** checkpoint-specific vLLM 0.32 compressed-tensors loader and BF16 direct mmap, 128-tensor mapping, no quantized head assumptions, piecewise graph boundary and startup safety, no default NVIDIA/RadixArk mutation.
4. **MTP overlay:** validated copy-by-reference/reproducible local overlay from 31 BF16 tensors, no copy into the original snapshot, independent MTP0 and MTP2 profile, exact runtime load guard (fail closed).
5. **Wizard UX:** implement `./wizard.sh model orcarouter-flash-next ...` / `./wizard.sh p5 ...` paths for doctor/recipe/prepare/start/verify/benchmark/status and history. Source-only `--plan`/`--dry-run`, exact approval when actions cause downloads/cache writing or planned service downtime; do not duplicate YSLAB's separate control plane.
6. **One-shot temporary judge:** add `scripts/temporary/p5-one-shot-acceptance.sh` and manager controller with `--plan`, `--cpu-only` (no host mutations), `--read-only` (DGX cache/Docker/API/ownership validation), and separate `--gpu-trial`/`--execute` **only after** a newly generated exact, expiring, operator-entered approval and explicit downtime acknowledgment. JSON results have per-gate PASS/BLOCKED/NOT_RUN/INCONCLUSIVE and a final evidence-backed status, nonzero exit on blocked; sanitized, append-only receipts, deterministic fixtures. Never auto-approve or silently progress from read-only to GPU.
7. **Tests in same batch:** CPU/Fake-DGX mocks for manifest schema/compatibility, pinned donor integrity and 31/31, unsafe paths/symlinks, checkpoint mismatch, model identity, vLLM ABI, PLE BF16 scale-free, MTP0/MTP2, command exactness, memory/disk budgets, rollback/partial failure, duplicate containers/ports, label ownership, blocked execution, redaction, idempotence and no regression of P1/P2/P3/P4.
8. **Runtime evaluation only after consent:** MTP OFF first, then MTP2; API identity `/v1/models`, Chat, Completions/Responses where supported, tool-call roundtrip and Open WebUI native-tool compatibility, reasoning, SSE/streaming, tokenizer and finish reasons; vision only if truly supported, benchmark TTFT/tokens/s/latency/VRAM and context/concurrency, numerical logprob parity with defined baseline. Collect receipts and restore verified prior 27B under the explicit trial/restore contract. One active GPU model and one :8000 owner throughout.
9. **GitHub completion:** update source/tests/permanent docs/acceptance and handoff in the existing branch, run GitHub CI and actual DGX operator-side one-shot when authorized, update Draft PR #1, no merge without separate consent. Distinguish code-ready/CPU PASS/real GPU PASS/production release.

## One-shot automatic adjudication (design contract; script does not exist yet)

Suggested CLI after implementation:

```bash
bash scripts/temporary/p5-one-shot-acceptance.sh --plan --json
bash scripts/temporary/p5-one-shot-acceptance.sh --cpu-only --json
bash scripts/temporary/p5-one-shot-acceptance.sh --read-only --json
# A separately reviewed/approved --gpu-trial is NOT part of automatic dry-run.
```

The unified read-only/bounded CPU output should cover source revisions, recipe schema, existing cache, disk/MemAvailable gates, vLLM 0.32 ABI/registry, PLE and MTP integrity, service/current ID, :8000 ownership, test totals, benchmark/evidence readiness and exact blockers. A `PASS` for CPU/metadata must not imply GPU load, inference, compatibility, benchmark, model switch, restoration or production acceptance; unknown conditions return `INCONCLUSIVE` or `BLOCKED`, never invented PASS.

## Operational rules / other stages

- Current active service last operator-observed: 27B `qwen38-27b`, API `qwen3.8-27b`, port 8000, service verified. Re-check just before a real operation. Preserve active 27B, stopped NVIDIA Flash, Orcarouter cache, Open WebUI, Portainer, P3 receipts and HF sources.
- The existing P4-A real inventory and P4-B/C combined real dry-run **PASS/CLOSED only read-only**. P4-C actual deletion adapter is absent/unreleased. P5 may use P4 capacity evidence, but actual deletion if P5 becomes blocked by storage needs another specific, fresh operator decision and an independently reviewed exact-resource plan. No implicit prune/removal.
- P3-A/B/C/G historical real transfer PASS/CLOSED: no replay. P6 actual Orcarouter↔27B switching (beyond a specific P5 bounded trial/restore) remains separately scoped. P8 fault injection, automatic fault recovery, Flash reinstall, lifecycle release and final operations signoff remain NOT_RUN/NOT_RELEASED.
- vLLM **0.32.0**, not YSLAB's 0.1.dev image, no SGLang, port **8000**, `ONE_ACTIVE_MODEL_ONLY`, immutable HF cache and pinned revisions, no `git reset --hard`/`git clean -fd`, no silent Docker rm/prune, no approval-token bypass, no unapproved service interruption, no PR merge.
- Historical strict logprob first-token pairwise absolute `1e-4` release gate was previously unresolved. Do not silently waive, re-label or claim parity without a defined comparable baseline and real evidence.

## Deliverables and acceptance statuses

`SOURCE_IMPLEMENTED`, `CPU_FAKE_DGX_PASS`, `REAL_DGX_READ_ONLY_PASS`, `TRIAL_APPROVAL_REQUIRED`, `REAL_DGX_MTP0_PASS`, `REAL_DGX_MTP2_PASS`, `REAL_DGX_INFERENCE_PASS`, `REAL_DGX_BENCH_PASS`, `RESTORED_27B_PASS`, `NUMERIC_GATE_PASS/FAIL/INCONCLUSIVE`, and separate `PRODUCTION_RELEASED=false` until P8. Each field must reflect evidence or explicit NOT_RUN. Report WHAT CHANGED / GITHUB HEAD-PR-CI / TESTS / DGX / SAFETY / BLOCKERS / NEXT.
