## R1AC — 2026-11-08 — P4-A read-only inventory authorized; no cleanup inferred

P4-A may inspect Docker container/API inventory, `docker system df`, configured/mounted HF caches and known model repository directory allocated sizes/free space with bounded no-shell read-only commands. Redact host paths, env and private resources. Report Docker reclaimable as unverified estimates and avoid adding model repo + parent cache totals. Model storage sizes are not verified safe-reclaimable bytes; P8 real Flash reinstall/rollback may require those cached assets. **No P4-B candidate decisions, P4-C execute/approval, Docker stop/start/rm, image/prune, cache writes or model switch** without later explicit user instruction and fresh per-action consent. P3 E/F source-level closeout is complete, but P8 production acceptance remains pending.

---

## R1AB — 2026-11-08 — P4 no-start instruction and P3/P8 scope boundary

No P4 source code, inventories, cleanups or container/storage activities without fresh explicit user authorization. P3-E is source draft and bounded read-only host evidence; P3-F is CPU/Fake-DGX source proof with production lock. P8 exclusively owns independently approved real Flash reinstall, lifecycle release, injected fault/automatic recovery and final signoff. Preserve vLLM 0.32, one active GPU model, :8000, HF caches, 27B canonical recipe and historical P3 receipts. `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`.

---

## 2026-11-08 — P3-E real DGX Flash host asset preflight blocked; diagnostic patch/source CI

**Actual operator DGX evidence, no Docker mutation:** `python3 -m scripts.manager.flash_host_assets --json` returned `status=BLOCKED`, issue `FLASH_HOST_ASSET_PREFLIGHT:ValueError`, `legacy_hf_bind_writable=true`, `indexed_shard_count=0`, `metadata_sha256={}`, `template_sha256=null`, `verified_model_revision=true`. This only establishes that the **old observer** advanced past pinned command/env/cache bind, then raised a ValueError during an unidentified local-file validation step. Neither zero shards nor `verified_model_revision=true` proves a missing model or verified revision bytes. **No user-provided evidence of broken inference or failed reinstall.**

**Source fix, not live DGX proof:** [9beb1d3](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/9beb1d3f73675ac4a22daedfc2167b380742305c) adds allowlisted `failed_stage`, `failure_reason_code`, `pinned_command_identity_matched`, `prepared_view_path_observed`, and stops falsely setting `verified_model_revision=true` from a directory name alone. Private exception messages/path/env values are never emitted. Tests cover metadata cap, malformed index, empty/missing/escaped marker, secret exception redaction. GitHub Actions [42391221418](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391221418) **SUCCESS: 874/874 CPU/Fake-DGX tests across 39 groups** (previous 870 + 4). Real DGX did not run this patch yet.

**Next safe operator command:** `git pull --ff-only origin feature/recipe-wizard-handoff`; then `python3 -m scripts.manager.flash_host_assets --json`. Inspect only redacted `failed_stage` and `failure_reason_code`. No cache repairs, container recreation, GPU activity or permissions escalation should follow from this result without separate evidence/approval. Flash canonical reinstall remains unqualified, lifecycle release disabled, historic P3-G real PASS/CLOSED and P8 NOT_RUN; preserve 27B at :8000.

---

## R1AA — 2026-11-08 — P3-E bounded Flash host inventory is observation, never authorization

`python3 -m scripts.manager.flash_host_assets --json` is **read-only** and must not invoke Docker create/stop/start/rm, model downloads or HF cache writes. A complete local metadata/template SHA-256 and indexed-shard presence check do not verify large-weight integrity, full Config/HostConfig/Env semantics, Docker registry provenance, restart/network/security policy or new container GPU execution. Never print or commit raw environment values, host paths, template contents or private Docker inspect payloads. A failing asset check is not a reason for automatic repair or retry. All model changes need a distinct fresh SHA, explicit TTY approval and recoverability review. P8 fault/automatic restore remains independently gated.

---

## R1Z — 2026-11-07 — Fake-DGX stop/start/rollback simulation NEVER authorizes runtime

`p2_27b_tool_cutover_simulation.py` is an isolated pure-injected simulation with NO production adapter or executable Wizard command. Its SHA and acknowledgements are intentionally domain-separated **simulation-only** and must never be accepted by any real DGX executor. It models failure/restoration paths for CPU tests, not actual journal integrity or validated Docker behavior. GitHub 722 CPU PASS on `fe4e6b01` is SOURCE ONLY; actual native tools and safe live rollback remain unqualified. Continue preserving original NVIDIA 27B, Flash, caches/receipts, single-model :8000, vLLM 0.32, no SGLang, no P3 replay, no release-gate flip.

---

## R1Y — 2026-11-07 — Native Tools V1 source-only candidate is not deployment consent

The new distinct `qwen38-27b-native-tools-v1` source candidate uses the same pinned NVIDIA 27B and served ID but a different container name; never reuse or remove preserved `qwen38-27b`. Read-only `--tools-variant-plan` returns exit code 3 intentionally, even on a clean preflight; its fingerprint and argv are NOT executable approvals. New `--tools-stream-probe` makes bounded local inference, not Docker changes, and cannot by itself qualify Open WebUI. Candidate YAML is schema-incomplete and not registered as production. Independent parser+tokenizer qualification, variant-aware service-policy, real stop/start rollback executor, explicit new TTY downtime consent, Fake-DGX faults and actual DGX native tool checks are still REQUIRED. No source changes auto-authorize Docker, port, service, P3 replay, receipt modification, or Wizard release. Historical P3-C is immutable; keep :8000, ONE_ACTIVE_MODEL_ONLY, vLLM 0.32, no SGLang.

---

## R1X — 2026-11-07 — Source-safe P2 FINAL Tool Calling next; no implicit restart/migration

