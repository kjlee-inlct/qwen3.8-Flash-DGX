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
