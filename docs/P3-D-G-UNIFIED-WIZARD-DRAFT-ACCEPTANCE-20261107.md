## 2026-11-07 — AUDITED P3-A–G; G CLOSED, FAILURE/FINAL RELEASE REASSIGNED TO P8

**Latest acceptance audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`. Historical **A/B/C REAL PASS/CLOSED** (Flash→27B, 27B→Flash, Flash→27B; immutable original receipts); **D REAL READ_ONLY_PASS** for single GPU and independently attributed IPv4/IPv6 host :8000 process ownership (measured before most recent roundtrip); **E DRAFT_REVIEW_REQUIRED** despite confirmed NVIDIA Flash `-fp8hybrid` source variant and source-draft documented-field match because **canonical reinstall-qualified Flash recipe is NOT registered or real tested**; **F 144/144 local Fake-DGX/CPU PASS** with production lifecycle release still OFF; **G REAL BIDIRECTIONAL PASS/CLOSED**, two separately authorized 27B→Flash→27B live transfers, current last observed 27B API `qwen3.8-27b`, `diff=[]`, journal `VERIFIED/COMMITTED` 28 events. **P3-A~G aggregate is NOT fully complete because E remains OPEN and F is only source-qualified.** Don't replay A/B/C/G. The operator reclassified deliberate fault injection, automatic source restoration and final production/UX signoff exclusively as **P8**, which is `NOT_RUN/NOT_RELEASED` and does not block G's closed successful-transfer scope. P7 remains component integration only. Source-only CI after P8 registration: [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS, **856/856 CPU tests / 38 groups**; that does not evidence new DGX runtime results.

**Historical draft runner limitation:** This D/E/F/G tool is read-only and will continue to print G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN` by its own **run scope**, even though an independent real two-way trial PASSED later. The real G receipt contract is reported separately. E still awaits installable Flash canonical recipe; F CPU source tests PASS, production executor remains locked. Intentional fault and final operations acceptance are now P8.

---

## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

**Post-draft real acceptance milestone:** The read-only unified script still has `real_switch_executed=false` by contract, but a **separate operator-approved one-switch real 27B→Flash trial succeeded**. This is not contradictory: draft aggregator measures only read-only tests, while separate executor has a real receipt. P3-G second direction and fault/rollback still pending.

---

## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

**Source/downtime distinction:** `--run --sudo-ss` remains safe/read-only; real P3-G proceeds exclusively through `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` with four TTY inputs. No automatic roundtrip. Separate reverse trial after evidence. See approved runbook. Default draft runner cannot execute real transfer.

---

## 2026-11-07 — THIRD ACTUAL DGX P3-D READ-ONLY PASS; P3-E FP8-HYBRID SOURCE DRAFT

**Actual operator evidence:** Third DGX batch after fast-forward to `1b785c6`: normal `--run` reported D no visible socket PIDs but E `DRAFT_REVIEW_REQUIRED`, F local **136/136 CPU PASS**, G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`. Operator then explicitly ran `sudo -v` followed by `--run --sudo-ss`: **P3-D READ_ONLY_PASS**, both IPv4+IPv6 :8000 `docker-proxy` PIDs (2051487,2051502) independently attributed to canonical active 27B; GPU compute PID 2051842 verified. Overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`, `blocked_stages=[]`, `acceptance_complete=false`; no service mutation or real G transfer. **P3-E** pinned NVIDIA `fc694b54fb0174e0913e6adf86691ef85a4ead47-fp8hybrid` derivative prepared/view files verified; canonical reinstall recipe NOT registered. Legacy Flash cache writable; source metadata and vLLM flags preserved. Evidence `docs/P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md`.

**NEW SOURCE P3-E DRAFT (UNRELEASED):** `recipes/qwen38-flash-next.runtime.draft.json` is `launch_allowed=false`, `register_as_runtime_recipe=false`, not linked into service-policy, no Flash install adapter/executor. `scripts/manager/flash_recipe_review.py` checks versioned pinned Flash 500K/Yarn/MTP2/native tools/image/env/template/mount *documented fields only*, returns `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` or explicit field differences. `P3-E.source_draft_field_review` added to single-script report. P3-E stays DRAFT_REVIEW_REQUIRED; direct live DGX comparison of new code still **NOT_RUN**. CI [42373758262](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42373758262) **854/854 CPU/Fake-DGX PASS / 38 groups**, source only. Full runbook `docs/P3-E-FLASH-FP8HYBRID-SOURCE-DRAFT-20261107.md`.

