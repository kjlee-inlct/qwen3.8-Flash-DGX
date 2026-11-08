## D-069 — 2026-11-08 — P5 source-only adoption with release-gated runtime, preserved 27B

Operator authorized source/CPU/read-only design integration, not actual GPU/service interruptions. Implemented pinned YSLAB Apache-2.0 safetensors, manifest, BF16 PLE audit, donor 31/31 MTP metadata and immutable overlay source, separate MTP0/MTP2 profile candidates, P5 Wizard and one-shot verdict; source commit `33adec1` [Actions 42429745463 SUCCESS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463), 20/20 P5 tests. Existing Blazux BF16 mmap source was statically inspected without installing foreign YSLAB vLLM development runtime.

**Decision:** no runtime image provenance, full vLLM 0.32 Qwen4Exp compressed-tensors/quantized lm_head/MTP load guard, actual pinned 3-shard SHA/shape, GPU graph and fallback qualification yet. `launch_allowed=false`, `register_as_runtime_recipe=false`, `runtime.image_id=null`, `GPU_EXECUTION_RELEASED=False`; service policy remains `orcarouter.served_id=null`. Vendor `build_mtp_overlay` is present but unexposed and not authorized to create derived files. The GPU trial command is blocked and has no executable approval plan. P5 full runtime acceptance NOT_RELEASED. Keep old 27B/Flash/caches/receipts, port8000 and one-model; no P3 rerun, P4 deletion, P6 switch/P8 fault, or Draft PR merge. A new explicit asset-write consent is required before generating any large overlay, and independent TTY downtime approval + proven restore before model load.

---

## D-068 — 2026-11-08 — P5 uses YSLAB BF16PLE as reference, Blazux vLLM 0.32 as runtime; one-shot implementation and verdict

Operator designated **P5** for `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` and BF16 PLE/MTP mechanisms drawn from `YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark` while maintaining the **existing Blazux vLLM 0.32/Wizard/manifest/service system**, one active model, host API :8000. No independent YSLAB service or vLLM 0.1.dev deployment. The following P5 conversation should implement as much as possible **in one coherent batch**, with an integrated temporary one-command CPU/Fake-DGX/DGX read-only automatic verdict (GPU trial separate via explicit approval). YSLAB main reference SHA `9492b78c6bc04638587b42f2ffeb0680b0fcb3ef`, original Orcarouter pinned revision `3a3b63161c0745390e5270179af42e46efc70799`, 31 BF16 MTP donor RadixArk pinned revision `7b719225242aacd3dbd3f9407468c2ee9a9d2594`; none is a current Blazux GPU qualification.

**P4-B/C real dry-run PASS/CLOSED** (read-only only) is preserved. Actual cache/container/image deletion remains deferred to a separately authorized P5 capacity problem or P8. P5 source permission does **not** include 27B downtime, live GPU trial, automatic P6 switch, P8 release, or Draft PR merge. `docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md` and `handoff/START-NEXT-P5-20261108.md` are the canonical P5 handoff; the P5 acceptance source/GPU results are NOT_RUN on this decision date.

---

## D-067 — 2026-11-08 — P3 source closeout verified; P4-A read-only capacity review precedes any removal decision

Operator's newest DGX logs completed P3-E bounded asset examination (11 reference shards, 129,771,270,410 apparent bytes, 299,845 weight-map entries, hashes/issues=[]), P3-F local seven-suite CPU 168/168 PASS (release false), and 27B current 8/8 health. These are not complete model weight integrity, canonical Flash reinstall, general production lifecycle or recovery approval, all handed to P8.

The operator clarified P4: do not begin deletion decisions or operations first. **P4-A must inventory actual current state and storage capacities using the Wizard, read-only**. Earlier P4 prohibition is superseded only to permit this inventory stage; P4-B candidate review and P4-C deletion remain NOT_STARTED/unapproved. Docker df reclaimable and nested HF repo allocations are not additive or intrinsically safe to remove. Explicit consent required for later B/C scope and each real mutating action. Source CI [42395243458](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42395243458) 887/887 PASS, 40 groups; actual DGX P4-A report pending. Document: `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md`.

---

## D-066 — 2026-11-08 — P4 held, P3 source closeout distinguished from P8 live acceptance

Current operator instruction **DO NOT START P4** supersedes earlier optional-phase sequencing. Premature P4 source-only work was reverted ([1110681](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/1110681f451bc72470454bbbee1e1d79d6406a1d)); P4 remains NOT_STARTED. P3-E requires only current read-only host-asset evidence before source-handoff completion, P3-F requires current CPU-only 7-suite evidence and release gate OFF. Their **real production** Flash reinstall, generic lifecycle execution and recovery are P8 acceptance work, not P3 PASS. Historical real P3-G successful two-way switch PASS/CLOSED. P8 fault/automatic restoration/production GO NOT_RUN; no new execution approval. See `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`.

---

## D-065 — 2026-11-08 — Do not equate a large FP8-hybrid weight_map with corruption or blindly enlarge its entry cap

Actual operator DGX read-only Flash metadata index: 31,907,813 bytes, successfully within 128 MiB file cap; `PARSE_SHARD_INDEX:FLASH_SHARD_INDEX_UNQUALIFIED` after JSON decoding. Historical code collapsed type/empty/>100,000-count conditions, so genuine tensor count **unmeasured**. Commit [135f75c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/135f75c8cc652ed63b8508d10fcf5f079dff24ef) separates safe numeric/shape diagnosis without increasing limits. 2 CPU tests; GitHub CI [42392277467](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42392277467) **878/878 PASS, 39 groups** (source-only). Model file damage, missing shard and fresh reinstall qualification not established; no service mutation or approval to execute. Keep P3-G original real PASS/CLOSED and P8 independently gated.

---

## D-064 — 2026-11-08 — Model index uses separate bounded read cap, not an 8 MiB general metadata cap

Real DGX read-only Flash preflight returned `READ_SHARD_INDEX:FILE_EXCEEDS_BOUNDED_READ`, showing a generic-metadata limit mismatch in the **observer**, not demonstrated model damage. Source-only fix [56d39e4](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/56d39e4acb5d4e69777372283fe5f8839a16fc7c) introduces a hard, independent 128 MiB max for the model's safetensors index, while retaining 8 MiB for small metadata and 256 KiB for chat template. Never read beyond limit+1 bytes; report only safe size numbers. Keep index JSON and path checks fail-closed. Operator did not provide actual index size; if it exceeds dedicated max, investigate and request a policy review rather than silently widening it. CI [42391564016](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391564016) **876/876 PASS source-only**. No promotion of Flash reinstall, no service mutation or P8 release.

---

## 2026-11-08 — P3-E real DGX Flash host asset preflight blocked; diagnostic patch/source CI

**Actual operator DGX evidence, no Docker mutation:** `python3 -m scripts.manager.flash_host_assets --json` returned `status=BLOCKED`, issue `FLASH_HOST_ASSET_PREFLIGHT:ValueError`, `legacy_hf_bind_writable=true`, `indexed_shard_count=0`, `metadata_sha256={}`, `template_sha256=null`, `verified_model_revision=true`. This only establishes that the **old observer** advanced past pinned command/env/cache bind, then raised a ValueError during an unidentified local-file validation step. Neither zero shards nor `verified_model_revision=true` proves a missing model or verified revision bytes. **No user-provided evidence of broken inference or failed reinstall.**

**Source fix, not live DGX proof:** [9beb1d3](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/9beb1d3f73675ac4a22daedfc2167b380742305c) adds allowlisted `failed_stage`, `failure_reason_code`, `pinned_command_identity_matched`, `prepared_view_path_observed`, and stops falsely setting `verified_model_revision=true` from a directory name alone. Private exception messages/path/env values are never emitted. Tests cover metadata cap, malformed index, empty/missing/escaped marker, secret exception redaction. GitHub Actions [42391221418](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391221418) **SUCCESS: 874/874 CPU/Fake-DGX tests across 39 groups** (previous 870 + 4). Real DGX did not run this patch yet.

**Next safe operator command:** `git pull --ff-only origin feature/recipe-wizard-handoff`; then `python3 -m scripts.manager.flash_host_assets --json`. Inspect only redacted `failed_stage` and `failure_reason_code`. No cache repairs, container recreation, GPU activity or permissions escalation should follow from this result without separate evidence/approval. Flash canonical reinstall remains unqualified, lifecycle release disabled, historic P3-G real PASS/CLOSED and P8 NOT_RUN; preserve 27B at :8000.

---

## D-063 — 2026-11-08 — Evidence-only Flash host asset preflight, no execution approval

**Code-level scope clarification, not an operator authorization.** To prepare P3-E Flash reinstall qualification, allow only a bounded source-implemented, read-only Docker/host-asset inspection with SHA-256 for small metadata and template, stat-only large shards, strict path containment, and allowlisted output without raw environment secrets/mount source paths. This evidence alone must never register a canonical Flash recipe or release the general lifecycle backend. The exact approved service-change runbook is a separate step; P8 exclusively handles deliberate fault injection and final release. GitHub source: [03cbe4c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/03cbe4cc45a750322c4f99616c85f1061f7b2288), [2b44ccc](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/2b44ccc0237fa34742e28608ad089cb3ca90fe55), and [8e8fcec](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/8e8fcec5acb280e01445a2bd773fc9f4ecedf2f6). Source-only CI [42390619936](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42390619936): **870/870 PASS, 39 groups**, including 5 new Flash host asset tests.

Latest DGX E proof is **field match** and verified strict command normalization, not full host asset or fresh install proof. A/B/C/G prior real successes stay CLOSED; D current read-only ownership attribution PASS. Preserve all historic receipts and keep PR Draft.

