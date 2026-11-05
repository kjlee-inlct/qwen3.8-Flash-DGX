# P2 — Qwen 27B Wizard source readiness (2026-11-05)

## State and evidence boundaries

P1 NVIDIA Flash-Next now has real DGX `verify=PASS` including basic
Completions/Chat and optional Tools/Vision, and a bounded `benchmark=PASS`
reported by the operator. Original P1 model and `:8000` stay protected.

P2 is **not** yet runnable. The draft 27B candidate is
`RadixArk/Qwen3.8-27B-NVFP4`, an upstream published ~22 GB NVFP4 file
set (public metadata only). The model card is oriented around SGLang
4-GPU deployment; that is **not** proof of vLLM 0.32 on single GB10.
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

- https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4
- `scripts/manager/p2_27b_inventory.py` and `wizard/menus/models/qwen_27b.py`
- `handoff/OPERATING-RULES.md`, `handoff/NEXT-ACTIONS.md`
