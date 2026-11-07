## 2026-11-08 — Flash command parser CI confirmation

The 3-test follow-up source commit [bb4d64e](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/bb4d64e02e0d73d6406e6e0d7c593ec86ba4c954) passed GitHub Actions [42388253469](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42388253469): **865/865 CPU/Fake-DGX tests in 38 groups, SOURCE-ONLY**. The operator's 150/150 DGX-local CPU result predates these 3 source tests; new DGX-local CPU execution has not yet been observed. P3-D privileged PID check remains optional explicit operator step; E remains reinstall-unqualified, F unreleased, G historically real PASS/CLOSED, P8 NOT_RUN.

---

## 2026-11-08 — DGX operator read-only P3-D/E/F/G follow-up

**Operator evidence:** `docs/P3-E-F-DGX-READONLY-20261108.md`. At DGX local read-only snapshot, 27B API at :8000 is `LIVE_SERVICE_VERIFIED` with 8/8 checks true. P3-D remains `BLOCKED` only because unprivileged `ss` exposed no port listener PID (`sudo_ss_requested=false`); not a measured GPU conflict. P3-E full Flash draft-field match `issues=[]`, but reinstall unqualified with 37 extra environment keys and zero extra mounts; 27B-only command normalization reported Flash `-cc` tokens as unexpected positionals. P3-F new code ran **150/150 CPU tests PASS on operator DGX**; P3-G is only preview in this run, while prior real two-way G is CLOSED. The source follow-up introduces strict read-only Flash FP8-hybrid argv normalization, no service operations or release gate changes. Historical P3-G, P8 boundaries and Source/DGX classifications remain intact.

---

## 2026-11-08 — New source-only P3-E/F evidence

Source change: [d68106a](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d68106a24c4c6071acff7a4d98d74e04c6ecbfe1). Actual GitHub Actions [42386939625](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42386939625): **862/862 PASS in 38 CPU/Fake-DGX groups** (856 baseline + 6 new). This is **SOURCE-ONLY**; no fresh DGX test or service change. Full scope: `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

Evidence class = **GITHUB_ACTIONS_SOURCE_CPU**, NOT DGX_OPERATED. Target source commit `d68106a24c4c6071acff7a4d98d74e04c6ecbfe1`; workflow job `128446200136` `manifest` succeeded. Actual job logs show 38 `Ran N tests` suites totaling **862 tests**, all OK; 6 new cases target partial stop, absent prior-service restoration, Flash host coverage, template source and P3-G/P8 scope. New Git-tracked rationale document is `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

**DGX ledger unchanged:** P3-G independent two-way transfer receipts remain historical REAL PASS/CLOSED, final last-observed 27B. No container recreation/stop/remove, no GPU or API probe, no simulated failure promoted to live acceptance. P3-E actual reinstall and P8 live fault/rollback are still NOT_RUN.

---

## 2026-11-07 — P3-A–G EVIDENCE AUDIT / P3-G CLOSED; P8 OWNS FAULT & FINAL RELEASE

**New canonical audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md` and `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`. Stage results: **P3-A/B/C** original immutable one-off real DGX PASS/CLOSED (A Flash→27B, B 27B→Flash, C Flash→27B); **D** real read-only GPU+IPv4/IPv6 host :8000 PID ownership PASS from operator `--sudo-ss` run (pre-latest switch); **E** Flash source `-fp8hybrid` prepared view and versioned draft-field match, but **canonical Flash reinstall recipe UNQUALIFIED** (`DRAFT_REVIEW_REQUIRED`, `launch_allowed=false`); **F** six Fake-DGX/CPU suites **144/144 local PASS**, but `PRODUCTION_LIFECYCLE_RELEASED=false` and generic live install/reinstall not accepted; **G** actual independent 27B→Flash→27B TTY-approved ordinary two-way transfers **REAL PASS/CLOSED** with two receipts, API identities, final 27B `diff=[]`, journal VERIFIED/COMMITTED 28 events, last actual active `qwen38-27b` on port 8000. **P3-A–G aggregate = PARTIAL (E open, F source only)** despite G closed. The user explicitly moved intentional failure injection, automatic restore and final operational/UX/production signoff to **P8** (NEW, NOT_RUN, not authorized to execute). P7 is integration only. Preserve old receipts, model assets and `ONE_ACTIVE_MODEL_ONLY`; no P3 A/B/C/G replays or fault injection to perform this audit. Latest P8-source registration CI [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS 856/856 CPU tests 38 groups (source evidence only). Basic post-switch service manager `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are **NOT PROBED** by that command, not conflicts; do not overclaim fresh D audit. The single-script D–G read-only runner prints G preview even after separate real G PASS by design.

**Proof scope:** A/B/C real historical receipts validated in previous DGX logs; not reread as bytes through GitHub today. D proven before latest G roundtrip with opt-in privileged ss; not retested after reverse. E source draft fields match but no reinstall. F 144/144 operator-local CPU PASS. G real 27B→Flash completed receipt `completed-365099fe...a3654.json` and reverse `completed-a909a147...84ed8b.json` (exact IDs in audit), each user-supplied PASS. Reverse postchecks: API qwen3.8-27b, journal 28 events COMMITTED, diff=[]; private receipt bytes not independently fetched here. P8 real failure/restore and release NOT_RUN.

---

## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

**Distinct actual forward receipt:** the private completed receipt *path was reported* by the operator, not fetched from the DGX filesystem through GitHub. The user shared the real executor's `PASS`, service manager postcheck and strict journal audit `VERIFIED/COMMITTED`. That evidence is sufficient to mark **forward direction actual PASS**, while it does not prove reverse, force-failure rollback, benchmark, fresh GPU/PID after switch or canonical Flash reinstall. See exact fields in new report.

---

## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

**Authorization evidence vs execution evidence:** Actual latest user-supplied P3-D-G JSON: `blocked_stages=[]`, D `READ_ONLY_PASS`, E documented Flash field match `issues=[]` but DRAFT_REVIEW_REQUIRED and canonical reinstall missing, F `144/144` local CPU pass, G only `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `executed=false`. Subsequent explicit user statement authorizes P3-G service downtime, **but no actual forward or reverse `OPERATING_SWITCH` execution receipt has been produced**. Do not record P3-G REAL PASS until receipt/journal/API evidence. P3-A/B/C receipts remain historically closed.

---

## 2026-11-07 — THIRD ACTUAL DGX P3-D READ-ONLY PASS; P3-E FP8-HYBRID SOURCE DRAFT

**Actual operator evidence:** Third DGX batch after fast-forward to `1b785c6`: normal `--run` reported D no visible socket PIDs but E `DRAFT_REVIEW_REQUIRED`, F local **136/136 CPU PASS**, G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`. Operator then explicitly ran `sudo -v` followed by `--run --sudo-ss`: **P3-D READ_ONLY_PASS**, both IPv4+IPv6 :8000 `docker-proxy` PIDs (2051487,2051502) independently attributed to canonical active 27B; GPU compute PID 2051842 verified. Overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`, `blocked_stages=[]`, `acceptance_complete=false`; no service mutation or real G transfer. **P3-E** pinned NVIDIA `fc694b54fb0174e0913e6adf86691ef85a4ead47-fp8hybrid` derivative prepared/view files verified; canonical reinstall recipe NOT registered. Legacy Flash cache writable; source metadata and vLLM flags preserved. Evidence `docs/P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md`.

**NEW SOURCE P3-E DRAFT (UNRELEASED):** `recipes/qwen38-flash-next.runtime.draft.json` is `launch_allowed=false`, `register_as_runtime_recipe=false`, not linked into service-policy, no Flash install adapter/executor. `scripts/manager/flash_recipe_review.py` checks versioned pinned Flash 500K/Yarn/MTP2/native tools/image/env/template/mount *documented fields only*, returns `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` or explicit field differences. `P3-E.source_draft_field_review` added to single-script report. P3-E stays DRAFT_REVIEW_REQUIRED; direct live DGX comparison of new code still **NOT_RUN**. CI [42373758262](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42373758262) **854/854 CPU/Fake-DGX PASS / 38 groups**, source only. Full runbook `docs/P3-E-FLASH-FP8HYBRID-SOURCE-DRAFT-20261107.md`.

**Next:** read-only `--run --sudo-ss` batch to inspect E draft comparison, then review remaining host env/mount/image provenance. Separate operator-approved real Flash install and G switch/rollback acceptance required; `PRODUCTION_EXECUTION_RELEASED=False` remains. P3-A/B/C closed, 27B unchanged, P4 optional, P5/P6/P7 queued.

---

Proof hierarchy: actual DGX D with opt-in `--sudo-ss` > ordinary D missing PID. E hybrid existence PASS as read-only observation, **not reinstall qualification**. F source 136/136 actual local and new CI 854/854 source suite; G PREVIEW only. New versioned candidate has not undergone real DGX runtime comparison.

## 2026-11-07 — SECOND ACTUAL DGX D–G BATCH + PINNED FP8 HYBRID / HIDDEN SOCKET PIDS

Actual operator DGX batch (**read-only; no model changes**) after previous source fixes: **P3-D BLOCKED** because `ss` showed BOTH IPv4 0.0.0.0:8000 and IPv6 [::]:8000 LISTEN but no process PID; Docker reported only running `qwen38-27b` as GPU/8000 port owner, NVIDIA compute PID 2051842 verified to active 27B. **P3-E BLOCKED** because the observed preserved Flash checkpoint was pinned NVIDIA source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` plus **`-fp8hybrid` local prepared variant**, not a different HF revision; canonical Flash reinstall recipe still unqualified. Flash /hf mount observed writable and legacy argv preserved. **P3-F PASS 128/128 actual local CPU tests. P3-G preview PASS**, current Docker ID and VERIFIED/COMMITTED journal; actual transfer/rollback NOT executed. Overall exit=3, acceptance_complete=false.

Subsequent SOURCE fix: E now recognizes only exact pinned NVIDIA source revision plus `-fp8hybrid` prepared view and verifies `.prepared`/essential files read-only; no recipe promotion. D now permits ONLY operator-selected `--sudo-ss` to run `sudo -n ss` (no prompt; no sudo by default) and independently reverify unchanged socket set and PID provenance. Unknown PID always BLOCKED. CPU CI [42371861344](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371861344) **846/846 PASS / 37 groups**, SOURCE-ONLY, actual DGX rerun pending. Full evidence `docs/P3-D-G-SECOND-DGX-PID-HYBRID-DIAGNOSTIC-20261107.md`. No P3-A/B/C replay, no production switch release.

---

## 2026-11-07 — FIRST ACTUAL UNIFIED P3-D/E/F/G DGX OUTPUT, THEN SOURCE FIX

User-supplied actual DGX unified `--run`: D BLOCKED `HOST_PORT_8000_LISTENER_NOT_UNAMBIGUOUS` despite single managed GPU/port Docker owner and `gpu_process_exclusivity_verified=true`, NVIDIA compute PID 2051842; E BLOCKED `FLASH_RUNTIME_CONFIG_UNPARSEABLE`, `FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED`; F `SOURCE_CPU_PASS_NOT_RELEASED`, 119/119 local tests; G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `VERIFIED/COMMITTED` journal, source CANONICAL_RECIPE, target HISTORICAL_P3_INSTANCE, no issues. Overall BLOCKED/acceptance_complete=false and no model mutation. Source corrections backed by [CI 42371091647](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371091647), **838/838 PASS / 37 groups**; no real DGX rerun of revised code yet. Reference: `docs/P3-D-G-FIRST-DGX-DIAGNOSTIC-FIXES-20261107.md`.

---

## 2026-11-07 — P3-D/E/F/G SOURCE DRAFT AND CI (NOT REAL DGX ACCEPTANCE)

**CI qualification for new source (not DGX):** GitHub Actions run **42369840239** SUCCESS on source commit `efb0dda`, **829/829 CPU/Fake-DGX tests across 37 groups**, including unified D-G `--cpu-only` orchestrator. Real D/G process measurements, Flash E reinstall qualification and G live roundtrip/fault restore remain not run.


New official stages defined by operator: D independent GPU/host port process audit; E preserved Flash canonical reinstall recipe; F unified lifecycle/rollback/journal/Fake-DGX; G real DGX general model-switch/rollback/UX. Historical P3-A/B/C actual PASS untouched. GitHub SOURCE now includes `scripts/manager/p3_dg_acceptance.py`, shell wrapper, dedicated CPU/Fake-DGX tests and `docs/P3-D-G-UNIFIED-WIZARD-DRAFT-ACCEPTANCE-20261107.md`. `--run` is read-only probes + CPU tests; no service change or GPU inference and **not real G acceptance**. Operator DGX output of this batch not yet received. For code proof inspect GitHub Actions associated with updated source HEAD. Do not conflate the previously actual `READY_FOR_OPERATOR_REVIEW_ONLY` switch preflight with live post-canonical-migration 27B↔Flash→27B switching.

---

## 2026-11-07 — DGX READ-ONLY CURRENT-ID SWITCH ACCEPTANCE (SECOND OPERATOR OBSERVATION)

Operator fast-forwarded 5456eae -> **4189a79**, then ran three read-only commands. `model 27b recipe-diff --cache-source /home/inlc/.cache/huggingface --json`: `diff=[]`, `issues=[]`, `advisories=[]`, Docker `qwen38-27b` ID `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`. `switch flash-next-27b operational --target flash-next --plan --json`: **`READY_FOR_OPERATOR_REVIEW_ONLY`, `issues=[]`**, `current_ids_from_live_docker=true`, source `27b/CANONICAL_RECIPE`, target `flash-next/HISTORICAL_P3_INSTANCE` preserved ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, `LOCAL_P3_A_B_C_RECEIPTS_VERIFIED`. `service manager status --json`: `LIVE_SERVICE_VERIFIED`, `API_IDENTITY_CONFIRMED`, all eight checks true. All three had `executed=false`, production operations disabled. No GPU exclusivity or port-process ownership proof; no real switch/recovery trial. Full scoped observation `docs/WIZARD-27B-OPERATIONAL-PREVIEW-DGX-PASS-20261107.md`. Code CI baseline 814/814 PASS (42367665200). Do not count any of the previews as an executable approval.

---

## 2026-11-07 — ACTUAL DGX READ-ONLY RECIPE DIFF: MATCHED + NEXT SOURCE TESTS

**Operator console output, after local fast-forward 9ec7420 -> 5456eae:** current `qwen38-27b` ID `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`; `model 27b recipe-diff` -> `READ_ONLY_STATUS`, `diff=[]`, `issues=[]`; served `qwen3.8-27b`; Docker image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; recipe SHA `301c9c7980690b97e357db5fb57090fc82c507ab9c1116c8e154739e360bbbbb`; observed HF mount host `/home/inlc/.cache/huggingface` to `/hf` read-only. `restart --plan` predicts RESTART_EXISTING; `reinstall --plan` predicts RECREATE by explicit action, neither executed. `service manager status` -> `LIVE_SERVICE_VERIFIED`, `API_IDENTITY_CONFIRMED`, issues=[] and all eight status checks true. The GPU exclusivity and process-level port ownership flags were NOT verified by this command.

**Independent SOURCE CI** after updating current-ID-aware ordinary switch and explicit read-only host mount comparison: GitHub Actions run 42367665200 SUCCESS **814/814 CPU/Fake-DGX tests across 36 groups**, no real DGX switching. Historic P3 stage files and benchmark unchanged. Full detail: `docs/WIZARD-27B-LIVE-DRIFT-CURRENT-ID-20261107.md`.

---

## 2026-11-07 — SOURCE-ONLY CI EVIDENCE (NO DGX RUNTIME CLAIM)

Generic recipe drift / lifecycle code was committed on feature/recipe-wizard-handoff and passed GitHub Actions SOURCE-ONLY run 42355750124: **799/799 CPU/Fake-DGX tests across 36 groups, conclusion SUCCESS**. New files scripts/manager/recipe_drift.py, scripts/manager/model_lifecycle.py, tests/test_recipe_drift_cpu.py, tests/test_model_lifecycle_cpu.py; new Wizard model menu option 7, CLI read-only recipe diff and lifecycle plans. Production executor disabled and actual DGX operations not run. No existing P2 Native Tools, P3-C, historical container-cleanup receipt, benchmark or active 27B state was changed. See docs/WIZARD-LIFECYCLE-SOURCE-IMPLEMENTATION-20261107.md. The following real-DGX observations remain historical evidence from the operator, not checks made this session.

---

## LATEST REAL DGX — 2026-11-07 Wizard manifest cleanup actually executed and VERIFIED: two historical test containers REMOVED

**Operator-provided real DGX terminal stdout** after fast-forward to `9518f25e614367ab0ebbb725d7568e5c6bf177ed`: `./wizard.sh service manager inventory --json` listed original canonical `qwen38-27b` active on :8000 and two retired stopped containers. `./wizard.sh service manager cleanup --plan` returned `READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL`, `issues=[]`, target_count=2, plan `39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5`, active container full ID `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`. User then supplied exact fresh SHA and both TTY approvals to `./wizard.sh service manager cleanup --execute`, which returned **`MANIFEST_RETIRED_CONTAINERS_CLEANED`**, `executed=true`, `issues=[]`, `remaining=[]`, `preserved_original_model_service=true`, `preserved_images_and_caches=true`. Exact removed names and Docker IDs:
- `qwen38-27b-failed-6d9ede0904c2` → `44920f80610c5787f7d72064269be175d18150fe68d5a2fe846499129fc596bc`.
- `qwen38-27b-native-tools-v1` → `d42a15e2f7959829eeb616d748522193999441c9f418ec5dcae98931dfe5da56`.

**INDEPENDENT POSTCHECK PASS:** `./wizard.sh service manager cleanup --status` → `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, `remaining=[]`, `active_service_preserved=true`, private immutable receipt `result-39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5.json`. `./wizard.sh service manager status --json` → `LIVE_SERVICE_VERIFIED`, `API_IDENTITY_CONFIRMED`, `issues=[]`, served model ID `qwen3.8-27b`, port 8000. `docker ps -a` lists ONLY running `qwen38-27b`, stopped `qwen38-flash`, running `open-webui` (healthy) and `portainer`. The status tool's `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are untested scopes, not observed conflicts. No separate file-by-file HF checksum check done; cleanup code only removed stopped Docker containers.

**SOURCE/HANDOFF UPDATE (AFTER this real run):** `docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md` contains complete actual-evidence breakdown. `runtimes/service-policy.json.retired_containers.completion` now records consumed plan, exact removed Docker IDs, verified active ID and immutable result pointer; historical target descriptions remain in place **for provenance, not as a pending deletion queue**. `scripts/manager/manifest_cleanup.py` now requires exact Git-tracked completed metadata + matching local 0600 immutable receipt + actual Docker target absence + current canonical API health before reporting DONE. Its `--plan` returns **`ALREADY_CLEANED` without a new approval SHA** when this is all verified; any mismatch blocks, never blindly deletes. The new source did not mutate DGX. Completion is authoritative only when live Docker/receipt agrees, not because Git says so.

**USER POLICY CLARIFICATION:** `qwen38-27b` and `qwen38-flash` are VALID removable/reinstallable managed model services, not globally protected from user-approved uninstall. This one-off cleanup never deleted either. General Wizard uninstall/reinstall, recipe-diff-aware restart/recreation and 27B↔Flash current-ID-aware switching remain NOT_IMPLEMENTED/NOT_RELEASED even though canonical 27B Native Tools real DGX migration + benchmark v2 and Open WebUI Native passed. P3-C historical real PASS closed; P8 conditional ticket inactive. Keep vLLM 0.32, one GPU model active, API port 8000, pinned checkpoint/cache, original P3/benchmark receipts and Draft PR #1 unmerged.

