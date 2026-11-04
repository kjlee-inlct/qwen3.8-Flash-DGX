# Blazux vLLM 0.32 — Recipe/Wizard Master Plan

> Status: **P0 N1 SOURCE IMPLEMENTED; N2+ PLAN ONLY / NO GPU VALIDATION** · Date: 2026-11-04 (KST) · Owner repo: `kjlee-inlct/qwen3.8-Flash-DGX`
>
> Base: `main@b0aa8b77604139557169387b2fa8386355d8b651`; planning branch: `feature/recipe-wizard-handoff`. Source evidence is not a DGX runtime validation.

## 1. Mission and non-goals

Deliver a **vLLM-only** recipe-driven single-DGX-Spark model-management system with:
- reproducible checkpoint selection, manifests, Docker image/config, API service, optional proxy/gateway, benchmarks and storage inventory;
- operator-friendly **wizard**, composable noninteractive scripts, dry-run and explicit approvals for destructive or service-affecting actions;
- safe one-active-large-model switching between Qwen3.8 Flash-Next, Qwen3.8-27B and Orcarouter Uncensored;
- rollback, audit logs and handoff that survives a new conversation;
- original Blazux NVIDIA/RadixArk recipes and upstream optimization behavior preserved.

**Out of scope for this phase:** SGLang, simultaneous residency of two large GPU models on a single 128-GB GB10, unapproved restart of the existing Orcarouter service, unapproved deletion, automatic release despite failed numeric gates. `aphex3k/Qwen3.8-27B-on-DGX-Spark` is a comparative benchmark/tuning reference **only**, not an engine dependency.

## 2. Known inputs vs unknowns

**Grounded in repository source:**
- Blazux vLLM 0.32.0 `flash`/profiles/`scripts/serve.sh`; NVIDIA and RadixArk NVFP4 Flash-Next paths supported by upstream. `serve.sh` issues `docker rm -f "$NAME"` before creating a new container: MUST guard before invocation.
- Orcarouter is a distinct `compressed-tensors` checkpoint with direct BF16 PLE (128 shards, 95.37 GiB) and an optional pinned 31-tensor BF16 MTP overlay, not interchangeable with Blazux ModelOpt hybrid conversion.
- Existing parallel design: `feature/orcarouter-bf16-adapter@620598c30cfe3521af99a935caf0baf5b83556d8` contains `docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md`. It is **not** merged into this branch.
- 27B references: `aphex3k/Qwen3.8-27B-on-DGX-Spark` and `MiaAI-Lab/Qwen3.8-27B-SGLang-DGX-Spark` document *SGLang* results; **no claim** that Blazux vLLM 0.32 directly boots 27B. Potential 27B checkpoints include `RadixArk/Qwen3.8-27B-NVFP4` and `RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead`; choose only after source audit.

**Unverified on actual DGX in this session:** free disk, current services/ports/images, checkpoint availability, 27B vLLM architecture mapping, model load and benchmarks, GPU memory headroom, compatibility of new image, rollback outcome, PR CI. All such entries start `NOT_RUN` or `NEEDS_DGX_EVIDENCE`.

## 3. Proposed stage sequence and gates

| Stage | Workstream | Exit criteria | Allowed without a separate DGX operations approval? |
|---|---|---|---|
| P0 | Read-only inventory, architecture contracts, recipe schema, safety baseline | Snapshot of exact current container/image/ports, mounted assets, disk usage, protected set; manifest schema reviewed | Read-only inspections and source/CPU tests only |
| P1 | **Flash-Next vLLM 0.32** prepare/boot/benchmark | Model loads; basic API, reasoning/tools, startup, TTFT, throughput, memory, correctness, repeatability evidence | **No**: GPU runtime requires approved window |
| P2 | **27B vLLM 0.32** compatibility/boot/benchmark | Architecture/quant/lm_head/tokenizer/vision/GDN + MTP OFF fit; measured GPU and API pass | Source/CPU audits yes; GPU no |
| P3 | Flash-Next ↔ 27B A→B→A switch | Both directions, stable alias routing, rollback and logs pass | **No** |
| P4 | Retire/remove downloaded **Flash-Next weights only as specifically approved** | P3 pass, exact deletion inventory/size, references clear, restore path documented, explicit approval | **No** (destructive) |
| P5 | **Orcarouter vLLM 0.32** adapter/boot/benchmark | Original direct-BF16 PLE MTP OFF, optional 31/31 BF16 MTP2, full API/quality/memory probes | Code/CPU yes; GPU no |
| P6 | Orcarouter ↔ 27B A→B→A switch | Repeat switch, failure injection, rollback, model IDs/client behavior, manifest consistency | **No** |
| P7 | Release/operations approval | Runbooks, replayable recipes, security/CI, numeric gate, evidence, approved cutover | **No** |

