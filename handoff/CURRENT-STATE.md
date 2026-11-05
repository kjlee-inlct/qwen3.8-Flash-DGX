# Current state — active snapshot

**Snapshot written:** 2026-11-05 (KST) · **Status:** `P0_N1_N2_SOURCE_IMPLEMENTED / N3_PARTIAL` · **Implementation:** Flash-Next default port 8000, N2 read-only Inventory and Wizard doctor/plan; **GPU:** `NOT_RUN`.

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
| Draft PR | [#1 — recipe wizard roadmap and handoff](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) against `main`; open, not merged |
| PR CI | New 2026-11-05 implementation commit 7e8f4a1: manifest 15/15 PASS, Inventory 10/10 PASS; **4 launcher tests FAIL (exit 126)** because executable mode lost. Follow-up commit restores script modes and adds regression; **recheck HEAD CI**. |

## Operational environment — protect; verify fresh

**User report 2026-11-05:** prior operating services have all been deleted; requests Blazux default NVIDIA Flash-Next on the **same external :8000/v1 API port**. This is a user-reported change, not yet independently observed with current DGX Docker/ss/df commands. Historical prior-session values (not rechecked):
- Container `qwen38-flash-orca-uncensored-bf16-mtp`.
- Container ID `3fc5a3d5be1d52595602287acd87895220219bad050484251ac0408a163ffc45`.
- Original image ID `sha256:b0984c4b724b6f8c0745acb654994e1bd3a6c50b75c2c76078f1bfd6b395f39a`.
- OpenAI-compatible `:8000/v1`, model ID `qwen3.8-flash-next-orca-uncensored-bf16-mtp`, existing external clients.
- Legacy workspace `~/Workspace/llm/blazux-phase6-gates`, target new workspace `~/Workspace/llm/blazux-orcarouter`.

**Actual current running/stopped status, capacity, local Docker images, model snapshots and ports: `NOT_OBSERVED_THIS_SESSION`.** No stop/delete/launch performed by this development session. Do not infer that port 8000 or container name is free just because previous services were reported deleted.

**Target default service source configuration:** `MODEL=nvidia/Qwen3.8-Flash-Next-NVFP4`, `MODE=hybrid`, `MTP=2`, `YARN=1`, `CTX=500000`, `NAME=qwen38-flash`, `PORT=8000`, served model `qwen3.8-flash-next`, Docker internal 8000. This is desired/source state, **not a running API**. Existing Orcarouter model ID is not an alias for this different checkpoint.

## Stage matrix

| Stage | Source/plan | CPU/CI | DGX/GPU | Release |
|---|---|---|---|---|
| P0 inventory + recipe/wizard architecture | `N1 schema + N2 inventory + default 8000 SOURCE_IMPLEMENTED`; N3 doctor/plan partial | N1 15 + N2 10 CPU PASS at 7e8f4a1; launch 4 FAIL from permissions; **CI_RECHECK_REQUIRED** after mode fix | `NOT_RUN` | `NOT_APPLICABLE` |
| P1 Flash-Next baseline | `SOURCE_CONFIGURED / NOT_DEPLOYED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
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
- N1 SOURCE IMPLEMENTED: schema, bounded YAML validator, intentionally invalid 27B candidate, synthetic fixture, 15 CPU tests, new GitHub Actions CPU workflow. See schemas/recipe.schema.json, scripts/manager/manifest.py, recipes/, tests/test_manager_manifest_cpu.py.
- Default Blazux `flash` + `profiles/default.env` + `scripts/serve.sh` now target host port 8000 and refuse implicit Docker name replacement. The built-in model is NVIDIA Flash-Next. This path requires image/model assets and explicit operational go-ahead on DGX.
- `scripts/manager/inventory.py` and `wizard/00-doctor.sh`/`10-plan.sh` provide read-only Docker/ss/disk/cache inspection. N3 is partial (no interactive or execute path).
- No pinned, launchable **manifest**; no service controller, proxy/gateway or 27B runtime adapter. Synthetic recipe SHA values are fake fixture data.

## Blockers / approvals

- Need fresh read-only DGX inventory **execution** before operational choices; the code now exists, but DGX observations do not.
- Need vLLM 0.32 source check for Qwen3.8-27B architecture, quantized `lm_head`, GDN, tokenizer and speculative support. SGLang is excluded.
- User requested implementation for Flash-Next on port 8000; no local GPU/model loading was performed and no command was executed against DGX. Obtain scoped operator confirmation and preflight evidence before actually running setup/serve; explicit deletion approval remains required for P4.
- Need plan for sufficient free disk. Do not delete existing images/cache or checkpoint automatically.

## Immediate next actions

1. On DGX execute read-only `wizard/00-doctor.sh` and `./flash doctor default`, check actual free port 8000, cache/weights/image, mounts and required capacity; record findings without secrets.
2. Complete N3 wizard and pinned image/model provenance, and add a guarded prepare/serve plan; do not auto-run setup or serve.
3. With separately scoped operation approval, run Blazux Flash-Next `setup/serve/wait/test` and bench, preserving rollback evidence. Then resume 27B source audit.

See [NEXT-ACTIONS.md](NEXT-ACTIONS.md), [EVIDENCE-LEDGER.md](EVIDENCE-LEDGER.md) and [../docs/MODEL-RECIPE-WIZARD-PLAN.md](../docs/MODEL-RECIPE-WIZARD-PLAN.md).