**No further DGX action necessary for retired-container cleanup.** If operator wants a read-only check after pulling this new source: `./wizard.sh service manager cleanup --status`; repeated `--plan` should report `ALREADY_CLEANED` (exit code 3, non-action; use status for success). **Do not run `--execute` again**.

---

## LATEST — 2026-11-07: Wizard manifest-owned retirement of two stopped test containers; canonical models ARE removable/reinstallable

**NEW USER CLARIFICATION (higher-priority than older blanket language):** Do NOT impose a permanent deletion prohibition on `qwen38-27b` or `qwen38-flash`. Both are **operator-removable and reinstallable** Docker model services, as managed model lifecycle policy now records in `runtimes/service-policy.json` `models.*.container_lifecycle`. A future general uninstall/reinstall or recipe-diff-aware recreate command requires its own scoped approval, downtime and qualified reinstall recipe; merely setting lifecycle policy does NOT mean that general Wizard executor has been implemented. For the current user-requested batch, **only** two named stopped historical DGX test containers are selected: `qwen38-27b-failed-6d9ede0904c2` and `qwen38-27b-native-tools-v1`. This is operation-specific scoping, **NOT a global ban on deleting other models**.

**Source committed, real DGX execution NOT RUN:** `runtimes/service-policy.json.retired_containers.targets` now registers exact names, original test provenance labels/known IDs, observed vLLM image, immutable local receipt paths, and cleanup lifecycle policy. `scripts/manager/manifest_cleanup.py` implements read-only `plan` (matches live canonical 27B Native Tools promoted recipe/benchmark, exact stopped target IDs, labels, read-only HF cache, result/evidence history, no foreign GPU owners), fresh exact SHA + two independent TTY approvals, and deletion of **only these two stopped Docker containers** through `docker rm`; no images, checkpoint files, HF cache, historical P3 receipts, or benchmarks deleted. A private immutable attempt/result receipt blocks blind partial-retry. Post `status` requires actual target absence plus live canonical service verification. Routed through **`./wizard.sh service manager cleanup --plan` / `--execute` / `--status`** and interactive Wizard → service menu → cleanup. `scripts/manager/service_manifest.py` read-only inventory now exposes `managed_container_lifecycle`, `retired_container_inventory`, manifest names, distinguishing desired policy from Docker observed state. Existing numeric service-menu shortcuts are preserved. Testing is source-only Fake-DGX, not real removal.

**Actual before-state:** user supplied second live canonical recipe migration `COMMITTED` all Native Tools/SSE, three-request benchmark v2 PASS (mean E2E 10.957 tok/s; TTFT P50 0.165412s), new container `qwen38-27b` and independent `LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED`, `LIVE_SERVICE_VERIFIED`, old backup container deleted. User separately confirmed **Open WebUI Native success**. Stopped forensic containers remain present until operator executes new cleanup plan; also stopped `qwen38-flash`. Keep stopped Flash as currently unselected; it remains deletable separately by a future appropriately scoped lifecycle action. P3-C historical PASS/closed, normal Wizard repeatable switch/reinstall recipe-diff code remains distinct unfinished work; old P3 IDs must not be recycled as live authority. P8 conditional migration ticket remains INACTIVE because second canonical recipe migration succeeded.

**New operator next actions (no automatic Docker mutation on Git pull):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager inventory --json
./wizard.sh service manager cleanup --plan
```
Require exact two stopped target names, `READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL`, `issues=[]`. Only then separate TTY `./wizard.sh service manager cleanup --execute` with new SHA and `I_APPROVE_MANIFEST_TWO_STOPPED_CONTAINERS_ONLY` / `I_CONFIRM_ACTIVE_27B_AND_ALL_MODEL_EVIDENCE_PRESERVED`. Finally `./wizard.sh service manager cleanup --status`, `./wizard.sh service manager status --json`, `docker ps -a`. No claim of deletion until actual DGX stdout. If BLOCKED, inspect source provenance rather than bypassing.

Permanent runbook: `docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-20261107.md`. User specifically rejects a hard-coded “canonical 27B and Flash can never be deleted” policy. Keep global uninstall ability possible; current cleanup's exact two-target allowlist is intentionally scoped.

---

## 2026-11-07 — Immediate DGX v2 RETRY authorized as next operator action; P8 contingency and P3-C closure boundary

User instruction: **Proceed to second REAL DGX canonical NVIDIA 27B Native Tools recipe migration test immediately after Git Pull and guarded read-only recovery audit**. User expressly does not require waiting for Fake-DGX CI. This is NOT permission to bypass existing irreversible attempt markers or TTY approval. Previously consumed first migration plan **01702fa1b0901a0dce7517ccbaee133fc253058a1c07abe63bc00c42bec52a15** returned REAL `FAIL_RESTORED`, `native_tools_pass=true`, `benchmark_pass=false`, and `original_restored=true`; independent current Docker/API postcheck has not been furnished. No second DGX run result exists yet.

External GitHub source comparison: [MiaAI-Lab start.sh](https://github.com/MiaAI-Lab/Qwen3.8-27B-DGX-Spark-RTX-6000/blob/main/start.sh) and [styles01 27B recipe](https://github.com/styles01/sparkrun-recipes/blob/main/recipes/qwen-38-27b.yaml) use **different unsloth checkpoint, compressed-tensors, patched/nightly image, sometimes MTP and FP8 KV**. These are **NOT** substituted for our proven pinned NVIDIA nv-community `nvidia/Qwen3.8-27B-NVFP4` / vLLM 0.32.0 `modelopt_mixed` container. `qwen3_coder` / `qwen3` / explicit per-request non-thinking mode are supported by both and already real-DGX tool/SSE tested. Additional [CloudRift vLLM 0.32.0 NVFP4](https://github.com/cloudrift-ai/emmy/blob/main/recipes/Qwen3.8-27B-NVFP4/RESULTS.md) supports parser/benchmark separation but is RTX5090, not GB10. Detailed analysis: `docs/P2-27B-EXTERNAL-RECIPE-RESEARCH-20261107.md`.

**NEW v2 source-only request profile:** `recipes/qwen38-27b.runtime.json` pins `benchmark.version=p2-27b-native-tools-canonical-benchmark-v2`, 3 sequential SSE requests, output cap **128 tokens**, `chat_template_kwargs={"enable_thinking": false}`, temperature 0 and seed 1234, with no literal informal `/no_think` suffix, preserving historical benchmark v1 and production thinking capability. The migration executor verifies benchmark-v2 version, prompt settings, samples and throughput before replacement/promotion; stores complete per-sample diagnostics BEFORE any fail-restore. No claims of successful v2 throughput until actual DGX stdout.

**IMMEDIATE DGX workflow:** `git pull --ff-only origin feature/recipe-wizard-handoff` → current service status/ordinary journal → `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --audit-failure`; require `PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY` and no issues; then manual TTY `--reconcile` (exact old failed SHA + phrase), `--plan` (new SHA, v2 benchmark profile, no issues), and only under NEW downtime and backup-deletion acknowledgements `--execute`. `--status` plus service status after test. If the audit is blocked, STOP; no manual bypass, deletion, old P3-C replay or uncontrolled third execution. GitHub CI is not a prerequisite per the user, but source itself is not a real DGX test.

**Explicit contingency:** IF the second **executed** DGX migration FAILS again, move remaining P2/P3-related canonical Native Tools recipe+benchmark rollout to **P8**, do not continue repeated P2/P3 tests now. Keep P1/P2 original baseline and P3-A/B/C historical real PASS immutable. **P3-C historical Stage-C was already completed at 2026-11-07 10:19:39 KST with `P3_C_PASS_FINAL_27B_ACTIVE`**. Finalize/ARCHIVE this stage without rerunning it; unrelated interactive Wizard production release stays OFF. Conditional tracker: `docs/P8-27B-NATIVE-RECIPE-DEFER-IF-V2-FAIL-20261107.md` is **INACTIVE/PENDING** until actual second result; DO NOT falsely mark P8 active before new output. If second FULL `COMMITTED` with benchmark and backup cleanup PASS, keep P8 inactive. Any `RECOVERY_FAILED` requires physical recovery first, regardless of backlog.

---

## 2026-11-07 — REAL DGX canonical Native Tools migration 1st attempt FAIL_RESTORED; BENCHMARK diagnostic and reconciliation fix

**Most recent actual DGX operator output:** TTY-approved `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --execute` consumed fresh plan `01702fa1b0901a0dce7517ccbaee133fc253058a1c07abe63bc00c42bec52a15`. JSON returned `status=FAIL_RESTORED`, `executed=true`, `native_tools_pass=true`, `benchmark_pass=false`, `benchmark_promoted=false`, `backup_container_deleted=false`, `original_restored=true`, `issues=["MIGRATION_ERROR_NEW_CANONICAL_BENCHMARK_NOT_QUALIFIED"]`. **Actual service independently checked AFTER this failure: NOT YET provided.** This is a real DGX Native Tools pass followed by an unsuccessful new 3-sample performance acceptance test and attempted original restore, **NOT a successful canonical migration**. Do not delete containers/cache/benchmark receipts or re-run the used SHA.

**Root-cause evidence boundary:** In the initial migration code, `p2_27b_benchmark.measure()` returned a structured measurement dictionary, then the caller rejected its acceptance criteria. The caller discarded `samples` and `metrics` before writing the immutable failure report. Therefore the actual failed sample or reason **cannot be reconstructed from the provided output**; not evidence of GPU/model inference failure. The benchmark also used legacy `/no_think` prompt text rather than explicit `chat_template_kwargs={"enable_thinking":False}` which the **successful Native Tools probe uses**. This is a plausible cause but NOT established. Avoid falsely claiming actual latency/TPS.

**Source remediation:** `scripts/manager/p2_27b_benchmark.py` now accepts opt-in pinned nonthinking kwargs while preserving historical defaults and captures per-sample `usage_reported`, `content_observed`, `reasoning_observed`, `stream_finish_reason`, exact failure reason codes, TTFT, tokens and sampled metrics (no generated text). `scripts/manager/p2_27b_recipe_migration.py` opts in to explicit `enable_thinking=false` and writes private immutable `benchmark-observed-<NEW SHA>.json` plus a `BENCHMARK_MEASURED` journal event **before** checking pass/rolling back. Result now includes `benchmark_diagnostics` even on `FAIL_RESTORED`. A `finish_reason=length` at the intended 64-token benchmark cap is recorded, **not automatically deemed a failure**. Do not loosen actual benchmark eligibility for missing usage, TTFT, SSE completion or generated tokens.

**Safe subsequent run protection:** Existing `attempt-<oldSHA>.json` remains immutable; source does NOT silently bypass it. Added `--audit-failure` read-only verification of exact one prior failed result, seven-event hash chain ending RESTORED, original P3 container ID running+API ready, stopped/owned failed candidate, Flash/variant stopped, original ordinary journal clean and no promoted benchmark. If and ONLY IF audit returns `PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY` / issues empty, operator may separately run interactive `--reconcile` and type exact prior used SHA plus `I_REVIEWED_27B_BENCHMARK_FAILURE_AND_RESTORED_SERVICE`; this writes **only a private reconciliation receipt**, never touches Docker. Then `--plan` issues **new distinct SHA** bound to prior reconciliation (also checks fresh current identity, recipe, cache and P3 lineage), and `--execute` STILL requires new TTY SHA, downtime and backup-deletion consent for any second attempt. Previously failed new container is **preserved**; new failed-container name is unique per NEW plan. Two unverified failures or state/evidence drift remain BLOCKED. **No next DGX attempt has been observed.**

**DGX Pull/read-only instructions (NO service mutation):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
docker ps -a --filter name=qwen38-27b --format 'table {{.Names}}\t{{.Status}}'
bash scripts/temporary/p2-27b-native-recipe-migrate.sh --audit-failure
```
If audit is BLOCKED, inspect actual Docker and private `~/.local/state/blazux-wizard/27b-recipe-migration/` rather than clearing markers. Only after reviewing evidence can operator choose interactive `--reconcile`, then `--plan`, then separately authorized live `--execute`. Any new migration result must be grounded in real DGX output; GitHub source-only CI is not DGX acceptance. Preserve original 27B model, HF cache, vLLM image, original P3 A/B/C and 14-event ordinary journal. Main Wizard production flag remains OFF; Draft PR #1 not merged.

---

## LATEST 2026-11-07 — User selects SINGLE canonical 27B recipe replacement (not variant switching); benchmark then delete verified old backup ONLY after PASS

Supersedes previous proposed persistent `qwen38-27b`↔`qwen38-27b-native-tools-v1` service-switch feature: user clarified to change **original 27B recipe**, stop existing service, **recreate the same canonical `qwen38-27b` name** with already DGX-proven native-tool flags, run NEW bounded benchmark, **replace latest active benchmark result**, then **remove the exact old backup Docker container only when every test PASSES**. Old benchmark evidence, model images, checkpoint cache and P3 A/B/C records must NOT be deleted/re-written. The separate unqualified persistent-switch prototype was removed from branch (not deployed). Native Tools 1-shot real DGX `PASS_RESTORED` remains prior proof and trial variant `qwen38-27b-native-tools-v1` remains stopped; its 9 chained events and receipt preserved.

**New Git source (NOT YET RUN on DGX):** `recipes/qwen38-27b.runtime.json` (single pinned 27B canonical source, vLLM 0.32.0, exact local image `sha256:9479fc92...`, revision `482ca0f...`, Jinja SHA `c3cf9e34...`, native-parser flags), desired `runtimes/service-policy.json` registration, `scripts/manager/p2_27b_recipe_migration.py` (read-only plan, independent exact-TTY execution, backup rename, canonical recreation, ordinary chat/structured tools/stream/SSE 3-sample fresh benchmark, private immutable receipts, atomic latest benchmark pointer, remove verified stopped old container only after all PASS, restore pre-change on precommit failure), and `scripts/temporary/p2-27b-native-recipe-migrate.sh` (`--plan`, `--execute`, `--status`). Permanent runbook: [docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md). **Per user request, do NOT block Git Pull on Fake-DGX CI**, but no source change alone authorizes downtime. User runs `git pull --ff-only` and `--plan` first; `--execute` still needs new independently accepted SHA + downtime acknowledgement + explicit verified-backup-deletion acknowledgement. Pull does not mutate Docker.

**CAUTION:** Original P3 receipts pin the PRE-MIGRATION 27B Docker ID. When user explicitly approves deletion after successful promotion, that old ID becomes historic, NOT active. Existing generic operating Flash↔27B code must remain fail-closed until later lineage-aware revision; ordinary service status sees canonical `qwen38-27b` by name but doesn't check tool flags, thus use new `--status` check to verify post migration actual flags / benchmark. Do NOT rewrite historical P3 receipts or indiscriminately delete caches or Docker images. Model stays `qwen3.8-27b` at `:8000`, ONE_ACTIVE_MODEL_ONLY, no SGLang.

**Current real DGX:** user most recently showed `qwen38-27b-native-tools-v1` `Exited (0)`, original `qwen38-27b` operating, 9 one-shot events, and validated `PASS_RESTORED`. **Canonical recipe migration, its new benchmark, backup cleanup, and new `--status` PASS are NOT_RUN.** The new action runs real Docker only on operator-approved TTY, not via connector or Fake-DGX. If `--plan` BLOCKED or execute reports `FAIL_RESTORED`, `RECOVERY_FAILED`, `COMMITTED_CLEANUP_PENDING`, stop and reconcile; never retry blindly.

---

## LATEST REAL DGX — 2026-11-07 P2-FINAL native tool_calls + streaming PASS_RESTORED

**Actual operator-provided DGX run, not CPU simulation:** fresh TTY-approved `scripts/temporary/p2-final-native-tools-operator.sh --execute` completed with `status=PASS_RESTORED`, `trial=PASS`, `structured_tool_call=true`, `tool_result_continuation=true`, `streamed_tool_call=true`, `structured_probe_status=LOCAL_STRUCTURED_TOOL_CYCLE_PASS`, `stream_probe_status=LOCAL_STREAMED_TOOL_CALL_PASS`, `issues=[]`, `original_restored=true` / `restoration.status=RESTORED`. Operator then independently verified original `qwen38-27b` serving sole API ID `qwen3.8-27b` at `:8000`, `LIVE_SERVICE_VERIFIED`, `issues=[]`. Ordinary operating journal still `VERIFIED`/`COMMITTED`, **14 events**, `issues=[]`, last event hash `ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e`. Docker running list contains original 27B, Open WebUI (healthy), Portainer; no second running model shown.