**Sequencing correction:** A model may be *retired from active operation* or its checkpoint *deleted from disk* only after an alternate, verified fallback exists. If P2 or P3 fails, **do not perform P4**. If disk is insufficient before P2, stop and request a specifically scoped cleanup decision; never infer approval from this roadmap. Existing live Orcarouter service is a separate protected asset until its migration is approved.

All stages have two statuses: **implementation** and **verification** (e.g. `DONE_SOURCE_ONLY / NOT_RUN_GPU`). Model load success is not performance or release acceptance.

## 4. Architecture

```text
wizard CLI/TUI -> plan + dry-run + confirmations
       |
       +-- recipe registry (versioned YAML; source-controlled)
       +-- inventory/storage graph (runtime facts; generated, non-secret)
       +-- image/runtime manager (Docker manifest + immutable image digests)
       +-- model manager (download, prepare, audit, verify, optional cleanup)
       +-- service manager (single active GPU model; state-machine + rollback)
       +-- API proxy/gateway (optional, introduced only with approved cutover)
       +-- benchmark/evidence collector (stable inputs, json metadata, traces)
       |
       +-- vLLM 0.32 runtime for Flash-Next / 27B / Orcarouter
```

**Reuse** existing `flash`, `profiles/`, `scripts/`, `bench/`, `tests/` instead of replacing them. Keep NVIDIA/RadixArk defaults intact; model-specific adapters are opt-in and fail closed if checkpoint assumptions do not match. The gateway routes to **one active target**. It does not magically make two huge models resident simultaneously.

Proposed full file tree (N1 subset now exists for schema, validator and intentionally invalid 27B recipe; the rest is planned):
```text
recipes/{flash-next-nvidia,flash-next-radixark,qwen38-27b,orcarouter-bf16-mtp}.yaml
wizard/{00-doctor,10-plan,20-prepare,30-verify,40-benchmark,50-switch,60-retire,70-rollback}.sh
scripts/manager/{manifest,inventory,approval,service,switch,cleanup,benchmark}.py
schemas/{recipe,runtime,service,inventory,benchmark}.schema.json
handoff/{README,CURRENT-STATE,OPERATING-RULES,NEXT-ACTIONS,EVIDENCE-LEDGER,DECISIONS,CHANGELOG,SESSION-START-PROMPT}.md
```
N1 implemented schemas/recipe.schema.json, scripts/manager/manifest.py, requirements-manager.txt and a deliberately invalid 27B candidate under recipes/. The associated CPU test fixture is synthetic. Other CLI naming/file layout are design targets, not established interfaces. Prefer shared Python core with thin shell wrappers over duplicated business logic.

## 5. Operations boundaries

- Keep the historic Orcarouter API `:8000/v1`, external model ID and existing clients untouched until approved cutover. Proxy on `:8000` cannot be bound while the existing process owns it.
- Existing runtime ID/image/volume references from older sessions are historical observations; reacquire via **read-only** `docker ps/inspect`, `ss`, `df` before making stateful decisions.
- Docker image pull/build may change storage; checkpoint download may consume huge disk. Treat download/build as separately gated resource operations and enforce quota/headroom.
- Protect HF cache blobs shared by more than one snapshot, pinned model revisions, overlay source shards, existing runtime image, volume, compiled caches and fallback snapshot.
- `serve.sh` is **not idempotent with respect to protection** because it removes the named container; use an external guard that prohibits protected `NAME`.
- No implicit model deletion, Docker prune, cache prune, or deletion because a stage calls for cleanup. Deletion is an independently approved transaction.
- A `1e-4` same-checkpoint logprob strict release blocker previously failed in the Preview work. Preserve its `RELEASE_BLOCKED` state for affected Orcarouter release until new valid proof or an explicitly recorded policy decision; benchmark metrics are not a substitute.

## 6. Completion criteria, handoff and references

A stage is complete only with: pinned source/recipe/image/weights, commands and resource impact, PASS/FAIL results, evidence artifact paths and hashes, test environment, rollback proof and release decision. Missing evidence is `NOT_RUN`, never PASS.

Every state-changing coding session must update `handoff/CURRENT-STATE.md`, `handoff/NEXT-ACTIONS.md`, and, if tests/decisions changed, `handoff/EVIDENCE-LEDGER.md`/`handoff/DECISIONS.md`. See [handoff instructions](../handoff/README.md) and [contracts](MANIFEST-CONTRACTS.md).

Reference code and design:
- [Blazux main README](https://github.com/blazux/qwen3.8-Flash-DGX/blob/b0aa8b77604139557169387b2fa8386355d8b651/README.md)
- [Existing Orcarouter adapter inventory](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/blob/feature/orcarouter-bf16-adapter/docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md)
- [Preview recipe repository](https://github.com/kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark)
- [YSLAB BF16 recipe](https://github.com/YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark)
- [aphex3k 27B performance reference — SGLang only](https://github.com/aphex3k/Qwen3.8-27B-on-DGX-Spark)
