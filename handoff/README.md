# Handoff index — START HERE

**Canonical starting point for every new ChatGPT, human or agent work session on this fork.** These files live on the **new planning branch** `feature/recipe-wizard-handoff` until merged. Do not assume they are on `main`.

## Confirmed delivery order (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

## Wizard CLI first-class entrypoint

**Wizard architecture decision (2026-11-05):** Implement all P1–P7 **menu/CLI modules first** and then integrate/debug actual runtime in P1→P7 order. Root operator entry is `./wizard.sh`; `wizard/menus/models/`, `switching/`, `storage/`, and `operations/` own per-menu behavior, with `wizard/main.py` and `wizard/menus/common.py` for routing and safe source contracts. Scripts accept explicit stage/action arguments and emit JSON and stable exit codes for operator-mediated DGX tests. Only P1 calls the existing guarded backend today; P2–P7 are SOURCE-ONLY plans and must never execute merely because a menu exists. No SGLang; vLLM 0.32 only.

CLI reference: [../docs/WIZARD-CLI-CONTRACT.md](../docs/WIZARD-CLI-CONTRACT.md). Current stage readiness: [CURRENT-STATE.md](CURRENT-STATE.md).

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

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