**Qualification update:** The actual bounded 27B Native Tools `tool_choice=auto` + synthetic tool-result continuation + SSE + original restoration **subgate is now REAL PASS**. Earlier “not run” / original API HTTP-400 historical entries below remain chronological evidence, **not current milestone status**. This run does NOT verify real Open WebUI Native end-to-end, production Wizard native-tools switching, crash/forced-error rollback, comprehensive generated reasoning leakage, physical GPU process exclusivity or host port process ownership. The ordinary status fields `manifest_status=OBSERVED_UNQUALIFIED`, `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `operations_enabled=false` remain unqualified scopes rather than observed conflicts. Do not declare complete P2-FINAL production acceptance; ordinary Wizard `PRODUCTION_EXECUTION_RELEASED=False`, old P3-C immutable, original containers/images/HF cache retained, vLLM 0.32, port 8000, ONE_ACTIVE_MODEL_ONLY. **No repeat trial with the same SHA**; private attempt marker blocks blind repetition.

**Evidence detail and remaining acceptance gates:** [docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md](../docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md). Next: private one-shot evidence/stopped variant inventory audit (read-only); design safe long-lived variant-aware service identity and production rollout (separately approved); live Open WebUI Native application end-to-end only during an independently approved maintenance period. No new service downtime authorized by this report.

---

## 2026-11-07 — User-authorized P2-FINAL Native Tools one-shot DGX trial SOURCE delivered; RUN NOT YET

**Actual real DGX prerequisites confirmed by operator:** vLLM 0.32.0 has registered `qwen3_coder` and `qwen3`; pinned NVIDIA revision `482ca0f3832238542f8f5295dde86b5f22711d80` Jinja SHA256 `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041` rendered all five CPU synthetic cases successfully on DGX: tool_prompt, tool_result, non_tool_prompt, no_thinking, thinking_prompt. Result `CPU_TEMPLATE_RENDER_VALIDATED_ONLY`, issues empty. User then requested to **proceed with actual server native `tool_calls` testing** and explicitly directed delivery of a **temporary committed script** for DGX `git pull`. No new live result yet.

**Implemented source-only + Fake-DGX PASS:** tracked `scripts/temporary/p2-final-native-tools-operator.sh` dispatches to `scripts.manager.p2_27b_tool_live_trial` with `--plan` (default, read-only) or `--execute` (TTY only). The new one-shot executor is **separate** from historical P3 and ordinary Wizard and uses fresh 64hex SHA plus two independent per-target downtime acknowledgements, operating and trial locks, independent private immutable attempt marker + phased event files, preserved original P3 lineage/image/port 8000, exact pinned NVIDIA tool-enabled argv, stop original `qwen38-27b` BEFORE creating uniquely named `qwen38-27b-native-tools-v1`, bounded structured `tool_choice=auto`, tool-result continuation and streaming probes, then **ALWAYS attempt to stop variant and restore/verify original 27B even after PASS**. One-shot variant remains stopped/preserved, original P3/operational receipts remain untouched. An interrupted/previous trial is blocked pending manual reconciliation. It does not set `PRODUCTION_EXECUTION_RELEASED` or enable normal Wizard variant switching; no service manifest migration. A host power failure, SIGKILL, OOM, Docker problem may defeat recovery and requires manual reconciliation. Do not claim live GPU acceptance from CI.

**Fake-DGX CI:** [Recipe manifest CPU run 42343502949](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42343502949) succeeded after fixing the empty `docker ps` fake fixture (the failed run 42343432619 was a fixture-only issue). New shell-wrapper tests also passed in [run 42343608738](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42343608738). These checks run NO real Docker/GPU. **No actual trial or downtime was executed** by source commit.

**Next operator steps on DGX:** `git status -sb`, `git pull --ff-only origin feature/recipe-wizard-handoff`, `bash scripts/temporary/p2-final-native-tools-operator.sh --plan`. Require `READY_FOR_INDEPENDENT_NATIVE_TOOLS_TRIAL_APPROVAL`, issues empty, original 27B currently live, original restoration required. Then the user may choose to run `bash scripts/temporary/p2-final-native-tools-operator.sh --execute` in a real TTY during a separately accepted maintenance interruption, type the new SHA printed during execute and exact two independent strings `I_ACCEPT_P2_FINAL_NATIVE_TOOLS_DOWNTIME` and `I_APPROVE_DISTINCT_27B_NATIVE_TOOLS_V1`. The result may be PASS_RESTORED / PARTIAL_RESTORED / FAIL_RESTORED / RECOVERY_FAILED; even PASS_RESTORED only validates trial probes and original restoration, not Open WebUI Native/ongoing service switch. After trial independently inspect `./wizard.sh service manager status --json` and `python3 -m scripts.manager.operational_audit --json`. **NEVER blindly retry or delete original containers/caches/receipts**; older P3 stages remain immutable, port 8000 and ONE_ACTIVE_MODEL_ONLY always enforced.

**Permanent runbook:** `docs/P2-FINAL-NATIVE-TOOLS-ONE-SHOT-OPERATOR-20261107.md`. PR #1 remains Draft/open/unmerged. Main Wizard production switch release remains OFF.

---

## 2026-11-07 — REAL DGX NVIDIA 27B pinned-template CPU rendering PASS (P2-FINAL subgate CLOSED)

Operator fast-forwarded `1295f30..a137e27` and ran `bash scripts/serve_27b.sh --tools-template-audit` on the actual DGX Spark. Actual **operator-provided** JSON (do not confuse with GitHub CI) reported `status=CPU_TEMPLATE_RENDER_VALIDATED_ONLY`, `issues=[]`, all five markers **TRUE**: `tool_prompt_rendered`, `tool_result_rendered`, `non_tool_prompt_rendered`, `no_thinking_rendered`, `thinking_prompt_rendered`. `tokenizer_auto_template_present=true`, local Transformers `5.19.0`, expected and observed SHA-256 exactly `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`, pinned NVIDIA `chat_template.jinja` revision `482ca0f3832238542f8f5295dde86b5f22711d80`. Prior real DGX registry import audit independently confirmed vLLM `0.32.0`, tool `qwen3_coder` and reasoning `qwen3` registered.

**Evidence boundary:** This closes the **CPU parser-registry presence + pinned tokenizer/Jinja prompt-render** subgates, not actual `--enable-auto-tool-choice` serving, structured tool_calls, streaming, reasoning separation in generated API output or Open WebUI Native, and not production cutover acceptance. Original `qwen38-27b` remains the most recently observed active model, original `qwen38-flash` preserved, API :8000, `ONE_ACTIVE_MODEL_ONLY`, HF cache, original Docker IDs and old P2/P3/P3-C plus ordinary-switch receipts/journal untouched. This last test reported `docker_state_mutated=false`, `gpu_inference_executed=false`, `execution_enabled=false`, `approval_accepted=false`, `plan_id=null`.

**Next development:** Implement and Fake-DGX-test distinct **variant-aware service inventory/identity policy, crash-safe independent journal/rollback and separate operator approval** before any live Native Tools cutover. Keep original service manifest semantics and `PRODUCTION_EXECUTION_RELEASED=False` until explicitly reviewed. The existing Fake-DGX simulation is NOT a real executor. No operator downtime consent is given by this CPU PASS; DO NOT run the inert Docker candidate, manually stop the original or replay P3. Draft PR #1 remains open/unmerged.

---

## 2026-11-07 — Real DGX pinned Qwen3.8 Jinja: 3/4 render checks TRUE; no-thinking predicate FIXED in source

After fast-forward on the real DGX, the non-mutating `bash scripts/serve_27b.sh --tools-template-audit` returned `BLOCKED` with only `TEMPLATE_RENDER_FAILED_NO_THINKING_RENDERED` and aggregate `CPU_TEMPLATE_NOT_VALIDATED`. **All actual positive render observations:** `tool_prompt_rendered=true`, `tool_result_rendered=true`, `non_tool_prompt_rendered=true`, `template_present=true`, `tokenizer_auto_template_present=true`, `transformers_version=5.19.0`, pinned NVIDIA template SHA-256 `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`. Exact revision remains `482ca0f3832238542f8f5295dde86b5f22711d80`. Execution flags `docker_state_mutated=false`, `gpu_inference_executed=false`, `execution_enabled=false`.

**Root cause: source diagnostic false negative, not an observed parser, tokenizer or Jinja failure.** The prior test mistakenly asserted that `enable_thinking=false` means no literal `<think>` tags in the **rendered prompt**. The actual [official Qwen3.8-27B model Jinja template](https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/chat_template.jinja) intentionally pre-fills a *closed, empty* thinking region `<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n` in non-thinking mode. In thinking-enabled mode it opens `<|im_start|>assistant\\n<think>\\n`. This is prompt formatting, **not model-generated reasoning or a leak**. No modification to the original NVIDIA Jinja is warranted.

**Source remediation:** fixed `p2_27b_tool_template_audit.py` to check both exact suffixes (reported as `no_thinking_rendered`, `thinking_prompt_rendered`), and pin the actual observed NVIDIA template SHA-256; a hash mismatch blocks. Added CPU regressions for both correct prompt suffix contracts and failure cases, SHA content pin, syntax compile, and safe Docker failure details. `--tools-template-audit` remains CPU-only and read-only in the original `qwen38-27b`; it does not launch the source-only `qwen38-27b-native-tools-v1` variant. Original P2/P3-C/ordinary-switch receipts, original Docker identity, GPU service port 8000, HF cache, and Flash fallback are not changed. This is **not live Native Tool Calling acceptance**. The real corrected audit has **NOT_RUN** until operator fast-forwards and runs it. Protected variant executor, journal, approval and rollback gates remain unimplemented; P2-FINAL NOT_QUALIFIED; main Wizard production OFF, PR #1 Draft/unmerged.

**Next non-disruptive operator experiment only after CI success:** `git pull --ff-only origin feature/recipe-wizard-handoff`, then `bash scripts/serve_27b.sh --tools-template-audit`. Expect five true fields including `thinking_prompt_rendered`, `no_thinking_rendered`, and `status=CPU_TEMPLATE_RENDER_VALIDATED_ONLY` provided the pinned runtime template is identical; actual output must still be checked before claiming PASS. Do not `docker run` candidate or execute `--tools-stream-probe` against the unqualified original.

---

## 2026-11-07 — DGX pinned Jinja CPU experiment: initial BLOCKED due embedded diagnostic Python syntax; corrected source + CI regression

Operator fast-forwarded to `7343cdf` and ran `bash scripts/serve_27b.sh --tools-template-audit` on real DGX. Actual output: `status=BLOCKED`, `docker_exec_returncode=1`, `issues=["DOCKER_EXEC_CPU_PROBE_NONZERO_EXIT"]`, `docker_state_mutated=false`, `gpu_inference_executed=false`, `execution_enabled=false`. Prior implementation suppressed captured `stderr`, so initial output did not disclose the root cause. **Do NOT classify this as vLLM, model, GPU, tokenizer or Jinja incompatibility.**

Source investigation identified a Python `SyntaxError` in the multiline `CPU_PROBE` injected by `scripts/manager/p2_27b_tool_template_audit.py`: the synthetic assistant tool-cycle message had a missing closing `}` after `tool_calls`. A new CPU regression `ast.parse(mod.CPU_PROBE)`/ `compile` reproduced `SyntaxError: closing parenthesis ']' does not match opening parenthesis '{' on line 78` in Actions run [42341080267](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42341080267) (expected failure during remediation), preventing silent re-release. The tool definitions and synthetic assistant tool-cycle are now rewritten with explicit balanced nesting. The source also corrects the no-thinking condition: `enable_thinking=false` must not be assumed to render literal `<think>\n\n</think>`. Structured inner JSON error details, bounded redacted last stderr line and injection process return code are now surfaced for genuine runtime errors; no raw traceback or private prompt bodies are published to Git.

**Next operator command ONLY after new green CPU CI and clean fast-forward:**

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/serve_27b.sh --tools-template-audit
```

This is a CPU-only read-only `docker exec` into **existing** `qwen38-27b`, with no service lifecycle changes or actual GPU inference. Successful synthetic rendering is not native tool inference, parser+template end-to-end qualification, rollback acceptance or downtime consent. Even if a tokenizer/Jinja render issue is identified after syntax repair, investigate the reported error without installing packages or switching models. Preserve source/Flash original containers/images, API :8000, pinned HF cache, all P2/P3/P3-C receipts/journal. P2-FINAL remains OPEN and Wizard production flag remains OFF; PR #1 stays Draft/unmerged.

---

## 2026-11-07 — Actual DGX parser registry PASS; pinned NVIDIA Jinja solution / CPU-only experiment (NOT LIVE ACCEPTED)

The DGX operator ran a **non-mutating import audit inside existing `qwen38-27b`** and reported `vllm_version=0.32.0`, tool parser `qwen3_coder` = `vllm.tool_parsers.qwen3_engine_tool_parser.Qwen3EngineToolParser`, reasoning parser `qwen3` = `vllm.parser.engine.adapters.Qwen3ParserReasoningAdapter`, all **FOUND**. The pinned snapshot's `tokenizer_config.json` exists but its inline `chat_template` is `null`. This is **not** evidence of an absent effective template.