Previous operating-rule headnotes saying 27B Tool Calling is deferred are now superseded **only in priority** by D-058 and the newest DGX evidence: P2-FINAL is the next source development goal; **not** pre-approved real runtime modification. Current preserved `qwen38-27b` is serving normally at :8000, but its actual Config.Cmd omits auto-tool/parser/reasoning switches; the local tool probe returns HTTP 400. Design a **separate pinned tool-enabled 27B variant** preserving both original NVIDIA/Flash Docker container IDs, image/cache and P2/P3/operating receipts, with independently reviewed rollback and ONE_ACTIVE_MODEL_ONLY/port 8000. Avoid in-place removal/recreation, forced Docker restart or approval string automation. P3-C historical PASS is final and never rerun. New ordinary operating backend both physical directions and independent postchecks PASS, but live normal Wizard main menu still `PRODUCTION_EXECUTION_RELEASED=False` and fault-injection restore is NOT qualified. Source-only development and GitHub CI are allowed; actual inference/proxy/service changes require separately scoped operator consent. Keep vLLM 0.32, no SGLang, Draft PR unmerged.

---

## R1W — 2026-11-07 — New ordinary operating switch source complete candidate; real DGX release distinct

Binding priorities: model-centered `./wizard.sh` everyday Flash-Next↔NVIDIA 27B switching, independent preflight, exact scoped approval, stop-before-start, verified API+bounded chat, evidence and safe best-effort rollback. Defer 27B Tool Calling / Open WebUI and Orcarouter until separately requested. Keep P3 A/B/C immutable as historical provenance; never reuse their plan IDs or repeat one-off stages. New source-only normal UX is production `PRODUCTION_EXECUTION_RELEASED=False`, while a dedicated one-switch DGX acceptance route offers `--plan` by default and separately approved `--execute` with four manually typed TTY inputs; no unattended `--execute --json`, env approval overrides, forced plan reuse or automatic reverse switch. Do NOT treat generic source-development permission as consent for current 27B downtime. Actual user controls trial separately under `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`; any unverified journal, model identity or rollback blocks subsequent switching. Original vLLM 0.32, single GPU model, API port 8000, active 27B, preserved Flash, HF cache, P3 private receipts, Draft PR unmerged remain binding.

---

## R1V — 2026-11-07 — P3 최종 PASS 이후 일반 운영 UX 개발, one-off 전환 재실행 금지

실제 DGX P3-A/B/C 전환이 모두 실행/검증되었고 최종 활성 모델은 **NVIDIA 27B :8000**. 원본 Flash 컨테이너/이미지/HF cache 및 27B 자산, 기존 canonical P3 journal/receipt/attempt marker를 그대로 보존한다. 아래 과거의 'P3-C 준비·별도 승인·NOT_RUN'은 **당시 승인 경계 기록**이지 완료된 Stage C를 다시 실행하라는 지시가 아니다. P1/P2/POST-B/P3 재시험·Flash 복귀·27B 중단은 새 작업 목적 및 신규 승인 없이는 금지.

`./wizard.sh` 메인 UI의 stage 선택은 `--plan`만 호출하므로 **P1~P3의 CLI/backend 검증 PASS와 최종 사용자 Wizard UX PASS를 혼동하지 않는다**. 다음 소스 목표는 모델 선택→신규 scoped 승인→일반 반복 전환→API 확인을 사용성 좋게 연결하는 것. 완성 전에는 P3 one-off `stage-a/b/c`를 일반 운영 전환에 전용하지 않는다. 대시보드는 actual canonical 증거, 실시간 API, 운영/UX 인수증을 구별해야 하며 정적 PASS 또는 정적 NOT_QUALIFIED로 실제 증거를 대체하지 않는다.

최신 [P1–P7 acceptance snapshot](../docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md), [new conversation starter](SESSION-START-PROMPT.md). 모든 변경은 기존 브랜치와 Draft PR #1에 코드/CPU 테스트 후 CI/문서 동기화. 실제 GPU/서비스 downtime/cleanup은 새 별도 승인. Docker 이미지/컨테이너/모델 파일/cache 증거 삭제 및 무단 머지 금지.

---

## R1U — 2026-11-07 — P3-C APPROVAL PLAN TIME WINDOW ROTATION IS READ-ONLY UNTIL NEW THREE MANUAL ACKS

The canonical Stage C SHA expires at the next 10-minute UTC bucket. Previous user attempts near the window end were BLOCKED/pre-dispatch, not a failure of model health. The temporary `--execute` wrapper MAY wait at most 150 seconds using only `service manager status --json` and canonical `stage-c --plan --json` to obtain a NEW, DISTINCT, fully qualified SHA with >=120s before expiry; `--plan` remains immediate and read-only. This wait is strictly pre-authorization; it MUST NOT execute the switch, rotate a previously typed SHA, script or pipe approval strings, auto-approve downtime, or run new benchmarks. If the source Flash API/model/images/27B CID/P1 or P2 evidence/Git state change, or SHA changes ahead of its expected time boundary, or wait times out/interrupted, fail closed and preserve service.

