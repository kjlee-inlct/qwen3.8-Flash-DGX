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
