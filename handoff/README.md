> **2026-11-06 LATEST ACTUAL GPU EVIDENCE:** NVIDIA Qwen3.8-27B startup/API/small text inference on DGX **PASS** and original Flash-Next normal-path restore **RESTORED**, zero issues (`PASS_RESTORED`). This supersedes historical `NOT_RUN` notes below; benchmark and repeat switching not yet qualified. **Live status now uses Manifest + API via `./wizard.sh service manager status --json`**, no separate raw Docker/curl commands. See [real P2 GPU evidence and Wizard workflow](P2-27B-GPU-TRIAL-PASS-20261106.md). No further service interruption authorized by this report.

> **2026-11-06 P2 superseding update:** Operator completed the NVIDIA 27B exact-revision download (19/19, exit 0, \`SOURCE_FILES_PRESENT_PINNED_CANDIDATE\`; GPU \`NOT_RUN\`). New read-only qualification: \`./wizard.sh model 27b status --inspect-runtime --json\`. Older 84% transfer comments below are historical, not current. No service switch/27B start is authorized. See \`CURRENT-STATE.md\`, \`EVIDENCE-LEDGER.md\`.

> **2026-11-06 full Wizard SOURCE handoff (D-021):** `./wizard.sh` now runs complete operator console `wizard/console.py`: 1 model → recommended next / all lifecycle actions, 2 service status/health/logs and guarded start/stop/restart/rollback/proxy/gateway, 3 advanced P3/P4/P6/P7 + readiness dashboard. `./wizard.sh workflow 27b --json`, `./wizard.sh workflow 27b --for-action start --json`, and `./wizard.sh roadmap --json` expose machine-readable plans. P1 and P2 execution backends **unchanged**, P2–P7 real runtime/switch/cleanup still **BLOCKED**. Full spec: [../docs/UNIFIED-MODEL-WIZARD-DESIGN.md](../docs/UNIFIED-MODEL-WIZARD-DESIGN.md). User's DGX 27B transfer started but no completion receipt yet; avoid pull while it runs.

# Handoff index — START HERE

> **2026-11-05 current Wizard UI decision (D-020):** `./wizard.sh` now presents **1 Select/run model, 2 Service, 3 Advanced, 0 Exit**. `./wizard.sh select 27b --json` produces a read-only consolidated lifecycle plan. Old P1–P7, model/switch/storage/operations/service commands remain supported, and the P1 guarded backend is retained verbatim. Approved design: [../docs/UNIFIED-MODEL-WIZARD-DESIGN.md](../docs/UNIFIED-MODEL-WIZARD-DESIGN.md). DGX user-reported pinned NVIDIA 27B download **started** (`Fetching 19 files: 84%`); receipt, runtime and switching **NOT_VERIFIED**. No DGX commands from source work; do not change the worktree under an active download.



**Canonical starting point for every new ChatGPT, human or agent work session on this fork.** These files live on the **new planning branch** `feature/recipe-wizard-handoff` until merged. Do not assume they are on `main`.

## Confirmed delivery order (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

## Wizard CLI first-class entrypoint

**Wizard architecture decision (2026-11-05):** Implement all P1–P7 **menu/CLI modules first** and then integrate/debug actual runtime in P1→P7 order. Root operator entry is `./wizard.sh`; `wizard/menus/models/`, `switching/`, `storage/`, and `operations/` own per-menu behavior, with `wizard/main.py` and `wizard/menus/common.py` for routing and safe source contracts. Scripts accept explicit stage/action arguments and emit JSON and stable exit codes for operator-mediated DGX tests. Only P1 calls the existing guarded backend today; P2–P7 are SOURCE-ONLY plans and must never execute merely because a menu exists. No SGLang; vLLM 0.32 only.

CLI reference: [../docs/WIZARD-CLI-CONTRACT.md](../docs/WIZARD-CLI-CONTRACT.md). Current stage readiness: [CURRENT-STATE.md](CURRENT-STATE.md).

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

### User-operated DGX temporary command bundles (D-016/R1D)

Prefer a **Git-committed, CI-tested, single-entry temporary script** in `scripts/temporary/` over pasting many shell commands. The operator completes any previous setup, then `git pull --ff-only`, runs one wrapper, and returns reviewed JSON evidence. See [OPERATING-RULES.md](OPERATING-RULES.md) R1D and [scripts/temporary/README.md](../scripts/temporary/README.md). Initial P1 bundle: source/CI PASS 131/131 tests/job ×2 at `b9f9a1b`, actual DGX execution NOT_RUN.

## Read order (mandatory)

1. **[CURRENT-STATE.md](CURRENT-STATE.md)** — latest known project, branch/HEAD, active stage, blockers and verification status.
2. **[OPERATING-RULES.md](OPERATING-RULES.md)** — do-not-touch boundary, evidence standards, update obligations.
3. **[NEXT-ACTIONS.md](NEXT-ACTIONS.md)** — tasks in priority order and exit conditions.
4. **[DECISIONS.md](DECISIONS.md)** — fixed decisions vs proposals.
5. **[EVIDENCE-LEDGER.md](EVIDENCE-LEDGER.md)** — what was actually tested, source vs DGX.
6. **[CHANGELOG.md](CHANGELOG.md)** — append-only significant updates.
7. **[../docs/MODEL-RECIPE-WIZARD-PLAN.md](../docs/MODEL-RECIPE-WIZARD-PLAN.md)** and **[../docs/MANIFEST-CONTRACTS.md](../docs/MANIFEST-CONTRACTS.md)** — scope, staging, interfaces and cleanup contract.

Use [SESSION-START-PROMPT.md](SESSION-START-PROMPT.md) for a new conversation. Do not paste full context repeatedly if GitHub can be read.

## Source-of-truth hierarchy

1. Fresh **read-only actual DGX evidence** and verified GitHub refs/CI (for runtime/git facts).
2. `CURRENT-STATE.md` and `EVIDENCE-LEDGER.md` (for previously observed facts; preserve timestamps).
3. Reviewed committed plan, contracts and decisions.
4. Legacy Preview/YSLAB documents and earlier chat summaries (historical context, **not** proof of this fork).
5. Assumptions must be labelled `UNVERIFIED`; no upgrade to PASS without evidence.

When refs disagree, do not silently merge/overwrite: record the discrepancy, refresh with tools and fix source documents in the same PR.

## Handoff closing checklist

On any session that changes GitHub, documents, tests, requirements or verified state:
- commit implementation and documentation, or record precisely why they cannot be committed;
- update `CURRENT-STATE.md` and `NEXT-ACTIONS.md` **in the same change set**; update ledger/decisions/changelog if affected;
- refresh actual branch, commit, PR and CI status using GitHub tool; never write a self-referential “this file contains its own HEAD” claim;
- include exact commands, what ran, test results, artifact/log links, what did **not** run, next safe action;
- open or update PR as appropriate; **do not merge merely because documentation exists**;
- end with a short handoff summary linking these files.

`CURRENT-STATE.md` is a **living snapshot**, not a history. Put the history in `CHANGELOG.md` and evidence in `EVIDENCE-LEDGER.md`. No secrets or credentials in these files. File and branch names are stable interfaces for future sessions.