**Root-cause hypothesis and concrete fix candidate:** The **same exact pinned NVIDIA revision** `482ca0f3832238542f8f5295dde86b5f22711d80` contains a *separate* `chat_template.jinja` (8.95 kB), with Qwen XML `<tool_call><function=...><parameter=...>` prompting, `<tool_response>` continuation and `enable_thinking=false`. This was independently checked at [NVIDIA pinned revision](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/482ca0f3832238542f8f5295dde86b5f22711d80) and [pinned Jinja source](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/blob/482ca0f3832238542f8f5295dde86b5f22711d80/chat_template.jinja). [vLLM 0.32 Online Serving documentation](https://docs.vllm.ai/en/v0.32.0/serving/online_serving/) explicitly supports `--chat-template path/to/file.jinja`. The `qwen3_coder` and `qwen3` flags match the [upstream Qwen3.8 recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-27B.yaml) and the DGX import audit.

The distinct **source-only candidate** `qwen38-27b-native-tools-v1` now appends `--chat-template /hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/482ca0f3832238542f8f5295dde86b5f22711d80/chat_template.jinja` before official opt-in parser flags. Original `qwen38-27b` `Config.Cmd`, `_candidate_argv(...,tool_calling=False)`, source image, all containers, API :8000 and every historical P2/P3 receipt remain unchanged. **Do not run the inert command** or launch a second GPU process.

**Next non-disruptive DGX experiment (after clean git pull):**

```bash
bash scripts/serve_27b.sh --tools-template-audit
```

Runs **one bounded 90s** `docker exec -i` Python `-B` in the existing original container with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `CUDA_VISIBLE_DEVICES=-1` and `PYTHONDONTWRITEBYTECODE=1`; no model weights, inference API, Docker lifecycle, host port or cache write. Reads pinned Jinja and reports its SHA, tokenizer auto-detection and whether synthetic tool-choice, no-thinking, non-tool chat and tool-result continuation prompts render with local Transformers `AutoTokenizer`. It **does not** contact another model, show prompt bodies, or make external tool calls. `CPU_TEMPLATE_RENDER_VALIDATED_ONLY` is **not P2-FINAL PASS**. If missing file/unsupported tokenizer/render fails, report the diagnostic and fix with a **pinned, provenance-preserving** source change; no floating updates, SGLang or replacement tokenizer downloads.

Outstanding: actual pinned template file on operator DGX not yet independently shown; runtime tokenizer/Jinja compatibility not yet tested; variant service integration, crash-safe journal/rollback and *new distinct downtime consent* not implemented; actual native tool calling, streaming, reasoning isolation and Open WebUI Native not qualified. Main Wizard `PRODUCTION_EXECUTION_RELEASED=False`, PR #1 remains Draft/unmerged, old P3-C PASS immutable.

---

## 2026-11-07 — P2-FINAL Fake-DGX cutover state-machine simulation added; 722 CPU PASS

Added `scripts/manager/p2_27b_tool_cutover_simulation.py` and `tests/test_p2_27b_tool_cutover_simulation_cpu.py`: a deliberately **Fake-DGX-only**, injected-adapter transaction state machine covering strict variant/source/fallback identity, domain-separated expiring simulated approval, two acknowledgements, lock/prior-journal refusal, stop original→port free→no GPU overlap→start separate variant→check tools/API→preserve original, and failure rollback/uncertainty. Its results are named `SIMULATED_*`, `executed_on_real_dgx=false`; there is NO live Docker adapter, CLI execute route, persistent journal, or production release flag. Simulated approvals must NEVER be treated as real operator consent.

Source code SHA `fe4e6b01c98c9244787a5bb8e034ca81d88bba08` passed GitHub Actions [42339247960](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42339247960): **722/722 offline CPU tests PASS, 34 groups**. This supersedes the earlier 706-test source validation. No DGX service, current original 27B Docker config, HF cache or immutable P3-C was changed. **P2-FINAL Native Tool Calling remains NOT_QUALIFIED** pending parser/image audit, real variant-aware executor/journal/rollback implementation, independent downtime consent, actual structured/streaming/reasoning/WebUI tests. Main Wizard release remains OFF.

---

## 2026-11-07 — SOURCE CI independently VERIFIED for protected Native Tools V1

GitHub Actions [Recipe manifest CPU run 42339037935](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42339037935) **SUCCESS** at exact source SHA `695e4b1f6a10825324d66b01695cda6b0ffeb02d`: **706/706 offline CPU tests in 34 groups PASS**, including the new protected identity, ModelOpt, streaming and malformed-request regressions; both intentionally unqualified candidate YAML recipes were confirmed non-launchable. This CI establishes SOURCE/Fake-DGX correctness only, not DGX parser availability, Tool Calling WebUI or a tested service rollback. Original 27B runtime and ordinary journal were not touched. The subsequent handoff-only update does not alter verified runtime code or CI workflow.

---

## E-20261107-P2-NATIVE-TOOLS-V1-SOURCE — GitHub SOURCE/CPU ONLY; NO new DGX evidence

Tracked source: `scripts/manager/p2_27b_tool_variant.py` (distinct new variant identity and read-only original/fallback/GPU checks); `scripts/manager/p2_27b_tool_streaming.py` (strict bounded SSE test); `recipes/qwen38-27b-native-tools-v1.candidate.yaml` intentionally schema invalid; new Fake-DGX/SSE tests, `scripts/serve_27b.sh` read-only/inference probe routes. CI outcome should be tied to the exact subsequent HEAD/run, not presumed from historical 680 tests. No protected container ID/image/cache or P2/P3/ordinary receipts changed by GitHub source writes; no observed live model or parser verification in this phase. Previously supplied REAL DGX remains authoritative: NVIDIA 27B LIVE_SERVICE_VERIFIED at :8000, ordinary journal VERIFIED 14 COMMITTED, Docker Cmd no tool flags, original local auto Tool probe HTTP 400. P2-FINAL remains NOT_QUALIFIED, P3-C historical PASS/CLOSED. The source-only preflight fingerprint is NOT a runtime plan/approval.

---

## E-20261107-LATEST-27B-POST-REVERSE-AND-P2-TOOLS-HTTP400 — actual operator DGX, source `09c6780`

**Real DGX after both independently approved ordinary switching directions PASS:**
1. `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, active `qwen38-27b`, one served ID `qwen3.8-27b`, port 8000, `issues=[]`; API identity confirmed. `gpu_exclusivity_verified=false` = not independently qualified by status inspector, not an observed conflict.
2. `operational_audit --json`: `VERIFIED`, final phase `COMMITTED`, **14** journal events, `issues=[]`, last event hash `ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e`. This is **new independent post-reverse corroboration**; supersedes prior statement that Flash→27B postcheck is pending.
3. Preserved `qwen38-27b` Docker `Config.Cmd`: pinned `nvidia/Qwen3.8-27B-NVFP4` revision `482ca0f3832238542f8f5295dde86b5f22711d80`; `--served-model-name qwen3.8-27b`, `modelopt_mixed`, BF16, 8192, 1 seq, 0.70, `--enforce-eager`, **none of three auto tool/reasoning switches**. The exact Docker Cmd was provided by operator, not inferred from source code.
4. Source `scripts/serve_27b.sh --tools-profile`: `SOURCE_PROFILE_ONLY_DGX_NOT_QUALIFIED`, all five candidate argument tokens (flag + parser pair + reasoning pair), `container_recreated=false`, `production_enabled=false`.
5. Local harmless `scripts/serve_27b.sh --tools-probe`: `BLOCKED`, `LOCAL_API_HTTP_ERROR_400`, `parser_flags_observed=false`, structured tool call/result continuation/reasoning separation **false**. The current API rejected the test; without raw HTTP body do not infer its exact wording from this probe. No actual Docker/GPU lifecycle change.

**Evidence-based verdict:** historical P2 GPU/benchmark PASS and original P3-C CLOSED/PASS preserved; ordinary operating switching both physical directions PASS with latest 14-event audit. **P2-FINAL Tool Calling is NOT PASS**; current running 27B lacks auto-parser startup flags. Updating opt-in Python source does not modify the container; a separately approved, pinned, rollback-safe tool-enabled runtime variant is required. Open WebUI Native actual end-to-end, streaming, parser compatibility and reasoning separation are not tested. Normal main Wizard release still OFF. Preserve original images/containers/cache, old P3 receipts and private operational receipts. Git source 680/680 CPU PASS at `09c6780` is distinct from these real-DGX results.

---

## E-20261107-P2-FINAL-TOOLS-PROFILE-SOURCE-AND-REVERSE-OPERATING-ACTUAL — evidence boundary

Operator's latest REAL DGX ordinary operating acceptance Flash→27B (distinct from earlier P3-C): 4 exact separate TTY approvals, `Live transition result: PASS`, `Observed model: 27b`, private receipt `completed-a811068f8059525f1960bbc4b746b78ad77f14da4ba55ed6a8006c5d9f5bf6f4.json`. Prior ordinary 27B→Flash real PASS with independent Flash API status `LIVE_SERVICE_VERIFIED` and operating audit `VERIFIED/COMMITTED`. Reverse 27B postcheck/audit NOT YET SUPPLIED, source-only tests are not actual DGX network proof.

After user priority change, inspected official vLLM Qwen3.8-27B recipe and vLLM 0.32 docs: native tool flags `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`. Implemented **opt-in source-only** `p2_27b_launch_preview._candidate_argv(...,tool_calling=True)`, isolated `p2_27b_tool_calling.py` read-only profile + localhost-only fixed tool result/continuation probe, and `scripts/serve_27b.sh --tools-profile|--tools-probe`. CPU Fake-GPU tests added. Actual existing Docker Cmd not inspected, no production parser qualified, no Open WebUI Native full cycle evidence. Prior operator saw `tool_choice=auto` parser-related HTTP error. Therefore old P2 pinned GPU/download/benchmark remains actual PASS; newly appended `P2_FINAL_NATIVE_TOOL_CALLING` remains **NOT_QUALIFIED**, not assumed fixed. Original one-off **P3-C already REAL PASS and FINAL/CLOSED** and is not rerun; all P2/P3 historical files preserved. Official refs and acceptance gating: `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.

---

## E-20261107-OPERATING-FLASH-POSTCHECK-AND-REVERSE-READINESS — REAL DGX, NO NEW SWITCH

After the **actual first ordinary 27B→Flash PASS** the operator provided independent read-only outputs:

`service manager status --json`: `status=LIVE_SERVICE_VERIFIED`, active `qwen38-flash`, `observed_model=flash-next`, only `qwen3.8-flash-next` served, `API_IDENTITY_CONFIRMED`, 8 checks true, `:8000`, `issues=[]`. `gpu_exclusivity_verified=false` denotes the read-only service checker did not establish GPU exclusivity, not that a foreign GPU user was found.

`operational_audit --json`: `status=VERIFIED`, `phase=COMMITTED`, `event_count=7`, `issues=[]`, final SHA `575197bd7fedcadf39751da4becdf7ca052943f37115b33b9398d736fa43a66a`. This independently confirms full event/snapshot/receipt consistency after first physical switch.

`operational-switch-acceptance.sh --target 27b --plan --json`: `READY_FOR_SEPARATE_TRIAL_APPROVAL`, source `flash-next`, target `27b`, `qwen3.8-27b` served ID, `issues=[]`, `executed=false`, `approval_accepted=false`, `production_release=false`, ephemeral SHA prefix `c2fed6bf`, `seconds_remaining=276` at capture. **No reverse GPU action has been attempted in this evidence.** Plans expire; do not use captured SHA as a future approval. Last live model = Flash-Next. Real reverse and failure-injection/rollback acceptance still outstanding.

---

## E-20261107-OPERATING-27B-TO-FLASH-REAL-DGX-PASS — first recurring Wizard trial

**Actual DGX source `4054eb2` after fast-forward, operator console supplied in conversation:**
- **Before:** read-only `service manager status --json` returned `LIVE_SERVICE_VERIFIED` and one served `qwen3.8-27b` on `:8000`, container `qwen38-27b` Up 2 hours; issues `[]`. Note `gpu_exclusivity_verified=false` in the service-status response means that particular command does not verify GPU exclusivity; this is independently guarded in the operating preflight.
- **Journal:** `python3 -m scripts.manager.operational_audit --json` returned `EMPTY`, count 0, issues `[]`.
- **Fresh read-only acceptance plan:** `READY_FOR_SEPARATE_TRIAL_APPROVAL`, source `27b`, target `flash-next`, served ID `qwen3.8-flash-next`, issues `[]`, execution SHA with prefix `72e0941f`, 242 seconds remaining at review. The full exact plan ID was entered only by the operator.
- **Actual four approvals and one-switch execute:** `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute`; `Live transition result: PASS`, `Observed model: flash-next`, private immutable completion evidence `~/.local/state/blazux-wizard/operational-switch/completed-72e0941f…json`. No automatic return was requested. This is the new **ordinary** independent backend, NOT a repetition of original P3-A/B/C.
- **Proof scope:** backend implementation only returns PASS after target model identity / bounded chat / single GPU recheck / source preservation and committed journal audit. Underlying private receipt and independent post-execution status output are **not** yet separately supplied; do not invent those. Live reverse Flash→27B and failure recovery **NOT_RUN**.
- **Current last observed active: Flash-Next**, and production ordinary menu gate **OFF**. Original 27B assets preserved by documented backend, pending independent user evidence of new running state.

**Acceptance split:** `REAL_OPERATING_27B_TO_FLASH_PASS`; `REAL_OPERATING_FLASH_TO_27B_NOT_RUN`; `REAL_FAILURE_RESTORE_NOT_RUN`; `NORMAL_MENU_PRODUCTION_RELEASE_GATED`. CPU Fake-DGX 671 tests at `4054eb2` remain separate source evidence.

---

## E-20261107-OPERATING-SWITCH-GUIDED-ACCEPTANCE-SOURCE — Fake-DGX, NOT real switch

Tracked source in `feature/recipe-wizard-handoff`: `wizard/console.py` main option 4/model option 6; `scripts/manager/operational_wizard.py` release-gated normal UX; `scripts/manager/operational_acceptance.py` independent four-input real-DGX trial-only CLI; `scripts/temporary/operational-switch-acceptance.sh` tracked operator wrapper; `scripts/manager/operational_executor.py` stop→start, exact-target verification, inference + recovery; `scripts/manager/operational_audit.py` full journal/hash/snapshot/receipt consistency; `scripts/manager/operational_probe.py` bounded chat. CPU tests `test_operational_{switch,executor,wizard,audit,probe,acceptance}_cpu.py`, CI workflow. **No new user-provided real DGX ordinary-transfer log**, no stop/start, no real restore, no model deletion, no P3 A/B/C replay. The user-provided last live check remains 27B only served model with successful generation on port 8000; current source changes do not alter it.

Acceptance statuses must remain: `SOURCE_IMPL_COMPLETE_CANDIDATE`, `CPU_FAKE_DGX_VALIDATED_IF_CI_GREEN`, `REAL_ORDINARY_DGX_NOT_RUN`, `PRODUCTION_RELEASE_GATED`. GitHub latest HEAD / CI link recorded independently after last source/doc updates. Runbook: `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`.

---

## E-20261107-OPERATING-WIZARD-GUIDED-SOURCE — not actual DGX switch

Current GitHub source branch includes `scripts/manager/operational_wizard.py` and `tests/test_operational_wizard_cpu.py`; existing ordinary-switch preview and independent executor are now connected **only through a release-gated guided operator boundary**. Execution SHA domain-separate from preview candidate; Fake-DGX simulated both directions, cancellation, no TTY, stale plan, and production release lock. Record latest head-specific GitHub CI separately when completed. **Actual ordinary model switch and rollback NOT_RUN**; current real DGX remains 27B active at :8000 from operator logs. No P3 A/B/C replay, actual Docker stop/start, model delete/restart, tool-parser addition or original private evidence mutation.

---

## E-20261107-27B-OPENWEBUI-AUTO-TOOL-BLOCKED — real operator observation

Direct actual DGX `/v1/chat/completions` with `chat_template_kwargs.enable_thinking=false`: matching `model=qwen3.8-27b`, `message.content="DGX_OK"`, `reasoning=null`, `finish_reason=stop`, `completion_tokens=4`, vLLM `0.32.0-bfe01fe9`. This confirms strict visible-output formatting for **one no-tool request** and no longer implies unconditional reasoning leakage. Separately, real Open WebUI 27B question failed with exact `"auto" tool choice requires --enable-auto-tool-choice and --tool-call-parser to be set`. Neither WebUI settings nor current Docker Cmd were supplied, so root cause is **strongly supported by source 27B launcher flags omission, not fully observed in container**. No changes to running 27B or Open WebUI settings by assistant. Investigate using `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`; do not infer Native Tool Calling PASS.

---

## E-20261107-27B-CURL-SMOKE-REAL-DGX-PASS — received original operator terminal output

Actual DGX operator ran direct localhost `curl` for `/health`, `/v1/models`, and `/v1/chat/completions`, followed by fast-forward from `df3ec01` to `05c1968` and `bash scripts/temporary/operational-27b-curl-smoke.sh`. No Docker mutation or model switch. Direct /v1/models sole ID `qwen3.8-27b`, NVIDIA model root revision `482ca0f3832238542f8f5295dde86b5f22711d80`, `max_model_len=8192`. Direct chat model `qwen3.8-27b`, finish `stop`, 26 completion tokens, `system_fingerprint=vllm-0.32.0-bfe01fe9`; success included `DGX_OK` but also reasoning-like text and literal `</think>` in `message.content` while `message.reasoning` null. Updated smoke printed `HEALTH_PASS`, `IDENTITY_PASS`, `INFERENCE_PASS`, `27B_CURL_SMOKE_PASS`. **REAL DGX generation PASS; EXACT OUTPUT FORMATTING NOT PASS.** Console text is the evidentiary source, not a fabricated private JSON receipt; raw private logs, request IDs and output are not published in repo.

New source-only separate formatting classifier and Fake-CPU tests distinguish `INFERENCE_PASS` from `FORMAT_DEVIATION`; no real DGX rerun of that new script has been claimed. Source CI must be checked at the final new HEAD. P3 general operating switch still `NOT_RUN`.

---

## E-20261107-27B-CURL-SMOKE-SOURCE — inference-specific proof gate

User correctly distinguished `LIVE_SERVICE_VERIFIED` (current API identity) from actual `/v1/chat/completions` functional inference. New bounded, localhost-only `scripts/temporary/operational-27b-curl-smoke.sh` and offline CPU tests `tests/test_operational_curl_smoke_cpu.py` ensure 27B health, exclusive served model identity and one user-visible response are separately checked. Wizard read-only preview provides exact command. Source CI to be checked at latest commit. **Real DGX inference smoke NOT_RUN / output not yet supplied.** Do not conflate script/test creation, old benchmark evidence or PREVIEW READY with fresh model functional acceptance; running 27B and preserved Flash assets remain untouched.

---

## 2026-11-07 — Source-only ordinary operating switch development evidence (NOT a new GPU trial)

GitHub source changes: independent read-only switch preview and new unexposed guarded transaction source, Fake-DGX CPU unit tests, CLI/TTY preview, separated readiness dashboard, and CPU workflow changes. Track \`scripts/manager/operational_switch.py\`, \`scripts/manager/operational_executor.py\`, \`tests/test_operational_switch_cpu.py\`, \`tests/test_operational_executor_cpu.py\` and \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`. Latest CPU run should be verified on GitHub at its actual HEAD; historical CI was 565/565 before these new suites. These are CI/source evidence **only**, not actual DGX. No new physical DGX probe, stop, start, API inference, benchmark, service switch or actual rollback occurred.

Historical independently user-provided P3-C success remains unchanged: 2026-11-07 10:19:39 KST, \`PASS\` with live 27B \`qwen3.8-27b\` on :8000. One-off P3-A/B/C receipts are immutable input evidence only. General operational switch, new rollback, menu execute and P7 release are NOT DGX qualified. Private source receipts and logs remain unmodified and absent from Git. No new release execution approvals were given.

---

## E-20261107-P3-C-FINAL-REAL-DGX-PASS — USER-APPROVED 27B REMAINS ACTIVE

**First actual successfully executed P3-C stage-C evidence from user DGX console, 2026-11-07 10:19:39 KST**: source branch was fast-forward pulled (reported 11 files changed 396 insertions), and operator ran `bash scripts/temporary/p3-stage-c-operator.sh --execute` on real DGX. Read-only preflight `status=READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL`, `issues=[]`, original Flash observed `qwen3.8-flash-next`, original 27B target preserved, after-B P1 Verify/Benchmark/diagnostics hash gate PASS, original P2 27B benchmark SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. C fresh plan SHA `cb88d3be38a4fe1fd965a57aee402c76d53d746fe1cac76640d5b0a4fb6293ad`, expires 2026-11-07 10:20 KST, no rollover (`plan_refreshed=false/refresh_probes=0`). Operator independently typed all three valid current approvals (C-only SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`). Core Wizard executed and returned `{status:PASS,stage:c,executed:true,live_verified:true,active_model:27b}`, exit code zero. Wrapper independently checked final service, observed `post_switch_status=LIVE_SERVICE_VERIFIED` and `post_switch_observed_model=27b`, canonical original `stage-c.json`; final wrapper `status=P3_C_PASS_FINAL_27B_ACTIVE`, `issues=[]`, `approval_accepted=true`, `execution_dispatched=true`, `executed=true`.

Original canonical receipt path: `/home/inlc/.local/state/blazux-wizard/p3/stage-c.json`. Private project report: `/home/inlc/Workspace/llm/blazux-orcarouter/reports/transitions/flash-next--to--27b/p3-c-operator-20261107T011939Z-5f26a6ff25a2.json`. User source original Flash CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`; target 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`. Shared Docker image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137` not model identity on its own. Canonical receipt and reports are PRIVATE on DGX and must never be published raw to Git. **NVIDIA 27B stays running on port 8000; original Flash remains preserved for potential independently approved return.**

**Critical distinction for next sessions:** P1/P2 Verify/Benchmark actual DGX and P3-A/B/C switching backend CLI accepted and evidence-verified. The current interactive `./wizard.sh` menu in `wizard/console.py` only displays P3 stage `--plan` and NEVER executes or guides the transfer. Actual P3-C was executed with `scripts/temporary/p3-stage-c-operator.sh` delegating to canonical `./wizard.sh switch flash-next-27b stage-c --execute`. This proves engine and operator wrapper, **not final user-friendly Wizard UI or routine reversible switch UX**. Preserve completed P3 receipts; don't rerun the one-off P3 acceptance sequence or inadvertently stop 27B. UX phase requires explicit design, separate implementation, fake-CPU tests and independent DGX validation.

---

## 2026-11-07 — TWO REAL P3-C PLAN-EXPIRY BLOCKS; SOURCE-ONLY ROLLOVER REPAIR

Actual DGX operator `bash scripts/temporary/p3-stage-c-operator.sh --execute` emitted two private unique receipts: `reports/transitions/flash-next--to--27b/p3-c-operator-20261107T010814Z-dd8b2073f8cc.json` at 10:08:14 KST and `p3-c-operator-20261107T010930Z-62cf3383e227.json` at 10:09:30 KST. Both show **status=BLOCKED**, `issues=["P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS"]`, `approval_accepted=false`, `executed=false`, `execution_dispatched=false`, source served `qwen3.8-flash-next`, original pinned Flash image/CID `90f39a4d...`, preserved 27B CID `6d9ede09...`, post-B P1 `PASS`, P2 digest `80f109db...`. Canonical SHA `30b2b29bb715e2393b65152ea8d1da2db61956d631efce2248aee2e9690610de` expiry 2026-11-07 **10:10:00 KST**, leaving 106s then 30s (<120s required). These are valid pre-approval safe blocks; no GPU/service mutation or P3-C completion.

Tracked source-only repair in `scripts/temporary/p3_stage_c_operator.py`: `--execute` with **TTY and fully READY initial stage-C provenance only** now runs bounded <=150s **read-only** re-observation across expiring window until a NEW different, still qualified SHA is available with >=120s remaining. Service/target/evidence/Git changes, unexpected before-boundary plan ID changes, non-rotating plans, Ctrl+C, timeout must block without dispatch. Only *new* exact SHA and independent two literals can authorize the unchanged canonical Stage C Wizard. `--plan` unchanged, no automatic consent or activation. New fake DGX virtual-time and full post-refresh C-dispatch tests under `tests/test_p3_stage_c_operator_cpu.py`. Source CI is distinct from **ACTUAL DGX** execution; current P3-C NOT_RUN. Original unmodified stage-A/B receipts and service containers preserved. See [runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## 2026-11-07 — REAL DGX ORIGINAL-TO-GIT BENCHMARK ROUND-TRIP VERIFIED

**New actual DGX operator result (not simulated CPU testing):** After Git fast-forward pull of the benchmark publication implementation, `bash scripts/temporary/verify-published-benchmarks.sh` returned **two `status=VERIFIED` records, each `issues=[]` and `executed=false`**, followed by `Published Flash-Next and NVIDIA 27B summaries match private DGX source receipts.`

- Flash-Next published `benchmarks/published/qwen3.8-flash-next/f506db4c76430674.json`: `VERIFIED`, source original raw SHA256 `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db`.
- NVIDIA 27B published `benchmarks/published/qwen3.8-27b/80f109dbd7c97460.json`: `VERIFIED`, source original raw SHA256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`.

This **closes the previously pending operator DGX source-byte/public-summary reproduction check**. The two allowlisted public JSON summaries exactly match what the validated exporter computes from the original private DGX receipts; no new benchmark, service mutation, stage-C dispatch, Git upload of original private telemetry, or port switch is asserted. This does **not** provide a fresh live model status check or authorize a Stage-C stop. P3-C remains NOT_RUN based on most recent run (cancelled due leading '[' in approval). Next optionally run the latest tracked `bash scripts/temporary/p3-stage-c-operator.sh --plan` for fresh current live gate; separate explicit Flash downtime consent remains mandatory for `--execute`.

---

## 2026-11-07 — PUBLIC/GIT BENCHMARK SUMMARY RECORDS + C APPROVAL CANCEL

