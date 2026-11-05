# Next actions — ordered work queue

> Updated 2026-11-05 KST. **Draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) open; zero CI checks on the initial documentation commit; verify current checks after N1 commit.** Status terms are scoped. Tasks are not achieved merely because listed in a plan.

## CONFIRMED IMPLEMENTATION ORDER — Wizard is the mandatory operator entrypoint

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

P1 **not yet complete**: current Wizard only supports read-only `00-doctor.sh` / `10-plan.sh`. Next coding milestone is Wizard-driven Flash-Next prepare/build/launch/health/bench/artifacts with no implicit mutation and mock CPU tests. **P2 only after P1 DGX benchmark evidence**; P3 only after both model baselines; P4 optional and separate exact deletion consent; P5 Orcarouter follows P4 decision (skipped if not needed). Keep external `:8000/v1` stable across switches and record actual served model ID. One large GPU model active at a time. Do not use SGLang.

## 2026-11-05 large P1 code batch / current operator action

**2026-11-05 operator-provided DGX terminal log (not directly observed through an SSH tool):** GB10/aarch64, Docker 29.6.2, 121 GiB unified memory (117 GiB available then); read-only Wizard Inventory showed no host :8000 collision and no `qwen38-flash` container, and initially 580,134,281,216 bytes free. The existing OpenWebUI and Portainer containers were running; preserve both. `./flash setup default` finished building `qwen38-flash-dgx:v0.32` (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`). The final log line showed **model download 9/25 = 36%**, NOT completed weights/Hybrid. The user's shell also entered `./flash serve default`, `./flash wait`, `./flash test` after setup, so these may run automatically after download/preparation. Do not compete with, modify or restart this running operator setup chain. Port availability and download progress can change after the log timestamp.

- **Source committed:** P1 Wizard `wizard/p1.sh` interactive/noninteractive mode plus pinned snapshot/image audits, plan-hash gate, guarded Hybrid preparation/start/wait, API verification and bounded sequential SSE benchmark with local JSON evidence. `tests/test_p1_*_cpu.py` added; CI at c625a49 verified 2/2 SUCCESS, 80/80 tests per job; DGX Wizard/API/bench NOT_RUN.
- **Immediate next:** fix new CPU/CI failures if any, no active DGX work. The operator's `./flash setup default` is already downloading and has queued later `serve/wait/test`. When it ends, inspect Wizard status and adopt any existing running service. Do not rerun setup or delete the cache.
- **Exit gate still unchecked:** Real P1 Wizard execution and DGX API/benchmark PASS (including tool/vision) and rollback verification. Source-only CI does not close P1.

## New implementation contract — modular Wizard before P1–P7 live testing

**User decision (2026-11-05):** Build the **whole Wizard menu/CLI skeleton first**. Keep each P-stage in a separate `wizard/menus/pN.py`, shared CLI/router/guards in common modules, and retain a **single root `./wizard.sh`** for both guided use and direct `--stage/--action` scripting. Use stable machine-readable JSON/exit codes so the operator can run commands on DGX and return output for analysis. Do not confuse source-only menu registration with an implemented service, validated 27B model, switch, cleanup or gateway.

- [x] **W0 — Modular menu and headless CLI routing (SOURCE/CI).** P1 delegates to existing tested P1 flow; P2–P7 have per-stage status/plan interfaces and fail-closed execution. Source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe` produced 2/2 CI success, 101/101 tests/job. Latest follow-up guard tests require fresh CI confirmation.
- [ ] **W1 — Complete shared execution service and model adapters.** Add stage-specific schema/recipes/provenance checks, guarded prepare/start/verify/bench/rollback controllers as phases qualify; do not enable unverified P2–P7 operations. Exercise P1 against the actual DGX **only after the current setup and queued commands finish**, with per-action approval.
- [ ] **W2 — Real Wizard baseline acceptance.** P1 measured API and benchmark, rollback and evidence; then implement and validate P2, P3, optional P4, P5, P6, P7 in the previously locked order. P4 is conditionally skipped if capacity is sufficient.

**Direct CLI examples:** `./wizard.sh list --json`; `./wizard.sh p1 status --json`; `./wizard.sh --stage p3 --action switch --from-model flash-next --to-model 27b --json` (BLOCKED by design). Detailed contract: `docs/WIZARD-CLI-CONTRACT.md`.

## NOW — P0, read-only/source-safe

**P1 ASSET STATE (USER_REPORTED 2026-11-05 11:46 KST):** `nvidia/Qwen3.8-Flash-Next-NVFP4` downloading **IN_PROGRESS**. Do **not** auto-download, re-download, build over shared cache, run `setup`/hybrid preparation, or launch the model while it may be incomplete. First safe work: implement full P1 Wizard orchestration using synthetic CPU fixtures; the Wizard must detect `DOWNLOADING/INCOMPLETE` vs `READY` and block serve/bench until checkpoint revision, shards and cache integrity are confirmed. On next user-reported completion, read-only verify exact snapshot and local resources before progressing. Actual DGX state, percent, completion and revision remain **NOT_OBSERVED**.


**CI regression note:** First N2+port commit `7e8f4a1` had four launch FAIL due to permission `100644` (exit 126), despite 15 schema and 10 inventory tests PASS. Script executable bits repaired in follow-up commit; check actual new HEAD CI before claiming all PASS.

**2026-11-05 priority revision (user request):** legacy services reported deleted; restore external `:8000/v1` with Blazux *NVIDIA Flash-Next* `default` profile, not Orcarouter. SOURCE changes to `flash`, `scripts/serve.sh`, `profiles/default.env` and manifest rules; N2 read-only inventory and deterministic plan implemented. **DGX state unobserved**. No setup, serve, GPU, download or cleanup done.


**N1 completed SOURCE/CPU only (2026-11-04):** JSON Schema Draft 2020-12, safe YAML loader, bounded guards and 15 isolated CPU tests PASS. 27B candidate intentionally FAIL (exit 2); synthetic valid fixture is not deployable. New PR CI requires GitHub readback at the actual commit SHA. No DGX/GPU/API execution.


- [x] **N1 — Make manifest schema machine-checkable.** Add `recipes/` and `schemas/` proposals implemented with validated, explicit repo revision, digest and immutable targets; a sample 27B placeholder must fail closed. CPU tests cover malformed manifest and unsupported engine.
- [x] **N2 — Implement read-only storage/Docker inventory.** Gather capacity and model references without changing caches, engines or services. Detect protected live service name/image/mount/port and disallow unsafe paths/names. Add `--dry-run` and deterministic plan output.
- [ ] **N3/P1 FIRST — P1 Wizard SOURCE implemented; verify CI and actual DGX API/benchmark before completion.** `wizard/00-doctor.sh` and `10-plan.sh` are read-only partial foundations. Add shared Python manager, interactive and noninteractive wrappers, exact pin/asset/disk/port validation, prepare/start/wait/API verify, benchmark and reproducible evidence export, gated approvals, rollback/failed-launch guard, deterministic dry-run, mock CPU tests. **No GPU readiness claim until actual Wizard execution on DGX**.
- [ ] **N4 — vLLM 0.32 27B source feasibility audit.** Determine exact architecture mapping, NVFP4 quantized output head, vision input, GDN, kernel/sm_121 constraints, context, MTP OFF baseline and DFlash2 scope. Record precise pinning and file/line evidence; **do not copy SGLang launcher**.
- [ ] **N5 — Integrate existing Orcarouter feature deliberately.** Review `feature/orcarouter-bf16-adapter` docs/commits, resolve against manifest contract, then merge/cherry-pick only after explicit integration/test plan. Preserve PLE/MTP count/dtype guards.

## THEN — ordered Wizard milestone gates (DGX operation requires scope-specific approval)

- [ ] P1 **Wizard** Flash-Next installation → preparation → start → API checks → pinned benchmark → artifact/evidence export. Requires DGX PASS for exit.
- [ ] P2 **Wizard** 27B feasibility source/CPU GO → install/start → API/benchmark/evidence on DGX. Requires DGX PASS for exit.
- [ ] P3 **Wizard** Flash-Next ↔ 27B repeated bidirectional switch on stable :8000, readiness check, rollback and failure injection.

## AFTER — independently gated

- [ ] P4 **Wizard** optional Flash-Next checkpoint cleanup **only if space is insufficient**; after P3 verified, dry-run exact paths/shared reference check, preserve fallback + get explicit exact approval. **Otherwise SKIP without treating it as a failed stage.**
- [ ] P5 **Wizard** Orcarouter-Flash-Next direct BF16 PLE MTP OFF → verified 31/31 BF16 overlay MTP2, install/start/API/benchmark/evidence.
- [ ] P6 **Wizard** Orcarouter ↔ 27B repeated bidirectional switch and rollback with stable :8000 and validated model IDs.
- [ ] P7 **Wizard** integrated operational acceptance: service/proxy/gateway/storage, retention, CI, numerical reproducibility, release gates, runbooks and rollback.

## Required action output format

Each completed N-step must report: file+commit SHA, `PASS/FAIL/NOT_RUN` with source/CPU/CI/GPU scope, exact commands, side effects, relevant evidence path and next blocker. Update `CURRENT-STATE.md`, `CHANGELOG.md`, and tests ledger. If blocked, retain task unchecked and add precise reason.

## Current exclusions

Current **source-only development**: no operational GPU usage; no `./flash setup` or `./flash serve` run on DGX; no image pull/build/download; no Docker stop/rm; no deletion; no SGLang. User-requested source default now targets :8000; actual port occupancy and service deployment remain unverified and require separate preflight.