---

## 2026-11-08 — DGX operator read-only P3-D/E/F/G follow-up

**Operator evidence:** `docs/P3-E-F-DGX-READONLY-20261108.md`. At DGX local read-only snapshot, 27B API at :8000 is `LIVE_SERVICE_VERIFIED` with 8/8 checks true. P3-D remains `BLOCKED` only because unprivileged `ss` exposed no port listener PID (`sudo_ss_requested=false`); not a measured GPU conflict. P3-E full Flash draft-field match `issues=[]`, but reinstall unqualified with 37 extra environment keys and zero extra mounts; 27B-only command normalization reported Flash `-cc` tokens as unexpected positionals. P3-F new code ran **150/150 CPU tests PASS on operator DGX**; P3-G is only preview in this run, while prior real two-way G is CLOSED. The source follow-up introduces strict read-only Flash FP8-hybrid argv normalization, no service operations or release gate changes. Historical P3-G, P8 boundaries and Source/DGX classifications remain intact.

---

## D-062 — 2026-11-08 — Source-only P3-E/F failure truthfulness and release boundaries

**Implementation clarification; NOT new authorization to operate DGX.** Based on existing `ONE_ACTIVE_MODEL_ONLY`, exact approval, immutable evidence and P3-G/P8 split: any rollback result must distinguish verified restoration of a *previously existing service* from failure to install when none existed. A Docker stop may have taken effect before returning an error; reconciliation must inspect current state before restart. Do not leak extra host environment values/paths in Flash recipe coverage; do not equate known-field match with complete reinstall qualification. P3-G successful real bidirectional switch is CLOSED, while P8 is the only stage for deliberate fault/auto-recovery and final release. This is a code/test safeguard on [d68106a](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d68106a24c4c6071acff7a4d98d74e04c6ecbfe1), not operator consent.