User explicitly suggested keeping measured benchmark results in Git. Source branch now tracks sanitized `benchmarks/published/qwen3.8-flash-next/f506db4c76430674.json` and `benchmarks/published/qwen3.8-27b/80f109dbd7c97460.json`, with historical ACTUAL DGX numerical values supplied in user logs and original immutable raw record SHA256 hashes. Flash: 2026-11-06T23:30:31Z, P1 post-B 3 x64 tokens concurrency1, mean 37.9527 tokens/s, TTFT p50/p95 1.384594/1.779602 s, E2E latency p50/p95 1.724560/1.813754 s, 192 output tokens; source raw SHA256 `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db`. 27B: 2026-11-06T04:26:42Z, actual bounded `BENCH_PASS_RESTORED_VERIFIED`, mean E2E 7.9002 tokens/s vs decode proxy 11.1801 (not measured vLLM engine decode throughput); TTFT p50/p95 0.179349/28.977990 s, latency p50/p95 5.818283/34.609889 s, source raw SHA256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`.

Published JSON contains ONLY model/revision/runtime, profile, numeric metrics, receipt SHA, status and limitations; no original raw file or private paths/plan ID/prompt/output/logs were committed. `scripts/manager/benchmark_publication.py`, `tests/test_benchmark_publication_cpu.py`, `scripts/temporary/verify-published-benchmarks.sh` added. **Initial reports transcribed from actual operator output; source-bytes round-trip verification has not yet run on operator DGX**. Read-only one-command verifier must return two VERIFIED events before claiming machine-reconciled publication. Source CI is CPU fixture/provenance validation only.

Actual latest user P3-C `--execute` entered SHA with an extra initial `[`. Wrapper output `status=CANCELLED`, `executed=false`, `execution_dispatched=false`, `approval_accepted=false`. Flash was still observed active; no C service change. New C plan needed for any future intentional switch.

---

## 2026-11-07 — OPERATOR ACTUAL STAGE-C READ-ONLY READY; SOURCE-ONLY C WRAPPER

New operator DGX text `붙여넣은 텍스트(1)(6).txt`: clean fast-forward from `ebebd60` to `20907793795f43b3999d4a6470cbbf766ea87385`; `./wizard.sh evidence list --model 27b --kind benchmark` found ONE original 27B benchmark `20261106T042642Z-0cacd3f29370.benchmark.json`, `mean_e2e_tokens_per_sec=7.9002`, `mean_decode_tokens_per_sec_proxy=11.1801`, `ttft_p50_sec=0.179349`, `status=BENCH_PASS_RESTORED_VERIFIED`. `./wizard.sh evidence migrate --plan` READY with 14 COPY candidates and SHA `44753008...`, but the guided approval prompt received literal `COPY`, so output `CANCELLED/executed=false/copied=0`. Original P1/P2/P3 files unmodified and no import completed.

Actual `./wizard.sh switch flash-next-27b stage-c --plan --json` returned **READY_TO_REQUEST_TRANSITION_APPROVAL**, `issues=[]`, `p1_evidence.status=PASS` (Verify `b5bab417...`, Benchmark `f506db4c...`, diagnostics `38227eee...`), original active Flash container CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, preserved 27B target `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`, source and target images `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, P2 receipt SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, `executed=false/approval_accepted=false`. Historical C SHA `d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7` is short-lived and **never authorizes reuse**. No actual C execution or GPU port transfer.

New **source only** `scripts/temporary/p3_stage_c_operator.py`, `scripts/temporary/p3-stage-c-operator.sh`, `tests/test_p3_stage_c_operator_cpu.py` control canonical Wizard, require three separate fresh manual confirmations for actual --execute and verify both live 27B and canonical stage-C receipt afterward. No actual DGX wrapper execution or C service mutation yet. Original read-only plan is real, source CI is not actual C. [Runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## 2026-11-07 — CPU SOURCE EVIDENCE: model history + copy-only consolidation

Historical actual DGX `blazux-wizard.zip` remains unchanged and is detailed in the earlier operator evidence entry (P3-A/B PASS, post-B P1 Verify/Benchmark PASS, stage-B receipts, original rc3 diagnostics). Added **source only** `scripts/manager/evidence_catalog.py`, `tests/test_evidence_catalog_cpu.py`, Wizard `evidence` route and console model option 4 plus Advanced copy option 8. Catalog reads original private JSON and project-local reports, including `p2/*.benchmark.json` real-shaped E2E/proxy stats and stage A/B transitions. Copy importer rehashes current plan and writes digest-named append-only 0600 copies without ever moving P2/P3 state/locks/journal. Its fake CPU tests do **not** prove any real DGX import or Stage-C readiness. See [contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md).

P3-C remains NOT_RUN, NOT_AUTHORIZED; latest source CI and fresh operator `stage-c --plan --json` must be examined. P1 original receipts and source proof are untouched.

---

## 2026-11-07 — NEW ORIGINAL OPERATOR DGX ZIP / POST-B REAL P1 RECEIPTS

New user-provided `blazux-wizard.zip`, **not source CI**:
- Canonical P3-B `blazux-wizard/p3/stage-b.json`: `PASS/executed=true/live_verified=true`; completed `2026-11-06T22:31:24Z`; Flash-Next restored.
- Read-only diagnostic `blazux-wizard/p3/p1-diagnostics-20261106T231959Z-8de8d9f283d8.json`: PASS, expected own Flash container name/port rc3.
- Latest read-only diagnostic `blazux-wizard/p3/p1-diagnostics-20261106T232509Z-42cd3f5e323f.json`: PASS, expected own Flash container name/port rc3.
- **Actual GPU Verify** `blazux-wizard/p1/20261106T232627Z-82b4aebbdd13.json`: `PASS`, baseline/extended `PASS`, all four probes `PASS`, explicit SHA `dbc86cd43d631ca012e1439c03d7ed7197429aae1e314fc04ee0782ccf20b020`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`.
- **Actual GPU Benchmark** `blazux-wizard/p1/20261106T233031Z-66af25d31aab.json`: `PASS`, separate explicit SHA `72f18943a69b04dad0b082bb1da4e12cac62e12017eeb6170a5fdebbc1a7882f`, 3 samples, 64 tokens each, concurrency 1, seed 1234. TTFT p50/p95 1.384594/1.779602 sec, latency p50/p95 1.724560/1.813754 sec, mean 37.9527 tokens/sec, 192 output tokens.
- The uploaded ZIP's `blazux-p1-reports/` and `blazux-p3-reports/` trees are *separate older operator reports*. The new project-local P1 evidence location contains **no claim of existing DGX files yet**: code-only default newly introduced in GitHub and unverified on real operator runtime.

New evidence layout and dual-read gate documented in [contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md). Historical records remain append-only. P3-C NOT_AUTHORIZED and NOT_RUN.

---

## E-20261107-P3-B-REAL-PASS-POST-B-READONLY-P1-AND-SOURCE-FIX

**OPERATOR-SUPPLIED ACTUAL DGX EVIDENCE (not assistant-observed live Docker):** P3-B canonical `/home/inlc/.local/state/blazux-wizard/p3/stage-b.json` with `stage=b,status=PASS,executed=true,live_verified=true,active_model=flash-next`; wrapper report `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T223124Z-14861d75.json` shows `P3_B_PASS_FLASH_NEXT_ACTIVE`, exit 0, `issues=[]`, independent post-switch `LIVE_SERVICE_VERIFIED` and `qwen3.8-flash-next`. Prefix `p3-a-operator-` is a WRAPPER naming error, not a failed B execution. Old wrapper `approval_accepted=false` is stale bookkeeping despite explicit separate terminal triple input and successful Wizard. Do not rewrite this historic private receipt.

**ACTUAL POST-B READ-ONLY P1 PREFLIGHT:** `/home/inlc/blazux-p1-reports/20261106T224010Z-d2095867/result.json` reports correct API served ID, clean branch, plan Verify+Benchmark READY, original/Hybrid READY, indexed 11 weight shards, source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`. Doctor/inventory each return 3; their latest raw JSON disposition is NOT PROVEN from supplied summary alone. Verify/Benchmark actions intentionally `BLOCKED/inspection_only` = NOT_RUN. This is not functional regression or performance PASS.

**SOURCE-ONLY IMPLEMENTATION:** fixes in tracked P3-A/B operator source and fake DGX tests; new `p1-post-b-audit.sh` uses existing inspect-only P1 checks, compares both raw rc3 JSON to exact running Flash source image, persists new 0600 immutable `p1-diagnostics-<UTC>-*.json` and never grants GPU or P3-C permission. P3-C gate picks latest attempt and blocks stale/invalid numeric/revision evidence. CI success for initial audited source `ea1a4ca1629acfd519fbfa839b615f45dd91c86e`; subsequent hardening must be evaluated at its own commit. Actual DGX run of new script **NOT_RUN**.

---

## E-20261106-P3-B-REAL-DGX-READ-ONLY-READY-B-NOT-AUTHORIZED

DGX operator pasted actual `bash scripts/temporary/p3-stage-b-inspect.sh` output at branch HEAD `e5d4171d07838e565510b1127f4a0b27dcd8423f`: `status=READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`, `operations_enabled=false`, `approval_accepted=false`, `current_model=27b`, `current_model_ids=["qwen3.8-27b"]`. Actual IDs: running 27B `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`, original preserved Flash `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Docker runtime image digest for both is `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; distinct served API/identity is needed, image digest alone does not differentiate models. Verified original P3-A plan hash `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`, P2 receipt SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. B inspection plan `7af40f009dd67975c77b98c03183833dd4997e16f9c9443bd11ea880f6d8162c` expiration `1793955000` (2026-11-06 17:50:00 KST), not valid later or as implicit operator authorization. Private receipt `/home/inlc/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`.

**Source-only change:** previous B core approval field erroneously named Flash downtime while B actually shuts down 27B; now distinct B-specific `I_ACCEPT_27B_DOWNTIME` + `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`. New default read-only B operator wrapper can execute only after separate real TTY triple confirmations with a fresh B SHA and updated core guard. Fake-DGX [PR 42190159738](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) **489/489 CPU PASS** across 22 groups on source `59046c4e17a5094f2c80a84025a763c2a767edcb`. Actual P3-B GPU transition **NOT_RUN**, no authorization. Preserve live 27B and source images/containers; stage-B source code is neither DGX qualification nor user permission.

---

## E-20261106-P3-A-REAL-DGX-COMMITTED-27B-ACTIVE

**Actual user-provided live DGX log** (not a CPU test): `feature/recipe-wizard-handoff` at HEAD `a3945bdc5cfec467478978c47b3a27bdafee84bd`; tracked `scripts/temporary/p3-stage-a-operator.sh --execute` output an initial plan READY with `issues=[]`, verified Flash source image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, P1 pre-A review `PRE_A_P1_REVIEW_READY`, P2 SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, `plan_id=b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`, expiry epoch `1793951400` (2026-11-06 16:50:00 KST), preserved Flash ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. All three exact manual confirmations typed independently. Result `execute_command_exit_code=0`, `executed=true`, `wizard_result.status=PASS`, `wizard_result.stage=a`, `wizard_result.live_verified=true`, `wizard_result.active_model=27b`; wrapper independently `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `status=P3_A_PASS_27B_ACTIVE`, `issues=[]`. Real stage A Wizard receipt `/home/inlc/.local/state/blazux-wizard/p3/stage-a.json`; local operator report `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. Original may remain stopped and preserved by design, but its post-A detailed Docker state has not yet been supplied; only independently qualify preservation from actual stage-B preflight.

**NEXT PHASE B NOT EXECUTED OR APPROVED.** A is the only approved completed live stage; B returns to Flash-Next, then new P1 functional/numeric evidence after B, then C to 27B final with separate approval. D-016 source-only B inspection `scripts/temporary/p3-stage-b-inspect.sh` compares actual A receipt to fresh service/API and canonical B read-only plan, validates original Flash immutable ID and 27B model/image provenance, writes private 0600 summary. It has no execute CLI, no GPU calls or Docker changes. Its CPU CI (fake fixtures) cannot replace actual DGX evidence and gives no B authorization. Preserve all images, checkpoints and stopped source container.

---

## E-20261106-P3-A-STALE-PLAN-REFUSAL-EXACT-PROMPT-FIX

**Actual operator DGX transcript:** HEAD `be6f3f9e6d757cc11c6299024900b637c7ca239d`, `scripts/temporary/p3-stage-a-operator.sh --execute`. Real preflight `status=READY_TO_REQUEST_OPERATOR_INPUT`, `issues=[]`, original source image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, P1 pre-A PASS report `p1-pre-a-20261106T065104Z-aaed31b2.json`, P2 receipt hash `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. Plan SHA `94b4dedae21eb72b12443029257931e123e33404c32898d9ae2bad52954c064f`, expires `1793950200` = 2026-11-06 **16:30:00 KST**. Operator **correctly** typed exact three strings: plan SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_P3_ENTRY`. Wizard rejected `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT` with `executed=false`, `approval_accepted=false`. Existing wrapper misleadingly surfaced `OPERATOR_REVIEW_REQUIRED`, but no actual stage A Docker service change occurred. Evidence `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T073049Z-4dc8be1b.json` (07:30:49Z=16:30:49 KST). Expiration highly consistent, not asserted as sole proven reason without fresh plan comparison.

**Source fix** at `fb34ce0ce985824cecd9c63159bf6f1eed408279`: show every exact typed literal adjacent to prompt, KST expiry and seconds left; guard <120s remaining before human confirmation; after acknowledgments replan read-only and refuse expired/changed SHA before canonical Wizard; nested stale refusal `executed=false` becomes `BLOCKED`. No automatic silent reapproval, no retry. Fake-DGX CPU tests 459/459 PASS ([push 42181851452](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181851452), [PR 42181858236](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236)); latest DGX code rerun NOT_RUN. D-016 operator workflow and D-037 scoped conditional approval unchanged; B/C and post-B P1 still separately gated.

---

## E-20261106-P1-PRE-A-ACTUAL-DGX-PASS-AND-P3-A-CONDITIONAL-ENTRY

User-provided DGX terminal transcript for source HEAD `834f823a76556a37a982e3dbf7f243db3edad6df` after tracked P1 pre-A wrapper rerun: `status=PRE_A_P1_REVIEW_READY`, `issues=[]`, `current_model=flash-next`, immutable image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; `current_rc3` and `historical_rc3` both `EXPECTED_ACTIVE_FLASH_COLLISION` (`check_count=2`); `p1_verify=PASS`; `p1_benchmark=PASS`, `sample_count=3`, TTFT P50/P95 1.398707/1.751198s, latency P50/P95 1.687357/1.780142s, mean 38.2968 tokens/s, total 192 completion tokens. Read-only local evidence `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`, `observed_at_utc=2026-11-06T06:51:04.065299+00:00`, no issues. Actual P3-A `executed=false`, `operations_enabled=false`, `p3_a_execution_authorized=false` **in the P1 receipt** because it was a read-only reconciliation, not actual stage-A approval/execution or API switch. Historical gaps have been reviewed successfully for **PRE-A only**.

D-037: operator's prior conditional P3-A intent is now eligible after P1 initial clearance, but actual P3-A remains a separate real live DGX event with a *fresh* short-lived plan ID, exact typed operator downtime and P3-entry confirmations, and service recovery risk. Newly tracked operator wrapper `p3-stage-a-operator.sh` requires private P1 PASS receipt, currently verified Flash, P2 receipt hash, current plan, interactive triple confirmations, canonical Wizard execute and independent 27B API identity; defaults to read-only plan, cannot chain B. Both models' checkpoint/images and original stopped source must survive. User has **not provided actual P3-A execution output** and therefore A/B/C statuses remain NOT_RUN. No GitHub activity here touches GPU service, Docker, port or cache.

---

## E-20261106-P1-PRE-A-REAL-DGX-PARSER-BUG-439-CPU-FIX

**Operator-supplied actual DGX output**, branch `feature/recipe-wizard-handoff` HEAD `3a59419305b31266f034fe4cbec2b384bb91d1f4`: tracked temporary P1 pre-A audit wrote `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T064009Z-70e9cef9.json`, returned `BLOCKED` with exactly `P1_ASSET_AUDIT_NOT_READY` and `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. `current_rc3` and `historical_rc3` each `EXPECTED_ACTIVE_FLASH_COLLISION` (`check_count=2`); P1 Verify PASS; benchmark PASS, 3 samples, 192 output tokens, TTFT P50/P95=1.398707/1.751198s, latency P50/P95=1.687357/1.780142s, mean 38.2968 tokens/s. Current model flash-next, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. Zero authorization, no P3 service mutation.

**Source-verified bug, not observed asset corruption**: persisted source report `p1_post_download.session` stores full cache diagnosis within `checks.cache_diagnosis.stdout`; console printing synthesizes `cache_diagnosis` only for the short terminal summary. Pre-A audit incorrectly accessed the nonexistent persisted top-level key and reported the missing revision as mismatch. Now uses original cache diagnosis summary helper to parse actual saved raw stdout, with revision validity/mismatch separately classified. Real-shaped fake-DGX regression checks no top-level diagnostic, raw stdout PASS, malformed/missing source blocked, actual changed SHA blocked. [Push 42176219970](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176219970), [PR 42176224898](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898), **439/439 CPU PASS on code `9adc9ab282a91c02e959dcb5c62f98527b556391`**. No claim of DGX reevaluation PASS yet. D-016 pending operator pull and single script rerun, preserve original service.

---

## E-20261106-D016-P1-PRE-A-WRAPPER-435-CPU-CI — no DGX run

Followed user-reaffirmed D-016 temporary script GitHub-first rule: tracked `scripts/temporary/p1-pre-a-readiness.sh` plus Python module, CPU fake DGX tests, workflow shell syntax validation, operating/runbook updates. One read-only wrapper reconciles **two** actual local P1 report files (2026-11-05 earlier and 2026-11-06 new), exact original private P1 verify+bench receipts, numerical TTFT/latency/tokens/s and samples, same source image, P1 plan readiness, and fresh Wizard service manager API/manifest. Separate `doctor`/`inventory-plan` outputs must each be actual parsed `rc=3` with expected active Flash owned-container image and port collision, `status=PASS` and `errors=[]`. Missing data/foreign image/unknown model/changed revision fails closed. Actual live execution remains `NOT_RUN`, no service change or GPU inference, no P3 automatic authorization.

**Another correctness issue fixed:** `p1_wizard.verify_api` obtains `identity = require_model(...)`, which returns `{"health":"PASS","models":["qwen3.8-flash-next"]}` on success, NOT `{"status":"PASS"}`. Initial pre-A and existing `p3_p1_evidence_gate` erroneously checked nonexistent `identity.status`; both now check actual health and served model list. New real-shaped positive tests and wrong-ID negatives added, no checks weakened. Intermediate CI failures before updating old fake fixtures are preserved; latest code SHA `75d22ce4303736ee84563a0f388a978379e4f228` [push run 42173798547](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173798547) and [PR run 42173805888](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) SUCCESS **435/435 CPU tests in 19 groups**. Cannot claim actual historical rc3 cause resolved until the operator runs the GitHub-pushed wrapper and shares JSON.

---

## E-20261106-P1-INSPECT-AND-NUMERICAL-RECEIPT — operator-provided direct facts, raw rc3 not yet seen

Operator's actual DGX latest `bash scripts/temporary/p1-post-download.sh --inspect-only` report at `/home/inlc/blazux-p1-reports/20261106T060941Z-e71a159c/result.json` has clean branch/head/tracked changes, no active setup process, API model IDs exactly `qwen3.8-flash-next`, HTTP health/models rc=0, GPU command=0, source+hybrid READY, `source_issues=[]` and `hybrid_issues=[]`, no incomplete blobs. Checkpoint revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`; source+Hybrid each report 11 indexed shards with compatible external symlinks. Verify and benchmark `plans.*.ready=true`; `actions.verify` and `actions.benchmark` `status=BLOCKED`, `reason=inspection_only` correctly mean **no new inference/benchmark was attempted**, not failure of historical P1 PASS. Both doctor and inventory_plan rc=3, but the pasted short report does not include raw stdout, so precise historical rc3 cause cannot be decided.

Separate operator P1 original Wizard benchmark receipt `~/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`: `status=PASS`, `benchmark.status=PASS`, `sample_count=3`, `total_completion_tokens=192`; actual numerical TTFT P50 1.398707 s/P95 1.751198 s; E2E latency P50 1.687357 s/P95 1.780142 s; average measured completion throughput 38.2968 tokens/s. These are **NVIDIA Flash-Next P1**, NOT 27B P2 metrics and not the required post-P3-B P1 benchmark. Distinguish source of these from client proxy prefill/decode metrics in P2. Historical 2026-11-05 P1 `verify=PASS`, baseline+extended and text/chat/tools/vision PASS unchanged. Actual rc3 raw cause remains unresolved pending tracked wrapper. No new GPU work or model switch performed from the user's read-only script.

---

## E-20261106-P1-OUTSTANDING-CONDITIONAL-APPROVAL-AND-RC3-RECONCILIATION — source checked, no DGX mutation

Actual P1 history recorded at E-20261105-16: NVIDIA Flash-Next source and Hybrid READY, 11/11 indexed shards; operator-supplied `verify=PASS` baseline+extended, completion/chat/tools/vision PASS; bounded `benchmark=PASS`; local receipt names `20261105T113119Z-eca4ec724ede.json` (verify) and `20261105T113125Z-586b2b46d93e.json` (benchmark). No TTFT/latency/token/sec numbers supplied in current conversation or ledger; previous `doctor=3`, `inventory_plan=3` had no accompanying JSON, so exact historical failure cause UNKNOWN. Post-B P1 receipts cannot exist before P3-A/B and remain NOT_RUN.

Operator's approval condition specifically requires **no unfinished P1 work before Flash→27B**; that condition is not fulfilled by current proof, so P3-A NOT AUTHORIZED and no actual service transition performed. The currently running Flash service identity `LIVE_SERVICE_VERIFIED` is not P1 benchmark proof.

Found exact **source semantics** of rc3: `scripts/manager/inventory.py` returns code 3 when collision_free=false due to an already present named container and occupied host port (even when `status=PASS` and `errors=[]`). Historic rc3 could be this, but no retrospective proof is invented. Fixed `p3_p1_evidence_gate.py` to require raw parsed doctor + inventory documents showing expected active same-image `qwen38-flash`/published :8000 collision with no inventory errors, instead of impossible rc=0; plus existing reviewed written disposition and actual post-B P1 receipts. **CPU-only tests** on `26a69507983dbcb2a7ab4c569f9d8baa6162e25c`: [push 42172119698](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172119698) and [PR 42172127412](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172127412) SUCCESS, **418/418 tests** in 19 groups. One intermediate source-only commit `f1dfc37` had red CI from old fixture; addressed by implementing real-shaped raw evidence fixture and five negative tests. No host container or model mutated.

---

## E-20261106-P3-SEQUENCE-STATUS-RECOVERY-SAFETY-CI — source-only continued, no GPU operations

After real DGX stage-A `READY_TO_REQUEST_TRANSITION_APPROVAL` with `issues=[]` (operator logs below), corrected misleading global sequence wording: staged source adapters exist, but `sequence --plan` remains permanently read-only and `BLOCKED` pending separate P3 entry. Changed P3 restore logic to recheck unexpected GPU-enabled Docker containers before restarting original service after a failure; fail closed as `RESTORE_FOREIGN_GPU_CONSUMER` / `RECOVERY_FAILED`. Added CPU fake-Docker normal/foreign-GPU recovery tests. **Does not establish host GPU process exclusivity.** Read-only P3 readiness remains a different evidence class from runtime operational PASS.

**Verified SOURCE HEAD `02bf94c1628828ce22fa338dd5a8e5a0955f9179`:** [push GitHub Actions 42170050031](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170050031) SUCCESS and [Draft PR Actions 42170056860](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860) SUCCESS, 413 CPU tests over 19 suites. Previous interim `d82122f` failed because simulated `docker ps` output incorrectly contained literal backslash-n rather than newline; corrected without weakening assertions. Actual DGX P3 execute remains **NOT_RUN**, no `:8000` downtime, no additional GPU model start, no file/cache deletion, no PR merge.

---

## E-20261106-P3-A-ACTUAL-DGX-READ-ONLY-READY — operator-provided JSON, no service mutation

2026-11-06 DGX operator read-only observation: current Flash-Next `qwen38-flash` on :8000/v1, `LIVE_SERVICE_VERIFIED`, served ID `qwen3.8-flash-next`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, exact container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Manifest/API check array 8/8 true, `issues=[]`, `executed=false`; **GPU exclusivity and process ownership remain unverified**, and current identity is not historical rollback proof. `sequence --plan`: `status=BLOCKED` with only `P3_SEPARATE_OPERATOR_ENTRY_REQUIRED` by D-034 (expected), with successful local P2 receipt SHA-256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, evidence path `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`. `stage-a --plan`: `status=READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, source `flash-next`, target `27b`, `plan_id=79be6bf05cb02306ec9155ade317e06c457238de427417ebab8946e35449247a`, expiry epoch `1793943600` (2026-11-06 14:40 KST), target image equal to preserved local Docker image ID, expected target container ID null (not yet created), `executed=false` and `operations_enabled=false`. **This was a plan only, not scoped downtime approval or P3 entry**; plan IDs must be regenerated when stale and must never be reused across stages. No GPU/Docker/service mutation was performed by these read-only queries.

**Interpretation:** P2 receipt was found and accepted by the read-only sequence planner. The P3-A plan's readiness says source/target preliminary guard conditions are satisfied; it does not certify actual GPU exclusivity, service interruption permission, persistence or rollback. The P3 global sequence remains BLOCKED until separately approved entry, and actual P3 A/B/C remain NOT_RUN. The local plan expiry is not a reusable authorization token. No user authorization to stop `qwen38-flash` is recorded.

---

## E-20261106-P3-PERSISTENT-SOURCE-CI — source and CPU only, no DGX P3 operation

New P3 standalone stages in `scripts/manager/p3_persistent_switch.py`, `p3_p1_evidence_gate.py` and Wizard menu. Durable approval boundary: P2 benchmark evidence does not automatically open P3; A requires a separate explicit operator-entry acknowledgment and exact current A plan; B, C each need new stage-specific plans and downtime approvals. A/B/C mock Docker implementations have been tested; label and ID tampering fails closed; successful C remains on 27B. Post-B fresh P1 numerical/functional receipts and rc=3 diagnostics required; absent data remains BLOCKED, no invented TTFT/throughput values.

**GitHub Actions, actual code HEAD `27728045907a1f2111dc4b8340fbea2cc365ff1d`:** [push run 42168518712](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168518712) SUCCESS and [Draft PR run 42168524464](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168524464) SUCCESS. Logs report 411 passing CPU unittest cases across 19 test groups. Earlier intermediate red CI steps were genuine syntax/new-mock issues and were fixed, not hidden. They are not runtime GPU test outcomes.

**P3 DGX actual:** A/B/C `NOT_RUN`; actual service state last provided after P2 was Flash-Next `LIVE_SERVICE_VERIFIED`. No updated DGX direct observation after source/doc commits. **P1 post-B remedy/verify/rebenchmark actual:** `NOT_RUN`; doctor/inventory-plan historical return code 3 reason still UNKNOWN. No model start/stop, Docker system cleanup, port change, cache mutation or PR merge occurred from code work.

---

## E-20261106-P2-DGX-BENCH-PASS-RESTORED — actual operator-provided DGX stdout, private files not independently fetched

Result: `status=BENCH_PASS_RESTORED_VERIFIED`, `trial=PASS`, `executed=true`, `target_api_ready=true`, `inference_ok=true`, `benchmark.status=PASS`, `restoration.status=RESTORED`, `restoration.issues=[]`, post-restore Wizard `LIVE_SERVICE_VERIFIED` with `observed_model=flash-next`, `expected_served_id=qwen3.8-flash-next`, `issues=[]`. NVIDIA `nvidia/Qwen3.8-27B-NVFP4` revision `482ca0f3832238542f8f5295dde86b5f22711d80`, exact served ID `qwen3.8-27b`, image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. This overrides plan-only `P2_BENCHMARK_RECEIPT_NOT_FOUND` entries from earlier in the day, which remain historical.

**Observed measured benchmark (3/3 successes, stream=true, concurrency=1, seed=1234, max_tokens=64):**

| Request | TTFT (s) | E2E (s) | Completion tokens | Client decode proxy (tok/s) |
|---|---:|---:|---:|---:|
| #0 | 32.177839 | 37.808956 | 64 | 11.1878 |
| #1 | 0.179349 | 5.818283 | 64 | 11.1723 |
| #2 | 0.178962 | 5.813945 | 64 | 11.1802 |

Aggregate TTFT P50=0.179349s, P95=28.977990s; latency P50=5.818283s, P95=34.609889s; mean E2E=7.9002 tok/s, mean client decode proxy=11.1801 tok/s, mean client prompt-ingest proxy=246.2744 tok/s. Do not conflate client proxies with vLLM engine metrics; first-request latency cause not yet established. GPU memory `UNAVAILABLE`; GPU peak and actual engine prefill/decode metrics `NOT_MEASURED`. Three small text requests do NOT prove broader feature/load readiness.

Paths on the operator's DGX (not accessible through GitHub, exact file contents independently unverified):
- `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`
- `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.json`
- `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.target.log`

**Disposition:** P2 approved limited scope COMPLETE and STOP. P3 persistent switching is **NOT_RUN / NOT_QUALIFIED**. D-034 demands separate operator entry/transition approvals and P1 corrective/remeasurement evidence before final 27B. No GPU/service mutation from this documentation update.

---

## E-20261106-P3-REORDERED-SOURCE-ONLY — user instruction, code/CI evidence; no new DGX runtime data

**Operator's new instruction:** Do not automatically enter P3 after P2; when P3 successfully switches **27B→Flash-Next**, resolve P1 shortcomings and benchmark Flash-Next before switching **Flash-Next→27B**. Since previous P2 design restores Flash-Next, P3 must separately and explicitly establish 27B as the source model for the requested 27B→Flash-Next test. Final intended active service after P3 is **27B** (not Flash-Next).

**Source-only changes:** retired `scripts/manager/p3_27b_roundtrip.py` previously executable two-cycle path (its `main`, `make_plan`, `execute` now always return `BLOCKED`); introduced read-only `scripts/manager/p3_transition_sequence.py` + Wizard `switch flash-next-27b sequence --plan --json` with `plan_id=null` and no auto progression. Read-only new sequence encodes per-stage explicit approvals and prerequisite P1 remediation/rebenchmark. CPU tests verify no receipt, successful receipt still requires manual entry, phase order, wrong model/API BLOCKED, and legacy direct execution prevented.

**Verification:** GitHub Actions [run 42163187058](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42163187058) **SUCCESS, 395/395 CPU tests, 19 test suites**, on code HEAD `f195e8bcc48333b5d40147c8b66e6c412c949818`. Subsequent docs-only commits do not constitute DGX runtime validation. No new actual P2 benchmark/P3 transition was performed. Previous actual DGX P2 `--plan` was only `READY_TO_REQUEST_TRIAL_APPROVAL`; no measured bench result supplied. Draft PR stays unmerged.

---

## E-20261106-DGX-P2-BENCH-PLAN-READY-P3-PLAN-BLOCKED — actual operator stdout

**P2 read-only plan evidence:** `action=Qwen3.8-27B-bounded-benchmark-and-original-restore`, `status=READY_TO_REQUEST_TRIAL_APPROVAL`, `issues=[]`, `executed=false`, `gpu_verified=false`, `image_id=sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, `source_container_id=90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, `plan_id=2f76c3b03865b6a15a5c2fe8f316231f532fbf8b7fe178ffd00db8383edc3399` (expired 2026-11-06 **12:20 KST**), benchmark `requests=3`, `max_tokens=64`, `concurrency=1`, `seed=1234`, `stream=true`. This is a **read-only plan**; no actual GPU benchmark result or performance numbers.

**P3 read-only prerequisite evidence:** `action=P3-two-temporary-roundtrips-with-original-restore`, `status=BLOCKED`, `plan_id=null`, `issues=["P2_BENCHMARK_RECEIPT_NOT_FOUND"]`, `executed=false`, `cycles=2`. Expected fail-closed behavior until a successful real P2 `BENCH_PASS_RESTORED_VERIFIED` private evidence file exists.

Do not call P2 bench PASS, repeat P3 plans as a workaround, reuse expired P2 plan, or interpret these logs as operator approval to interrupt Flash-Next.

---

## E-20261106-P2-BENCH-P3-ROUNDTRIP-SOURCE — no new DGX GPU execution

**Source on `feature/recipe-wizard-handoff` only:** new P2 distinct-hash benchmark plan and 3 sequential SSE timing requests; original one-shot stop/restore executor reused, protected local metric evidence, post-restore Wizard status; new P3 exactly two temporary roundtrips conditional on real P2 benchmark success. CPU fake-backend tests verify approval separation, invalid and stale approval fail-closed, no HTTP/GPU from plans, SSE bounds, recording measured TTFT/e2e vs proxies, and source ID/API restore checks. **Do not record any actual performance numbers until real DGX execution.**

**Existing real DGX evidence remains separate:** first 27B GPU one-shot API/inference `PASS_RESTORED` and actual Flash-Next `LIVE_SERVICE_VERIFIED`. Neither is a timed benchmark nor a two-cycle result. P3 plan is deliberately BLOCKED until `*.benchmark.json` produced by the newly approved real benchmark. Source CPU CI does not qualify either GPU runtime command, persistent P3 switch, GPU peak memory or true engine prefill throughput.

---

## E-20261106-ACTUAL-DGX-MODEL-INVENTORY — Orcarouter original and BF16/MTP recipe still exist

**Actual operator JSON:** `./wizard.sh model list --installed --json` => `status=READ_ONLY_INVENTORY`, two cache roots checked, three registered sources observed, `other_cached_repos_truncated=false`, `service_status=LIVE_SERVICE_VERIFIED`, active `flash-next`, `executed=false`. Model revisions/shards/metadata/missing shards:
- `nvidia/Qwen3.8-Flash-Next-NVFP4` `fc694b54fb0174e0913e6adf86691ef85a4ead47`: **11**, missing **0**, `source_files_present=true`, active + API verified.
- `nvidia/Qwen3.8-27B-NVFP4` `482ca0f3832238542f8f5295dde86b5f22711d80`: **3**, missing **0**, `source_files_present=true`, inactive.
- `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` `3a3b63161c0745390e5270179af42e46efc70799`: **17**, missing **0**, `source_files_present=true`, inactive; original legacy HF cache `/home/inlc/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`; recipe view directory `/home/inlc/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2` has `directory_present=true`. This **directly confirms preservation, not runtime functionality**.

Also **4 unregistered cache snapshots**: `maurienne-ai/Qwen3.8-27B-DFlash2-NVFP4-RTNcal`, `RadixArk/Qwen3.8-27B-NVFP4`, `dealignai/Qwen3.8-Flash-Next-ABLITERATED-NVFP4`, `RadixArk/Qwen3.8-Flash-Next-NVFP4`. These were only discovered by revision listing; **index/shards not validated** for unregistered cache entries. Unknown locations beyond the two configured roots were not searched.

**Evidence boundary:** source inventory and current Flash-Next API confirmed, no GPU operations performed here. Orcarouter BF16 PLE/MTP recipe contents not audited and no Orcarouter runtime qualification yet. No cleanup/re-download.

---

## 2026-11-06 — Read-only installed model inventory, including protected legacy Orcarouter

An earlier example `./wizard.sh model list --installed --json` was suggested **before implementation** and gave `{"status":"BLOCKED","error":"choose a valid submenu item for model"}` when the operator tried it. That error was a **missing Wizard route**, NOT evidence that any model was deleted.

This command is now implemented and tested:
```bash
./wizard.sh model list --installed --json
```

Canonical config `runtimes/model-discovery.json` lists known Hugging Face caches (`~/.cache/huggingface`, `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`, and `HF_CACHE`/`HF_HOME` overrides). It maps registered service models to their source repo identifiers **without changing `runtimes/service-policy.json` or granting launch permission**. Includes protected original Orcarouter source `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4`, revision `3a3b63161c0745390e5270179af42e46efc70799` and original BF16/MTP recipe view `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2`. The previous project originally reported ~180GB `hf-cache`, ~5GB `recipe-views`; this was historical storage evidence and has **not been rechecked today**.

Read-only inventory validates selected snapshot's bounded weight index and existence of every indexed nonempty shard (following HF symlinks), tokenizer and config. It reports exact cache/revision and source state. A recipe view alone yields `RECIPE_VIEW_ONLY_SOURCE_UNVERIFIED`; missing weights yield `SNAPSHOT_INCOMPLETE_OR_UNVERIFIED`; found complete indexed weights yield `SOURCE_FILES_PRESENT_UNQUALIFIED`. Unknown caches beyond configured roots are **not** conclusively absent; limited other cached repos are reported as `UNREGISTERED_CACHE_SNAPSHOT_OBSERVED`. Active API identity comes from the manifest-led live service inspector. All these are observational; no model is moved, deleted, downloaded, registered as ready, started, restored, or switched.

The new command has **not yet run on the real DGX**. After clean Git fast-forward, operator executes one read-only Wizard command and provides JSON. Any Orcarouter result must be reconciled with current disk evidence before asserting continued asset availability or runtime compatibility. Original service `qwen38-flash` remains untouched. Existing P2 first GPU trial `PASS_RESTORED` and `LIVE_SERVICE_VERIFIED` are separate, already reported facts.

---

## E-20261106-P2-ACTUAL-GPU-TRIAL-PASS-AND-WIZARD-STATUS-SOURCE

**Real operator DGX terminal**: `./scripts/serve_27b.sh --trial-execute --approve-plan "$PLAN_ID" --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME` reported `{"executed":true,"target_api_ready":true,"inference_ok":true,"trial":"PASS","restoration":{"status":"RESTORED","issues":[]},"status":"PASS_RESTORED"}`. Private local evidence `/home/inlc/.local/state/blazux-wizard/p2/20261105T230229Z-a4fc14cf8079.json` and associated `.target.log`; only stdout was supplied, file contents not inspected. Supports **real GPU Qwen3.8-27B load/API/small generation and normal-path original Flash-Next return**, not comprehensive GPU benchmark or emergency recovery testing.

**Source-only follow-up**: user requested **Manifest-based Wizard** rather than standalone `docker ps` and `curl`. Added new `scripts/manager/service_status.py`; `./wizard.sh service manager status --json` now composes a single fresh Manifest observation with a bounded API health check using exactly the same snapshot. It compares actual managed container/model/port, `runtimes/service-policy.json` expected served model ID and `/v1/models` response. Returns `LIVE_SERVICE_VERIFIED` only if the recorded checks all pass; otherwise `BLOCKED` with issues. `inventory` and `health` remain separate diagnostics. **No actual DGX run of the newly combined Wizard status yet.** `gpu_exclusivity_verified=false`, `previous_trial_provenance_verified=false` expressly separate current status from historical trial receipt.

---

## E-20261106-P2-CPU-REGISTRY-PASS-AND-GPU-TRIAL-SOURCE

**Actual user-supplied DGX:** refreshed isolated CPU `./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only` reported **all 9 checks true**, including `qwen3_5_module_imported`, `qwen3_5_class_present`, `modelopt_module_imported`, `modelopt_nvfp4_class_present`, `quant_registry_factory_present`, `modelopt_mixed_registry_class_matches`, `modelopt_mixed_cli_name`. `observed_quantization_name=modelopt_mixed`, `issues=[]`, `status=IMPORT_AND_REGISTRY_PRESENT_UNQUALIFIED`, `gpu_verified=false`, `launch_authorized=false`. Actual Qwen3.8 checkpoint continues to declare internal `Qwen3_5ForConditionalGeneration`.

**Source only:** Implemented opt-in exact-approved, single-GPU 27B trial and strong original-container restoration. Source commit `ea28b0c0ddbe085782617cc1445c2fcaf613f2a4`; [GitHub Actions run 42124595787](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42124595787) **SUCCESS 354/354 CPU tests, 16 suites**. No real DGX GPU model load, inference, stop/start, or recovery has been run yet. This capability must not be described as tested rollback.

**External comparative sources** (not direct proof of this pinned image):
- `https://github.com/MiaAI-Lab/Qwen3.8-27B-DGX-Spark-RTX-6000`: Unsloth compressed-tensors, separate from NVIDIA ModelOpt `nvidia/Qwen3.8-27B-NVFP4`.
- `https://forums.developer.nvidia.com/t/qwen3-8-27b-nvfp4-on-a-single-dgx-spark-up-to-1m-context-vllm-mtp-measurements/380244/17`: GB10 NVFP4-specific community kernel caveats, MTP after basic start.
- `https://github.com/eugr/spark-vllm-docker`: supports NVIDIA checkpoint and DGX Spark-specific images; adopt only after checking exact format/recipe.
- `https://build.nvidia.com/spark/vllm/intermediate`: official Spark guide includes NVIDIA 27B, alternative NVIDIA vLLM image as potential contingency.

---

## E-20261106-P2-CPU-IMPORT-DGX — observed import PASS, name-probe false negative

Operator DGX `git pull --ff-only` fast-forward `99dde4c..9db92f7`. Image inspected `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. `./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only` yielded **five PASS** checks (Qwen3.5 module and model class, ModelOpt module, ModelOpt MixedPrecision config class, NVFP4 config class). `modelopt_mixed_cli_name=false` and `MODEL_OPT_NAME_LOOKUP_FAILED:TypeError` were due to audit code calling instance method `get_name(self)` as a classmethod. Output `status=BLOCKED`, `runtime_qualified=false`, `executed_gpu=false`. Incidental restricted-container warning `vllm._C ModuleNotFoundError` and CUDA runtime missing; not proof of production loader failure. **No GPU run or source Flash-Next stop.**

Follow-up code `0a14f189c4dae61827298fde46f3148d316f8c72` changes check to vLLM public `get_quantization_config("modelopt_mixed")` registry/class identity. CI run `42121160545` **SUCCESS 336/336 CPU tests**. This **corrected registry probe has not yet been executed on DGX**; record its actual JSON when provided.

---

## E-20261106-P2-DGX-SERVE-SPLIT — actual DGX status and startup preview after file separation

User-supplied DGX stdout: `git pull --ff-only origin feature/recipe-wizard-handoff` advanced `b1c9b2e..c44aa72` and then `c44aa72..99dde4c`. After split, `./scripts/serve_27b.sh --status` yielded `action=runtime-preflight`, immutable NVIDIA revision `482ca0f3832238542f8f5295dde86b5f22711d80`, ModelOpt FP8 208/NVFP4 193, 401 total, image id `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, ARM64/v0.32, `status=BLOCKED`, `runtime_qualified=false`, six explicit unresolved gates. `./scripts/serve_27b.sh --plan` returned `action=start-preview`, `observed_source.api_identity_confirmed=true`, original `qwen38-flash` with the **same image ID** as 27B candidate, 27B proposed `modelopt_mixed` / 8192 / seqs1 / 0.70/eager; `status=BLOCKED`, `operations_enabled=false`, `plan_id=null`, `executed=false`. This proves the split routing and live source identity; not GPU import/launch or benchmark.

**New source CI, not yet DGX evidence:** commit `834c750fc966f73c885fcfc5d81d054a60ae419e`, Actions `42112730764` SUCCESS **333/333** CPU tests including eight CPU import audit unit tests. The import tool was NOT_RUN on the operator DGX at evidence capture time.

---

## E-20261106-SERVE-SPLIT-CI — dedicated model serve entrypoints

GitHub source branch `feature/recipe-wizard-handoff`, commit `67a54afc615e51f207f12238e8473200c62a1aad`, Actions run `42111216055` **SUCCESS 325/325 CPU tests, 16 suites**, including 10 new `tests/test_serve_split_cpu.py` tests. Modified `flash` to invoke copied original `scripts/serve_flash-next.sh`, preserving P1 options, legacy `scripts/serve.sh` as a thin dispatcher, and source-only `scripts/serve_27b.sh` with no Docker run/stop. Existing `tests/test_flash_launch.py` continued PASS with synthetic Docker. No actual DGX process or GPU service execution occurred as part of this source edit. Latest real DGX 27B pinned ModelOpt metadata and image static source proof are in earlier E-20261106 entries.

---

## E-20261106-P2-DGX-STATIC — exact pinned 27B CPU source proof from operator

Operator supplied actual DGX outputs (2026-11-06 KST):
1. Exact `nvidia/Qwen3.8-27B-NVFP4` revision `482ca0f3832238542f8f5295dde86b5f22711d80` source found. Quantization audit `MIXED_PRECISION`, `producer=modelopt`, `layer_algorithms={"FP8":208,"NVFP4":193}`, `layer_count=401`, `issues=[]`, `mixed_fp8_nvfp4_metadata=true`, `runtime_qualified=false`.
2. `./scripts/temporary/p2-27b-image-audit.sh --plan`: `CPU_ONLY_PROBE_PLAN`, local image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, no GPU/network/port mutation.
3. `--execute-cpu-only`: `SOURCE_SURFACES_PRESENT_UNQUALIFIED`, image registry Qwen3.5 true, Qwen3.5 class true, ModelOpt FP8/NVFP4/mixed algorithm literals true, mixed config classes true; all three Python source modules parsed. `executed_gpu=false`, `gpu_verified=false`, `runtime_qualified=false`, `launch_authorized=false`.
4. User reported git pull 13 changed files, no service stop/restart, and old Flash-Next status `observed_model=flash-next`, `:8000` listening from live preflight. Full 27B runtime remains `BLOCKED` as designed.

**SOURCE CI:** GitHub commit `ae4490d66d9c1b9306435165a9821253ee6f38d7`, Actions run `42110115101`: SUCCESS **315/315 CPU tests PASS**. Added dedicated non-executable 27B launch argv and API identity/baseline checks, not a GPU run. Initial `234a8e4a` CI had one failing *test-only placeholder assertion*, fixed by `ae4490d6`; latest success supersedes the first failure.

---

## E-20261106-P2-QUANT-SOURCE-CI — Pinned ModelOpt audit unit tests

GitHub `cd63f25f0bf7282ea06dbb13c3499798394322b0`, Actions `42065472163` — **303/303 CPU tests PASS**, all 15 test batches and deliberately unqualified candidate-recipe check SUCCESS. The added P2 audit uses `hf_quant_config.json` in exact NVIDIA immutable snapshot and reports layer algorithm counts; malformed/oversize/unknown algorithms fail closed. Neither the new quantization fields nor static image source checks have been run on DGX yet; GPU/27B loader/bench/API/transition and recovery **NOT_RUN**. The previous DGX `status --inspect-runtime` result remains a **config-only** observation, not a per-layer audit.

---

## E-20261106-P2-READONLY — DGX real NVIDIA 27B qualification observation

- Operator ran `git pull --ff-only origin feature/recipe-wizard-handoff`: fast-forward `e99914c..edf0968`, checkout clean as reported.
- Real DGX `./wizard.sh model 27b status --inspect-runtime --json`: source candidate **present** at full SHA `482ca0f3832238542f8f5295dde86b5f22711d80`, architecture `Qwen3_5ForConditionalGeneration`, model type `qwen3_5`, quant method `modelopt`, context 262144, vision config yes, host aarch64; Docker image `qwen38-flash-dgx:v0.32` image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, Linux/ARM64, `qwen38.base=v0.32`, `repo_digests=[]`.
- Observed original Flash-Next active on host port 8000; NVIDIA download container no longer running. No GPU residency validation (`gpu_verified=false`), actual loader/model start/27B API/benchmark/rollback `NOT_RUN`.
- Read-only preflight correctly BLOCKED: `VLLM032_27B_LOADER_NOT_QUALIFIED`, `MODEL_OPT_MIXED_NVFP4_FP8_GPU_NOT_QUALIFIED`, `IMAGE_DIGEST_NOT_PINNED_IN_VALIDATED_RECIPE`, `GPU_MEMORY_AND_CONTEXT_PROFILE_UNVERIFIED`, `27B_START_AND_FLASH_NEXT_ROLLBACK_NOT_VERIFIED`, `ACTIVE_MODEL_REQUIRES_SEPARATE_TRANSITION_APPROVAL`.
- Public vLLM 0.32.0 supported models list `Qwen3_5ForConditionalGeneration` and versioned ModelOpt code provides NVFP4+FP8 mixed config. **Public upstream != local patched image**: image static audit developed but actual DGX execution of image source probe still `NOT_RUN`. See https://docs.vllm.ai/en/v0.32.0/models/supported_models/ and https://docs.vllm.ai/en/v0.32.0/api/vllm/model_executor/layers/quantization/modelopt/ .
- **CI on `acf5d64a37929811af9e2da33fa1b30de5e38cb0`: SUCCESS, 294/294 CPU tests PASS.** No GPU/API/inference actions performed by GitHub development.

---

## E-20261106-P2-DOWNLOAD — NVIDIA pinned download PASS (operator DGX evidence)

- Command: `./wizard.sh model 27b download --guided`; approval ID `e7d3ee776b65c3c5e3395fbeff5d0d739ef432028c030df8d604578412570c49`.
- `Fetching 19 files: 100%` (19/19); process exit 0; final `status=PASS`, `executed=true`, `scope=DGX_NETWORK_DISK`, `checkpoint_status=SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, `issues=[]`.
- Repo/revision: `nvidia/Qwen3.8-27B-NVFP4` / `482ca0f3832238542f8f5295dde86b5f22711d80`.
- Evidence: `/home/inlc/.local/state/blazux-wizard/p2/evidence/20261105T150433Z-bd8cf46ef5.json`.
- Independent weight-shard cryptographic rehash **NOT_RUN**; loader/GB10/GPU/API/benchmark/rollback **NOT_RUN**. `gpu_verified=false`.
- GitHub-only new preflight/test code: **SOURCE implemented; CI pending final HEAD**. No DGX source update or GPU operations by this coding session. This record supersedes older transfer 84% observations.

---## 2026-11-06 — Complete Wizard SOURCE; actual runtime remains gated

- GitHub SOURCE: `wizard/console.py` full three-level operator UI; `wizard/workflow.py` consistent P1/P2/P5 model action catalog; `wizard/roadmap.py` release evidence view; `scripts/manager/service_logs.py` bounded read-only log tail. Existing `scripts/manager/p1_wizard.py` and `scripts/manager/p2_27b_download.py` preserved. Added test suites `test_wizard_workflow_cpu.py`, `test_wizard_roadmap_cpu.py`, `test_service_logs_cpu.py`; no real Docker/GPU/network operations executed from GitHub code edits.
- A CPU regression exposed a bypass where P1 guarded start dispatch ignored its own capability BLOCKED result. Fixed by requiring `GUARDED_P1` and preventing P1 quickstart when 27B/Orcarouter is active; latest CI must show PASS before releasing source.
- Last DGX runtime evidence remains operator-reported NVIDIA 27B download started at `Fetching 19 files: 84%`, NOT_VERIFIED complete. No P2 NVFP4 loader, GPU acceptance, P3/P6 switch, P4 deletion, Orcarouter runtime or P7 release PASS evidence exists in this turn.

## 2026-11-05 — Service health and transition preview CPU evidence

- SOURCE: local :8000 GET-only health/model-ID observer, with no inference POST, no Docker mutation, fixed request/size/time bounds; source-only stop-old → port release → new start → API verify → rollback preview, always BLOCKED without verified executor.
- CPU mock tests cover correct served model ID, ID mismatch, bad or oversized response, unqualified Orcarouter, unknown service, stop-before-start and rollback invariants, and no hidden GPU/Docker actions.
- Actual DGX service health action, 27B model start/switch and rollback: **NOT_RUN**. Source CI status must be confirmed at final HEAD. Last real DGX transfer evidence still only `Fetching 19 files: 84%`.

## 2026-11-05 — First DGX NVIDIA 27B transfer and unified Wizard source

- **Actual DGX operator terminal:** `./wizard.sh model 27b download --guided` with exact approved plan id `e7d3ee776b65c3c5e3395fbeff5d0d739ef432028c030df8d604578412570c49`, `Fetching 19 files: 84% (16/19)`. Scope DGX NETWORK/DISK, actual transfer **STARTED**; completion, source checksum/index audit and outcome evidence **NOT_OBSERVED**. Existing `qwen38-flash` still Up with external host :8000 at initial plan.
- GitHub SOURCE: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`, `wizard/quickstart.py`, three-choice root TTY menu, live `download_running` manifest, unqualified Orcarouter policy, new CPU test matrix and legacy CLI compatibility. This is **SOURCE/CI evidence only**, no DGX UI update or GPU execution.
- Final HEAD CI must be checked after all documentation and tests. Old P1 bounded verify/benchmark PASS remains historical and does not imply 27B qualification.

## 2026-11-05 — Guided NVIDIA download refusal evidence and correction

- Actual DGX console: operator supplied the full Wizard-computed plan ID `b190c936072038bc55c14c62dd2f9a63e3ddbf5c2e1ebbf0d1710551a7ec21ce`. Wizard returned `status=BLOCKED`, `executed=false`, `issues=[PREFLIGHT_CHANGED_REPLAN_REQUIRED]`. There is **no actual NVIDIA download execution evidence**.
- GitHub source analysis: live preflight hashed mutable `free_inodes`, free GiB floor and human Docker status. The lock/state directory is created between plan generation and the second preflight, so drift can arise without a meaningful safety change.
- SOURCE remedy: stable `_approval_facts` fingerprint; retain dynamic safety gates and ten-minute approval period; add regression tests. CPU/CI PASS verdict must be checked at final HEAD. DGX second attempt `NOT_RUN`.

## 2026-11-05 — NVIDIA 27B pinned acquisition SOURCE and single-model policy

- Authoritative public checkpoint: `nvidia/Qwen3.8-27B-NVFP4`, immutable `482ca0f3832238542f8f5295dde86b5f22711d80`, 3 indexed safetensors shards (~21.9GB): https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/482ca0f3832238542f8f5295dde86b5f22711d80 .
- Prior actual DGX user-provided inventory (before current code): `NO_PINNED_LOCAL_SNAPSHOT` for NVIDIA 27B. No evidence of downloaded NVIDIA checkpoint or running 27B service yet.
- New GitHub SOURCE: guarded no-GPU, no-port Wizard download, pinned-without-refs scanner, single-model service policy, read-only observed manifest and transition journal primitives. Actual DGX download/GPU/API 27B/start-stop-switch: **NOT_RUN**. The runtime approval boundary remains independent of download approval.
- Latest CPU CI should be checked against final commit before claiming PASS.

## 2026-11-05 — NVIDIA P2 cache and service-menu evidence

- DGX user console: `nvidia/Qwen3.8-27B-NVFP4`, `refs.main=null`, `local_revision=null`, `indexed_shard_count=0`, `incomplete_blob_files=0`, `source_files_present=false`, `issues=[NO_PINNED_LOCAL_SNAPSHOT]`. Scope: read-only `~/.cache/huggingface` only; actual download NOT_RUN.
- New GitHub SOURCE: Wizard `service manager` module and `model 27b plan --for-action download` fail-closed action. CI verdict requires latest-HEAD check. No DGX service, download, GPU, benchmark execution.

## 2026-11-05 — P2 model selection and provenance split

**DGX observation (historical, not NVIDIA):** user-supplied Wizard read-only inventory for `RadixArk/Qwen3.8-27B-NVFP4` at revision `52d1adc5f38aa5ebf099c29ed7025ba34cfbb854`; 3/3 indexed shards, 0 incomplete transfers, `issues=[]`. **Current chosen P2 model:** `nvidia/Qwen3.8-27B-NVFP4`; NVIDIA cache inspection, immutable SHA, vLLM 0.32 GPU operation and benchmark remain NOT_RUN. Public NVIDIA model card lists vLLM on GB300 TP4, not a qualification of this single Spark GB10. https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4

## 2026-11-05 P2 — config audit SOURCE evidence

- GitHub-connected source patch: `scripts/manager/p2_27b_inventory.py`, `tests/test_p2_27b_inventory_cpu.py` on `feature/recipe-wizard-handoff`.
- Evidence level: **SOURCE committed**. CI at new HEAD requires separate run confirmation; no local DGX, GPU, Docker, network download or model service test was executed.
- Previous P1 operator report remains valid with its original dated scope. No P2 runtime qualification inferred from candidate checkpoint metadata.

# Evidence ledger — observed facts and test reports

## E-20261105-16 — P1 baseline, advanced tests, and bounded GPU bench PASS

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

## E-20261105-17 — 27B source-only cache discovery

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

**Source/CPU**: code/testing/CI in this branch, independent of DGX GPU acceptance. No 27B GPU benchmark, install, live switch, or production rollout observed.


Use an append-only entry for every meaningful result. Never substitute README claims or previous chats for locally reproduced tests.

## Entry template

| Field | Value |
|---|---|
| ID / KST | `E-YYYYMMDD-NN` / timestamp |
| Model / recipe / revision | full id + immutable revision |
| Git HEAD / branch | exact actual SHA and branch |
| Runtime image / host | immutable digest, vLLM version, GPU/driver/OS |
| Scope | SOURCE / CPU / CI / GPU / API / SWITCH / RELEASE |
| Exact invocation | command/environment; redact secrets |
| Inputs | test names, prompt/seed hashes, dataset scope |
| Result | PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE |
| Artifacts | paths/URLs/digests |
| Limits | scope, caveats, unresolved mismatches |

## E-20261104-01 — source-only planning baseline

- **Scope:** SOURCE / GitHub metadata and public source inspection, **not** GPU.
- **Repo:** `kjlee-inlct/qwen3.8-Flash-DGX`.
- **Source commit:** `blazux/qwen3.8-Flash-DGX@b0aa8b77604139557169387b2fa8386355d8b651`; user fork main same at branch creation.
- **Source observations:** `flash` and `profiles` cover NVIDIA and RadixArk Flash-Next; `scripts/serve.sh` removes container matching `NAME`; `feature/orcarouter-bf16-adapter` already holds a design doc; aphex3k 27B recipe uses SGLang, **not** local vLLM 0.32 proof.
- **Result:** `PASS_SOURCE_INSPECTION` for cited facts; `NOT_RUN` for CPU tests, CI, DGX runtime/benchmark.
- **Artifacts:** [Blazux source](https://github.com/blazux/qwen3.8-Flash-DGX/tree/b0aa8b77604139557169387b2fa8386355d8b651), [Orcarouter parallel branch design](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/blob/feature/orcarouter-bf16-adapter/docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md), [27B external reference](https://github.com/aphex3k/Qwen3.8-27B-on-DGX-Spark).
- **Limits:** No current disk, container, memory or actual 27B vLLM evidence.

## E-20261104-02 — new planning branch and documentation

- **Scope:** GitHub SOURCE / documentation-only.
- **Branch base:** `feature/recipe-wizard-handoff` created from `b0aa8b77604139557169387b2fa8386355d8b651`.
- **Result:** `PASS_SOURCE/GITHUB`: 10-file commit `76cd8dae16b0f34e47c353b56b6e9dbcc5fcde25` confirmed by branch readback and compare with `main`; draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) opened against `main`, unmerged. `NO_CHECKS_REPORTED` for that original commit (0 check-runs, 0 PR workflow runs). **No CPU, CI, GPU or service tests run.** This entry does not qualify any runtime.
- **Artifacts:** `docs/MODEL-RECIPE-WIZARD-PLAN.md`, `docs/MANIFEST-CONTRACTS.md`, `handoff/*`.
- **Limits:** Manifest examples, wizard commands and state machines are designs, not implemented software.

## E-20261104-03 — N1 isolated CPU source contract check

- **Scope:** SOURCE/CPU (2026-11-04 KST). Executed in a separate CPU container, **not DGX**. Previous fork HEAD read: feature/recipe-wizard-handoff@07b0e3d49b387ecc29c00e3f5338e4e7065bcc27; new commit must be verified independently.
- **Tools:** Python 3, PyYAML 6.0.3, jsonschema 4.26.0; no vLLM/CUDA/Docker.
- **Exact commands:** python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -q => **15 PASS**; python3 -m scripts.manager.manifest validate recipes/qwen38-27b.candidate.yaml => expected **FAIL**, exit 2, 6 invalid/unverified fields; same command with tests/fixtures/recipe-valid.synthetic.yaml => schema **PASS**, exit 0, launch_authorized=false.
- **Artifacts:** schemas/recipe.schema.json; scripts/manager/manifest.py; recipes/qwen38-27b.candidate.yaml; tests/test_manager_manifest_cpu.py; tests/fixtures/recipe-valid.synthetic.yaml.
- **Limits:** synthetic a/b/c-character SHA values are fake fixture data; schema PASS is not repository existence/image runtime compatibility evidence. CI awaits new PR SHA observation. GPU/API/SWITCH/RELEASE NOT_RUN. No current DGX state observed.

## E-20261105-01 — Flash-Next 8000 default/N2 inventory source implementation

- **Scope:** SOURCE/CPU TEST CODE. Old fork HEAD was `bf453aea425c0d9136d67ac003a4f296a0a96885`; GitHub commit/CI outcome must be re-read after updating branch.
- **Change:** default Blazux NVIDIA Flash-Next, hybrid/YaRN/MTP2, exposed :8000/v1, served `qwen3.8-flash-next`; refactored unsafe implicit Docker container replacement into fail-on-name-exists. Removed outdated schema hard-coding of port 8000 and historic Orcarouter name.
- **Added read-only inspections:** `python3 -m scripts.manager.inventory doctor --dry-run` and `plan --dry-run` via Wizard. Commands collect local Docker/ss/disk/HF cache metadata; never execute model/Docker mutation.
- **New tests:** `tests/test_manager_inventory_cpu.py` (10 synthetic scenarios), `tests/test_flash_launch.py` (+4 cases), `tests/test_manager_manifest_cpu.py` updated old port expectations. GitHub CPU workflow expanded; **CI_NOT_YET_OBSERVED** in this source entry.
- **DGX:** user reports old services removed, **NOT_INDEPENDENTLY_VERIFIED**. No model/download/GPU/API/bench, no new runtime measured; required source/model image revisions still to be pinned for release.

## E-20261105-02 — CI failure and corrective script mode

- **Scope:** CI, commit `7e8f4a109a04c130a5dba0d73e3ece0881d85478`.
- **Observed:** GitHub Actions jobs [push failure](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41947918546/job/126984612955) and [PR run](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41947924748/job/126984632242) reported manifest **15/15 PASS**, N2 Inventory **10/10 PASS** and launch **4 FAIL/13**. Exact failures: `test_capable_dflash_launch`, `test_default_options_remain_empty`, `test_default_port_8000_and_next_flash_model_id`, `test_docker_options_reach_docker_not_vllm`; shell exit 126.
- **Root cause:** GitHub tree update accidentally wrote executable shell paths `flash` and `scripts/serve.sh` as `100644`. Root Git tree confirmed incorrect modes; not a demonstrated model/runtime bug. Correction restores `100755`; actual CI rerun must be independently checked. No failure history removed.
- **DGX:** NOT_RUN, no status observed.

## E-20261105-03 — Confirmed Wizard-first P1–P7 roadmap (decision, not test)

- **Scope:** USER_DECISION / DOCUMENTATION. The user reconfirmed sequential Wizard execution for all milestones. Evidence is the user request; not runtime testing.
- **Last independently verified source CI:** `feature/recipe-wizard-handoff@017319a5394155797bcb7e5c933ccef35080d669`; [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41948116286/job/126985272415) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41948122438/job/126985292140) **SUCCESS** (15 manifest + 10 inventory + 13 launch + 1 script modes = 39/39 tests each). Historical `7e8f4a1` four test failures remain recorded in E-20261105-02.
- **Current deliverable:** documentation-only alignment, no new source-test execution; CI for resulting documentation HEAD to be read back. **GPU/API/BENCH/SWITCH/RELEASE = NOT_RUN**; live DGX and :8000 occupancy **NOT_OBSERVED**.
- **Boundary:** Roadmap confirmation does not itself approve GPU loading or model/cache deletion. P4 is conditional with exact approval; `SKIPPED_NOT_NEEDED` permitted.

## E-20261105-05 — DGX terminal log supplied by operator

- **Source/scope:** user-attached terminal output, 2026-11-05; `USER_SUPPLIED_DGX_LOG`, **not direct SSH observation**. `wizard/00-doctor.sh`, `wizard/10-plan.sh` reported `collision_free=true`, host :8000 unoccupied, no `qwen38-flash` container, 580,134,281,216 bytes free. OpenWebUI and Portainer were still running. `./flash doctor default` showed aarch64 GB10, unified memory 121 GiB total /117 GiB available, Docker 29.6.2.
- `./flash setup default` image build **FINISHED**, `qwen38-flash-dgx:v0.32` image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, then resumed download for `nvidia/Qwen3.8-Flash-Next-NVFP4`; last output **9/25 (36%)**. **No proof** download/hybrid/serve/API/bench complete.
- The shell already received `./flash serve default`, `./flash wait`, `./flash test` sequentially after setup. These may run without any additional assistant action once setup finishes. Do not start a second `setup`, `serve`, change the active worktree, or remove any assets.
- Observation is time-bounded; fresh current status remains required.

## E-20261105-06 — P1 Wizard code + CPU mock suite

- **Scope:** SOURCE (GitHub commit `c625a49276272e90d19ab6367f580a0230754890`), CI verified: 2/2 SUCCESS, 80/80 CPU tests each. Added `p1_assets.py` fail-closed snapshot/index and symlink audit, `p1_wizard.py` live plan/approval/action runner, `p1_bench.py` SSE benchmark, `wizard/p1.sh` shell entry, and `tests/test_p1_*_cpu.py` fake backends. Extended GitHub workflow: 41 new P1 CPU tests and 39 baseline CPU tests PASSED in each of two jobs; [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41959325678/job/127021656282) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41959334560/job/127021682353).
- **Limit:** No DGX Wizard operation performed by assistant; no new GPU/API/benchmark results claimed. Plans require complete assets, live image identity, container/port checks and fresh exact approval, and cannot automatically download/clean up/switch.

