> **2026-11-07 P3-C REAL DGX PASS — 최신 우선 판정:** P1 Flash-Next API/Verify/3요청 Benchmark 및 P3-B 후 P1 재검증·진단 PASS, P2 NVIDIA 27B GPU trial/Benchmark/원본 복구 PASS, P3-A/B/C 실제 DGX 순차 전환 모두 PASS. 최종 관측은 NVIDIA 27B `qwen3.8-27b` `:8000/v1` ACTIVE, canonical `stage-c.json`, wrapper `P3_C_PASS_FINAL_27B_ACTIVE`, 독립 API `LIVE_SERVICE_VERIFIED`. 기존 Flash/27B 컨테이너/HF 캐시 보존. **이 문서에 남아 있는 P2/P3 NOT_RUN / Flash ACTIVE / P3-C 승인 준비는 당시 역사적 시점이며 현재 수행 지시가 아님.** 단, 메인 `./wizard.sh`의 P3 메뉴는 여전히 `--plan` only이므로 **대화형 Wizard UX/반복 가능한 일반 전환의 수용은 미완료**. 다음 작업은 기존 서비스 변경 없는 Wizard UX 개발/CPU 테스트. 최신 기준: [P1–P7 검증 현황](P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md), [최신 상태](../handoff/CURRENT-STATE.md), [새 대화 프롬프트](../handoff/SESSION-START-PROMPT.md).

---

> **2026-11-05 accepted UX supersession:** Operator selected **model-first consolidated Wizard**, not the older multi-group primary menu. New design and batch acceptance: [UNIFIED-MODEL-WIZARD-DESIGN.md](UNIFIED-MODEL-WIZARD-DESIGN.md). Preserve existing P1 backend/CLI and P1–P7 acceptance sequence; P2 download has started per operator terminal (`Fetching 19 files: 84%`) but full checkpoint receipt and runtime are unverified. Older paragraphs below contain historical RadixArk/source-only snapshots; apply the current NVIDIA model selection and Git policy instead. One active GPU model, host port 8000, separate download vs transition approval.

# Blazux vLLM 0.32 — Recipe/Wizard Master Plan

## Live evidence and next source gate (2026-11-05)

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

P2 status usage:
```bash
./wizard.sh model 27b status --inspect-cache --json
```
Read-only exit zero describes a successful **inspection**; JSON status is still BLOCKED and `operations_enabled=false`. It does not imply a cached model, valid candidate recipe or authority to launch.


> Status: **P0 N1/N2 SOURCE IMPLEMENTED, N3 PARTIAL; GPU/actual DGX NOT_RUN** · Updated 2026-11-05 (KST) · Owner repo: `kjlee-inlct/qwen3.8-Flash-DGX`
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

## 1A. User-confirmed Wizard-first milestone contract (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

Each model baseline milestone (P1/P2/P5) MUST be operable through Wizard from preflight and pinned preparation to serve, API functional checks, benchmark, immutable evidence and failure recovery. P3/P6 bidirectional switching MUST be Wizard-controlled with safe transition state, readiness check, rollback and stable external API :8000. P4 may be skipped where capacity suffices and must not delete shared data; if needed it is an independent exact-path approval transaction via Wizard. P7 qualifies the completed operating workflow; a CLI command succeeding alone does **not** close a Wizard stage. No GPU/runtime action is authorized by this decision.

**Present:** `wizard/00-doctor.sh` and `10-plan.sh` read-only source; default NVIDIA Flash-Next profile port 8000, CPU test baseline. **Missing:** prepare/setup/serve/verify/benchmark/evidence Wizard and real DGX validation. This missing P1 path is the next implementation target.

## 1B. P1 Wizard batch source implementation and evidence boundary

P1 Wizard source now includes scripts/manager/p1_assets.py, p1_wizard.py, p1_bench.py, wizard/p1.sh, tests/test_p1_*_cpu.py and CI. Source commit c625a49276272e90d19ab6367f580a0230754890: two CI jobs passed all 80 CPU tests each (41 new P1 and 39 baseline). Wizard provides asset/image inspection, stale-plan approval, Hybrid preparation/start/wait, API model/text/tool/vision checks and bounded SSE throughput/TTFT measurement with JSON evidence. 2026-11-05 user-supplied DGX log: vLLM 0.32 Docker image build finished; model download 9/25 files (36%) at last visible line. OpenWebUI and Portainer remained running; port 8000 was free at the earlier scan. The operator entered flash setup, serve, wait and test sequentially, so subsequent commands may run without assistant action. Do not modify the worktree, restart the process, repeat setup, or replace an already running container before the original chain ends. These are time-bounded facts, not proof of full download or API readiness. **Actual DGX Wizard GPU/API/benchmark and automated rollback NOT_RUN**. P1 cannot exit solely on these source tests.