Source change: [d68106a](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d68106a24c4c6071acff7a4d98d74e04c6ecbfe1). Actual GitHub Actions [42386939625](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42386939625): **862/862 PASS in 38 CPU/Fake-DGX groups** (856 baseline + 6 new). This is **SOURCE-ONLY**; no fresh DGX test or service change. Full scope: `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

---

## 2026-11-07 — P3-A–G EVIDENCE AUDIT / P3-G CLOSED; P8 OWNS FAULT & FINAL RELEASE

**New canonical audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md` and `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`. Stage results: **P3-A/B/C** original immutable one-off real DGX PASS/CLOSED (A Flash→27B, B 27B→Flash, C Flash→27B); **D** real read-only GPU+IPv4/IPv6 host :8000 PID ownership PASS from operator `--sudo-ss` run (pre-latest switch); **E** Flash source `-fp8hybrid` prepared view and versioned draft-field match, but **canonical Flash reinstall recipe UNQUALIFIED** (`DRAFT_REVIEW_REQUIRED`, `launch_allowed=false`); **F** six Fake-DGX/CPU suites **144/144 local PASS**, but `PRODUCTION_LIFECYCLE_RELEASED=false` and generic live install/reinstall not accepted; **G** actual independent 27B→Flash→27B TTY-approved ordinary two-way transfers **REAL PASS/CLOSED** with two receipts, API identities, final 27B `diff=[]`, journal VERIFIED/COMMITTED 28 events, last actual active `qwen38-27b` on port 8000. **P3-A–G aggregate = PARTIAL (E open, F source only)** despite G closed. The user explicitly moved intentional failure injection, automatic restore and final operational/UX/production signoff to **P8** (NEW, NOT_RUN, not authorized to execute). P7 is integration only. Preserve old receipts, model assets and `ONE_ACTIVE_MODEL_ONLY`; no P3 A/B/C/G replays or fault injection to perform this audit. Latest P8-source registration CI [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS 856/856 CPU tests 38 groups (source evidence only). Basic post-switch service manager `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are **NOT PROBED** by that command, not conflicts; do not overclaim fresh D audit. The single-script D–G read-only runner prints G preview even after separate real G PASS by design.

**Operator phase decision:** P3-G successful two-way transfer is **REAL PASS/CLOSED**; remove fault injection, automatic source restoration, and final operator signoff from P3-G and P7 acceptance scope and assign exclusively to **P8** (not waived). P3-E still responsible for Flash canonical reinstall recipe; F 144 CPU test gate passing does not itself unlock lifecycle execution. No backward proof promotion from successful G transfers into E install/reinstall or P8 recovery. Preserve prior no-hard-delete-ban policy; approved install/remove may be enabled later only under proper separate lifecycle plan.

---

## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

**Operator approved and executed ONE live switch:** 27B→preserved Flash now actually PASS; preserve per-switch TTY/fresh SHA approval and stop-before-start. Current model Flash-Next. Reverse Flash→27B needs its own four-input approval; consent to original downtime does not authorize unattended replay or automatic roundtrip. Do not force fault injection, install/delete model, touch HF caches, or merge PR without separately scoped action.

---

## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

**User decision:** P3-G actual operating acceptance and associated active API downtime explicitly authorized (user: “P3-G 허용”, then “문서 업데이트 + 서비스 중단 허용”). This is **scope approval**, not a blanket release or substitute for each execution's exact TTY token and 4 input acknowledgements. Do not schedule/auto-chain both transfers, recreate/delete containers, force fault injection or bypass release gate. Use existing `operational_acceptance.py` one-switch manual CLI; keep P3-A/B/C immutable. The production routine switching gate remains locked. No live switch yet.

---

## 2026-11-07 — THIRD ACTUAL DGX P3-D READ-ONLY PASS; P3-E FP8-HYBRID SOURCE DRAFT

**Actual operator evidence:** Third DGX batch after fast-forward to `1b785c6`: normal `--run` reported D no visible socket PIDs but E `DRAFT_REVIEW_REQUIRED`, F local **136/136 CPU PASS**, G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`. Operator then explicitly ran `sudo -v` followed by `--run --sudo-ss`: **P3-D READ_ONLY_PASS**, both IPv4+IPv6 :8000 `docker-proxy` PIDs (2051487,2051502) independently attributed to canonical active 27B; GPU compute PID 2051842 verified. Overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`, `blocked_stages=[]`, `acceptance_complete=false`; no service mutation or real G transfer. **P3-E** pinned NVIDIA `fc694b54fb0174e0913e6adf86691ef85a4ead47-fp8hybrid` derivative prepared/view files verified; canonical reinstall recipe NOT registered. Legacy Flash cache writable; source metadata and vLLM flags preserved. Evidence `docs/P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md`.

**NEW SOURCE P3-E DRAFT (UNRELEASED):** `recipes/qwen38-flash-next.runtime.draft.json` is `launch_allowed=false`, `register_as_runtime_recipe=false`, not linked into service-policy, no Flash install adapter/executor. `scripts/manager/flash_recipe_review.py` checks versioned pinned Flash 500K/Yarn/MTP2/native tools/image/env/template/mount *documented fields only*, returns `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` or explicit field differences. `P3-E.source_draft_field_review` added to single-script report. P3-E stays DRAFT_REVIEW_REQUIRED; direct live DGX comparison of new code still **NOT_RUN**. CI [42373758262](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42373758262) **854/854 CPU/Fake-DGX PASS / 38 groups**, source only. Full runbook `docs/P3-E-FLASH-FP8HYBRID-SOURCE-DRAFT-20261107.md`.

**Next:** read-only `--run --sudo-ss` batch to inspect E draft comparison, then review remaining host env/mount/image provenance. Separate operator-approved real Flash install and G switch/rollback acceptance required; `PRODUCTION_EXECUTION_RELEASED=False` remains. P3-A/B/C closed, 27B unchanged, P4 optional, P5/P6/P7 queued.

---

Decision: Flash observed draft is source evidence, NOT canonical `runtime_recipe`, cannot drive lifecycle install/recreate; do not promote/read for executable plans. Retain legacy writable /hf as measured but do not assume secure future install. Keep deletion/removal permitted on separately approved action (no blanket ban).

## 2026-11-07 — SECOND ACTUAL DGX D–G BATCH + PINNED FP8 HYBRID / HIDDEN SOCKET PIDS

Actual operator DGX batch (**read-only; no model changes**) after previous source fixes: **P3-D BLOCKED** because `ss` showed BOTH IPv4 0.0.0.0:8000 and IPv6 [::]:8000 LISTEN but no process PID; Docker reported only running `qwen38-27b` as GPU/8000 port owner, NVIDIA compute PID 2051842 verified to active 27B. **P3-E BLOCKED** because the observed preserved Flash checkpoint was pinned NVIDIA source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` plus **`-fp8hybrid` local prepared variant**, not a different HF revision; canonical Flash reinstall recipe still unqualified. Flash /hf mount observed writable and legacy argv preserved. **P3-F PASS 128/128 actual local CPU tests. P3-G preview PASS**, current Docker ID and VERIFIED/COMMITTED journal; actual transfer/rollback NOT executed. Overall exit=3, acceptance_complete=false.

Subsequent SOURCE fix: E now recognizes only exact pinned NVIDIA source revision plus `-fp8hybrid` prepared view and verifies `.prepared`/essential files read-only; no recipe promotion. D now permits ONLY operator-selected `--sudo-ss` to run `sudo -n ss` (no prompt; no sudo by default) and independently reverify unchanged socket set and PID provenance. Unknown PID always BLOCKED. CPU CI [42371861344](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371861344) **846/846 PASS / 37 groups**, SOURCE-ONLY, actual DGX rerun pending. Full evidence `docs/P3-D-G-SECOND-DGX-PID-HYBRID-DIAGNOSTIC-20261107.md`. No P3-A/B/C replay, no production switch release.

Decision: do not accept missing PID solely from Docker port binding or healthy API; opt-in sudo -n *only* for ss. Do not treat suffix -fp8hybrid as a revision mismatch or qualified reinstall. Writable historical Flash cache remains review advisory.


---

## 2026-11-07 — P3-D/E DIAGNOSTIC SAFETY CHOICES AFTER FIRST DGX RUN

Do not lower process provenance standards merely to force D PASS: IPv4 and IPv6 host listener rows may both be valid but must be attributed; Docker proxy may be accepted only by matching real `/proc/PID/cmdline` with Docker inspected target IP and published :8000, not by process name. Missing PID, cgroup, Docker-IP or host binder evidence stays BLOCKED. Do not auto-promote legacy Flash writable HF cache, image, or argv into the canonical reinstall recipe; observed candidate is DRAFT, and unexpected model path/served ID remains hard blocker. P3-F local 119/119 tests and P3-G current-ID preview PASS do not supersede pending real-G roundtrip and rollback. P3-A/B/C remain immutable, 27B untouched. Corrected source CI 42371091647 838/838 PASS. `docs/P3-D-G-FIRST-DGX-DIAGNOSTIC-FIXES-20261107.md`.

---

## 2026-11-07 — OPERATOR DECISION: P3-D / E / F / G FORMAL STAGE EXPANSION

The operator declared that the four common Wizard functionality tasks after historical P3-C are **P3-D/E/F/G**, rather than a new unnumbered workstream or proceeding directly to P4. D = independent GPU process/:8000 ownership diagnosis; E = canonical Flash-Next recipe and reinstall qualification; F = generic model lifecycle and rollback/journal/backup mechanics; G = actual DGX bidirectional/failed-transfer recovery and Wizard UX acceptance. The operator requested a one-shot local `git pull` followed by a **single script that automatically tests/judges D-G**. Implementation is an explicitly non-mutating **DRAFT** runner `bash scripts/temporary/p3-d-g-acceptance.sh --run` that performs safe read-only D/E/G checks and automatic CPU/Fake-DGX F tests, with truthfully incomplete G real switch acceptance. A later real G maintenance operation **cannot be approved unattended** and requires a new separately scoped operator TTY/downtime decision; draft does not release executor. P3-A/B/C historic real PASS/CLOSED remains immutable, P4 optional, P5/6/7 unchanged. Preserve vLLM 0.32, port 8000, ONE_ACTIVE_MODEL_ONLY and canonical 27B recipe SHA.

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

## LATEST 2026-11-07 — User selects SINGLE canonical 27B recipe replacement (not variant switching); benchmark then delete verified old backup ONLY after PASS

Supersedes previous proposed persistent `qwen38-27b`↔`qwen38-27b-native-tools-v1` service-switch feature: user clarified to change **original 27B recipe**, stop existing service, **recreate the same canonical `qwen38-27b` name** with already DGX-proven native-tool flags, run NEW bounded benchmark, **replace latest active benchmark result**, then **remove the exact old backup Docker container only when every test PASSES**. Old benchmark evidence, model images, checkpoint cache and P3 A/B/C records must NOT be deleted/re-written. The separate unqualified persistent-switch prototype was removed from branch (not deployed). Native Tools 1-shot real DGX `PASS_RESTORED` remains prior proof and trial variant `qwen38-27b-native-tools-v1` remains stopped; its 9 chained events and receipt preserved.

**New Git source (NOT YET RUN on DGX):** `recipes/qwen38-27b.runtime.json` (single pinned 27B canonical source, vLLM 0.32.0, exact local image `sha256:9479fc92...`, revision `482ca0f...`, Jinja SHA `c3cf9e34...`, native-parser flags), desired `runtimes/service-policy.json` registration, `scripts/manager/p2_27b_recipe_migration.py` (read-only plan, independent exact-TTY execution, backup rename, canonical recreation, ordinary chat/structured tools/stream/SSE 3-sample fresh benchmark, private immutable receipts, atomic latest benchmark pointer, remove verified stopped old container only after all PASS, restore pre-change on precommit failure), and `scripts/temporary/p2-27b-native-recipe-migrate.sh` (`--plan`, `--execute`, `--status`). Permanent runbook: [docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md). **Per user request, do NOT block Git Pull on Fake-DGX CI**, but no source change alone authorizes downtime. User runs `git pull --ff-only` and `--plan` first; `--execute` still needs new independently accepted SHA + downtime acknowledgement + explicit verified-backup-deletion acknowledgement. Pull does not mutate Docker.

**CAUTION:** Original P3 receipts pin the PRE-MIGRATION 27B Docker ID. When user explicitly approves deletion after successful promotion, that old ID becomes historic, NOT active. Existing generic operating Flash↔27B code must remain fail-closed until later lineage-aware revision; ordinary service status sees canonical `qwen38-27b` by name but doesn't check tool flags, thus use new `--status` check to verify post migration actual flags / benchmark. Do NOT rewrite historical P3 receipts or indiscriminately delete caches or Docker images. Model stays `qwen3.8-27b` at `:8000`, ONE_ACTIVE_MODEL_ONLY, no SGLang.

**Current real DGX:** user most recently showed `qwen38-27b-native-tools-v1` `Exited (0)`, original `qwen38-27b` operating, 9 one-shot events, and validated `PASS_RESTORED`. **Canonical recipe migration, its new benchmark, backup cleanup, and new `--status` PASS are NOT_RUN.** The new action runs real Docker only on operator-approved TTY, not via connector or Fake-DGX. If `--plan` BLOCKED or execute reports `FAIL_RESTORED`, `RECOVERY_FAILED`, `COMMITTED_CLEANUP_PENDING`, stop and reconcile; never retry blindly.

---

## D-061 — 2026-11-07 — Add only Fake-DGX transactional simulation; no native-tools executor release

After D-060 protected Tools V1 candidate, develop isolated `p2_27b_tool_cutover_simulation.py` with injected fake backend to exercise exact-id/version/expiry checks, simulated multi-ack, lock and uncertain-journal denial, stop-before-start port/GPU checks, original preservation and rollback outcomes. Simulator reports `SIMULATED_PASS`, `SIMULATED_FAIL_RESTORED` or `SIMULATED_RECOVERY_FAILED` and **cannot execute Docker from its CLI or write real receipts**. Its simulated digest is NOT a production approval plan. Source CI [42339247960](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42339247960) on `fe4e6b01c98c9244787a5bb8e034ca81d88bba08` passed **722/722 CPU tests**. Real parser qualification, live variant-aware source/target identity, persistent journal, TTY approval, actual restore and Open WebUI Native are independently required before P2-FINAL PASS or any release. P3-C remains immutable and original 27B active per last operator observation.

---

## D-060 — 2026-11-07 — Choose isolated protected 27B Native Tools V1 source candidate, DO NOT release runtime

The existing original Docker `qwen38-27b` is provenance-pinned by P2/P3/ordinary switching, so changing `_candidate_argv(tool_calling=True)` on that same name cannot safely deliver the new service. Decision: introduce separate `nvidia-27b-native-tools-v1` / `qwen38-27b-native-tools-v1` with the same pinned 27B/source image/cache/served ID and tool/reasoning parser args. Keep candidate YAML deliberately unvalidated, off `service-policy.json`; use `p2_27b_tool_variant.py` to inspect original/source/fallback/GPU inventory and emit NO valid execution plan, and `p2_27b_tool_streaming.py` for bounded SSE parsing with malformed/HTTP guard. A clean source preview remains BLOCKED_PENDING_PARSER_AND_LIVE_ACCEPTANCE. Before any executable cutover, independent source proof and human authorization must establish variant-aware identity, single GPU/port, rollback/fault journal/receipt, exact parser/tokenizer compatibility, tool + WebUI acceptance. Current ordinary Wizard release remains OFF, P2-FINAL remains OPEN, actual DGX unchanged and historical P3-C immutable. See `docs/P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md`. This decision extends D-059, not a production release.

---

## D-059 — 2026-11-07 — Confirm current 27B missing auto parser flags and require protected new variant

New **real operator DGX** `docker inspect qwen38-27b Config.Cmd` supplied, confirming the preserved `nvidia/Qwen3.8-27B-NVFP4` 27B loader uses `modelopt_mixed` and lacks `--enable-auto-tool-choice`, `--tool-call-parser`, and `--reasoning-parser`. The source opt-in `--tools-profile` shows expected `qwen3_coder/qwen3`, while actual bounded `--tools-probe` returns `BLOCKED/LOCAL_API_HTTP_ERROR_400` (no HTTP 400 body captured). Old `Config.Cmd` is immutable for `docker restart`; source edits alone do not enable tools. **Decision:** treat P2-FINAL as live NOT_QUALIFIED; develop a distinct versioned tool-enabled 27B recipe/service variant with model, image, container, port, journal and rollback provenance explicitly reviewed, while preserving the original pinned qwen38-27b/Flash containers/receipts and existing ordinary switch contract. Actual migration or proxy/UI change needs new scoped downtime consent. **Do not reopen P3-C**. Operator also independently verified reverse ordinary model transfer at 27B `:8000` `LIVE_SERVICE_VERIFIED` and operating journal `VERIFIED/COMMITTED/14`, resolving prior reverse postcheck pending; main Wizard live menu release still OFF. Supersedes outdated pre-reverse/Config.Cmd-not-observed notes, not their historical evidence.

---

## D-058 — 2026-11-07 — P2-FINAL Tool Calling, P3-C closed without replay

Per operator request, add **NVIDIA Qwen3.8-27B Tool Calling + reasoning parser + Open WebUI native tool cycle** as the FINAL P2 acceptance item. Verify official vLLM Qwen3.8-27B recipe flags `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3` against vLLM 0.32. Distinguish original checkpoint/API `nvidia/Qwen3.8-27B-NVFP4` / `qwen3.8-27b` from internal `Qwen3_5` architecture. Source candidate profile must be opt-in, preserve historical P2/P3 pinned container IDs and receipts, and NEVER auto-replace original Docker container. New separately approved migration and actual DGX tool cycling, streamed parsing and WebUI Native verification required to mark P2-FINAL PASS. Existing P2 download/loader/trial/benchmark already REAL PASS; appended Tool Calling acceptance remains OPEN. Historical **P3-C stage A/B/C already REAL PASS and CLOSED**, never rerun to close P2 Tool Calling or normal operating UX. Ordinary switching direction 27B→Flash and reverse Flash→27B both reported REAL PASS; reverse independent postcheck and normal main menu release still pending. Source record: `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.

---

## D-057 — 2026-11-07 — Isolate ordinary recurrent model switches from one-off P3 acceptance (SOURCE ONLY)

Accepted development contract: keep P3-A/B/C immutable and never re-run or repurpose their stage execute commands for generic operating transitions. A new \`operational_switch.py\` may read/prove P3 A/B/C historical lineage but no old plan ID is an operational approval. Independently namespace recurring operations under \`~/.local/state/blazux-wizard/operational-switch\`; require a NEW exact short-lived plan, two distinct manual approvals, verified live source/API identity, pinned Docker target image/CID, stop-old-before-start, port 8000 release, single GPU model, append-only journal, one-use attempt marker, protected original model assets and exact API post-start verification. Recovery failures must not be reported as successful. 

Current \`operational_executor.py\` is **source-only and not exposed by \`./wizard.sh\`** until complete fake-DGX tests, separate real DGX operator consent and explicit qualification. No service mutation was performed. Read-only model menu preview and phase/evidence-separated dashboard are approved as SOURCE changes only. This decision supplements D-016/D-056 and does NOT supersede their stricter real-DGX approval boundary. Existing Draft PR remains unmerged.

---

## D-056 — 2026-11-07 — Treat actual P1/P2/P3 engine qualification and user-facing Wizard UX as separate acceptance gates

**Evidence-first confirmation:** On real DGX the existing `./wizard.sh` CLI and guarded backend for Flash P1 Verify/Benchmark and pinned NVIDIA 27B P2 trial/benchmark were exercised; actual P3-A Flash→27B, P3-B 27B→Flash, and P3-C Flash→27B all completed PASS. Actual final P3-C consumed three independent TTY acknowledgments and called the canonical `scripts.manager.p3_persistent_switch` route. It returned `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_observed_model=27b`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `issues=[]`, and wrote original `stage-c.json`; the current live 27B stays active on :8000. **Do not rerun this one-off acceptance sequence.** Original Flash container, image and HF caches must remain preserved.

**UX qualification is a DIFFERENT gate:** The main `./wizard.sh` interactive console (`wizard/console.py`) can select models, inspect current state, show P1 actions and historical Verify/Benchmark evidence; however `_stage_actions()` invokes P3 `stage-a/b/c --plan` only and explicitly states that execution did not begin. Thus success with `scripts/temporary/p3-stage-c-operator.sh --execute` validates the same canonical Wizard backend but NOT an actual *interactive menu* transfer, ordinary model selection-to-service-switch, recurrent Flash↔27B switching, or OpenWebUI/proxy/gateway integrations. CPU test PASS validates source guards, not usability evidence.

**Decision:** Preserve and freeze one-off P1–P3 success evidence. Treat model-centric interactive Wizard switching as the NEXT implementation milestone: design simple active-model → installed target → benchmark/history → downtime disclosure → fresh approved exact plan → canonical backend → live identity and recovery result flow; never show internal P1/P2/P3 as the primary navigation path. Requirements: one model active, port 8000 fixed, no accidental deletion, retries/rollback under journal/locks, human consent required, fail-closed on stale SHA, clear post-switch result. Implement/test this as a distinct repeatable operating transition and independently validate on DGX under its own new downtime consent; do not repurpose completed stage-c receipt or infer operator consent from previous acceptance. Keep Draft PR #1 unmerged pending review.

[Current state](CURRENT-STATE.md); [actual DGX final evidence](EVIDENCE-LEDGER.md).

---

## D-055 — 2026-11-07 — Bounded read-only Stage-C plan refresh instead of operator clock guessing

Actual DGX user attempts near 10:10 KST plan window boundary (10:08:14 and 10:09:30) both returned `P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS`, `executed=false`, `execution_dispatched=false`. This refusal correctly preserved source Flash service but required operators to manually guess the next boundary. Decision: modify ONLY tracked `scripts/temporary/p3_stage_c_operator.py` to read-only poll a NEW current canonical Stage-C plan for max 150 seconds when remaining time <120 seconds on a valid initial plan. Each polling observation checks all original A/B/P1/P2/model/service/port/provenance constraints; require a changed SHA (at the proper expiry boundary) and new expiry >=120s away. No wait for noninteractive/no TTY, `--plan` remains unchanged. Timeouts, source drift, earlier-than-boundary plan ID change, Ctrl+C and current Git changes block; no execution/approval state carried forward. Only after refresh, full new SHA and two separate TTY acknowledgments may allow canonical Wizard C execute (still locked/guarded). All actual service/canonical state semantics unchanged; P3-C not run by source work.

[Runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## D-053 / D-054 — 2026-11-07 — Git-public measured benchmark registry, no private raw evidence

**D-053: Git stores sanitized benchmark **facts**, not execution logs.** Public, versioned `benchmarks/published/<served-model-id>/<source-SHA16>.json` holds model repo, pinned revision, vLLM engine version, UTC source timestamp, hash of original private receipt, explicit small request profile and whitelisted latency/TTFT/throughput numeric metrics only. Initial entries are grounded in the user-supplied actual DGX Flash post-B (37.9527 mean tokens/s, receipt SHA `f506db4c...`) and 27B restored trial (7.9002 mean E2E, 11.1801 decode proxy, receipt SHA `80f109db...`). Interpret them as client-measured bounded three-request trials, not a normalized head-to-head ranking. NEVER commit raw `~/.local/state/blazux-wizard` receipts, ignored `reports/`, credentials, API paths, request/response samples, plan IDs/approvals, Docker/container IDs or private logs. Source hashes provide provenance and do not themselves prove numeric data matches original receipts until original-byte comparison on DGX.

**D-054: Future publication remains separate opt-in and fail-closed.** `python3 -m scripts.manager.benchmark_publication` performs allowlist-only local source conversion; `--plan` read-only, `--verify-published` compares expected published JSON to the original source, `--write` requires exact current original file SHA256, refuses overwrite and never Git stages/commits/pushes. `bash scripts/temporary/verify-published-benchmarks.sh` rechecks the two initial tracked summaries against original local private evidence. CI uses private fake CPU fixtures, cannot claim actual DGX byte verification. This does NOT change vLLM single-model runtime, host port 8000, P3-C exact SHA approval, or service rollback. Latest attempted C was CANCELLED before executor dispatch due leading bracket in input; no service mutation.

See [public benchmark registry](../benchmarks/published/README.md).

---

## D-050 / D-051 / D-052 — 2026-11-07 — Tracked P3-C final model operator

**D-050 (canonical C ready, execution not authorized):** Actual DGX `./wizard.sh switch flash-next-27b stage-c --plan --json` returned `READY_TO_REQUEST_TRANSITION_APPROVAL/issues=[]/p1_evidence.status=PASS/executed=false`, active original Flash `qwen38-flash` CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, preserved 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`, shared original image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, POST-B P1 Verify+Benchmark+diagnostics SHA proofs and unchanged P2 receipt hash. Its old short-window SHA `d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7` is historical and not reusable. Optional evidence-copy operation was cancelled (`COPY` input, `copied=0/executed=false`); not a Stage C prerequisite.

**D-051 (new D-016 tracked C UX):** `scripts/temporary/p3-stage-c-operator.sh` + Python controller. `--plan` default read-only. `--execute` only after **independent operator approval of the LIVE Flash downtime**, a real TTY, fresh SHA printed in prompt, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, and independent `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Wrapper third literal is additional human authorization but is **not sent as `--enter-p3`**; canonical C expects null. Fresh plan and live identity rechecked before dispatch; canonical Wizard alone executes switch, locks, journal and best-effort rollback. C SUCCESS must independently pass served 27B API on :8000 AND immutable original `stage-c.json`. No automatic switch-back after successful C; preserve original Flash.

**D-052 (operator report separation):** Stage-C operator writes append-only private 0600 `<repo>/reports/transitions/flash-next--to--27b/p3-c-operator-<UTC>-<nonce>.json`, ignored by Git. This is **supplementary** to immutable `~/.local/state/blazux-wizard/p3/stage-c.json` and original P3 journal, lock and attempt marker (never copied away/deleted/moved for rollout). CPU fake-DGX tests and GitHub CI required before operator fast-forward pull. Source change does **not** authorize C execution, additional GPU tests, source/cache deletion, or Draft PR merge.

[Runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## D-047 / D-048 / D-049 — 2026-11-07 — Historical evidence view + staged copy migration / Stage C order

**D-047** Model-centric report catalog uses the service-policy Manifest `served_id` and reports Verify/Benchmark/GPU trials/transitions independently of internal P1/P2/P3. It reads legacy plus project `reports/`, verifies source file regularity/size/private mode, deduplicates exact SHA256 bytes and uses original UTC completion/filename time. NVIDIA 27B mean end-to-end throughput and decode proxy must be distinctly labeled, not conflated with Flash-Next measured throughput. It is strictly read-only and shall never call Docker or perform inference.

**D-048** P2/P3 report consolidation is **copy-only with current full plan approval**, not state relocation: new `./wizard.sh evidence migrate --plan|--guided` and Advanced 8. JSON bytes are copied with digest-bound names to project `reports/models/<served_id>`, `reports/transitions/<direction>`, and `reports/diagnostics/<served_id>`. Private 0700 folders, immutable O_EXCL 0600 records; originals, P2/P3 locks, stage state and journal, retry markers, raw target logs remain undisturbed and canonical. If preflight/source changes or destination collision, fail closed; later native writer mirroring/state relocation requires separate plan and actual DGX approval.

**D-049** Actual post-B Flash P1 Verify + Benchmark are PASS and P3-A/B are PASS. This qualifies considering Stage C **now**, not approving it. After fresh source CI and clean DGX pull run **only** `./wizard.sh switch flash-next-27b stage-c --plan --json`; check current live source, preserved 27B, P1 evidence PASS and required downtime ack. P3-C execution requires a **new** exact SHA and explicit Flash-Next downtime consent, regardless of report importer completion. No automatic service transition, forced stage retry, model deletion or PR merge.

[Detailed contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md).

---

## D-044 / D-045 / D-046 — 2026-11-07 — Operator UX and model-centric evidence

**D-044 (evidence path):** New NVIDIA Flash-Next Wizard execution receipts are stored under Git-ignored `<repo>/reports/models/qwen3.8-flash-next/`, named by the *served model ID* rather than an unmemorable stage code. Keep unique append-only JSON (0600; directory 0700). Do not alter historical `~/.local/state/blazux-wizard/p1/` receipts. P3 stage-C evidence gate reads both roots and evaluates newest finished UTC action receipts, including FAIL; no historical PASS masking. P2/P3 state/locks/reports require their own safety-qualified migration, NOT moved now.

**D-045 (approval UX):** Model menu already selected the action; direct guarded entry performs only that action. Show `Type exactly [<current SHA>]` like P3; empty/wrong cancels, fresh plan revalidated immediately before execution. Show human-readable preflight/Verify outcomes/Benchmark metrics and evidence path. Keep machine JSON/CLI and exact-plan SHA safety boundaries intact. User-facing labels identify model/action, not P1/P2/P3 implementation phases.

**D-046 (source versus runtime):** User-provided 2026-11-06 post-B Flash Verify + Benchmark are *actual* PASS; their distinct approvals and real bounded measurements supersede prior `NOT_RUN` positions. New GitHub source UX changes and CPU-only CI are **not** DGX validation. P3-C authorization requires independent downtime approval even when the evidence prerequisite test passes. No unapproved GPU run or service modification, no automatic PR merge.

---

## D-043 — 2026-11-07 — POST-B P1 diagnostic is append-only; final P3-C remains separately approved

Use D-016 GitHub-tracked `scripts/temporary/p1-post-b-audit.sh` as the next **read-only** DGX action after CPU CI PASS and operator fast-forward pull. It reuses the P1 inspect-only collection and verifies actual P3-B receipt + current Flash service/API/source image, both exact doctor/inventory launch preflight raw JSON outputs (benign own Flash collision only), readiness of Verify/Benchmark plans and pinned original asset revision. Every attempt produces a new private 0600 `p1-diagnostics-<UTC>-<nonce>.json` outside Git/HF cache; no overwrites. P3-C gate assesses the newest diagnostic attempt (including BLOCKED), with legacy fixed-name fallback, and still requires **separately approved actual post-B P1 Verify and measured numeric Benchmark** newer than B. Source tests are not DGX/GPU evidence and this audit conveys no GPU or P3-C authorization. On any mismatch stop; preserve caches/containers/images and unmerged Draft PR.

## D-042 — 2026-11-07 — P3-B ACTUAL DGX PASS supersedes pre-execution planning; rectify operator bookkeeping

Actual operator terminal output confirms canonical P3-B `PASS/executed=true/live_verified=true`, wrapper `P3_B_PASS_FLASH_NEXT_ACTIVE`, `issues=[]`, independent live Flash API `qwen3.8-flash-next`; original Flash is last verified active model. Canonical `~/.local/state/blazux-wizard/p3/stage-b.json`. Historical wrapper report incorrectly named `p3-a-operator-20261106T223124Z-14861d75.json` and its `approval_accepted=false` persisted because imported A `persist()` used a hardcoded prefix and B never set the field after successful manual confirmation. Preserve the original records and document the inconsistency; change source to stage-aware new filename plus separate `approval_accepted` (manual typed inputs), `execution_dispatched` (core invoked) and `executed` (Wizard observed). P3-A/B actual completed, NO stage repetition. P1 POST-B read-only preflight PASS only; Verify/Benchmark/RC3 disposition pending. Final C stays NOT_RUN/NOT_AUTHORIZED.

---

## D-041 — 2026-11-06 — Operator EXPLICITLY APPROVED P3-B ONLY; live execution still requires fresh terminal triple-ack

After actual DGX P3-B read-only `READY_FOR_SEPARATE_P3_B_APPROVAL` with `issues=[]`, the operator responded **"승인"** to the direct, scoped question **"P3-B(현재 NVIDIA 27B 중단 → 원본 Flash-Next 복귀)를 승인하시겠습니까?"**. This is **explicit P3-B downtime permission only**, superseding the approval-waiting clause in D-040. It does NOT approve post-B P1 GPU verify/benchmark automatically or final P3-C, merging Draft PR, deletion, or any other service change. Existing tracked `scripts/temporary/p3-stage-b-operator.sh --execute` remains the ONLY operator command, after DGX fast-forward pull; its new stage-B exact plan ID, `I_ACCEPT_27B_DOWNTIME`, and `I_SEPARATELY_AUTHORIZE_P3_STAGE_B` are independent mandatory typed runtime approvals. No old P3-A SHA or 17:50-expired B inspection SHA may be reused. Canonical Wizard rechecks before stopping live :8000; failure recovery is best effort and no automatic retry or stage progression is permitted. This GitHub source/doc step does NOT execute B. Until operator supplies actual `P3_B_PASS_FLASH_NEXT_ACTIVE` with verified API, stage B remains NOT_RUN and last observed active model stays 27B. D-034 order still requires new, post-B Flash P1 functional Verify, numerical Benchmark and rc3 disposition before separate P3-C approval.

---

## D-040 — 2026-11-06 — Real P3-B read-only READY; independent 27B downtime and B-stage entry required

Operator supplied actual DGX output after fast-forward to `e5d4171d07838e565510b1127f4a0b27dcd8423f`, executing only `bash scripts/temporary/p3-stage-b-inspect.sh`. Result `status=READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`, `approval_accepted=false`, `operations_enabled=false`. Active API `qwen3.8-27b` and preserved source container `qwen38-27b` ID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`; original preserved Flash-Next container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Both use runtime image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; distinguish MODELS by API ID/immutable container provenance, NOT by shared image digest. Prior successful P3-A plan `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4` linked to immutable stage-A receipt; P2 SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9` matches. Operator's B read-only evidence `/home/inlc/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. The plan `7af40f009dd67975c77b98c03183833dd4997e16f9c9443bd11ea880f6d8162c` has expiration epoch `1793955000` (**2026-11-06 17:50 KST**) and is inspection evidence only. **Never reuse it for a future switch.**

**NO P3-B DOWNTIME APPROVAL WAS GIVEN.** Success of read-only B plan is not permission to stop 27B. Specific core UX/safety finding: `p3_persistent_switch.py` previously used `I_ACCEPT_FLASH_NEXT_DOWNTIME` for ALL stages, even though B stops **27B**. This was incorrect operator-facing approval semantics, despite being guarded. Source now requires B-specific **`I_ACCEPT_27B_DOWNTIME`** plus **`I_SEPARATELY_AUTHORIZE_P3_STAGE_B`**, alongside a freshly computed exact 64-character B-only plan SHA. A/C retain existing scoped ACK strings; B refuses reused A Flash ack or A entry. Only after a **new user decision explicitly authorizing B** may DGX operator invoke `scripts/temporary/p3-stage-b-operator.sh --execute` via D-016. Wrapper default `--plan` is read-only; execute demands real TTY and independent typed three fields, checks live 27B+actual A receipt+preserved Flash ID/image and fresh short-lived plan before/after inputs, then delegates only B to canonical Wizard, verifies Flash API after return, records local private evidence and never auto-runs P1/C. Host process GPU exclusivity and restoration after host/daemon failure remain unqualified. Until authorization, **leave 27B active** and preserve original Flash and 27B containers/images/caches and unmerged Draft PR. After separately approved B PASS, D-034 still demands new P1 functional and measured benchmark+diagnostic disposition, then separately approved C final 27B.

---

## D-039 — 2026-11-06 — P3-A REAL DGX PASS, 27B ACTIVE; P3-B approval NOT GIVEN

User's operator transcript on DGX `feature/recipe-wizard-handoff` HEAD `a3945bdc5cfec467478978c47b3a27bdafee84bd` confirms successful distinct P3-A Flash-Next→NVIDIA 27B persistent transition. Fresh stage-A plan `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`, TTL until 2026-11-06 16:50:00 KST, operator typed plan SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_P3_ENTRY` **independently**, all exact. Canonical Wizard `stage=a`, `executed=true`, `status=PASS`, `live_verified=true`, evidence `/home/inlc/.local/state/blazux-wizard/p3/stage-a.json`. Independent post-switch check `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`; operator wrapper `status=P3_A_PASS_27B_ACTIVE`, `issues=[]`, `execute_command_exit_code=0`. Local report `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. The transition completed at approximately 2026-11-06 16:43 KST, with 27B deliberately LEFT ACTIVE. Prior D-038 expired-plan refusal is history and superseded by this *separate* successful new SHA. Original Flash preserved under existing P3-A source safeguards; inspect its precise stopped-container ID before B rather than assuming preservation from a source CI run.

**P3-B (27B→Flash-Next) is a new service interruption, NOT implicitly authorized** by P3-A or by sharing the success log. Do NOT run `stage-b --execute`, shut down 27B, restart Flash, create a P1 GPU workload, or advance to C automatically. Only read-only stage-B checks are permissible pending a new explicit stage-B scoped decision. D-016 tracked wrapper `scripts/temporary/p3-stage-b-inspect.sh` uses the *actual private stage-A receipt*, fresh Wizard service manager status and canonical `stage-b --plan`, compares immutable original/target IDs and image provenance and saves local read-only evidence. It exposes **no execute mode**. A READY preflight is **not** downtime approval, nor production rollback qualification. After B is separately authorized and successfully executed, D-034 requires full new P1 functional verify and numeric rebenchmark plus diagnostic disposition before an independently approved C, final 27B active. Draft PR #1 remains open/unmerged; do not delete model images/checkpoints or perform unattended service changes.

---

## D-038 — 2026-11-06 — User must see exact approval values; expired P3-A plan refusals are not recovery attempts

Operator entered correct P3-A SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_P3_ENTRY`, but Wizard rejected `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT`, `executed=false`, no Docker service mutation. Plan `94b4dedae21eb72b12443029257931e123e33404c32898d9ae2bad52954c064f` expired `2026-11-06 16:30:00 KST`; recorded operator report `20261106T073049Z` is 16:30:49 KST. Expiry is the leading explanation, without asserting exclusion of other preflight drift. Original service / model remains protected and no P3 stage completed. User specifically requires **showing the exact input characters** at each terminal confirmation, not an abstract "type acknowledgment exactly" prompt.

D-016 scoped change: P3-A wrapper prints the actual current plan ID, full downtime and separate entry ACK values, KST expiry and time remaining. Fail before human prompts if less than 120 seconds remain. After input, read-only plan refresh must yield same full plan SHA with >15s remaining or block before mutation; canonical Wizard still performs its own live preflight. Show nested Wizard `executed=false` stale refusal as `BLOCKED` rather than `OPERATOR_REVIEW_REQUIRED`. Never reuse stale SHA, silently regenerate an approved hash, automate ACK input or chain P3-B/C. New real-world DGX trial requires fresh user TTY input per D-037; no blanket service change allowed. Source CPU CI PASS is not runtime model qualification.

---

## D-037 — 2026-11-06 — Operator's P1-clear conditional P3-A authorization becomes eligible; stage-A exact interactive gates still mandatory

User explicitly authorized **Flash-Next→NVIDIA 27B** conditional on no remaining **pre-A P1** deficiencies. Actual DGX operator output from tracked `p1-pre-a-readiness.sh`, source HEAD `834f823a76556a37a982e3dbf7f243db3edad6df`, now confirms `status=PRE_A_P1_REVIEW_READY`, `issues=[]`: both historical/current `doctor` and `inventory-plan` rc3 are `EXPECTED_ACTIVE_FLASH_COLLISION` (2/2 each), original Flash API/immutable image checked, P1 functional Verify PASS, original P1 benchmark PASS (TTFT P50=1.398707s, latency P50=1.687357s, mean=38.2968 tokens/s, 3 requests). Original local receipt `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`. **The original user's condition is met for considering P3-A entry**, superseding the *pre-A* hold in D-035/D-036. Do NOT claim post-B P1 or actual P3 switching was completed: `p3_a_executed=false`, `p3_a_execution_authorized=false` in the **read-only receipt by design**, and actual P3-A/B/C remain NOT_RUN.

A P1 PRE-A evidence PASS alone is never a daemon/GPU or port-mutation permit; the operator must additionally complete *fresh action-scoped* stage-A plan and independently type the **full exact plan ID**, downtime acknowledgment `I_ACCEPT_FLASH_NEXT_DOWNTIME` and separate entry acknowledgment `I_SEPARATELY_AUTHORIZE_P3_ENTRY` at the DGX terminal. These strings and source target must be read back from the live plan, not synthesized or reused from P2. Only stage A is included in this conditional approval. A successful A leaves **27B active** and stops, with **no automatic B**, service recovery best-effort on failure, no host GPU exclusivity/daemon fault recovery guarantee. B, post-B P1 functional+numerical rebenchmark, and C are independently staged and approved per D-034. Preserve original Flash container/image/checkpoint and unmerged Draft PR.

D-016 workflow: use tracked `scripts/temporary/p3-stage-a-operator.sh` from the GitHub branch after tested push and DGX `git pull --ff-only`. Default `--plan` is read-only; `--execute` requires TTY and exact three interactive tokens, then invokes **the canonical Wizard** stage-A guarded execute, independently rechecks 27B active API, writes local private evidence, and never advances to B. No hidden Docker mutation in the wrapper itself and no copy-pasted multi-command Python snippets.

---

## D-036 — 2026-11-06 — P1 numerical metrics now supplied; require tracked read-only pre-A audit before conditional approval

Supersedes **only the "P1 benchmark numerical metrics absent" claim** in D-035: user shared actual local original P1 Wizard receipt `~/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`, status PASS with 3 samples / 192 completion tokens, TTFT P50=1.398707s/P95=1.751198s, E2E latency P50=1.687357s/P95=1.780142s, mean throughput=38.2968 tokens/s. The new 2026-11-06 P1 `--inspect-only` report has source/Hybrid READY, both plans READY, API `qwen3.8-flash-next`, no setup process and clean tree. `actions.verify/benchmark.status=BLOCKED` with `reason=inspection_only` is intentionally read-only, **not P1 evidence regression**. Raw `doctor=3`, `inventory_plan=3` outputs from historic/current reports were not included in the pasted summary and need examination. The user reaffirmed D-016: a tracked, tested temporary script must be pushed to GitHub before asking DGX operator to pull and invoke it. `p1-pre-a-readiness.sh` reconciles old+new raw rc3 output, original verified receipts and fresh current Manifest/API with no GPU. As long as this pre-A reconciliation is incomplete, the operator's conditional P3-A approval has not been established; no GPU start/stop or P3 --execute. D-034 post-B P1 functional and measured rebenchmark remains mandatory before final C.

---

## D-035 — 2026-11-06 — Operator's conditional P3-A permission is NOT satisfied while P1 work remains

Operator instruction: "Flash-Next에서 추가로 해야하는거 있나요? P1 에서 안한거 있는지 점검 후 없다면 27B 전환을 승인합니다." This is **conditional**, not blanket downtime/P3-A permission. Based on retained actual DGX P1 history, verify=PASS (baseline/extended completion, chat, tools, vision), benchmark=PASS (3 bounded requests), but actual numerical P1 TTFT/latency/tokens-per-second measurements have **not been supplied**; historic doctor and inventory-plan rc=3 stdout/stderr are still missing; post-P3-B P1 rerun is by definition NOT_RUN. **Therefore the condition is NOT MET and P3-A is NOT AUTHORIZED to execute.** Keep live Flash-Next, all assets and :8000 unchanged. D-034 still requires actual post-B P1 functional/numeric evidence before C. No automatic stage progression.

Source code review identified an independent logic error: `scripts.manager.inventory.main` returns rc=3 when `qwen38-flash` and its listening :8000 already exist even if `inspect_host.status=PASS` and `errors=[]`. Historical rc=3 might reflect an expected collision but cannot be asserted without original JSON. `p3_p1_evidence_gate.py` previously required rc=0 for both doctor and inventory, an incompatible success gate with the active source after B. Source corrected to accept **only rc=3 with both full parsed inventory documents proving that exact active Flash image/container owns :8000, no read errors, correct launch-preview target and consistent collision flags**, plus still-required reviewed disposition, timestamps, new functional and measured benchmark receipts. No actual P1 completion or operator permission is implied by CPU CI.

---

## D-034 — 2026-11-06 — P2 stops; P3 separately entered; Flash-Next P1 remediation then final 27B (OVERRIDES D-033)

User explicitly specifies: **P2 completion MUST NOT automatically enter P3**. P3 must first verify 27B as the source state, then **27B → Flash-Next** transition. Only after that succeeds, **address P1 deficiencies and rebenchmark Flash-Next** using actual measured evidence. Then **Flash-Next → 27B** transition and verification; final expected active model is **27B**. Because P2 currently restores original Flash-Next, 27B must be made active through its own approved gate before the requested 27B→Flash-Next verification. Do not imply this preliminary activation is automatic. Independent plan/approval/restore on each transition; pause at each phase, no auto chaining. Old P3 two temporary roundtrips conflict with this order and are retired/fail-closed. New read-only `sequence --plan` is not a persistent switch executor, never issues an execution plan or starts GPU. D-033 is explicitly superseded. No new live downtime authorized.

---

## D-033 — 2026-11-06 — P3 acceptance starts with two temporary verified roundtrips, not permanent switch

P3 first acceptance instrument is **exactly two** sequential Flash-Next → temporary NVIDIA 27B → original Flash-Next cycles using the existing proven one-shot recovery executor. It is **blocked absent actual P2 benchmark receipt** `BENCH_PASS_RESTORED_VERIFIED` and additionally requires **new P3-specific plan ID plus explicit downtime acknowledgment**. After every cycle, recheck actual original container identity, running state and Manifest-based API served ID; on first failure never begin another cycle. Reporting P3 temporary-roundtrip PASS must **not** be called persistent production model-switch readiness. Persistent switch, failure injection and recoverability remain later independent work. No service, image or model change authorized by source-level readiness.

## D-032 — 2026-11-06 — P2 benchmark must reuse the proven exact-identity restoration path

The actual 27B DGX smoke `PASS_RESTORED` means do not repeat source import probes. Add bounded 3-request/64-token **benchmark-specific** approval that cannot reuse the first smoke trial's plan ID. Reuse the original one-shot target launch, exclusive GPU container policy, preserved original identity and mandatory original restore; capture client metrics, not generated text, and local 0600 evidence including fresh Manifest/API check after restore. Mark client TTFT, decode/prefill **proxies** separately from engine speed, and memory point sample distinctly from peak. Any result absent real measured data or independent return-to-Flash proof is not benchmark PASS. Disruptive execution still needs fresh exact plan and new typed downtime approval; no user "continue" instruction by itself grants a service interruption.

---

## D-031 — 2026-11-06 — Wizard must use Manifest-led live service status as primary operator interface

After real one-shot Qwen3.8-27B GPU `PASS_RESTORED`, the user chose **Manifest-based Wizard** instead of manual `docker ps` + `curl` for verifying original Flash-Next recovery and future switching. Keep a **single** `./wizard.sh service manager status --json` command with fresh actual Docker/socket observation + declared `runtimes/service-policy.json` expectations + localhost `/health` and `/v1/models` exact model ID. Return `LIVE_SERVICE_VERIFIED` or fail closed `BLOCKED`, never infer operation authority or API identity from a stale manifest. Preserve `inventory`, `health`, `logs` for diagnostics. Do not conflate current API verification with prior trial provenance, GPU exclusivity, permanent switch readiness, memory/latency measurements or user authorization to stop production. No Docker or GPU mutation from any status command.

---

## D-029 — 2026-11-06 — Permit FIRST 27B GPU trial only via exact-approved, bounded, restoring experiment

A real DGX CPU-only ModelOpt registration pass justifies trying GPU startup instead of further speculative CPU checks. This is **not** permission to interrupt the running Flash-Next without operator acknowledgment. Implement 27B **experimental one-shot** guarded CLI, with default read-only planning and exact full SHA plan ID + typed interruption acknowledgment. A trial deliberately stops original `qwen38-flash` and must try restoring the **existing same original container** regardless of target launch success. No parallel GPU models, permanent model transition, cache deletion, image rebuild/pull, or reuse of Flash-Next PLE/MTP options. Protect on unknown Docker target/GPU status; if recovery cannot be verified, show failure and require operator intervention. Original service may be disrupted temporarily and power/daemon failure can defeat auto-recovery.

Keep NVIDIA `nvidia/Qwen3.8-27B-NVFP4` ModelOpt FP8/NVFP4 separate from community Unsloth compressed-tensors examples; checkpoint's internal `Qwen3_5ForConditionalGeneration` is *only a loader identifier*, not the model product name. Start with ctx8192/one sequence/0.70 GPU/eager, no MTP/YaRN; qualify kernels/API first, optimize later.

---

## D-028 — 2026-11-06 — Verify ModelOpt mixed name through public registry, not instance method

The installed vLLM 0.32 `ModelOptMixedPrecisionConfig.get_name(self)` is an **instance** method. The initial CPU-only audit's class-level zero-argument call yielded a self-binding TypeError unrelated to model compatibility. Correct strategy: import `vllm.model_executor.layers.quantization`, call `get_quantization_config("modelopt_mixed")` (no config or model instantiation), and verify identity to the imported `ModelOptMixedPrecisionConfig`. Preserve fail-closed checks and exact raw DGX evidence. No method-call issue may be treated as GPU kernel/load failure; no source-only/CPU result can authorize GPU transition.

---

## D-027 — 2026-11-06 — Opt-in CPU loader import is distinct from GPU runtime acceptance

After actual DGX read-only `serve_27b.sh --status/--plan` success, separately check installed Python imports of vLLM Qwen3.5 and `ModelOptMixedPrecisionConfig`, plus the declared quantization name `modelopt_mixed`, in a bounded **operator-opted-in CPU-only runc container**. Do not mount model cache, publish ports, request GPUs, start the vLLM engine, call inference or modify the original Flash-Next process. The wrapper must default to `--plan`. Import failure in this restricted environment is ambiguous; even a clean import/class/name result does not qualify GB10 GPU kernels, checkpoint loading, memory fit, API, benchmarks or rollback. GPU/start/transition requires separately scoped approval.

---

## D-026 — 2026-11-06 — Serving scripts split per model, preserve legacy call path

Choose model-specific serving entrypoints: `scripts/serve_flash-next.sh` contains original Flash-Next PLE/MTP/QSA implementation; `scripts/serve_27b.sh` is an independent NVIDIA ModelOpt entrypoint (initially plan/status only); `scripts/serve.sh` remains default-compatible Flash-Next dispatcher with optional explicit `27b` selection. `./flash serve` retains existing Flash-Next behavior and tests. Do not inherit Flash-Next-only PLE/MTP/hybrid settings into 27B and never allow 27B to start/switch without separately approved, exact-plan executor with tested old-service restore. `serve.sh` with no args is **not** a harmless preview: it keeps legacy Flash-Next start behavior. Prefer explicit `scripts/serve_27b.sh --plan` for P2 read-only evidence.

---

## D-025 — 2026-11-06 — P2 27B dedicated initial-run preview without implicit transition

Once operator-supplied 27B pinned source metadata (FP8 208/NVFP4 193) and installed vLLM 0.32 source registry/ModelOpt AST checks pass, develop a **separate 27B runner** instead of reusing Flash-Next `scripts/serve.sh` (PLE/MTP/QSA defaults). The new `model 27b plan --for-action start --launch-preview` returns a **non-executable, unapproved** argv with exact local image ID, pinned snapshot path, `modelopt_mixed`, conservative *unvalidated* 8192 context/1 sequence/0.70 GPU memory/eager. Preview inspects original Flash-Next container image and localhost API identity but never calls Docker run/stop. No `plan_id`, no `--execute` override, no `operations_enabled`. A registry digest/validated recipe, GPU memory/kernels, exact source recovery and separate stop-before-start approval are still required. A preview command displayed in JSON must **never be copied to the shell**.

---

## D-024 — 2026-11-06 — Quantization source audit is a distinct release gate

Verify the local immutable NVIDIA 27B `hf_quant_config.json` rather than assuming the main-branch model card reflects downloaded revision. Require a bounded read-only `MIXED_PRECISION` description with layer-level FP8 and NVFP4 for source shape audit. Missing/invalid/unrecognized metadata blocks further qualification; valid metadata is still **not** proof of ModelOpt GPU kernel support, image import, memory capacity, runtime functionality or service transfer approval. No GPU launch and no implicit cleanup.

---

## D-023 — 2026-11-06 — Installed image source audit before P2 GPU runtime

Use a **separately invoked, explicitly CPU-only, isolated Docker runc image-source audit** to inspect patched vLLM 0.32 model registration/Qwen3.5 classes and ModelOpt NVFP4/FP8 before building/enabling a 27B launcher. A local image ID is not a registry digest, source symbols are not executed kernel proof, and neither gives service start authorization. The default operation is `--plan`; `--execute-cpu-only` uses no network, GPU or published ports, temporarily creates one runc container and removes it upon exit, and never touches Flash-Next. GPU start/old-service stop/transition and cache deletion remain separately gated.

---

## D-022 — 2026-11-06 — P2 download is evidence, not 27B runtime approval

Operator-supplied immutable NVIDIA 27B download PASS (19/19; exit 0; pinned source candidate) supersedes stale in-progress entries. Preserve exactly one active GPU inference model and host port 8000; never re-download without missing/corrupt evidence. Approve adding a **read-only** runtime preflight interface without enabling a GPU start, implicit service switch or recipe validity. The existing Flash-Next-specific serve script and hybrid/MTP defaults must not be repurposed as a validated 27B launcher. Actual 27B vLLM 0.32 loader, ModelOpt NVFP4/FP8, memory, image digest and safe rollback remain independent gates; P2 GPU service requires separate explicit authorization.

---# Decision record — accepted constraints vs proposals

Record what has been **decided** and what still needs approval. Proposals in docs are not automatically accepted implementations.

| ID | Date | Decision | Status / boundary |
|---|---|---|---|
| D-001 | 2026-11-04 | Use **Blazux vLLM 0.32 only**, no SGLang engine; aphex3k is tuning/benchmark reference | DECIDED |
| D-002 | 2026-11-04 | Keep NVIDIA/RadixArk existing Blazux capability while adding Orcarouter and 27B via model-specific opt-in recipes | DECIDED as target architecture; NOT_IMPLEMENTED |
| D-003 | 2026-11-04 | Create new `feature/recipe-wizard-handoff` branch from fork `main`; preserve `feature/orcarouter-bf16-adapter` separately | DECIDED / branch created |
| D-004 | 2026-11-04 | P0→P7 order: Flash-Next benchmark, 27B benchmark, switch test, **conditional Flash-Next cleanup**, Orcarouter benchmark, switch test, release gate | DECIDED as roadmap; all GPU work gated |
| D-005 | 2026-11-04 | Manage model as recipes, manifests, bounded wizard steps, service/proxy/gateway, Docker and storage inventory | DECIDED as design target; NOT_IMPLEMENTED |
| D-006 | 2026-11-04 | Preserve current original Orcarouter container, its API clients, data/image; explicit scoped approval before stateful GPU ops, restart or deletion | DECIDED / hard safety rule |
| D-007 | 2026-11-04 | Model deletion may be necessary due to storage; approve **exact candidate plan**, not automatic stage advancement | DECIDED / no deletion authorized |
| D-008 | 2026-11-04 | Single large active GPU model by default; stable gateway later, not at the expense of operating port `:8000` | DESIGN ASSUMPTION pending capacity/operations tests |
| D-009 | 2026-11-04 | Existing numerical strict `1e-4` Orcarouter release gate remains unresolved; no implied release PASS | DECIDED / release block |

| D-010 | 2026-11-04 | Implement N1 recipe with YAML + JSON Schema Draft 2020-12, CPU PyYAML/jsonschema verifier, required full pinned source/model SHA and Docker image digest, vLLM 0.32 only, and no launch/deletion approval bypass. 27B candidate stays invalid. | DECIDED / SOURCE_ONLY; not runtime authorization |

| D-011 | 2026-11-05 | User reports old services removed and asks Blazux default NVIDIA Flash-Next to occupy previous host API `:8000/v1`; model ID uses Blazux `qwen3.8-flash-next` (not the old Orcarouter identifier); keep vLLM 0.32 default profile and no SGLang. Remove static ban on 8000 and historic container name, replacing with live Docker/socket collision check. Never implicitly rm -f a container. | DECIDED / SOURCE_CHANGE; actual host deployment NOT_OBSERVED/NOT_RUN, supersedes D-006 and D-008 **only for presumed presence and reserved port**, not for protection of any actual resources |

| D-012 | 2026-11-05 | **User reaffirmed Wizard-first sequential P1–P7 delivery:** P1 Flash-Next implement+benchmark via Wizard → P2 27B implement+benchmark via Wizard → P3 bidirectional Flash-Next/27B switch via Wizard → P4 optional Flash-Next cleanup if disk constrained, via Wizard and exact approval → P5 Orcarouter-Flash-Next implement+benchmark via Wizard → P6 Orcarouter/27B switch via Wizard → P7 integrated operation. All steps must be Wizard-operable; CLI is underlying execution only; source CI ≠ DGX bench PASS. Preserve :8000/v1 external endpoint where feasible; vLLM 0.32 only, no SGLang. | DECIDED / ROADMAP LOCK; supersedes any task ordering that bypasses Wizard or promotes Orcarouter before P1–P3 verification; no GPU/deletion permission implied |

| D-013 | 2026-11-05 | While operator-owned `./flash setup default` is downloading, implement P1 Wizard source only; do not run competing download/prepare/start. Wizard must verify complete shards and image label, detect active setup, refuse Docker/name/port conflicts, use a fresh exact SHA-256 plan approval, keep benchmark bounded and record JSON evidence. Source CI ≠ DGX qualification. | DECIDED / SOURCE_IMPLEMENTED, GPU/delete not implicitly approved |

| D-014 | 2026-11-05 | User requested full P1–P7 **Wizard interface scaffold up front**, separately debug model-specific P1–P7 execution later. Use modular `wizard/menus/pN.py` files, shared router/contracts and both interactive `./wizard.sh` and headless `--stage/--action/--json` CLI. P1 retains existing approval/preflight implementation; P2–P7 default to read-only status/plan with no operational adapter/approval acceptance. Keep P1→P7 acceptance order unchanged. | DECIDED / SOURCE_IMPLEMENTED; GPU, switch, cleanup, gateway NOT_AUTHORIZED by scaffolding |

| D-015 | 2026-11-05 | **Supersedes D-014's numbered source-file layout:** classify Wizard by capability. Top-level Model management (P1/P2/P5), Model switching (P3/P6), Storage (P4), Operations (P7); descriptive submodules under `wizard/menus/models/`, `switching/`, `storage/`, `operations/`. Keep P identifiers and direct `./wizard.sh pN ...` / `--stage pN` as compatibility aliases. Group+item CLI and nested interactive menu use same handlers and guards. | DECIDED / SOURCE+CI PASS; DGX runtime NOT_RUN, P2–P7 execution BLOCKED |

| D-016 | 2026-11-05 | For repeatable user-mediated DGX workflows, develop **one Git-tracked temporary script per bounded milestone** in `scripts/temporary/`, accompanied by a CPU-only fake test, README lifecycle and handoff. User workflow is GitHub commit/CI → finish existing operator setup/serve tasks → `git pull --ff-only` → invoke one wrapper for preflight → separately approved Wizard verify/benchmark → evidence summary. Default read-only; no script-level auto-git-update, implicit operational approval, cache deletion, service disruption or secret log uploads. Temporary wrappers must be retired only by a reviewed commit after evidence is recorded; shared logic belongs in permanent Wizard modules. | DECIDED / SOURCE+CPU CI VERIFIED; DGX/GPU NOT_RUN |

| D-017 | 2026-11-05 | User confirmed Blazux default NVIDIA Flash-Next must remain compatible and authorized **bounded non-disruptive P1 GPU/API verify+benchmark without separate interactive plan-hash typing**. Correct new P1 checker false positives for existing shared metadata cross-repository symlinks (`tokenizer.json`, `model.safetensors.index.json`), retaining strict shard checks and bounded JSON index. Use `scripts/temporary/p1-post-download.sh --auto-gpu`, deriving live action-specific plan IDs and letting the Wizard revalidate each one. No change to permissions for service start/stop, setup/download, Hybrid repair, cache deletion, model switches or gateway. API model ID shows some server is active; preserve it. | DECIDED / SOURCE+CI PASS at 0063b0e (2/2 jobs, 155 tests/job); DGX GPU verdict PENDING |

| D-018 | 2026-11-05 | Preserve native Blazux default Flash-Next acceptance in Wizard: mandatory /v1/completions + standard chat baseline, separate tool/vision probes, mark partial advanced failures without blocking bounded baseline benchmark, retain nonzero-rc Wizard evidence, keep model/server untouched. Original DGX verify failure still needs evidence to identify precise cause. | DECIDED / SOURCE+CI PASS 391a2844 / DGX RECHECK PENDING |

## D-019 — Single active GPU model, fixed API :8000 and manifest-first orchestration (2026-11-05)

**DECIDED by operator:** At any given time DGX Spark hosts **one active GPU inference model**. Both NVIDIA Flash-Next and NVIDIA Qwen3.8-27B must expose the same host API `:8000/v1` when active. **27B start requires Flash-Next stop, port release, identity verification and approved rollback**; never run both GPU models or bind a second external port as an implicit workaround. Conversely, 27B → Flash-Next requires the same ordered stop/start/verify/restore discipline. Download is a separate **network/disk-only** operation allowed while Flash-Next serves (no GPU use, service stop, host port binding or API cutover). Maintain a versioned committed desired policy `runtimes/service-policy.json` and a live observed manifest from Docker/socket inventory; historical manifest records are evidence, not proof of current reality. State transitions must be lock-protected, auditable, checkpoint/image-preserving and explicitly plan-approved. Approval for download does **not** approve service stop, GPU startup or model switch. **SOURCE implemented / DGX transition NOT_RUN**, P3 acceptance remains separate.

## D-020 — Model-first consolidated Wizard (accepted 2026-11-05)

Operator approved `./wizard.sh` with only **1 Select/run model, 2 Service, 3 Advanced, 0 Exit** and model choices **Flash-Next / NVIDIA 27B / Orcarouter**. Wizard detects missing assets, in-flight download, active model and runtime readiness to propose the minimum required steps. It may invite checkpoint-only download through the existing P2 exact-plan gate. **Service switching (stop current model → free host :8000 → start new → API identity verification → rollback) remains separately gated and NOT_IMPLEMENTED/NOT_RUN.** Retain old Flash-Next P1 backend and all CLI names; this supersedes D-015 only for the interactive primary menu, not its stable internal category routes. Git desired policy/actual observation/event journal remain distinct. Per operator terminal, pinned NVIDIA 27B download **started** (`Fetching 19 files: 84%`); completion not evidenced. Full design: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`.

## D-021 — Full P1–P7 Wizard source-first delivery (operator accepted 2026-11-06)

Operator instructed **finish the entire Wizard interface now**, even if P2–P7 execution is not yet enabled; qualify and debug real adapters progressively as P2 onward develops. This explicitly approves full menus/action plans/status/roadmap and backend interface wiring in GitHub, **not** Docker/GPU/runtime/service mutation. Root menu remains model-first (D-020), all model actions are available for planning. Implement `wizard/console.py`, `wizard/workflow.py`, `wizard/roadmap.py`, bounded service log viewer and tests. Preserve original P1 `p1_wizard.py`, exact-approval P2 pinned downloader, all P1–P7 CLI aliases, one active GPU model, stable host `:8000/v1`, and separately scoped approval before any stop/start/switch/recovery. No in-flight 27B download disturbance. SOURCE complete does not imply runtime/gateway/recovery PASS; Draft PR remains open until qualifying DGX evidence.

### Design choices not yet finalized

- Remaining runtime/service/inventory contract fields and wizard flags. The source-only N1 recipe schema has been implemented.
- Whether 27B NVFP4/BF16-head vLLM 0.32 support can use stock backend or requires an opt-in patch; exact checkpoint and draft engine mode.
- Proxy/gateway implementation and host port layout; any port or model alias changes require operational approval.
- GPU benchmark thresholds, allowable downtimes, retention policies and available disk capacity.
- Integration strategy and merge ordering of Orcarouter adapter and this management branch.

### When creating a decision

Add a dated ID, why, alternatives, evidence, affected files/branches, rollback if relevant and approval boundary. If reversing a decision, append a superseding ID; never silently overwrite.