## E-20261105-07 — Modular P1–P7 Wizard CLI source/CI

- **GitHub SOURCE commit:** `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`, branch `feature/recipe-wizard-handoff`; [CI push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961358317/job/127028222400) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961362251/job/127028234413), both **SUCCESS**. Per job: 15 manifest + 10 inventory + 13 legacy Flash + 1 shell mode + 41 P1 + 21 routing = **101/101 CPU PASS**.
- **Contract:** `./wizard.sh list --json`; `./wizard.sh p1 status --json`; `./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json`; `./wizard.sh --stage p3 --action switch ... --json`. P2–P7 are **INTERFACE_ONLY / runtime NOT_RUN / operations_enabled=false**; execute/approval arguments return BLOCKED. P1 delegates to existing approval-protected core.
- **Follow-up:** P1 JSON-guided handling improvement and 2 tests submitted in a separate commit; verify updated CI independently. **No assistant DGX command, GPU/API/BENCH, switch, cache cleanup or Docker operation**. Prior operator-supplied download and queued commands not interrupted.

## E-20261105-08 — Final modular Wizard CLI source CI

- **Source/docs HEAD tested:** `feature/recipe-wizard-handoff@43f5131b63b7e3f20cde0c409b3ddd672ddb349b`. Two GitHub Actions `manifest` checks completed **SUCCESS**: [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961837000/job/127029761586) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961842431/job/127029780582).
- **Observed CI logs per job:** 15 manifest PASS + 10 Inventory PASS + 13 legacy Flash PASS + 1 executable mode PASS + 41 P1 CPU PASS + 23 Wizard router PASS = **103/103 CPU tests**. P1 guided mode in JSON returns BLOCKED without prompting and normal TTY path remains supported. Unsupported stages and fake approvals are blocked.
- **Runtime boundaries:** all code tests are GitHub-hosted CPU-only mocks; **DGX Wizard GPU/API/BENCH/SWITCH/RELEASE NOT_RUN**, no new images/weights served and no cleanup. P2–P7 are non-executable planning interfaces. Previous user-supplied DGX image-build/download log is time bounded and not superseded by CI results.