## 1C. Unified Wizard CLI scaffold, ahead of runtime integration

**Wizard architecture decision (2026-11-05):** Implement all P1–P7 **menu/CLI modules first** and then integrate/debug actual runtime in P1→P7 order. Root operator entry is `./wizard.sh`; `wizard/menus/models/`, `switching/`, `storage/`, and `operations/` own per-menu behavior, with `wizard/main.py` and `wizard/menus/common.py` for routing and safe source contracts. Scripts accept explicit stage/action arguments and emit JSON and stable exit codes for operator-mediated DGX tests. Only P1 calls the existing guarded backend today; P2–P7 are SOURCE-ONLY plans and must never execute merely because a menu exists. No SGLang; vLLM 0.32 only.

Directory layout after initial source implementation:

```text
wizard.sh                    # root interactive + noninteractive entry
wizard/__main__.py          # python3 -m wizard
wizard/main.py              # stage routing, JSON catalog, --stage/--action
wizard/menus/common.py      # stage contract/status/plan and safety gates
wizard/menus/models/flash_next.py          # existing Flash-Next P1 backend adapter
wizard/menus/models/qwen_27b.py          # 27B interface, BLOCKED
wizard/menus/switching/flash_next_27b.py          # Flash-Next ↔ 27B switch interface, BLOCKED
wizard/menus/storage/flash_next_cleanup.py          # optional storage cleanup interface, BLOCKED
wizard/menus/models/orcarouter_flash_next.py          # Orcarouter interface, BLOCKED
wizard/menus/switching/orcarouter_27b.py          # Orcarouter ↔ 27B interface, BLOCKED
wizard/menus/operations/system.py          # integrated services/proxy/gateway interface, BLOCKED
wizard/p1.sh                # legacy P1 compatibility wrapper
```

The source router/CLI and interfaces are implemented and covered by synthetic CPU CI. **This is not complete P2–P7 functionality** and does not qualify the GPU, service start/stop/switch or production cutover. See [Wizard CLI contract](WIZARD-CLI-CONTRACT.md) for operator/agent instructions and exit semantics.

## 1D. Domain-grouped, descriptive Wizard menu modules (supersedes numbered source layout)

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

```text
wizard/
  main.py                         # group/selection/legacy-alias CLI router
  menus/
    models/
      flash_next.py               # P1 NVIDIA Flash-Next
      qwen_27b.py                 # P2 Qwen 27B
      orcarouter_flash_next.py    # P5 Orcarouter Flash-Next
    switching/
      flash_next_27b.py           # P3 two-way switch
      orcarouter_27b.py           # P6 two-way switch
    storage/
      flash_next_cleanup.py       # P4 conditional exact-approved retirement
    operations/
      system.py                   # P7 service/proxy/gateway acceptance
    common.py                     # shared fail-closed source-only contracts
```

New category-structured source and compatibility aliases CI verified at `571e1c2` (2 jobs, each 112/112 CPU PASS). P2–P7 runtime handlers are still NOT IMPLEMENTED; this layout change is **not** a stage exit or deployment permission.

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

**Sequencing correction:** A model may be *retired from active operation* or its checkpoint *deleted from disk* only after an alternate, verified fallback exists. If P2 or P3 fails, **do not perform P4**. If disk is insufficient before P2, stop and request a specifically scoped cleanup decision; never infer approval from this roadmap. User reported prior operating Orcarouter service deleted 2026-11-05; treat that as a report only and recheck live Docker/port evidence on DGX before any action.

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

- 2026-11-05 user report supersedes historic live-service assumption: prior Orcarouter operating services have been removed, according to user (not independently confirmed). New Blazux NVIDIA Flash-Next **default** target is `PORT=8000`, `SERVED_MODEL_NAME=qwen3.8-flash-next`, `NAME=qwen38-flash`. External client model ID changes from Orcarouter; clients must use the new ID. No gateway cutover or API startup was executed in this session.
- Existing runtime ID/image/volume references from older sessions are historical observations; use the N2 read-only `wizard/00-doctor.sh` and `./flash doctor default` and reacquire actual `docker ps/inspect`, `ss`, `df` before stateful decisions.
- Docker image pull/build may change storage; checkpoint download may consume huge disk. Treat download/build as separately gated resource operations and enforce quota/headroom.
- Protect HF cache blobs shared by more than one snapshot, pinned model revisions, overlay source shards, existing runtime image, volume, compiled caches and fallback snapshot.
- **Current fork** `scripts/serve.sh` refuses an already existing exact container name; old upstream worktrees may still use `docker rm -f "$NAME"`. Always verify the actual checked-out revision and dynamic port/name occupancy before launching.
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