**Next:** read-only `--run --sudo-ss` batch to inspect E draft comparison, then review remaining host env/mount/image provenance. Separate operator-approved real Flash install and G switch/rollback acceptance required; `PRODUCTION_EXECUTION_RELEASED=False` remains. P3-A/B/C closed, 27B unchanged, P4 optional, P5/P6/P7 queued.

---

## 2026-11-07 — SECOND ACTUAL DGX D–G BATCH + PINNED FP8 HYBRID / HIDDEN SOCKET PIDS

Actual operator DGX batch (**read-only; no model changes**) after previous source fixes: **P3-D BLOCKED** because `ss` showed BOTH IPv4 0.0.0.0:8000 and IPv6 [::]:8000 LISTEN but no process PID; Docker reported only running `qwen38-27b` as GPU/8000 port owner, NVIDIA compute PID 2051842 verified to active 27B. **P3-E BLOCKED** because the observed preserved Flash checkpoint was pinned NVIDIA source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` plus **`-fp8hybrid` local prepared variant**, not a different HF revision; canonical Flash reinstall recipe still unqualified. Flash /hf mount observed writable and legacy argv preserved. **P3-F PASS 128/128 actual local CPU tests. P3-G preview PASS**, current Docker ID and VERIFIED/COMMITTED journal; actual transfer/rollback NOT executed. Overall exit=3, acceptance_complete=false.

Subsequent SOURCE fix: E now recognizes only exact pinned NVIDIA source revision plus `-fp8hybrid` prepared view and verifies `.prepared`/essential files read-only; no recipe promotion. D now permits ONLY operator-selected `--sudo-ss` to run `sudo -n ss` (no prompt; no sudo by default) and independently reverify unchanged socket set and PID provenance. Unknown PID always BLOCKED. CPU CI [42371861344](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371861344) **846/846 PASS / 37 groups**, SOURCE-ONLY, actual DGX rerun pending. Full evidence `docs/P3-D-G-SECOND-DGX-PID-HYBRID-DIAGNOSTIC-20261107.md`. No P3-A/B/C replay, no production switch release.

---

## 2026-11-07 — ACTUAL DGX FIRST RUN + D/E DIAGNOSTIC FIXES

Operator's first `--run` returned **P3-D BLOCKED** despite Docker one-model/port ownership and GPU process verification true: old `ss` parser incorrectly required exactly ONE host socket and reported `HOST_PORT_8000_LISTENER_NOT_UNAMBIGUOUS`. **P3-E BLOCKED** because old Flash argv did not fit the 27B parser; Flash reinstall recipe still unqualified. **P3-F passed all 119/119 local CPU tests**; **P3-G returned `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`**, journal VERIFIED/COMMITTED. No actual model switching took place.

Source fixes now accept independently attributed IPv4+IPv6 port listeners, verify host-cgroup Docker proxy PIDs only when their actual `/proc` argv and current Docker container IP/port binding agree, and expose detailed socket/PID diagnostics without falsely approving absent data. Flash E now records a legacy observed command candidate even when the canonical-27B parser rejects its options; a writable historical Flash `/hf` mount is a review advisory, not a qualified reinstall recipe. **No canonical Flash recipe is promoted**. Current source CI: [42371091647](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371091647) SUCCESS **838/838 tests / 37 groups**. First actual DGX results and limitations: `docs/P3-D-G-FIRST-DGX-DIAGNOSTIC-FIXES-20261107.md`. New DGX read-only rerun is still required to observe real fixes; do not mark D/E PASS based on CPU.

---

# P3-D / P3-E / P3-F / P3-G — Unified Wizard Acceptance Draft

**SOURCE CI VERIFIED (final implementation commit `efb0dda78a4e6f894afe39c97a6839e1d7cf4d53`):** GitHub Actions run [42369840239](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42369840239) completed **SUCCESS, 829/829 CPU tests in 37 reported groups**, including an automatic `python -m scripts.manager.p3_dg_acceptance --cpu-only` invocation. This is source/CI verification, **not actual DGX hardware acceptance or production release**. The subsequent handoff-document-only commits did not require/source-trigger a new hardware test.


**Status:** SOURCE DRAFT IMPLEMENTED, CPU tests pending/qualifying, real DGX D-G acceptance NOT COMPLETE.  
**Branch:** `feature/recipe-wizard-handoff`; existing PR #1 remains Draft, unmerged.  
**Policy:** vLLM 0.32, one GPU model active at a time, fixed API port 8000. SGLang not permitted. Canonical 27B Native Tools recipe SHA and historic P3 A/B/C receipts must not be changed.

## 1. Stage contract

Historical P3-A/B/C are **already REAL PASS and CLOSED** and do not need to rerun. New D–G are **additional stages**. Recurrent switching and general recipe lifecycle apply to all future models, while P4 remains an optional Flash removal/recovery decision, P5 Orcarouter serving/benchmark, P6 Orcarouter/27B transfer, P7 final integrated system release.

| Stage | Objective | Automatic read-only/CPU checks | REAL acceptance gate | Current classification |
| --- | --- | --- | --- | --- |
| **P3-D** | Independent GPU process exclusivity and port 8000 process ownership | Docker complete inventory + `ss -ltnp` port listener + `nvidia-smi` compute-app PIDs + `/proc/<pid>/cgroup` attribution, local active API check | Both GPU and port PID attribution must pass; unavailable tools or docker-proxy outside cgroup are **UNVERIFIED**, not PASS | Source draft only, real DGX pending |
| **P3-E** | Flash-Next canonical runtime/reinstall recipe | Inspect the preserved `qwen38-flash` (current Docker ID + image, command, env, read-only `/hf` mount, GPU/port, P3 provenance); emit **candidate observation**, no recipe promotion | Qualified, versioned Flash runtime recipe and safe reinstall/rollback tested independently on DGX; never auto copy 27B Native Tools flags | Source draft candidate; qualified recipe missing |
| **P3-F** | Repeatable model lifecycle and safe operating executor | Five Python CPU/Fake-DGX suites; existing exact SHA, locks, journal, stop-before-start and rollback code remains release-gated | Production integration, crash/recovery and benchmark pointer/backup cleanup semantics independently accepted; no blind retry | CPU source gate only, not released |
| **P3-G** | General Wizard end-to-end real DGX acceptance | Read-only current-ID operating switch preview, private journal integrity, API identity; no mutation | **Separate authorized** real 27B→Flash→27B, deliberate safe fault test, rollback, postcheck, Wizard UX and persistent evidence, with fresh approval per disruptive action | Preview real DGX PASS in previous observation; actual renewed post-change execution pending |

The automatic single-script D–G runner cannot silently grant downtime/approval. **P3-G cannot become REAL PASS from read-only checks, source-only CI, or a plan SHA.**

## 2. Single command on DGX after fast-forward

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff

# 1. Does not access Docker/GPU/API; prints D-G test and risk contract
bash scripts/temporary/p3-d-g-acceptance.sh --plan

# 2. One command runs CPU/Fake-DGX suites + actual DGX READ-ONLY inspections
bash scripts/temporary/p3-d-g-acceptance.sh --run \
  --report /tmp/blazux-p3-d-g-draft-$(date +%Y%m%dT%H%M%S).json

# Optional CPU-only developer workstation/CI
bash scripts/temporary/p3-d-g-acceptance.sh --cpu-only

# Optional: explicit nonzero exit unless ALL stages have real acceptance.
# Source-only draft always exits nonzero here even if all read-only probes pass.
bash scripts/temporary/p3-d-g-acceptance.sh --run --strict
```