## E-20261105-09 — Domain-grouped Wizard refactor and compatibility CI

- **Source commit:** `571e1c204d76bcb66b9e02cb1315ac775013a130` on `feature/recipe-wizard-handoff`. GitHub Actions [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41967161260/job/127046714703) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41967169194/job/127046737309) both **SUCCESS**.
- **CPU test logs per job:** 15 manifest + 10 inventory + 13 legacy Flash + 1 permission + 41 P1 + 32 grouped CLI router = **112/112 PASS**. Newly verified: grouped catalog, four domain categories, P1/P2/P5 model routes, P3/P6 switch routes, legacy stage aliases, no-TTY/JSON safety and fail-closed future stages.
- **Boundaries:** `SOURCE/CI PASS` only. **DGX GPU/API/BENCH/SWITCH/CLEANUP/RELEASE=NOT_RUN** for this refactor; current live download/port status not re-probed, no user-owned shell process modified. P2–P7 are `INTERFACE_ONLY` and execution is blocked.

## E-20261105-10 — Temporary P1 operator bundle source/CI boundary

- **Scope:** SOURCE/CPU/CI pending exact new commit; `scripts/temporary/p1-post-download.sh` shell wrapper, `p1_post_download.py` Python coordinator, `scripts/temporary/README.md`, `tests/test_p1_temporary_cpu.py`; CI workflow extended with fake backend tests and shell/executable mode checks.
- **Safety design:** only read-only diagnostics by default; per-action plan hash validated through current P1 Wizard; terminal consent separate for verify and benchmark, no benchmark without verify PASS, process/branch/dirty-tree guards; JSON report outside Git and model cache with 0600 permissions, no automatic model mutation.
- **Evidence outstanding:** new GitHub Actions results and actual DGX operator log. User's prior download/setup chain must be confirmed finished **before** using the wrapper. No assistant-executed DGX/GPU/API/benchmark, no service changes or cache deletion; `DGX=NOT_RUN` until operator returns evidence.