After read-only rollover, old plan and any prior approval are discarded; prompt a fresh exact SHA (no brackets) plus exact independent `I_ACCEPT_FLASH_NEXT_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. After typing, re-observe and require matching typed plan; canonical Wizard must re-check independently under original lock and own recovery logic. On success keep 27B running on port 8000 and preserve original Flash container/image/HF cache. Do not update canonical P3 approval schema or bypass attempt markers. Source/CPU CI is distinct from actual DGX service proof.

---

## R1T — 2026-11-07 — Git BENCHMARK RESULTS MUST BE ALLOWLISTED, NOT RAW

Model-based operator benchmark publications belong under **Git-tracked** `benchmarks/published/<served-model-id>/<original-sha256-prefix>.json` and index `benchmarks/published/README.md`. Source raw JSON under original `~/.local/state/blazux-wizard` or ignored `reports/` stays immutable, PRIVATE and never committed. Published fields only: stable model ID/repository/revision, explicit runtime, report timestamp, original raw SHA256 digest, exact bounded profile, benchmark and actual service-restoration outcome, allowlisted numeric throughput/TTFT/latency, and interpretative measurement limitations. NEVER publish original prompt/output, cache/log host filesystem paths, network/API endpoints, container IDs, plan IDs, user tokens, approval acknowledgments, keys, configuration secrets, memory telemetry, or complete raw execution JSON. Never confuse 27B client E2E throughput with decode proxy or standardized head-to-head model comparisons.

Future export is user-reviewed, one original private receipt at a time: `python3 -m scripts.manager.benchmark_publication --model ... --source ... --plan`; `--write` requires explicitly matching current original source SHA256 and does not stage/commit/push. Existing published summary can only be verified or blocked on mismatch, never overwritten. Read-only original-file verification is `bash scripts/temporary/verify-published-benchmarks.sh`. CI tests exercise whitelisting and privacy; CI cannot validate original DGX receipt bytes not in Git. Any discovered mismatch blocks claiming full machine verification until reconciled.

P3-C executed **NO** service transition in recent user log: exact SHA was typed with leading `[`, returned CANCELLED/executed=false/dispatched=false; plan readiness PASS does not grant downtime. Preserve current Flash-Next and explicit C approval policy.

---

## R1S — 2026-11-07 — P3-C TRANSITION REQUIRES TRACKED OPERATOR + THREE NEW TTY ACKS

Original D-016 agreement: agent may commit tracked operator-only scripts, tests, permanent docs and source CI on existing `feature/recipe-wizard-handoff`; **actual DGX source changes require clean fast-forward pull by operator**. No agent-initiated Docker stop/start/GPU benchmark, no PR merge. Latest DGX canonical C `--plan` showed READY/issues=[]/P1 evidence PASS, original Flash/27B identities unchanged. That is **NOT** authorization for actual Flash downtime. Historical C SHA `d5f200ff...` expires in the original plan window. Optional `evidence migrate --guided` was CANCELLED/copied=0 by typing `COPY`; it is NOT a C prerequisite and never authorizes it.

New `scripts/temporary/p3-stage-c-operator.sh` defaults `--plan` (read-only), creates unique 0600 Git-ignored project report, leaves original P3 stage receipts, lock, journal and model files unchanged. `--execute` is exclusively operator-initiated after separate consent, requires a real TTY and manually input **CURRENT** exact stage-C SHA + **`I_ACCEPT_FLASH_NEXT_DOWNTIME`** + **`I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`**. The controller checks A/B original receipts, current Flash live identity, preserved exact 27B container, P2 receipt SHA and P1 post-B Verify/Benchmark/diagnostics SHA; refuses expired/rotated plan. It only dispatches canonical Wizard stage-C. Core C expects **no** `--enter-p3` (null) while the wrapper independently requires the third C-specific input. Stage-C success additionally requires immutable `stage-c.json` and live 27B `:8000/v1` identity, preserving original Flash for rollback. Any ambiguous result is NOT success and forbids blind retry. No automatic P3 post-success stage or Flash switch-back. See [operator runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## R1R — 2026-11-07 — READ-ONLY HISTORY + EXPLICIT P2/P3 COPY, P3-C SEPARATE AUTHORIZATION

The model history command and integrated Wizard menu are READ ONLY: no CUDA, inference, health check, service or Docker commands. Scan private bounded JSON records from declared legacy and new report directories; dedup by immutable SHA256 and report unreadable/untrusted files. Model names come from `runtimes/service-policy.json` not internal rollout stage numbers. 27B throughput reports separate E2E and decode proxy; do not compare it unqualified with Flash direct throughput.

Import is a separately approved COPY-ONLY operation, not service migration: `./wizard.sh evidence migrate --plan` then optional `--guided` requiring current full plan_id. Plans are rehashed immediately before execution. Use O_EXCL, 0600 immutable JSON and private 0700 project directories. Do NOT copy mutable P2/P3 locks/journal/state/attempt markers or .target.log, do NOT delete originals, and do NOT silently switch the canonical P2/P3 paths. Any partial/invalid/mismatched copy BLOCKS review, never overwrite. Imported files are Git-ignored local artifacts, not synchronized backups. Phase-2 native P2/P3 report mirrors and phase-3 active state relocation are postponed pending independent design/recovery qualification.

Original actual P3-B + post-B P1 Verify/Benchmark evidence remains valid as previously supplied. P3-C currently NOT_AUTHORIZED, NOT_RUN. Next operator action is fresh `./wizard.sh switch flash-next-27b stage-c --plan --json` (read-only), after source CI+clean pull; only if all gates READY and the operator separately approves Flash downtime can stage-C execute through the canonical guarded switch. Never infer live approval from prior test results or historical stage A/B plan IDs. See [contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md).

---

## R1Q — 2026-11-07 — Model-centric UX change; actual post-B P1 PASS and private evidence continuity

Operator ZIP contains actual POST-B P1 Verify PASS (baseline/extended plus all four functional probes) and 3-request numeric Benchmark PASS, distinct fresh action SHA approvals; the latest earlier read-only doctor/inventory rc=3 diagnosis PASS for the original Flash own-name/own-port collision. These facts supersede old P1 NOT_RUN entries. They **do not** grant P3-C downtime authorization. Keep Flash-Next service API :8000 active, ONE_ACTIVE_MODEL_ONLY, vLLM 0.32, SGLang unused.

Roll out UX source only after CPU CI and a clean DGX fast-forward pull; no hidden inference re-runs, service transitions, cleanup, or PR merge. Operator-facing Wizard menus show model/action instead of P1/P2/P3 and repeat exact current SHA in the approval prompt, retaining rechecked action-specific approval. Future P1 JSON receipts write append-only, 0600 into ignored `<repo>/reports/models/qwen3.8-flash-next`; historical `~/.local/state/blazux-wizard/p1` never moves or gets overwritten. P3-C gate checks both roots and latest finish timestamps including failures. P2/P3 state and locks must **not** be naively relocated; their readers require a separate staged migration and CPU/fake-DGX tests. See [contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

## R1P — 2026-11-07 — P3-B ACTUAL PASS; POST-B P1 is the only current work

Supersedes historical R1O/R1N "B pending, 27B active" positions: real DGX operator returned `P3_B_PASS_FLASH_NEXT_ACTIVE`, executed/live verified by canonical stage-B and a separate Flash API check. Flash-Next is the latest verified active model, API `:8000/v1`. P3-A/B **must not be repeated**. Do not retroactively edit the historically misnamed old P3-B report or infer failure from its stale `approval_accepted=false` field.

D-016: GitHub source + Fake DGX CPU tests + CI + tracked docs first, then clean DGX fast-forward pull and **one** read-only `bash scripts/temporary/p1-post-b-audit.sh`. This script never requests or accepts `--execute`/GPU approvals; it checks current stage-B receipt and Flash API, existing P1 plan readiness, raw doctor/inventory rc=3 cause, and exact original image/revision. Append-only private 0600 evidence only; failures BLOCKED and no automatic retry/transition. No cache/model/container cleanups, no change to vLLM 0.32, port 8000 or ONE_ACTIVE_MODEL_ONLY.

Even a diagnostic PASS only qualifies **P1 POST-B diagnostics**, NOT new P1 Verify/Benchmark or P3-C. Each live API inference step requires a newly scoped approval and current action-bound SHA; P3-C separately requires explicit downtime approval and all real post-B evidence. Draft PR #1 remains Open/Draft/Unmerged until user authorizes merge.

---

## R1O — 2026-11-06 — P3-B read-only READY, 27B remains ACTIVE until newly scoped B approval (LATEST)

Actual DGX read-only B inspection (17:41:56 KST) reported `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, active API ID `qwen3.8-27b`, immutable 27B running container and original preserved Flash container identities; `executed=false`. **Do not treat READY as permission to stop the live 27B service.** B's operator approval must be separately given, with an unexpired fresh SHA and **correctly named shutdown target**: `I_ACCEPT_27B_DOWNTIME` plus independent `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`; neither P3-A's SHA nor `I_ACCEPT_FLASH_NEXT_DOWNTIME` is valid for B. Record the change under D-040.

D-016 remains binding: agent prepares `scripts/temporary/p3-stage-b-operator.sh` + Python, fake-DGX tests and permanent handoff on GitHub, confirms CI and PR, then operator fast-forward pulls. `--plan` is read-only and safe; **`--execute` is not authorized by this source work** and must NOT be asked of DGX operator until a separate explicit B downtime approval is obtained. If authorized, wrapper requires exact printed live SHA, 27B downtime and B-entry literals, fresh preflight/replan, and stops after B; no automatic post-B P1 or C. Canonical Wizard owns Docker mutation with best-effort rollback. No GPU-service changes from source-only GitHub work, preserve active 27B, old Flash container/image, P2 assets, API :8000 and Draft PR unmerged. Stale B inspect SHA expired 2026-11-06 17:50 KST, NEVER reuse for execution.

---

## R1N — 2026-11-06 — Actual P3-A PASS means 27B is ACTIVE; mandatory STOP before separate P3-B authorization (LATEST)

Operator reported real `P3_A_PASS_27B_ACTIVE` and `LIVE_SERVICE_VERIFIED` after `stage-a --execute` with exact newly generated SHA and downtime+entry acknowledgments, stored `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`, Wizard immutable receipt `~/.local/state/blazux-wizard/p3/stage-a.json`. This supersedes R1M's "A not run" state. **P3-A PASS (actual runtime)** is distinct from GitHub source CI success. Keep the active 27B service untouched until user explicitly approves B; sharing A's PASS is not a second-stage approval. No automatic B, P1 after B, or C, no hidden GPU tests, no cache/image cleanup, no Draft PR merge. Original Flash image/container must be preserved.

Per D-016, agent may push a **read-only** B preparation wrapper `scripts/temporary/p3-stage-b-inspect.sh`, fake-DGX CPU tests, docs; DGX user pulls fast-forward and runs the single read-only wrapper to ground 27B API and preserved Flash IDs. No `--execute` is supported by the inspector. A fresh B exact plan, source ID, stopped preserved Flash ID and separate operator downtime acknowledgment must still be reviewed before any future dedicated B execution procedure; old A SHA and A permission never apply to B. Follow D-039 and D-034's later post-B P1 rebenchmark then separately approved final C.

---

## R1M — 2026-11-06 — P1 PRE-A now PASS; scoped conditional P3-A entry must be freshly and interactively authorized (LATEST)

Actual DGX P1 report `~/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json` returns `PRE_A_P1_REVIEW_READY`, `issues=[]`, same verified Flash source/image, P1 functional PASS, 3-request numeric benchmark PASS and exact own-container historical/current rc3 resolution. Initial P1 backlog in older R1K/R1L is **superseded for pre-A only**. User's explicit condition "P1에 추가로 하지 않은 것이 없다면 27B 전환 승인" is met for **P3-A stage only**, not B/C and not permission for an automated model interruption. Read-only P1 receipt's `p3_a_execution_authorized=false` is intentional and does not reflect a failed P1 audit.

D-016 remains mandatory: GitHub-tracked `scripts/temporary/p3-stage-a-operator.sh`, CPU tests and docs are pushed/tested before DGX fast-forward pull. The wrapper DEFAULTS to `--plan`, does not git pull or mutate Docker under a plan; `--execute` requires an actual TTY, current unexpired action-bound SHA plan and three separately typed operator inputs (full plan SHA, Flash downtime ack, independent P3-entry ack). Only then canonical Wizard executes stage A with exact source stop, target start, live ID check and best-effort source restore. Successful A **leaves 27B active**; NEVER auto-execute B or C or P1 after B. Fault injection, host PID GPU exclusivity and host/daemon recovery unqualified; unexpected runtime result requires operator intervention, never auto retry. Preserve images/containers/model caches and :8000 contract; Draft PR #1 stays unmerged without explicit release approval. Binding decision D-037.

---

## R1L — 2026-11-06 — D-016 temporary GitHub→DGX workflow reaffirmed; P1 numerics supplied (LATEST)

**Operator corrected process:** never substitute pasted complex DGX Python/shell snippets for tracked temporary scripts. For every new operator-side P1/P2/P3 diagnostic: create/modify one coherent `scripts/temporary` wrapper plus CPU fake-runtime tests and docs; **push branch `feature/recipe-wizard-handoff` to GitHub, verify CI/PR, then tell DGX operator to `git pull --ff-only` and run the one tracked wrapper**. Wrapper must not git pull, switch model or perform unapproved GPU/service changes; write private evidence outside Git/HF. This is D-016 and `scripts/temporary/README.md`, not a new discretionary preference. User provided actual P1 inspect output and actual benchmark metrics; record the results and avoid rerunning GPU work solely to obtain figures.

**P1 latest evidence:** 2026-11-06 read-only report `/home/inlc/blazux-p1-reports/20261106T060941Z-e71a159c/result.json`: source+Hybrid READY, source/hybrid issues=[], index 11/11 compatible, source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, API model ID `qwen3.8-flash-next`, branch/clean/health checks PASS. `--inspect-only` action verify/benchmark reported `BLOCKED/inspection_only` **by design**, not a P1 failure. Both `doctor=3`, `inventory_plan=3` still require **actual raw JSON** analysis; current summary supplies only exit codes. Historical P1 2026-11-05 BENCH PASS receipt was read by operator: 3 samples / 192 completion tokens, TTFT P50/P95 1.398707/1.751198 s, latency P50/P95 1.687357/1.780142 s, mean 38.2968 tokens/sec. This supersedes earlier "no P1 numeric metrics supplied" claims. Prior functional verify PASS remains recorded. Per conditional approval D-035, with rc3 exact-cause still unexamined **P3-A is not authorized**; use tracked `p1-pre-a-readiness.sh` for evidence reconciliation, do not mutate Flash-Next. A pre-A baseline PASS does not cancel D-034 mandatory post-B P1 verification/rebenchmark and independent P3 stage approvals.

---

## R1K — 2026-11-06 — P2 STOP boundary / manually entered revised P3 sequence (LATEST OVERRIDES old R1H/J and D-033)

- **P2 bench PASS must not auto-start P3.** End P2 with actual metrics evidence + original Flash-Next `LIVE_SERVICE_VERIFIED`; wait for explicit operator request and new scoped approval before P3 planning/execution. A general instruction to "continue" is not downtime approval.
- **P3 order is immutable unless user changes it:** after P2 restored Flash-Next, separately activate 27B and verify; switch **27B → Flash-Next** with approval and verify; **while Flash-Next runs resolve outstanding P1 verification/measurement issues, then rebenchmark P1 and preserve actual numeric evidence**; finally switch **Flash-Next → 27B** with a new scoped approval and verify **27B active** as intended final service. Every transition is an independent guard/rollback unit, no automatic chaining or hidden start/stop.
- P1 initial backlog: historical `doctor=3` and `inventory_plan=3` issues not explained; earlier P1 verify and bounded benchmark PASS but **actual TTFT/latency/tokens/sec measurements not supplied**. Retest existing functional probes and collect measured benchmark evidence after verified 27B→Flash-Next transition. Block final 27B switch until P1 evidence accepted.
- Existing P3 two-roundtrip `roundtrip --execute` and direct legacy module execution are **RETIRED/BLOCKED** because they always restore Flash-Next and conflict with final 27B goal. Canonical source-only read-only plan: `./wizard.sh switch flash-next-27b sequence --plan --json`; `plan_id=null`, `operations_enabled=false`. No real persistent switch executor approved yet.
- Continue single active GPU model on :8000, stable public API, preserved original containers/images/checkpoints, fresh actual Manifest and API served ID, exact scoped approval and mandatory rollback. No P2/P3 automatic handoff, no cache cleanup, no Orcarouter work and no Draft PR merge as side effect.
- Binding document: `docs/P3-MANUAL-TRANSITION-SEQUENCE-20261106.md`. Older D-033 and `docs/P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md` are historical/superseded on P3 ordering; do not use their P3 execute instructions.

---

## R1J — Full Wizard source first, P2–P7 qualify later (2026-11-06)

- D-021 operator direction: finish **all user-facing model / service / advanced / P1–P7 lifecycle menu pathways now**, while execution adapters for P2–P7 remain deliberately blocked until independently qualified. Source-level completeness, CPU CI and DGX acceptance must be tracked as three different statuses.
- `wizard/console.py` implements model-first operator UX; `wizard/workflow.py` owns action capability matrix; `wizard/roadmap.py` reports P1–P7 evidence-scoped status. Don't remove P1 action-specific approval runner or P2 approved revision downloader, and do not accept any new `--execute` bypass from generic UI.
- For model actions `inspect/download/prepare/start/wait/verify/benchmark/switch/rollback/recipe`, display `BLOCKED` with exact reason when adapter not qualified. Do not silently start models via generic `flash serve` or auto-stop Flash-Next.
- Service log view is opt-in, bounded, targets only observed managed model and is potentially sensitive; no automatic upload or logging of its contents to GitHub.
- Keep in-flight NVIDIA 27B download and active Flash-Next/API untouched. After operator-owned transfer finishes, reconcile pinned source and new GitHub Wizard code; only then plan P2 GPU validation and P3 recovery window.

## R1I — Model-first root Wizard UX (operator accepted 2026-11-05)

- Current canonical UI: **Select/run model, Service, Advanced** (plus Exit). Model choices Flash-Next / NVIDIA 27B / Orcarouter. Do not make the operator navigate P1–P7 for ordinary operations.
- The same read-only decision planner serves root TTY selection and `./wizard.sh select MODEL --json`. It must suppress duplicate downloads while `qwen38-27b-dl` is running; no automatic start, stop, rollback or model conversion from merely selecting a model.
- Preserve `scripts/manager/p1_wizard.py` and its existing exact action-specific approvals and DGX evidence. Reuse `p2_27b_download.py`, do not restart its existing active download. Keep old CLI aliases stable.
- Desired Git manifest, observed live Docker/socket (with API/GPU verification separated), and event journal are distinct layers. No stale manifest may authorize a service change. The download's approval scope is **checkpoint-only**, never a transition.
- During an ongoing DGX download, GitHub source/CI/docs work is allowed, but do not ask the user to `git pull`, `docker stop`, start another download or touch live `:8000` without carefully coordinating with completion; preserve user-owned in-flight container and mount.
- Source acceptance does not imply 27B GPU, vLLM 0.32 runtime, model switch or recovery PASS. Implementation plan: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`.

## R1H — One model per DGX, one external API port (operator-confirmed 2026-11-05)

- `runtimes/service-policy.json` is the reviewed desired-state policy. Exactly **one active GPU inference model** may run. Both NVIDIA Flash-Next and NVIDIA 27B must use host `:8000/v1` when active; no dual loading or permanent secondary port.
- A service transition from Flash-Next to 27B requires: validated pinned 27B files/image → fresh live service+GPU+API identity manifest → exact approval and rollback resources → stop Flash-Next → verify port 8000 free → start 27B → verify served ID and bounded API health → commit; on failed startup restore Flash-Next and record recovery outcome. Reverse direction has symmetric gates.
- The model **download only** may overlap Flash-Next inference because it uses disk/network, without GPU, host port binding, service stop or API change. Download plan approval cannot authorize a transition, start, stop, rollback, cleanup or GPU use.
- Stored manifests and journals document desired/previous state, but **actual Docker/socket/API/GPU evidence wins**. Incomplete or contradictory observations block transitions; no success inferred from a stale manifest. The current implementation provides read-only live manifest and an approved downloader, **not** a qualified runtime switch executor.
- Never run a 27B start through generic `flash serve` that overwrites/stops Flash-Next. Treat P3 as independent service handover acceptance and P2 first runtime as separately approved action.

# Project operating rules (must follow in every conversation)

## R1G — P1 live evidence and P2 guarded progression (2026-11-05)

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

- Do not conflate `benchmark=PASS` with a specific throughput target or full Wizard lifecycle qualification.
- Stage P2 begins with **read-only Wizard inventory** and source/CPU validation; retain actual `flash-next` server, caches, model recipes and storage unmodified.
- No guessing immutable 27B SHA or vLLM compatibility from public release marketing; do not auto-download 27B or switch models based only on source inventory.



> Applies to `kjlee-inlct/qwen3.8-Flash-DGX` development, planning, deployment and handoff.

## R1 — Repo, branch and concurrent work

- Canonical new fork `kjlee-inlct/qwen3.8-Flash-DGX`; upstream `blazux/qwen3.8-Flash-DGX`. Preserve upstream behavior and periodically verify pinned upstream SHA before integration.
- Mainline `main` remains a stable base. Plan/handoff work: `feature/recipe-wizard-handoff`. Parallel Orcarouter adaptation: `feature/orcarouter-bf16-adapter`. Do not merge/cherry-pick either automatically without reading diff, resolving conflicts and checking regressions.
- Legacy `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark` and YSLAB references are **read-only historical sources**, not the new implementation base. Never silently replace new fork code with old vLLM patches.
- One coherent topic per branch; meaningful commits, draft PRs for unvalidated work, CI/readback. Record PR and Git SHA. No unverified claim of merge.

## R1A — User-confirmed sequential Wizard delivery contract (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

- Do not advance a milestone merely because source/CPU CI succeeded: require actual **Wizard-driven DGX** installation, API/benchmark and evidence for P1/P2/P5; switch and restore verification for P3/P6.
- Existing `flash`, scripts and Python manager are allowed as **subprocess engines** invoked by the Wizard, not as substitutes for a complete Wizard entrypoint. Both interactive and batch/noninteractive operations should share validation, plans, gates and evidence. Wizard should reject implicit destructive defaults.
- Keep external host API `:8000/v1` where feasible and consistently manage served-model IDs. No simultaneous assumption that two heavy models fit GPU memory. Any change to external clients/port/gateway requires explicit operator review.
- P4 is conditional: if sufficient space exists, record **SKIPPED_NOT_NEEDED** rather than delete weights. If required, enforce exact-path dry-run and explicit separate approval, verified safe fallback, no shared-cache blob deletion and rollback plan. Preserve source, recipes, tests, logs and evidence.

## R1B — Modular Wizard and user-mediated command execution

**Wizard architecture decision (2026-11-05):** Implement all P1–P7 **menu/CLI modules first** and then integrate/debug actual runtime in P1→P7 order. Root operator entry is `./wizard.sh`; `wizard/menus/models/`, `switching/`, `storage/`, and `operations/` own per-menu behavior, with `wizard/main.py` and `wizard/menus/common.py` for routing and safe source contracts. Scripts accept explicit stage/action arguments and emit JSON and stable exit codes for operator-mediated DGX tests. Only P1 calls the existing guarded backend today; P2–P7 are SOURCE-ONLY plans and must never execute merely because a menu exists. No SGLang; vLLM 0.32 only.

- All P-stage menus use one root `./wizard.sh` entrypoint; direct command syntax and interactive choices must share the same stage implementation. Never build separate secret execution paths for headless runs.
- Default to read-only status/plan with machine-readable JSON; use exit 0 for successful inspection, exit 3 for blocked plans, and nonzero for failures. A plan printed with BLOCKED is evidence of **refusal**, not approval. P1 execution retains its fresh full `plan_id` gate. Do not allow `--dry-run` with `--execute`.
- The adapter for P2, P3, P4, P5, P6, P7 must remain `INTERFACE_ONLY` and `executed=false` until separate pinned, tested implementation, source/CPU/CI and real DGX acceptance prove each operation. In particular P4 may be skipped and never deletes anything without its own exact-path approval; P3/P6 do not switch any live services until qualification.
- Do not update the active DGX worktree while the user-owned `./flash setup default` or its queued `serve/wait/test` commands may still be running. The last supplied log showed download at 9/25 (36%), image build PASS; current state must be rechecked after completion.

## R1C — Functional categories override numbered module filenames

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

- Do not create a new numbered `wizard/menus/pN.py` module. Extend only the appropriate descriptive category module. The numeric P-stage IDs are metadata/legacy CLI aliases; never reintroduce numbered filenames as the primary architecture.
- Root `./wizard.sh` defaults to two-level group/selection navigation and supports noninteractive `./wizard.sh model flash-next status --json` or `./wizard.sh switch flash-next-27b plan --for-action switch --from-model flash-next --to-model 27b --json`. Legacy `./wizard.sh p1 ...`, `--stage p3` and `wizard/p1.sh` remain supported.
- P2–P7 remain `INTERFACE_ONLY` with no operational permissions, regardless of menu naming or presence; no resumed download, Docker changes, cache cleanup or model switch from this refactor.

## R1D — Git-tracked temporary script batches for user-operated DGX (D-016)

**Default for multi-command DGX checks/tests:** Do not repeatedly paste a long ad-hoc shell transcript. Implement one **descriptively named, tested, version-controlled temporary wrapper** in `scripts/temporary/`. GitHub-first changes (script + CPU fake-backend tests + docs) must be committed on the active branch, CI checked and recorded in handoff. The operator then **finishes any existing processes**, runs `git switch` / `git pull --ff-only`, and invokes **one script**; the script itself must not automatically pull, reset/clean the worktree, install/upgrade packages, or mutate in-use services.

- **Required pipeline:** (1) **preflight/inventory + safe diagnostics**, (2) **Wizard-mediated, explicit per-operation approval + bounded verification/benchmark** only when ready, (3) **report/evidence export**. Missing readiness, wrong branch, dirty tracked files, active setup or missing approval must fail closed; still export an honest BLOCKED result.
- **Approval:** Source/CPU checks are read-only and may run unattended. **Except the user-authorized, non-disruptive P1 auto-GPU procedure in R1E**, real API/GPU operations require an exact currently valid action-specific Wizard `plan_id`, independent consent for *verify* and *benchmark*, a second Wizard preflight, and benchmark only after verification PASS. R1E still mandates action-specific current IDs and a second preflight but permits the script to supply them without separate typed consent. In interactive shells ask for that full hash; in headless mode never auto-consent and accept only explicitly supplied exact identifiers. Never hide consent inside `--yes` or a global preapproval.
- **Evidence:** Use date-stamped folders under a user-owned location **outside** Git/HF cache, restricted to the operator, containing raw command return codes and structured JSON plus Wizard evidence paths; print the result path. The user may selectively share reviewed logs with the assistant. Do not commit/upload live logs, model data, API credentials or proprietary prompts to GitHub automatically.
- **Temporary lifecycle:** Each script needs a one-line purpose, run preconditions, exact commands, side effects, safety boundary, owner/stage, test path and disposal condition in `scripts/temporary/README.md`. Keep the wrapper until the results have been analyzed and recorded; then archive/remove by a separate reviewable Git commit. Never have the script self-delete or purge broad folders. Leave stable implementations in `wizard/` or `scripts/manager/`, not permanently hidden in `scripts/temporary/`.
- **Non-authorized actions:** No automatic `setup`/download, Docker stop/remove/recreate, HF cache cleanup, image prune, model switching, gateway changes, `git reset --hard` or `git clean -fd`. These need an independent scoped plan and explicit operational permission when/if requested. Existing OpenWebUI/Portainer and the user's prior queued `flash setup/serve/wait/test` must be preserved.

**First implementation:** `scripts/temporary/p1-post-download.sh` with `p1_post_download.py`, CPU tests `tests/test_p1_temporary_cpu.py`, and the canonical instructions `scripts/temporary/README.md`. Run only **after the original setup/serve/wait/test shell chain ends**. `--inspect-only` is non-executing; default TTY interactive prompts for separate current verify/benchmark hashes. This is not authorization to perform live DGX operations from the assistant.

## R1E — Default Blazux compatibility and scoped P1 GPU test authorization (D-017)

**Operator DGX facts (2026-11-05):** The latest post-download diagnostic returned `api_model_ids=["qwen3.8-flash-next"]`, `refs/main=fc694b54fb0174e0913e6adf86691ef85a4ead47`, 0 incomplete HF blobs, a source index and tokenizer that are **existing nonempty symlinks whose targets resolve outside the model repository**, and a Hybrid tokenizer with the same layout. The Hybrid index is a normal 31,907,813-byte file and the `.prepared` marker exists. These observations show the previous `TARGET_OUTSIDE_REPOSITORY` reason is a **new P1 checker policy stricter than Blazux's original `os.path.exists`-based policy**; they do not establish that any metadata is missing. Previous plans were blocked before actual GPU verification or benchmark. The user explicitly allows non-disruptive GPU compute tests to run without separate per-step approvals, provided the actual target service is confirmed. The presence of an API response means some server is listening; do NOT assume there are literally no processes running or stop/replace any service.

- **Default-first compatibility:** For default `nvidia/Qwen3.8-Flash-Next-NVFP4`, match supported Blazux source/snapshot/Hybrid metadata conventions. The earlier P1 strict audit wrongly treated **existing metadata-only cross-repository symlinks** (`tokenizer.json` and `model.safetensors.index.json`) as missing. Accept these two names when the target resolves to an existing nonempty regular file; fully parse and validate the bounded index JSON and referenced shards. Keep arbitrary external **weight shard** symlinks blocked. The new P1 64MiB index-size guard remains; do not disable it or silently bypass missing files.
- **Operator-granted P1 GPU scope:** On the DGX, user authorizes **non-disruptive** GPU inference/API verification and a bounded benchmark **without typing a plan hash or approving each subtest again**. Run via `bash scripts/temporary/p1-post-download.sh --auto-gpu` after `git pull --ff-only`; script obtains the *current* distinct verify and benchmark plan IDs itself and submits them to the existing Wizard's second revalidation. It still blocks on wrong branch, dirty worktree, missing/wrong served model ID, active setup/download, failed or changing asset audits, failed verification, and port/image/container mismatch.
- This authorization is **not** permission to stop/restart/replace containers, modify the listening API, run setup/download, regenerate Hybrid assets, delete model/cache files, switch to 27B/Orcarouter, change proxy/gateway, or run heavy unbounded load. Do not treat the statement that no prior service is operating as evidence no current model process exists; `/v1/models` returned `qwen3.8-flash-next` and must be respected.
- **Default script behavior unchanged:** `--inspect-only` remains strictly read-only; without `--auto-gpu`, the script continues to request individual manual hashes or blocks non-TTY. Auto GPU is opt-in at script invocation, only for P1 verify (text/tool/vision) then 3 bounded SSE requests by default. CPU CI does not prove DGX performance.

## R1F — Preserve native Blazux baseline; never gate it on Wizard-only probes (2026-11-05)

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

- Distinguish **native model baseline** (Blazux coherence /v1/completions and ordinary chat) from **optional feature probes** (strict tool invocation, synthetic image). A partial optional failure is NOT a failure of default Blazux. Record `baseline_status`, `extended_status`, named `probes`, and `status=PARTIAL` where appropriate.
- Never hide a Wizard failure on nonzero returncode: parse its bounded JSON stdout regardless of returncode, preserve evidence path and sanitized probe errors. Do not mistake `evidence:null` in a wrapper summary for absent stored Wizard evidence.
- Baseline PASS may enable already-authorized bounded P1 benchmark even if extras fail; baseline FAIL may not. Full P1 acceptance is still pending until required extended features and benchmark meet their own exit criteria.
- Never correct a Wizard-specific test mismatch by re-downloading 124GiB weights, regenerating Hybrid or changing a live API without separate concrete evidence and scoped authorization.

## R2 — Live operations, authorization boundaries

- **Superseded observed-operational assumption (2026-11-05):** user reports all previous operating services deleted. The old Orcarouter container `qwen38-flash-orca-uncensored-bf16-mtp` and old `:8000/v1` are **historical**, no longer presumed active or statically reserved. Still perform fresh read-only Docker/socket/volume inspection on DGX; a user report does not prove the port and name are free. Preserve any actually existing unrelated containers, image assets, weights, HF cache, integrations or mounted storage.
- Do not stop/kill/exec/remove/replace/retag/rebind/reconfigure any **observed existing container**, or mutate shared cache/models, without separately scoped approval. Refuse a name conflict: no implicit docker rm -f. Do not treat deletion of old services as authorization to remove other resources.
- This fork removes the implicit `docker rm -f "$NAME"` from `scripts/serve.sh`, replacing it with an exact-name collision refusal; still verify collision checks and race behavior before approving operational launch. Existing upstream scripts in other worktrees may retain the destructive behavior.
- Current user request authorizes **implementing** new Blazux default source/config for port 8000. Do not infer approval for GPU/model loading, Docker image replacement, gateway cutover, service stop, model/cache deletion or other disruptive resource actions. Before deployment obtain actual DGX preflight/port/image evidence and a scoped operation/rollback agreement.
- Read-only GitHub/source/test inspection and local CPU-only tests are allowed. DGX read-only inspections should be scoped and recorded, avoiding sensitive output.
- **vLLM 0.32 only** for all three model recipes. No SGLang integration.

## R3 — Destructive cleanup is separate

- Stage P4 `retire Flash-Next` means cleanup *candidate*, not advance permission to delete.
- Require specific cleanup plan ID, confirmed inventory, exact paths/digests, size estimates, disjoint protected roots, no running/bound/shared references, rollback capacity and explicit approval.
- Default `dry-run`; never `rm -rf` a whole workspace/Hub cache, `docker system prune -a` or delete unknown blobs/images.
- Keep recipe, config, benchmark, logs, source and provenance even after checkpoint deletion. Prevent cleanup of the last validated fallback.

## R4 — Verification and assertions

- Status vocabulary: `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`. Each status must carry **scope** `SOURCE/CPU/CI/GPU/API/SWITCH/RELEASE`.
- A source audit `PASS` is **not** GPU runtime `PASS`; upstream/other-author benchmarks are not local benchmarks; default branch compatibility does not imply 27B compatibility.
- Record full model repository revision, image digest, Git HEAD, recipe SHA, runtime config, host resources, command, seeds, comparison method, observed output, log/artifact location and timestamp for every claimed result.
- Orcarouter strict same-checkpoint logprob max absolute delta `1e-4` previously failed in Preview. Carry forward as `RELEASE_BLOCKED` until proven otherwise or a separately reviewed gate decision is recorded. Avoid comparing logprobs across different checkpoints.
- Test failures must be recorded, not concealed, renamed or marked `PASS` for task completion.

## R5 — Efficient development and update rules

- Prefer a meaningful **batch of related changes per conversation**: inspect → implement → write tests → run CPU checks → docs → commit → PR/verify.
- If needed, add or update scripts, manifests, tests and docs, rather than leaving long transient manual commands as the implementation.
- Keep `README.md` external references intact; cite aphex3k only for transferable tuning and benchmark methodology. No SGLang runtime.
- Every state-changing session ends with updated `handoff/CURRENT-STATE.md`, `handoff/NEXT-ACTIONS.md`, and `handoff/CHANGELOG.md`. If there are new tests, update `EVIDENCE-LEDGER.md`; if new policies, update `DECISIONS.md`.
- On a new chat, read handoff first, verify against GitHub and real runtime evidence, proceed directly with the next safe actions. If no tool/action is available, record `BLOCKED` honestly; do not fabricate execution.
- No secrets, personal tokens or private host-only strings in GitHub markdown, logs or PRs.

## R6 — Exit report format

Every meaningful handoff update must include: `WHAT CHANGED`; `SOURCE BRANCH + ACTUAL SHA`; `PR + CI`; `TESTS (PASS/FAIL/NOT_RUN by scope)`; `DGX STATE (observed vs historical)`; `BLOCKERS/APPROVAL`; `NEXT 1–3 ACTIONS`; `FILES UPDATED`. Unknown values must say unknown.
