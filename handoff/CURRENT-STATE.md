# Current state — active snapshot

**Snapshot written:** 2026-11-05 (KST) · **Status:** `WIZARD_P1_P7_ROUTER_SOURCE_IMPLEMENTED / P1_GPU_NOT_VERIFIED` · **Implementation:** Flash-Next default port 8000, N2 read-only Inventory and Wizard doctor/plan; **GPU:** `NOT_RUN`.

## Confirmed user goal — Wizard-first, P1 through P7

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

**Current P1 exit gate:** Wizard handles preflight → pinned recipe/image/checkpoint verification → explicit plan/approval → setup/prepare → model serve → /v1/models + reasoning/tool/vision smoke → reproducible benchmark (throughput, TTFT, peak resource, seed/config) → evidence export → safe failure/recovery. No GPU/benchmark exit claim is permitted before real DGX measurements.

**CI readback:** At `017319a5394155797bcb7e5c933ccef35080d669`, two GitHub Actions `manifest` jobs succeeded, 39/39 CPU tests per job (15 manifest + 10 inventory + 13 launch + 1 executable-mode). This is **CI PASS only**, not P1 acceptance. Actual HEAD must still be fetched per session.

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
| PR CI | New 2026-11-05 implementation commit 7e8f4a1: manifest 15/15 PASS, Inventory 10/10 PASS; **4 launcher tests FAIL (exit 126)** because executable mode lost. Follow-up commit restores script modes and adds regression; **recheck HEAD CI**. Prior verified HEAD `017319a` has two successful CI jobs (39/39 CPU tests each); live HEAD check required each session. |

## Operational environment — protect; verify fresh

**User report 2026-11-05:** prior operating services have all been deleted; requests Blazux default NVIDIA Flash-Next on the **same external :8000/v1 API port**. This is a user-reported change, not yet independently observed with current DGX Docker/ss/df commands. Historical prior-session values (not rechecked):
- Container `qwen38-flash-orca-uncensored-bf16-mtp`.
- Container ID `3fc5a3d5be1d52595602287acd87895220219bad050484251ac0408a163ffc45`.
- Original image ID `sha256:b0984c4b724b6f8c0745acb654994e1bd3a6c50b75c2c76078f1bfd6b395f39a`.
- OpenAI-compatible `:8000/v1`, model ID `qwen3.8-flash-next-orca-uncensored-bf16-mtp`, existing external clients.
- Legacy workspace `~/Workspace/llm/blazux-phase6-gates`, target new workspace `~/Workspace/llm/blazux-orcarouter`.

**Actual current running/stopped status, capacity, local Docker images, model snapshots and ports: `NOT_OBSERVED_THIS_SESSION`.** No stop/delete/launch performed by this development session. Do not infer that port 8000 or container name is free just because previous services were reported deleted.

**Target default service source configuration:** `MODEL=nvidia/Qwen3.8-Flash-Next-NVFP4`, `MODE=hybrid`, `MTP=2`, `YARN=1`, `CTX=500000`, `NAME=qwen38-flash`, `PORT=8000`, served model `qwen3.8-flash-next`, Docker internal 8000. This is desired/source state, **not a running API**. Existing Orcarouter model ID is not an alias for this different checkpoint.

**P1 checkpoint download (2026-11-05 11:46 KST, USER_REPORTED):** `nvidia/Qwen3.8-Flash-Next-NVFP4` is **DOWNLOAD_IN_PROGRESS** on the user's machine. This is **not** independently observed on DGX and has no verified completion percent, downloaded bytes, checkpoint revision, sha256, download command or cache path. **DOWNLOAD_COMPLETED=NOT_VERIFIED**, **HYBRID_PREPARED=NOT_VERIFIED**, **SERVICE/API/BENCH=NOT_RUN**. This session has not started, stopped, retried, removed or modified the download. Do not run a second download, `./flash setup default` (could download/build and mutate cache), hybrid preparation, model launch or cleanup while a write may still be in progress. Continue with P1 Wizard implementation and mock CPU tests independently of download, and inspect completed snapshot/index/shards after the user reports completion.

## New evidence and P1 Wizard source batch