## E-20261105-11 — P1 temporary operator bundle CPU CI accepted

- **Code HEAD:** `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b`, `feature/recipe-wizard-handoff`. GitHub Actions [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970955588/job/127058833280) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970960007/job/127058848658), both **SUCCESS**: 131 unique CPU tests each (15 manifest, 10 inventory, 13 launch, 1 script mode, 60 P1 including 19 temporary tests, 32 router).
- **Tested behaviors (mock DGX):** safe read-only inspection; no setup/Git reset/Docker rm; independent live Wizard plan approval; blocked/dirty/wrong-branch/active-setup refusal; mid-run race prevention; benchmark only after verify PASS; restricted JSON artifact outside Git/HF cache.
- **Real DGX:** `NOT_RUN_BY_ASSISTANT`. No GPU/API/benchmark results, operator's queued `flash setup/serve/wait/test` completion still not observed and must be confirmed before `git pull`/wrapper.

## E-20261105-12 — DGX operator report: checkpoint download finished, Wizard blocked

- **Source:** user-provided DGX terminal output and operator clarification, 2026-11-05. **Evidence scope:** USER-REPORTED download complete; console wrapper evidence for `git pull` and `bash scripts/temporary/p1-post-download.sh`; not assistant SSH and not complete raw `result.json`.
- **Git/host:** `feature/recipe-wizard-handoff@dea7c5aa183da770b6b467288f2f6eedf8e94946` fast-forward; working tree clean; no relevant active setup process detected. Result path `/home/inlc/blazux-p1-reports/20261105T052545Z-1e6ec592/result.json`.
- **Read-only command statuses:** doctor=3, inventory_plan=3, HTTP health=0, HTTP models=0, GPU command=0, Docker command=0. Response contents and model ID were not pasted. P1 verify and benchmark `status=BLOCKED`, issues `checkpoint_downloading_or_incomplete` and `hybrid_not_prepared_or_incomplete`; no Wizard actions executed.
- **Interpretation:** generic P1 source/Hybrid audit failure; not evidence of ongoing download. Could be refs-main-only handling, stale incomplete blobs, missing Hybrid marker/files or a different configured cache/mount; no cause selected without new diagnostic facts. New `p1_cache_diagnosis.py` provides read-only facts from actual snapshot and strict audit. SOURCE/CPU CI verified at `4c0041dd230e2abe22ba8379aca74068933ecece`: GitHub push and PR both SUCCESS, each **138/138 CPU tests PASS** (15 manifest + 10 inventory + 13 launcher + 1 executable-mode + 67 P1 + 32 Wizard router). The earlier `eb759ad` source attempt failed its tests because the optional new diagnostic key was absent from an old fake fixture; fixed in `4c0041d` without changing runtime assets. Real DGX evidence still pending.
- **P1 GPU/API/benchmark:** Wizard verification and benchmark `NOT_RUN`; observed curl GET is an API reachability test, not a workload benchmark or complete model identity verification.

## E-20261105-13 — Default NVIDIA index cap regression fixed, actual missing files unresolved

- **Model release fact:** NVIDIA `nvidia/Qwen3.8-Flash-Next-NVFP4` revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` includes `model.safetensors.index.json` (~31.3 MB) and `tokenizer.json` (~12.8 MB). Source: https://huggingface.co/nvidia/Qwen3.8-Flash-Next-NVFP4/tree/main
- **Source bug:** Python strict index parser refused >16MiB (incompatible with official file), though the operator's **observed filenames** were initially rejected before this parser. Source change now permits ≤64MiB while retaining bounds; diagnostic returns exact file/symlink/size status, not merely `checkpoint_downloading_or_incomplete`.
- **GitHub evidence:** code/test commit `66c6c448c1922f958886fa4696c403a4b6227685`, push job https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41976231273/job/127075608240 and PR job https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41976236273/job/127075624614 — both **SUCCESS**, per job 15 + 10 + 13 + 1 + 74 + 32 = 145 CPU tests PASS.
- **Operator DGX prior evidence:** source files `model.safetensors.index.json`, `tokenizer.json` failed `_good_file` metadata validation; Hybrid `tokenizer.json` failed with `.prepared` present. HF blob incomplete-count=0, refs/main valid. Exact failure mode (missing vs dangling symlink vs zero-size) NOT YET OBSERVED. No actual P1 Wizard GPU/API workload BENCH acceptance.
- **Next**: `git pull --ff-only` then one read-only temporary wrapper; review exact file metadata and served API ID. No guessed setup/download/prepare, and no modifying current services.

## E-20261105-14 — DGX confirms externally linked Flash-Next metadata

- **Operator-supplied output:** `/home/inlc/blazux-p1-reports/20261105T055849Z-084c3609/result.json` summary after `git pull` to `4708fe9ef396404d823ca385cde013b67e4d098a`. `api_model_ids=["qwen3.8-flash-next"]`; full snapshot revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`; incomplete blob count 0. Original model index + tokenizer and Hybrid tokenizer: `TARGET_OUTSIDE_REPOSITORY`, `symlink=true`, successful target resolution; Hybrid index `PRESENT_NONEMPTY`, `size_bytes=31907813`; Hybrid marker present.
- **Interpretation:** Existing Blazux-compatible shared metadata link layout was over-rejected by the new P1 file containment check. This alone does not prove that every model tensor is valid or any GPU workload passed. The API served ID indicates there is an API service listening despite the user's description of no existing services.
- **Test authorization:** user approves bounded, non-disruptive GPU inference/benchmark without manual per-action hash entry. Implement `--auto-gpu` as a scoped script option; still validate each current Wizard plan ID and fail closed on changed preflight or failed P1 verification. No service lifecycle or cache changes authorized.
- **Source/CPU CI evidence:** `0063b0e004902408f980c155076c098d49d4569e`, GitHub push and PR jobs **SUCCESS**, 155 CPU PASS each (15 manifest, 10 inventory, 13 launch, 1 script mode, 84 P1, 32 router). [Push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978150843/job/127081754127), [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978155433/job/127081768853).
- **Next DGX scope:** after code pull, single `bash scripts/temporary/p1-post-download.sh --auto-gpu` call. Actual GPU/API/benchmark statuses remain `NOT_RUN` for the new version until operator evidence.


## E-20261105-15 — DGX P1 assets pass, Wizard's combined verify fails

- **Raw-report path:** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` (operator-owned); only console summary supplied.
- **Facts:** snapshot `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, 11/11 listed shards resolved in source+Hybrid, API model ID `qwen3.8-flash-next`, verify+benchmark plans READY, **verify=FAIL, benchmark=BLOCKED verification_not_passed**. These are verified user-supplied runtime outcomes. No benchmark inference was executed.
- **Known source defect:** original temporary runner only parsed Wizard JSON result on rc=0; Wizard returns rc=2 with evidence even on FAIL, hence console `evidence:null` does not demonstrate no evidence. Original combined `_chat_probe` demanded 48 token text, tools required and tiny vision; one failure throws and masks others. Exact original error is UNKNOWN without reading the saved raw result; do not call this a model failure.
- **SOURCE/CI corrective commit:** `391a2844f4c8549e282eae3e266806c89801ad1a`, [push CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42015135913/job/127203693134), [PR CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42015144016/job/127203722486); 2/2 SUCCESS, 173 CPU tests/job. Separates default completions/chat baseline from optional tools/vision and retains nonzero Wizard evidence; actual DGX post-fix GPU validation NOT_RUN.
- **Next:** inspect stored evidence for original failure, then single auto-GPU wrapper on new code. Do not alter operating service, HF data, Hybrid, or gateway.

## Historic evidence not transferred

## E-20261105-04 — User-reported Flash-Next download still in progress

- **Time/subject:** 2026-11-05 11:46 KST, `nvidia/Qwen3.8-Flash-Next-NVFP4`.
- **Evidence:** user said checkpoint was **still downloading**. Classification: `USER_REPORTED / DOWNLOAD_IN_PROGRESS`, not a DGX/filesystem observation and **not** a checksum or completion proof.
- **Unknown:** actual download process, command, bytes, completion percentage, snapshot revision, local cache path and storage headroom.
- **Verification:** `DOWNLOAD_COMPLETE=NOT_VERIFIED`; `HYBRID_PREPARED=NOT_VERIFIED`; `GPU/API/BENCH=NOT_RUN`. No upload/download/cache/operational operation by the assistant.
- **Next safe action:** build P1 Wizard flows and download-in-progress fail-closed tests from synthetic data; after reported completion, verify snapshot and all weight shards read-only before preparation/serve, avoiding concurrent writes.


Old Preview/YSLAB projects reported Orcarouter BF16 PLE/MTP results; those are **reference evidence only**, not proof of the new vLLM 0.32 fork. Historical Preview strict same-token logprob `1e-4` release blocker remains unresolved. DGX status is unobserved this session.

## Update policy

Append new measured entries, never replace failures. When rerunning a test, give it a new ID and reference prior entry. If an entry proves wrong, add an explicit correction with link; do not rewrite history. Publish non-sensitive artifact locations and keep credentials/private data out.