The shell script is a thin wrapper for `python3 -m scripts.manager.p3_dg_acceptance`. It does NOT include `--execute` or an approval flag. No Docker stop/start/run/rm, model download, benchmark, delete, cache writes, journal mutations, or live model changes. `--report` is the only optional local file output; it uses exclusive creation (existing report will not be overwritten). Written reports may include Docker IDs, process PIDs and local host cache paths; inspect before sharing.

The script runs CPU-only suites:
`test_recipe_drift_cpu.py`,
`test_model_lifecycle_cpu.py`,
`test_operational_switch_cpu.py`,
`test_operational_executor_cpu.py`,
`test_p3_dg_acceptance_cpu.py`.
Each yields a PASS/BLOCKED verdict and test count. It **does not** run existing destructive operator trials or P3 A/B/C stages.

## 3. Verdict and exit semantics

| Status | Meaning |
| --- | --- |
| `P3-D.READ_ONLY_PASS` | Docker GPU-exclusive AND host port PID and NVIDIA compute PID provenance actually verified |
| `P3-D.BLOCKED` | Unverified/inconsistent processes, no privileges, unsupported GB10 NVML reporting, unknown Docker ownership, or anomaly |
| `P3-E.DRAFT_REVIEW_REQUIRED` | Preserved Flash runtime was observed and historically qualified, but no canonical reinstall-ready Flash recipe exists |
| `P3-E.READ_ONLY_PASS` | A registered qualified Flash recipe was found and observation checks passed; **not itself proof of reinstall** |
| `P3-F.SOURCE_CPU_PASS_NOT_RELEASED` | All 5 CPU/Fake-DGX regressions passed; no real operating release |
| `P3-G.PREVIEW_PASS_REAL_SWITCH_NOT_RUN` | Current-ID ordinary switch preflight and journal check passed; no transfer/rollback test |
| `overall.DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` | Runner executed, no hard blocker, but real acceptance incomplete |
| `overall.BLOCKED` | At least one read-only or CPU check has a concrete blocker |
| `overall.CPU_ONLY_SOURCE_PASS_NOT_DGX` | CPU-only development run; no DGX observation |
| `acceptance_complete=false` | **Always false** for this draft runner; independent real G acceptance and production release are separate |

