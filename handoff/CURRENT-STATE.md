# Current state — active snapshot

**Snapshot written:** 2026-11-04 (KST) · **Status:** `P0_PLANNING` · **Implementation:** docs only · **GPU:** `NOT_RUN`.

## Repository/branch tracking

| Item | Last verified state |
|---|---|
| New fork | `kjlee-inlct/qwen3.8-Flash-DGX` |
| Upstream `main` baseline | `b0aa8b77604139557169387b2fa8386355d8b651` |
| Fork `main` baseline at branch creation | `b0aa8b77604139557169387b2fa8386355d8b651` |
| **Active work branch** | `feature/recipe-wizard-handoff` — created from fork `main` |
| Parallel Orcarouter branch | `feature/orcarouter-bf16-adapter@620598c30cfe3521af99a935caf0baf5b83556d8` (as last checked) |
| Parallel Orcarouter design | `docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md` on the parallel branch |
| Old Preview repository | `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark`; frozen preservation, historic `feature/blazux-phase6-runtime-gates@2e6a5794b0fe282ae4bf6f4852acd919fea6d55a` |
| New branch exact HEAD | **Read actual GitHub branch HEAD**. Do not embed a file's own eventual HEAD as authoritative; the branch commit changes when this file changes |
| PR / CI | To be filled from GitHub after initial documentation commit/PR creation |

## Operational environment — protect; verify fresh

The existing user-operated service is **Orcarouter**. Historical prior-session values (not rechecked on DGX in this conversation):
- Container `qwen38-flash-orca-uncensored-bf16-mtp`.
- Container ID `3fc5a3d5be1d52595602287acd87895220219bad050484251ac0408a163ffc45`.
- Original image ID `sha256:b0984c4b724b6f8c0745acb654994e1bd3a6c50b75c2c76078f1bfd6b395f39a`.
- OpenAI-compatible `:8000/v1`, model ID `qwen3.8-flash-next-orca-uncensored-bf16-mtp`, existing external clients.
- Legacy workspace `~/Workspace/llm/blazux-phase6-gates`, target new workspace `~/Workspace/llm/blazux-orcarouter`.

**Actual current running/stopped status, capacity, local Docker images, local checkpoints and ports: `NOT_OBSERVED_THIS_SESSION`.** No stop/delete/launch has been performed. Do not infer the historical ID still matches.

## Stage matrix

| Stage | Source/plan | CPU/CI | DGX/GPU | Release |
|---|---|---|---|---|
| P0 inventory + recipe/wizard architecture | `PLAN_IN_PROGRESS` | `NOT_RUN` | `NOT_RUN` | `NOT_APPLICABLE` |
| P1 Flash-Next baseline | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P2 27B vLLM 0.32 | `PLANNED/COMPAT_UNKNOWN` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P3 Flash-Next ↔ 27B switching | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P4 Flash-Next file retirement | `PLAN_ONLY/APPROVAL_REQUIRED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P5 Orcarouter BF16/MTP adapter | `PARALLEL_DESIGN_ONLY` | `NOT_RUN_THIS_FORK` | `NOT_RUN` | `BLOCKED` |
| P6 Orcarouter ↔ 27B switch | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P7 operations acceptance | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |

**Outstanding historic release blocker:** same-checkpoint strict max logprob delta `<=1e-4` not satisfied in old Preview baseline, therefore do not claim Orcarouter numerical qualification.

## Current deliverables

- `docs/MODEL-RECIPE-WIZARD-PLAN.md` — stage roadmap and architecture.
- `docs/MANIFEST-CONTRACTS.md` — manifest schema intent, switch/rollback/deletion gates.
- `handoff/*` — persistent entrypoint, rules, decisions, evidence, action list and starter prompt.
- **No actual recipes, wizard scripts, API gateway, service manager or 27B adapter in this branch yet.**

## Blockers / approvals

- Need fresh read-only DGX storage/container inventory before operational choices.
- Need vLLM 0.32 source check for Qwen3.8-27B architecture, quantized `lm_head`, GDN, tokenizer and speculative support. SGLang is excluded.
- Need user-approved GPU window for P1/P2/P3/P5/P6 and explicit, exact deletion approval for P4. This documentation commit authorizes neither.
- Need plan for sufficient free disk. Do not delete existing images/cache or checkpoint automatically.

## Immediate next actions

1. Finish initial documentation commit + draft PR; refresh actual PR/CI fields here.
2. Implement **P0 read-only inventory + manifest schema validators + protection and dry-run guards**, with CPU tests. No GPUs.
3. Inspect 27B vLLM 0.32 interfaces (source-only) and draft separate 27B recipe; record `GO/BLOCKED` evidence before GPU work.

See [NEXT-ACTIONS.md](NEXT-ACTIONS.md), [EVIDENCE-LEDGER.md](EVIDENCE-LEDGER.md) and [../docs/MODEL-RECIPE-WIZARD-PLAN.md](../docs/MODEL-RECIPE-WIZARD-PLAN.md).