**2026-11-05 operator-provided DGX terminal log (not directly observed through an SSH tool):** GB10/aarch64, Docker 29.6.2, 121 GiB unified memory (117 GiB available then); read-only Wizard Inventory showed no host :8000 collision and no `qwen38-flash` container, and initially 580,134,281,216 bytes free. The existing OpenWebUI and Portainer containers were running; preserve both. `./flash setup default` finished building `qwen38-flash-dgx:v0.32` (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`). The final log line showed **model download 9/25 = 36%**, NOT completed weights/Hybrid. The user's shell also entered `./flash serve default`, `./flash wait`, `./flash test` after setup, so these may run automatically after download/preparation. Do not compete with, modify or restart this running operator setup chain. Port availability and download progress can change after the log timestamp.

**New P1 SOURCE implementation at `c625a49276272e90d19ab6367f580a0230754890`:** `wizard/p1.sh`, `scripts/manager/p1_assets.py`, `p1_wizard.py`, `p1_bench.py`, new CPU tests and CI coverage. Wizard supports read-only inventory/snapshot/image proof, deterministic plan SHA, explicit per-action approval, guarded Hybrid prepare/start/wait, API health/model/text/tool/vision probes, bounded SSE benchmark and JSON evidence. **SOURCE IMPLEMENTED, CPU CI 2/2 PASS (80/80 per job), DGX Wizard/API/bench NOT_RUN.** It never automatically runs `setup`, downloads, deletes containers or caches or switches services.

## P1–P7 unified Wizard architecture (2026-11-05)

- User requested **build the entire Wizard navigation/CLI framework up front**, then incrementally connect and debug real P1–P7 model/runtime adapters. One stage file per menu: `wizard/menus/models/`, `switching/`, `storage/`, and `operations/`, shared `wizard/menus/common.py`, dispatcher `wizard/main.py`, executable root `./wizard.sh`, legacy `wizard/p1.sh`.
- `./wizard.sh` offers the interactive stage menu. The same handlers support direct noninteractive CLI, `--stage`, `--action`, `--json`, `--dry-run`, `--execute`, `--approve-plan`. The P1 adapter reuses `p1_wizard.py` and current exact-plan approval. P2–P7 have typed source-only status/plan interfaces; **execution remains hard-BLOCKED** until each model adapter, recipe, GPU evidence and rollback gate is actually implemented.
- Initial modular source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`: 2 GitHub CI checks SUCCESS, **101/101 CPU tests per job** (80 previous + 21 router tests). Follow-up full source/docs commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b`: GitHub CI **2/2 SUCCESS**, **103/103 CPU tests per job** (15 manifest, 10 inventory, 13 launch, 1 script mode, 41 P1, 23 Wizard router). No actual DGX actions performed by this batch.
- `./wizard.sh p1 status --json` and `./wizard.sh p1 plan --for-action verify --json` are read-only. `./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json` returns BLOCKED until P3 qualifies. No model switching or deletion feature was secretly enabled.
- **Current DGX source-of-evidence remains** the prior user-supplied log: image built, Flash-Next download 36% last observed, queued original setup/serve/wait/test; current live service still unverified. Do not update the live worktree while that shell chain may be running. See `docs/WIZARD-CLI-CONTRACT.md`.

## Descriptive Wizard menus, grouped by capability

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

**Source evidence:** `571e1c204d76bcb66b9e02cb1315ac775013a130` refactor, GitHub Actions push/PR **2/2 SUCCESS**, **112/112 CPU tests per job** (15 manifest + 10 inventory + 13 Flash launch + 1 script mode + 41 P1 + 32 router). No real DGX model operations performed or authorized by this rename.

## Temporary one-command DGX P1 handoff workflow (D-016)

- New `scripts/temporary/` is the canonical place for **single-invocation, short-lived, Git-committed operator bundles**. `p1-post-download.sh` dispatches `p1_post_download.py` with source-safe diagnostics → explicit independent Wizard verify/benchmark approvals → JSON evidence collection. `--inspect-only` is safe and can run unattended; on a TTY, each real action requires the full current 64-character plan hash. Script never calls `./flash setup`, downloads, starts/stops a service, removes images/cache, changes the active worktree or performs `git pull`.
- Operator must complete the **already entered** original `setup/serve/wait/test` shell chain **before** Git Pull; do not infer from the old 9/25 download log that current operations have finished. Operator local entrypoint: `git pull --ff-only origin feature/recipe-wizard-handoff`, then `bash scripts/temporary/p1-post-download.sh` (interactive) or `... --inspect-only`. Non-TTY with no explicit plan hashes executes only inspection. Logs stored with restricted permissions under `~/blazux-p1-reports/`, outside Git/HF cache. Wizard-generated evidence remains under `~/.local/state/blazux-wizard/p1/`.
- This code is **SOURCE+CPU CI verified at `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b` (2/2 jobs SUCCESS, 131/131 tests/job); actual DGX/API/GPU/bench still NOT_RUN pending operator evidence**. 27B/Orcarouter runtime phases remain gated; P2–P7 are not executable. See `scripts/temporary/README.md` and `handoff/OPERATING-RULES.md#r1d--git-tracked-temporary-script-batches-for-user-operated-dgx-d-016`.

## Stage matrix

| Stage | Source/plan | CPU/CI | DGX/GPU | Release |
|---|---|---|---|---|
| P0 inventory + recipe/wizard architecture | `N1 schema + N2 inventory + default 8000 SOURCE_IMPLEMENTED`; N3 doctor/plan partial | N1 15 + N2 10 CPU PASS at 7e8f4a1; launch 4 FAIL from permissions; **CI_RECHECK_REQUIRED** after mode fix | `NOT_RUN` | `NOT_APPLICABLE` |
| P1 Flash-Next **Wizard** implementation + DGX bench | `WIZARD_SOURCE_IMPLEMENTED / CI_VERIFY_REQUIRED` | Existing 39/39 previous PASS, new P1 CPU suite 41/41 PASS; total 80/80 CPU tests PASS per CI job (2 successes) | `IMAGE_BUILD_USER_LOG_PASS`, download last seen 36%; **Wizard GPU/API/BENCH NOT_RUN** | `BLOCKED` |
| P2 27B **Wizard** implementation + DGX bench | `PLANNED/COMPAT_UNKNOWN` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P3 Flash-Next ↔ 27B **Wizard** switching/rollback | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P4 Flash-Next **Wizard** optional removal, only if capacity requires | `PLAN_ONLY/EXACT_APPROVAL_REQUIRED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P5 Orcarouter-Flash-Next **Wizard** implement + DGX bench | `PARALLEL_DESIGN_ONLY` | `NOT_RUN_THIS_FORK` | `NOT_RUN` | `BLOCKED` |
| P6 Orcarouter ↔ 27B **Wizard** switching/rollback | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P7 **Wizard**/service/proxy/gateway/storage operations acceptance | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |

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

## Immediate dependencies and next safest actions

1. Verify new GitHub Actions CPU checks on `c625a492…`, remedy any failures and preserve failure evidence.
2. Let operator's existing `./flash setup default` download/Hybrid preparation and queued `serve/wait/test` commands finish **without restarting or changing the worktree mid-run**. Once done, use `bash wizard/p1.sh status`; if container is already running, do not rerun `start`.
3. Obtain fresh Wizard `plan --for-action verify`, explicit action approval, run Wizard API text/tool/vision verify; then separately plan/approve a bounded 3-request benchmark and save local JSON evidence. Do not claim P1 PASS until real DGX data proves it. P2 remains next after P1.

## Immediate next actions

1. **P1 Wizard end-to-end implementation first:** add guided/noninteractive `prepare/serve/verify/benchmark/evidence` flow, approvals, idempotent state + fail-closed plan with mock CPU tests. Existing `doctor/plan` are only partial; no launch without gated operator action.
2. Read-only DGX `wizard/00-doctor.sh` and `./flash doctor default`; establish current port 8000 availability, checkpoint/image provenance, HF cache mounts and disk capacity. No claims of service running until observed.
3. After scope-specific operational go-ahead and rollback plan, execute **P1 via Wizard** on DGX, collect actual API/benchmark evidence, then advance to P2 (27B Wizard), not directly to Orcarouter.

See [NEXT-ACTIONS.md](NEXT-ACTIONS.md), [EVIDENCE-LEDGER.md](EVIDENCE-LEDGER.md) and [../docs/MODEL-RECIPE-WIZARD-PLAN.md](../docs/MODEL-RECIPE-WIZARD-PLAN.md).