Exit 0 means the chosen **non-mutating draft checks completed without a hard blocker** (not P3-D~G completion). Exit 3 denotes a hard blocker or unsatisfied `--strict` acceptance. The full JSON must be inspected for per-stage statuses. A `--strict` run is intentionally nonzero until an independently documented real-G acceptance process exists.

**Important nuance:** `ss` may show `docker-proxy` instead of the model container PID; `nvidia-smi` may omit compute-app rows on the DGX GB10 or hide cgroup provenance. This requires more accurate read-only attribution, not removal of the test. The conservative `P3-D.BLOCKED` result should be treated as **verification pending**, not automatic evidence of a GPU conflict or a malfunctioning vLLM service.

## 4. Rollback, immutable receipts, and promotion criteria

- Do not replay P3-A/B/C: their stage receipts are historic. Existing canonical 27B remains running and validated, port 8000.
- `P3-E` discovery is an **observed candidate**; do not write it directly into `runtimes/service-policy.json.runtime_recipe` or promote without reviewing Docker argv, model revision, image, NVFP4 loader and cache path against the actual pinned repository.
- `P3-F` generic lifecycle `PRODUCTION_LIFECYCLE_RELEASED=False` stays locked. Model removal is an allowed future approved action but never automatic. Do not add permanent no-delete bans.
- `P3-G` execution requires a new separate scoped operator maintenance approval, independent fresh SHA/TTY, stop-before-start, single-model API identity and bounded smoke/benchmark, failure restore, append-only receipts and independent status + journal postcheck. Existing script intentionally lacks this authority.
- Changes to canonical 27B recipe JSON may invalidate existing benchmark-SHA lineage; keep the current SHA immutable unless a separately accepted versioned migration is executed.
- Only after P3-G real acceptance and reviewed source gates may a separate release decision enable daily Wizard operations. It is not enabled by a successful `--run`.

## 5. Transition to P4 / P5 / P6 / P7

Once P3-D–G are accepted under their separate actual-vs-CPU scopes, decide P4: Flash removal/recovery is optional; storage sufficiently available may justify `NOT_APPLICABLE`, leaving Flash preserved for testing. P5 then qualifies Orcarouter on vLLM 0.32, P6 proves Orcarouter ↔ 27B, P7 unifies model/recipe lifecycle, proxy/gateway/service observability and release. **Do not equate phase numbering with unattended permission to mutate the DGX.**
