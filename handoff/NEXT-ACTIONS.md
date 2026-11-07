## 2026-11-07 — ACTIVE NEXT ACTIONS after Wizard SOURCE implementation (CI 799/799 PASS)

1. Pull the latest feature/recipe-wizard-handoff commit with a clean fast-forward on DGX. Run READ-ONLY ./wizard.sh model 27b recipe-diff --json and ./wizard.sh service manager status --json; inspect false-positive differences against current 27B actual Docker Cmd, mount RO/source, GPU, ports, API. No execute.
2. Pin/verify trusted host HF cache location and qualified Flash-Next recipe before generic model uninstall/reinstall release. Do not edit the existing qualified 27B recipe SHA casually.
3. Replace stale P3 receipt Docker IDs used by operational_switch.py / operational_executor.py live checks with fresh observed IDs while preserving historical receipt integrity.
4. Complete source-level private journal/crash guarantees, independent verified backup cleanup and atomic benchmark latest-pointer promotion; test idempotence, interrupted writes, uncertain rollback. Existing generic lifecycle execution remains hard-gated False.
5. Separate DGX operator authorization and real UX, fault/rollback, one-active-model, :8000 and 27B tool/benchmark acceptance before production gates change. P4-P7 remain later; P2-FINAL and P3-C stay PASS/CLOSED.

Implementation scope and caveats: docs/WIZARD-LIFECYCLE-SOURCE-IMPLEMENTATION-20261107.md. New GitHub CI run 42355750124, **799 CPU/Fake-DGX PASS in 36 groups**. This is NOT actual DGX live qualification.

---

## 2026-11-07 — HANDOFF DOCUMENT AUDIT / NEXT CONVERSATION READY

The user starts the next development phase in a separate conversation. **Audit verified all 8 handoff docs, 12 implementation docs and 5 recipe/manifest/benchmark indices exist (25/25), plus both published benchmark collection directories and current source/evidence files.** The pre-audit HEAD `9ec7420b74369e7a76785577dc543f9dafb8897d` had GitHub Actions run `42352654468` SUCCESS, **757/757 CPU tests in 34 groups**. This CI is source-only. New documentation commits advance HEAD; inspect GitHub afresh.

A new **complete standalone** prompt is in `handoff/START-NEXT-WIZARD-LIFECYCLE-20261107.md` and prominently at the top of `handoff/SESSION-START-PROMPT.md`; older prompts below are ARCHIVED / superseded. Missing-document/staleness audit: `docs/HANDOFF-DOCUMENT-AUDIT-20261107.md`. Next implementation contract: `docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md`.

**Latest actual DGX:** canonical NVIDIA 27B native-tool recipe, 3/3 benchmark v2, Open WebUI Native user-confirmed PASS, two old diagnostic containers removed via verified Wizard manifest cleanup; original `qwen38-27b` runs at :8000 with served `qwen3.8-27b`, Flash container stopped, Open WebUI/Portainer running. P3-C historical PASS/CLOSED, P8 conditional migration ticket INACTIVE. Do not restart the old P2 Tool HTTP-400 diagnosis; it was resolved. Old original 27B Docker container IDs recorded in P3 stage receipts remain HISTORICAL. `PRODUCTION_EXECUTION_RELEASED=False` for main Wizard generic switch; post-ID-change real guided switch/recovery acceptance still open.

**Next target:** general Wizard lifecycle/recipe-diff detection at install/start/restart/switch, scoped container remove/reinstall/recreate with fresh approval, new runtime receipt and rollback. No global deletion prohibition on canonical 27B or Flash. No live DGX mutation is authorized by this documentation step. The canonical `recipes/qwen38-27b.runtime.json` file's exact SHA is tied to current approved benchmark pointer: do NOT silently edit this file to fix text/metadata. Preserve old P3/bench receipts, images/caches, vLLM 0.32, one GPU model, port 8000, Draft PR #1.

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

## LATEST NEXT ACTIONS 2026-11-07 — after source-only protected 27B Native Tools V1

1. **CI and source review:** confirm latest feature branch CI for `p2_27b_tool_variant.py`, `p2_27b_tool_streaming.py`, new test suites, intentionally invalid V1 YAML and shell CLI. GitHub CPU PASS is not DGX qualification.
2. **Read-only DGX audit (optional operator run):** after clean `git pull --ff-only`, use `--tools-profile` and `--tools-variant-plan` (exit 3 by design). Preserve original 27B/Flash and existing port 8000. Do not invoke SSE probe repeatedly against original HTTP-400 container.
3. **Develop missing executor safely:** validate exact pinned vLLM 0.32 parser/tokenizer; design variant-aware service-policy/manifest, domain-separated expiring execution plan, TTY approvals, stop-old→free :8000→start distinct variant→verify native tools, locked journal, rollback and ambiguous crash-denial. Add Fake-DGX launch/restore/failure and concurrent-service regression tests. **No live execution authorization**.
4. **Later separate real approval:** only after source/CI safety and independent downtime consent, qualify DGX auto Tool Calling + continuation + streaming + reasoning + non-tool chat, Open WebUI Native, original restore and independent final journal. Then decide P2-FINAL PASS. Keep `PRODUCTION_EXECUTION_RELEASED=False` until its own Wizard menu and fault recovery qualifications.
5. Historical P3-C must never be repeated, original image/container/cache/receipts never removed, no auto approval, no PR merge. P4–P7 retain their separate ordering.

Contract: `docs/P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md`.

---

## LATEST NEXT ACTIONS — 2026-11-07: P2-FINAL real HTTP 400, protected tool-enabled variant design required

**P0 — Record closure/evidence, no operation:** newest user-provided `LIVE_SERVICE_VERIFIED` current 27B, journal `VERIFIED/COMMITTED` with **14** events; both real ordinary 27B→Flash and Flash→27B PASS and independently post-checked. Historical P3-C remains FINAL/CLOSED, never re-run. Normal main Wizard is NOT production released and real fault injection/recovery not accepted. Reconfirm current status before any action.

**P1 — P2 last Tool Calling gap:** verified preserved `qwen38-27b` `Config.Cmd` lacks `--enable-auto-tool-choice`, `--tool-call-parser` and `--reasoning-parser`; source opt-in profile has intended `qwen3_coder` / `qwen3`; actual bounded local probe `BLOCKED/LOCAL_API_HTTP_ERROR_400`. **Do not retry repeatedly or pretend Tool Calling works.** Plan separate named, immutable 27B tool-enabled recipe/profile variant on vLLM 0.32, with image/parser support inspection, pinned model & original protected containers, formal single-model :8000 cutover, rollback and private evidence paths. Do NOT reuse the P2 first-boot trial, P3 stage C, or casually recreate `qwen38-27b` (ordinary switching pins its ID/provenance).
 
**P2 — Implement & qualify on source:** profile variant (non-default); safe migration plan and separate authorization/executor contract; offline CPU Fake-DGX tests for parser flags and name/port/image/candidate identity, approval expiry, no parallel GPU, failed launch/rollback, tool `auto`/structured JSON/continuation, streaming chunks, thinking separation, Open WebUI Native expectations. New source/tests/docs commit to existing feature branch, CI green. Obtain actual DGX user approval **before** any stopping, starting, recreating or replacing inference containers, benchmark rerun or Open WebUI service modification.

**P3 — Actual P2-final acceptance only after new consent:** bounded live tool-enabled runtime / Open WebUI Native tools accepted and original model assets retained, evidence for streaming and tool cycle. Only then consider P2-FINAL closed; original P2 and P3-C historic receipts untouched. Normal `./wizard.sh` release gate stays false pending its own menu UX and real failure-recovery acceptance. P4/P5/P6/P7 are deferred.

See `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`, `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`, `docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md`.

---

## NEXT after user P2/P3-C closure decision — 2026-11-07

1. **P3-C historical real DONE/CLOSED**: original Flash→27B one-off actual P3-A/B/C accepted, no additional Stage-C run or receipt editing. Separately, new ordinary 27B→Flash and Flash→27B operators reported PASS; reverse final independent status/audit must still be observed. Last reported active is now 27B.
2. **P2-final Native Tool Calling is the only appended P2 acceptance gate** (prior P2 GPU/benchmark/restore PASS retained). Source vLLM 0.32 Qwen3.8-27B profile `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3` is opt-in, never automatically retrofits original 27B container. See `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.
3. DGX no-downtime read-only + small inference checks: `./wizard.sh service manager status --json`; `python3 -m scripts.manager.operational_audit --json`; `docker inspect qwen38-27b --format '{{json .Config.Cmd}}' | python3 -m json.tool`; `bash scripts/serve_27b.sh --tools-profile`; `bash scripts/serve_27b.sh --tools-probe`. The probe intentionally returns BLOCKED if auto-parser is absent; no need to retry/restart. New source requires clean fast-forward and CPU CI first.
4. Before actual P2-FINAL remediation, design a **distinct pinned tool-enabled 27B recipe/service variant**; do not recreate/delete historical `qwen38-27b`. Qualify parser on vLLM 0.32, tool_call, tool-result continuation, **streaming**, non-tool inference, reasoning separation, Open WebUI Native. Requires independently approved outage/restore risk and a separately reviewed rollback plan. Do not disturb active 27B or port 8000 while creating read-only profile.
5. **Normal everyday Wizard main menu release still OFF**; Fake-DGX CPU and actual trial-only dual direction PASS do NOT alone qualify main TTY menu or failure recovery. No forced recovery test, P3 replay, P4 cleanup, Orcarouter changes or PR merge without independent approval.

---

## LATEST NEXT — 2026-11-07: first ordinary switch + independent postcheck PASS; reverse source READY only

- [x] Actual DGX ordinary `27b→flash-next`: operator's `PASS` and private receipt plus **separate after-action** `LIVE_SERVICE_VERIFIED` for sole `qwen3.8-flash-next`, `operational_audit=VERIFIED/COMMITTED/7 events`.
- [x] Reverse `flash-next→27b` **READ-ONLY** preflight: `READY_FOR_SEPARATE_TRIAL_APPROVAL`, `issues=[]` (the recorded 276s remaining and SHA expired/rotate according to time; never assume still valid).
- [ ] **Real reverse execution NOT_RUN.** Need new, separately scoped Flash-Next API downtime authorization, fresh `--target 27b --plan --json` and (only when approved) human `--target 27b --execute` with FOUR *new* exact TTY inputs; do not auto-fill, pipe, or reuse first direction's SHA. Successful reverse leaves 27B active, no auto-return.
- [ ] Separately authorize and qualify real error/restore behavior before normal production switch release. `PRODUCTION_EXECUTION_RELEASED=False` continues to protect normal `./wizard.sh` main/model menus; P3 A/B/C remain historical, not to rerun.
- [ ] Preserve private operating/P3 receipts, model containers/image/caches, Portainer/Open WebUI and port 8000. Keep 27B Tool Calling deferred and PR #1 unmerged until independently assessed.

**Next exact safe command (read-only)**: `bash scripts/temporary/operational-switch-acceptance.sh --target 27b --plan --json`, followed by separate operator consideration of the trial. No automatic action authorized merely by this log.

---

## NEXT after REAL DGX ordinary 27B → Flash-Next PASS — 2026-11-07

1. **Record current active model as FLASH-NEXT**: the new actual single-switch `operational acceptance --target flash-next --execute` returned `PASS` and `Observed model: flash-next`. Prior next-actions saying this first direction has NOT_RUN are superseded. P3 A/B/C receipts and operations journal are distinct; do NOT replay P3 stages.
2. **Immediate safe read-only post-check on DGX:** `./wizard.sh service manager status --json`; `python3 -m scripts.manager.operational_audit --json`; `bash scripts/temporary/operational-switch-acceptance.sh --target 27b --plan --json`. Check `LIVE_SERVICE_VERIFIED` with only Flash ID `qwen3.8-flash-next`, journal `VERIFIED` / terminal `COMMITTED`, next fresh plan source `flash-next`→target `27b`, no issues. If output disagrees, stop; no destructive action.
3. **Separate consent still required for reverse direction:** a new operator-approved Flash-Next downtime window and fresh four exact human TTY approvals are needed before `--target 27b --execute`. First plan hash/approval **cannot** be reused. Success would leave 27B active; no automatic toggle or repetition. Do not run merely on instruction to review status.
4. After actual bidirectional trials, verify independently supplied journal/receipt status and still assess real rollback/failure behavior under separately approved conditions. Do not trigger intentional failure on the live DGX without a dedicated controlled test plan.
5. Keep `PRODUCTION_EXECUTION_RELEASED=False` and Draft PR #1 unmerged until acceptance evidence and safety review meet the ordinary menu release gates. Keep Open WebUI Tool Calling, recipe modifications, P4/P5/P6/P7 deferred.

---

## LATEST TOP PRIORITY — Ordinary Wizard source finished; independently approved DGX acceptance is next

1. Verify latest GitHub commit and **green source CPU CI** (Fake-DGX only). `./wizard.sh` main option **4**, model option **6**, `operational guided --target flash-next|27b`, and one-off acceptance `operational acceptance --target ... --plan|--execute` are new and source-wired. Production release gate is intentionally false.
2. Next safe DGX operator step is **READ ONLY**, after clean fast-forward source pull: `./wizard.sh service manager status --json`, `python3 -m scripts.manager.operational_audit --json`, then `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --plan --json`. No stop, GPU start, benchmark or P3 replay in these commands.
3. To complete ACTUAL hardware acceptance, obtain a fresh, independently scoped **27B downtime/possible restore failure** approval. Only then can the DGX human voluntarily run the tracked `--execute` (four independent exact TTY approvals). PASS leaves Flash active. Flash→27B requires **another separate new operator approval**, plan and physical trial. Stop immediately on `RECOVERY_FAILED` / committed uncertainty, no blind retries or state deletion.
4. On supplied actual DGX outputs, review private evidence vs current journal, target chat, post-switch identity and rollback. Only AFTER both real directions and recovery behaviors are independently qualified can the reviewed normal production release gate be enabled. Do not infer DGX acceptance from CI or one-off P3 receipts.
5. Keep **Open WebUI 27B Tool Calling and recipe parser updates deferred**. Later P4 conditional cleanup, P5 Orcarouter, P6 Orcarouter↔27B, P7 proxy/gateway are separate phases. Preserve active 27B, original Flash fallback, HF cache, port 8000, all historical evidence and Draft PR #1.

Primary runbook: `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`.

---

## TOP PRIORITY 2026-11-07 — Resume normal model switching Wizard UX, DEFER Tool Calling

1. Complete GitHub CPU CI for newly wired guided path `wizard/console.py` option 6 / `operational guided --target` / `operational_wizard.py` / `operational_executor.py`. Resolve any regressions before user source pull. Preserve Draft PR #1.
2. Continue executor recovery-hardening source + Fake-DGX failure-injection and journal tests. Keep `PRODUCTION_EXECUTION_RELEASED=False` until independent real DGX acceptance; release flag is **not** a user-configurable toggle.
3. Make guided operator review concise: current/target, port :8000, protected container and model identity, plan expiry, interruption warning, exact independent SHA, target-specific downtime consent, PASS/restored/uncertain outcomes. Current CLI `operational guided --target` and console menu are **REVIEW ONLY**.
4. After all code/recovery gates, separately review a **new downtime approval** and conduct independently approved real DGX ordinary 27B→Flash and Flash→27B trials and failure recovery; never replay historical P3 A/B/C or auto-switch.
5. Only after P3 general recurring switch acceptance, revisit P4 conditional cleanup, P5 Orcarouter, P6 and P7. **Open WebUI 27B Tool Calling and recipe parser configuration intentionally postponed**, despite prior diagnosis.

---

## 2026-11-07 — Current WebUI-vLLM 27B integration issue

- [x] Real DGX 27B default chat/inference PASS; with `chat_template_kwargs.enable_thinking=false`, direct strict `DGX_OK` **PASS**. Distinguish formatting from actual generation.
- [ ] On Open WebUI 27B model only, disable Builtin Tools and attached/chat Tools; retest plain text chat. **Real WebUI outcome NOT_RUN** as of evidence received.
- [ ] Optionally `docker inspect qwen38-27b --format '{{json .Config.Cmd}}' | python3 -m json.tool` (read-only). Real live arguments not yet observed.
- [ ] Source-only test per-model tool parser configuration using pinned vLLM 0.32 and NVIDIA 27B chat template; no parser assumption. Any new native tool-capable container requires a separately approved downtime/rollback plan, not restart of existing preserved container. Full Open WebUI tools and general operating switch NOT_QUALIFIED.
- [ ] Preserve active 27B, Flash fallback assets, historical P3 A/B/C, API port 8000 and Draft PR #1 unmerged. See `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`.

---

## 2026-11-07 — Follow-up after actual DGX 27B curl PASS

- [x] Real DGX 27B health, sole API model ID and actual chat completion **PASS** from operator console. `/v1/models=qwen3.8-27b`, completion model matches, stop finish, vLLM 0.32.0, original source at `05c1968`. Previous `curl smoke NOT_RUN` note is superseded.
- [ ] Investigate **response formatting only**, separately: `content` contains reasoning-like text and `</think>` before `DGX_OK`, `reasoning=null`. Optional non-disruptive per-request `chat_template_kwargs.enable_thinking=false` experiment after reviewing actual Qwen/launcher compatibility. Never edit the live 27B runtime or restart blindly. Updated `FORMAT_DEVIATION` classifier is SOURCE+CPU until independently run on actual DGX.
- [ ] Source-only general switch executable release gates: recovery/crash testing, non-reusable scoped operator consent, integrated Wizard UX and independent approved DGX bidirectional/rollback acceptance. **NOT YET AUTHORIZED**. Do not replay P3 A/B/C or automatically switch models, delete caches, or merge Draft PR.

---

## 2026-11-07 current immediate operator read-only / inference task

- [ ] On *real DGX*, while NVIDIA 27B is still active, pull source only and run `bash scripts/temporary/operational-27b-curl-smoke.sh`. Supply output (health, served ID, completion). It makes **one bounded localhost GPU inference** but does NOT switch/stop/start containers. `LIVE_SERVICE_VERIFIED` alone is not inference proof. Do not claim actual pass before output.
- [ ] Review source-only CPU CI for the new fake-curl tests and Wizard hint. Do not authorize general switch execution from a smoke result.
- [ ] Continue source hardening of the separately guarded general operating switch, crash-recovery fail-closed behavior and guided UX, with **real DGX switching NOT_RUN**. P3-A/B/C are complete and must never be replayed. Draft PR #1 remains unmerged.

---

## 2026-11-07 — NEXT after source-only operating switch implementation

The new ordinary switch PREVIEW and independent guarded executor SOURCE are implemented on the existing branch. **No Wizard execute route and no actual DGX operation were enabled.** Next: (1) confirm the new Fake-DGX executor and preflight CI passes including stop→start, exact identity, rollback success/fail and retry denial; (2) review the new execution contract and identify state machine/lock/recovery limitations; (3) implement a real user-friendly guided review/approval flow only after safety gates and CPU tests qualify, keeping live execution disabled until separately authorized DGX maintenance; (4) run operator-initiated read-only \`./wizard.sh switch flash-next-27b operational --target flash-next --plan --json\` optionally after safe fast-forward pull; (5) request a separately scoped consent before ANY live 27B downtime or repeated switch test. P4 remains conditional, P5 Orcarouter source audit after UX, P6 after P5 GPU qualification, P7 after service/proxy/gateway integration. Do not reuse one-off P3 stage receipts as authorization.

Read latest design: \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`. Retain original 27B active :8000, entire original HF cache, containers/images, original immutable P3 receipts and journals. Draft PR #1 must remain Draft/unmerged.

---

## 2026-11-07 — P3-C SUCCESS; STOP REPEATING P3 STAGES, NEXT WIZARD USABILITY PHASE

**P3-C is now DONE on actual DGX, not just preflight!** Operator's real `--execute` used a newly approved C SHA and both distinct explicit downtime/activation strings; canonical Wizard returned PASS and `active_model=27b`; wrapper `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `issues=[]`, original immutable `stage-c.json` verified. Private report `reports/transitions/flash-next--to--27b/p3-c-operator-20261107T011939Z-5f26a6ff25a2.json`. Flash assets/containers preserved. DO NOT RE-RUN A/B/C, P1/P2 benches, restore Flash, prune models, or change port 8000 as part of this handoff. Preserve running 27B for operational use. Real P1+P2+P3 backend qualification is COMPLETE for the specified bounded scenarios; generic recurring switch and interactive menu acceptance are NOT.

**Next source work only (requires separate scoped UX plan before changing live services):** deliver model-centric, ease-of-use main `./wizard.sh` menu, not exposing internal P1/P2/P3 as default. Recommended interaction: observe and verify current live model; show installed qualified alternative and historical Verify/Benchmark, preview specific exact transition and any clients that will lose service; show clear final confirmation with exact plan/approval value as needed; under the hood invoke the same canonical guarded backend/lock/journal/restore; then independently show FINAL active API/port; private receipts append-only and model-indexed. No silent approval, no automatic target start, no model cache cleanup, no plan SHA reuse. Design robust expiring-plan refresh pre-approval. Add CPU fake-DGX tests for menu navigation/approval/cancellation/post-switch/recovery; actual 27B→Flash and Flash→27B ordinary operating transition must be separately approved and demonstrated only later.

**Architectural status:** P1 interactive guided actions and backend Verify/Benchmark ran real DGX; P2 bounded trial/benchmark and original restore ran; P3-A/B/C original Wizard CLI engine ran; but `wizard/console.py::_stage_actions` currently calls `module.run([selected, "--plan"])` and prints "Execution NOT initiated". Therefore the main UX cannot yet execute a stage and P3 C success does not prove regular model selection-to-switch. Original CLI can start/stop the existing services under approvals; don't conflate it with a user-friendly menu.

Use read-only `./wizard.sh service manager status --json` only if an additional independent live check is wanted. Actual user already supplied post-switch successful independent API status and canonical C receipt. Draft PR #1 still unmerged. After source docs commit, ask operator to ff-pull only when needed; no model operations implied by Git updates.

---

## 2026-11-07 — STAGE-C TIME WINDOW HANDLING: NEXT OPERATOR ACTION

After latest source CI PASS and a clean `git pull --ff-only origin feature/recipe-wizard-handoff`, the operator can run `bash scripts/temporary/p3-stage-c-operator.sh --execute` on actual DGX **only if explicit live Flash-Next downtime consent remains in force**. Current user explicitly authorized Flash-Next stop and final NVIDIA 27B switch earlier. The two attempted `--execute` commands at 10:08:14 and 10:09:30 KST were safely BLOCKED by <=120s remaining; **no dispatch occurred**. Keep original Flash :8000 active until canonical C actually succeeds.

The wrapper now handles the edge of the canonical 10-minute window: if current plan has >=120s remaining, show exact three TTY prompts; if shorter, perform only read-only status + Stage C plan rechecks, bounded <=150 seconds, for a NEW DIFFERENT SHA with >=120s left. No sleep/refresh in `--plan`; no previous SHA, approvals or old C plan are reused. New plan requires unchanged original A/B receipt lineage, pinned preserved 27B, P2 SHA and post-B P1 PASS. Then user must independently type the new full 64-char SHA without brackets and the exact `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Original canonical Wizard rechecks again under its lock; success requires actual 27B API and canonical immutable C receipt. If any BLOCKED/CANCELLED/UNCERTAIN status, HALT and review report, never skip gate or force retries. No PR merge/prune/P1 reruns.

[Updated operator runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md). Both Git-published benchmark summaries are ALREADY VERIFIED against original DGX receipts; no repeat bench needed.

---

## 2026-11-07 — NEXT: STAGE-C FRESH READ-ONLY PLAN; BENCHMARK PUBLICATION ALREADY VERIFIED

**Completed by operator on actual DGX:** `bash scripts/temporary/verify-published-benchmarks.sh` checked private Flash and NVIDIA 27B original JSONs against two Git-tracked metric-only public summaries: both `VERIFIED`, `issues=[]`, `executed=false`; original SHA256s match expected. No need to repeat publication verification or run GPU benchmarks without new reason. Git `benchmarks/published/` entries are now actual source-reconciled and private originals remain local.

**Next operation, non-disruptive:**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p3-stage-c-operator.sh --plan
```
Require `status=READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL`, empty issues, active Flash-Next expected model and original preserved 27B target, P1 post-B evidence PASS, fresh plan SHA and expiry. This must be rechecked because the benchmark verifier does not query current live service.

**DO NOT auto-execute Stage C.** When operator separately and explicitly approves stopping the live Flash API on :8000, `bash scripts/temporary/p3-stage-c-operator.sh --execute` prompts for 3 independently typed literals: NEW SHA **with no brackets**, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, and `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Any stale/changed plan or issue blocks; canonical Wizard alone owns Docker and rollback; final success requires actual live 27B identity and immutable C receipt. Prior C attempt was cancelled before dispatch; no C state or running model change was established by this new benchmark verification log. Do not merge PR #1, delete caches/models/containers, reuse old SHA, or perform unattended downtime.

---

## 2026-11-07 — APPROVAL PROMPT FIX AFTER REAL BRACKETED INPUT

New C operator `confirm()` now displays `Paste exactly <current 64-char SHA> (no brackets; Enter cancels):`, with explicit warning against `[` or `]`. The real previous `[<sha>` submission safely returned CANCELLED/dispatched=false and is NOT a switch. When operator *separately* decides to stop Flash-Next, use a NEW fresh plan, then type only the 64 hex chars and both exact independent acknowledgements; no auto approval. This UX change does not change canonical C, service status or model files. Verify original Git-tracked benchmark summaries first with read-only `bash scripts/temporary/verify-published-benchmarks.sh`.

---

## 2026-11-07 — NEXT: VERIFY PUBLISHED BENCHMARK SUMMARIES READ-ONLY, THEN SEPARATELY APPROVED C

1. Confirm latest GitHub branch and CI, then on operator DGX `git pull --ff-only origin feature/recipe-wizard-handoff`. **Do not** restart GPU containers, merge PR or edit/copy original benchmark receipts.
2. Validate both Git-published metric-only summaries against exact original local JSON with `bash scripts/temporary/verify-published-benchmarks.sh`. Expected TWO `VERIFIED` JSON records and final confirmation. If mismatch, STOP and compare allowlisted fields; do not overwrite source or hide discrepancy. This check is read-only and independent of P3-C.
3. For future bench publications: `python3 -m scripts.manager.benchmark_publication --model <flash-next|27b> --source <private-original-json> --plan`, then operator-review summary (no paths/keys/requests/responses), use hash-approved `--write --approve-sha256 <actual source SHA>` to create **local** untracked Git-ready record, manually review before Git add/commit/push. Never auto-publish private evidence.
4. P3-C prior `--execute` was CANCELLED **before dispatch** because typed SHA included a leading bracket; current observed model Flash-Next, Stage-C NOT_RUN. At separate explicit operator decision, re-run `bash scripts/temporary/p3-stage-c-operator.sh --plan` for fresh status then `--execute` only if accepting live Flash downtime and independently typing the full new SHA **without brackets**, `I_ACCEPT_FLASH_NEXT_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Expired old SHA must never be reused. Do not run Stage A/B or P1 benchmarks again.

Documentation and sanitized entries: `benchmarks/published/README.md`. Original telemetry still stored locally in `~/.local/state/blazux-wizard/`. No model deletion, no automatic Git commit of new future runs, no P3-C execution in source work.

---

## 2026-11-07 — NEXT OPERATOR: FAST-FORWARD PULL + TRACKED STAGE-C PLAN, THEN SEPARATE ACTUAL DOWNTIME CONSENT

Operator has already shown **canonical** `./wizard.sh switch flash-next-27b stage-c --plan --json` READY/issues=[]/P1 gate PASS on actual DGX. Do NOT demand another P1 benchmark/diagnostic, repeat A/B or optional `evidence migrate`. The optional import was cancelled via input `COPY` and copied **0** files; Stage C does not depend on it.

1. Check latest GitHub source HEAD, PR #1 Draft/Unmerged, CPU tests SUCCESS and fast-forward pull in clean `~/Workspace/llm/blazux-orcarouter`.
2. Run exactly **`bash scripts/temporary/p3-stage-c-operator.sh --plan`**. This is the tracked P3-C wrapper's default read-only live preflight. It never stops services. Confirm `READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL`, `issues=[]`, source current Flash, target original preserved 27B, P1 evidence PASS, `executed=false` and report path.
3. **STOP for separate operator consent to actually stop the live Flash-Next API on port 8000.** Only if the human explicitly approves C downtime, run `bash scripts/temporary/p3-stage-c-operator.sh --execute`. Three new terminal inputs are mandatory: fresh 64 SHA printed in the new plan prompt, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Must be typed manually, never scripted/auto-piped. A/B or historic C SHA invalid. Expiry/changed live service blocks before core.
4. Wrapper invokes canonical Wizard stage C with exact SHA + downtime ack (NO `--enter-p3` since canonical C requires null), which exclusively owns Docker, original Flash preservation and rollback. Stage C succeeds only if canonical `stage-c.json` and independent 27B live API on :8000 both verified, yielding `P3_C_PASS_FINAL_27B_ACTIVE`. No switch-back after success.
5. If BLOCKED/OPERATOR_REVIEW_REQUIRED/RECOVERY_FAILED, **STOP**, collect appended operator report and original P3 journal/status; no blind retry, no deleting attempt markers/locks/old containers. Do not merge Draft PR, prune caches or start extra models.

[Stage-C controller runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md). Latest real source observations are **read-only only**; C service transfer itself has not yet run.

---

## 2026-11-07 — NEXT DGX OPERATOR READ-ONLY HISTORY AND P3-C PLAN (NO TRANSITION)

1. Confirm latest branch HEAD / GitHub CPU CI; `git pull --ff-only origin feature/recipe-wizard-handoff`. Do not merge PR #1, delete models, or restart/stop any service.
2. In `./wizard.sh` select NVIDIA Flash-Next or NVIDIA 27B → option **4 Past Verify / Benchmark / transitions**, read-only. Or `./wizard.sh evidence list --model flash-next --kind benchmark` and `--model 27b --kind benchmark`. Validate original 2026-11-06 metrics and both A/B transitions visible without GPU activity.
3. Optional separate evidence COPY step: `./wizard.sh evidence migrate --plan` first; if READY with no issues, `./wizard.sh evidence migrate --guided` and type current literal SHA. This copies only JSON report snapshots into Git-ignored project `reports/`, no legacy state/lock/journal relocation. Operator approval is separate; do NOT preapprove the copy.
4. **P3-C NOW THE NEXT POTENTIAL GPU OPERATION** (not dependent on doing optional copy): on same updated DGX run `./wizard.sh switch flash-next-27b stage-c --plan --json` **ONLY**. Report `status`, `issues`, `p1_evidence.status`, `source_model`, `target_model` and current observed IDs. If BLOCKED, STOP. If READY with current exact SHA and valid P1 gate, require a separately scoped decision/Flash-Next downtime approval before building/running C guided operator procedure. P3-C has **not** been authorized or executed.
5. Only after independently approved C may original Flash be stopped and original preserved 27B started on :8000 with actual API identity verification; preserve all HF assets, Flash image and rollback container. No automatic restore on successful final 27B.
   
Source contract: [model history/migration](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md). Actual post-B P1 Verify+Benchmark already PASS; do not repeat inference merely because history or copy code changed. P2/P3 future writer redirection and control-state relocation require separate design/test and are **not** part of this source PR.

---

## 2026-11-07 — CURRENT: P1 VERIFY + BENCHMARK ACTUAL PASS; UX CI + OPERATOR RECHECK

Supersedes previous "P1 POST-B audit then Verify/Benchmark NOT_RUN" instructions. The operator provided immutable actual DGX evidence: original Flash-Next still active and served on :8000, two post-B diagnostics PASS for expected original-own-port rc3; Verify baseline/extended + all probes PASS and separately approved 3-request Benchmark PASS with **37.9527 tok/s, TTFT p50/p95 1.384594/1.779602 sec, latency p50/p95 1.724560/1.813754 sec**. Both original receipts reside under OLD `~/.local/state/blazux-wizard/p1/` and MUST NOT be moved, overwritten or deleted. Source updated to show P3-style exact SHA prompts, remove duplicate action entry, display numeric metrics, use new Git-ignored project-local `reports/models/qwen3.8-flash-next/` for **future** evidence, and dual-read old/new for P3-C evidence qualification.

**Next:** confirm fresh GitHub HEAD + BOTH CI checks (including new operator-UX tests) and Draft PR #1, then operator may `git pull --ff-only origin feature/recipe-wizard-handoff` and inspect the new Wizard UX. No additional real Verify/Benchmark inference is implied by an interface change; an actual re-run would require fresh distinct operator approvals. P3-C downtime/transition remains **separately NOT_AUTHORIZED**, even if the evidence prerequisite checker is now PASS. Never merge PR, clean models or restart/switch services automatically. See [UX/evidence contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

## 2026-11-07 — READY FOR OPERATOR READ-ONLY CHECK (SOURCE CI PASS)

The targeted source audit and P3-B operator metadata fix are implemented; latest source-tested `67ff9cc2e4ece0c89c911513673f7d5d55c98fa4` passed [GitHub CPU CI 42310408411](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42310408411): **501/501 PASS / 23 groups**. PR #1 has a review COMMENT (ID `5808289782`) and remains Draft/Unmerged. No new GPU/DGX execution. After checking the latest HEAD/CI and a clean DGX fast-forward pull, the ONE authorized next read-only action is `bash scripts/temporary/p1-post-b-audit.sh`. PASS with raw own Flash collision evidence is diagnostic readiness only; subsequent P1 Verify and Benchmark need individual approvals. P3-C NOT_AUTHORIZED.

---

## 2026-11-07 — POST-B P1 READ-ONLY AUDIT NEXT; P3-B ACTUAL PASS (supersedes old B execution TODO)

**Completed in actual operator DGX output:** P3-B stage B `P3_B_PASS_FLASH_NEXT_ACTIVE`, canonical `stage-b.json`, original Flash restored and served `qwen3.8-flash-next`, post-B `p1-post-download.sh --inspect-only` preflight PASS/Verify+Benchmark plans READY. P3-A/B must NOT be repeated. Old P3-B operator report was misnamed `p3-a-operator-20261106T223124Z-14861d75.json`; preserve as original evidence.

**Next operator step only AFTER new GitHub CPU CI PASS** (D-016): clean branch and `git pull --ff-only origin feature/recipe-wizard-handoff` in `~/Workspace/llm/blazux-orcarouter`, then run exactly **`bash scripts/temporary/p1-post-b-audit.sh`**. This is source/API/read-only preflight and doctor/inventory RAW rc3 diagnosis: NO GPU inference, benchmark, Docker start/stop or P3-C. New private `~/.local/state/blazux-wizard/p3/p1-diagnostics-<UTC>-<nonce>.json` is append-only, `0600`; existing evidence never overwritten.

**Expected:** `status=PASS`, `issues=[]`, `doctor_exit_code=3`, `inventory_plan_exit_code=3`, `post_b_verify=NOT_RUN`, `post_b_benchmark=NOT_RUN`, `p3_c_authorized=false`. If `BLOCKED`, retain report and stop; do not infer benign collision from exit 3 alone, repeat P3 stages or auto-enter GPU tests. Historical successful P1 numeric results cannot substitute for new post-B samples.

**After successful new diagnostics:** independently propose/obtain new action-specific P1 Verify plan ID and operator approval; after actual successful Verify, separately approve new numeric P1 Benchmark (at least 3 samples, `requests=3,max_tokens=64,seed=1234,concurrency=1` when supported). Only with verified immutable post-B receipts, metrics, timestamps, same Flash revision/image and fresh evidence gate PASS is P3-C eligible for **its own explicit downtime approval**. Do not supply P3-C execute commands earlier.

---

## 2026-11-06 — User approved ONE P3-B shutdown/return; execute only with fresh exact interactive B gates

- [x] Operator separately answered **"승인"** to explicitly scoped P3-B **NVIDIA 27B downtime → preserved Flash-Next restoration** question after actual B-read-only PASS; D-041 records this approval. Original P3-A approval alone was not used.
- [x] Latest tracked P3-B execution wrapper `scripts/temporary/p3-stage-b-operator.sh` is source and CPU CI PASS (489 tests), current branch HEAD at permission check `2f914242ae98ef678477386e1a26b1d6668d717e`. Distinct B exact ACKs required: `I_ACCEPT_27B_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_P3_STAGE_B` and a freshly generated full B plan SHA. CI does not prove any live runtime execution.
- [ ] Operator DGX `git pull --ff-only origin feature/recipe-wizard-handoff`, then **one** `bash scripts/temporary/p3-stage-b-operator.sh --execute`; read current source=27b, target=flash-next and exact immutable container/image. Type all three currently displayed strings, do not reuse expired 17:50 inspection SHA. Port :8000 will experience downtime; on BLOCKED/RECOVERY_FAILED/OPERATOR_REVIEW_REQUIRED stop and report evidence, never retry blindly.
- [ ] After actual `P3_B_PASS_FLASH_NEXT_ACTIVE` and `LIVE_SERVICE_VERIFIED` for `qwen3.8-flash-next`, stop at B. D-034 requires **new post-B P1 Verify + measured Benchmark + rc3 diagnosis** under independent action-specific approval and evidence, then independently authorize C final 27B; no hidden chain.

---

## 2026-11-06 — P3-B DGX preflight PASS; require explicit NEW permission before any live 27B shutdown

- [x] Actual DGX tracked B inspector HEAD `e5d4171`: `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, active API `qwen3.8-27b`, source CID `6d9ede...`, preserved original Flash CID `90f39...`, actual A/P2 provenance complete. Evidence `~/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. `executed=false`, `approval_accepted=false`, no 27B interruption. Old inspection-only plan `7af40f...` expired Nov 6 17:50 KST and must not be reused.
- [x] Stage-B source guard formerly demanded `I_ACCEPT_FLASH_NEXT_DOWNTIME`, semantically wrong for **27B stop**. Updated canonical Wizard core to `I_ACCEPT_27B_DOWNTIME` + independently typed `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`; A/C contracts unchanged. **Source change, no execution.**
- [x] D-016 GitHub tracked `scripts/temporary/p3-stage-b-operator.sh` / Python and CPU fake-DGX tests: default read-only; `--execute` only after separate user scope permission, checks current live 27B + exact A receipts + immutable original Flash + short-lived B plan, separately asks current full SHA, new 27B downtime and B-entry strings; refuses expiry/changed plan before calling guarded Wizard, verifies returned Flash API, records private evidence and NEVER auto-runs P1/C. [489/489 CPU CI PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) on source `59046c4e17a5094f2c80a84025a763c2a767edcb`.
- [ ] Obtain **user's explicit P3-B 27B→Flash-Next downtime approval**. The B inspector PASS and P3-A typed approvals are **not** this approval. Until then leave 27B service live; no `--execute` and no spontaneous P1 test.
- [ ] Only if separately authorized, D-016 fast-forward pull after CI followed by `bash scripts/temporary/p3-stage-b-operator.sh --execute` with user independently typing current printed full B SHA, `I_ACCEPT_27B_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`. Don't replay old B inspection SHA. Report `P3_B_PASS_FLASH_NEXT_ACTIVE` and original preserved Flash container restored; on BLOCKED/RECOVERY_FAILED STOP, do not retry. Never auto-start stage C.
- [ ] D-034 after B PASS: collect fresh functional P1 verify+measured benchmark with individual plans/approvals and rc3 diagnosis after B, then independently approve C final 27B. Preserve original image/cache/containers, API :8000 and unmerged Draft PR.

---

## 2026-11-06 — P3-A completed on actual DGX; prepare B read-only, require fresh B authorization

- [x] **REAL P3-A SUCCESS:** user ran `p3-stage-a-operator.sh --execute` with a new exact plan SHA `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4` and both individually typed ACKs; Wizard `PASS/executed=true/live_verified=true`, wrapper `P3_A_PASS_27B_ACTIVE` with `issues=[]`, after-switch `LIVE_SERVICE_VERIFIED` and `27b`. Evidence `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json` plus `~/.local/state/blazux-wizard/p3/stage-a.json`. Supersedes prior failed/expired SHA refusal history. No P3-B runtime action.
- [x] Build a D-016 GitHub-tracked **read-only** stage-B inspector `scripts/temporary/p3-stage-b-inspect.sh`, Python, fake-DGX tests, CI. It checks actual successful immutable stage-A receipt, active 27B API, new canonical B-stage plan and preserved original Flash container ID/image with P2 provenance; **no execute mode**.
- [ ] After GitHub-tested source push, DGX user fast-forward pulls and runs **only `bash scripts/temporary/p3-stage-b-inspect.sh`** to collect actual `READY_FOR_SEPARATE_P3_B_APPROVAL` / `BLOCKED` with issues and private evidence. Inspection never stops 27B or starts Flash; keep 27B LIVE.
- [ ] **Separate operator B approval** required after inspecting evidence: no `stage-b --execute` from A approval, no reusing A plan SHA, no automatic downtime. B is 27B→Flash-Next and needs its own fresh plan, independent typed downtime approval, original Flash container preservation and target API verification.
- [ ] Only **after** B PASS, run actual new P1 full functional Verify and numerical Benchmark with explicit individual P1 plans/approvals, plus reviewed rc3 diagnostic evidence newer than B before contemplating P3-C. C final 27B active likewise independently approved. Preserve Draft PR unmerged, checkpoints, original Docker objects and public :8000/v1 contract.

---

## 2026-11-06 — P3-A exact-input UX fixed; previous approved input refused as stale, no transition

- [x] Operator had typed **all three correct** P3-A strings. Wizard returned `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT`, `executed=false`, `approval_accepted=false`; former wrapper displayed ambiguous `OPERATOR_REVIEW_REQUIRED`. Plan expiration `1793950200` was **16:30:00 KST**; report time `16:30:49 KST`. No P3-A Docker stop/start, Flash→27B NOT_RUN. Preserve original Flash.
- [x] Fix tracked `scripts/temporary/p3-stage-a-operator.sh`: terminal prompts now print exact current plan SHA and **both exact ACK strings**, 10-minute plan expiry KST and remaining seconds; stop when <120s remain for input, replan read-only after three typed confirmations and block changed/expired SHA. A Wizard reject with `executed=false` is `BLOCKED`, never false recovery warning. No auto retry/plan swap.
- [x] Fake-DGX tests for old failure, exact prompt literals, short plan window and after-typing SHA change. [Source CI 459/459 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236) on code `fb34ce0ce985824cecd9c63159bf6f1eed408279`.
- [ ] D-016 only: operator DGX clean fast-forward pull then rerun **one** `bash scripts/temporary/p3-stage-a-operator.sh --execute` if still explicitly choosing P3-A downtime. Read actual **NEW** plan SHA printed at prompt; DO NOT reuse the old SHA. Enter three independent typed current literals; cancel on unfamiliar model/image or plan expiry. If `P3_A_NOT_ENOUGH_TIME_FOR_MANUAL_CONFIRMATIONS` then rerun wrapper in a later fresh plan window; do not auto-cycle.
- [ ] Only `P3_A_PASS_27B_ACTIVE` plus independent live model ID and stage A receipt qualifies actual A completion. On `BLOCKED`, `CANCELLED`, `OPERATOR_REVIEW_REQUIRED`, `RECOVERY_FAILED`, STOP and review evidence. D-034 B, post-B P1 rebenchmark, C independently approved and NOT_RUN. No automatic merge/cleanup.

---

## 2026-11-06 — P1 PRE-A proof complete; next P3-A only via D-016 interactive exact-gate wrapper

- [x] Actual operator-reported P1 audit source HEAD `834f823`: `PRE_A_P1_REVIEW_READY`, `issues=[]`, both historical/current expected own-Flash :8000 rc3 collisions, functional Verify PASS, numerical benchmark 3/3 PASS (38.2968 tokens/s, TTFT/latency included), original model/image still active. Evidence: `~/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`. No need to repeat initial P1 GPU benchmark.
- [x] Original operator **conditional** approval (P1 initial work resolved ⇒ 27B transition) is now eligible for **P3-A only**; no blanket GPU/Docker authorization from P1 read-only status itself. D-037 supersedes earlier pre-A hold. P3-A/B/C are not yet executed.
- [x] Add tracked `scripts/temporary/p3-stage-a-operator.sh` and Python helper with default `--plan`, independent `--execute` TTY exact fresh SHA plan, downtime and entry strings, fake-DGX tests, Actions CI and docs; preserves original image/container, does not auto-run B/C.
- [ ] **Only after latest GitHub CPU CI PASS and fast-forward pull**, DGX operator runs `bash scripts/temporary/p3-stage-a-operator.sh --execute` if choosing real P3-A downtime. Review fresh printed `source_model=flash-next`, `target_model=27b`, exact source image/container, immutable P2 receipt; type full fresh plan ID, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_P3_ENTRY` at three prompts. The Wizard rechecks its plan immediately before actual stop/start; any changed state/expired plan cancels without action. This interrupts port :8000 and GPU and may fail to restore on host/Docker outage; P3 source-only pass not a production qualification.
- [ ] Check return `P3_A_PASS_27B_ACTIVE` only with independent manifest/API served `qwen3.8-27b` and local stage-A receipt. On `BLOCKED`, `CANCELLED` or `OPERATOR_REVIEW_REQUIRED`, stop; DO NOT auto retry or run B/C. Report concise summary and evidence path.
- [ ] D-034 next: B 27B→Flash-Next needs separate actual scoped approval; fresh post-B P1 functional+TTFT/tokens/sec benchmark and rc3 reviewed `p1-diagnostics.json`; only then C new separate approval to 27B final active. Keep Draft PR unmerged and don't clean caches.

---

## 2026-11-06 — Fix verified source-report schema error; DGX only reruns tracked P1 audit

- [x] Real DGX first P1 pre-A audit HEAD `3a594193` returned `BLOCKED` **only** for `P1_ASSET_AUDIT_NOT_READY` / `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. All historic/current expected active Flash collision checks, original Verify and 3-sample numerical benchmark, current API ID/image were confirmed; no P3 runtime mutation.
- [x] Root cause in source: `p1_post_download.session` persists raw `checks.cache_diagnosis.stdout`, while console-only short summary prints top-level `cache_diagnosis`. New pre-A script read the wrong place and falsely labeled missing SHA as real `DRIFT`.
- [x] Reuse canonical `cache_diagnosis_summary` to parse real persisted raw JSON; report missing revision as `P1_CURRENT_CHECKPOINT_REVISION_UNAVAILABLE` and actual mismatch only if both concrete SHA values exist. Update tests to match actual report schema and prove malformed/changed/checks fail closed. [Code CI 439/439 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898) on `9adc9ab282a91c02e959dcb5c62f98527b556391`.
- [ ] **Operator DGX:** use D-016: `git pull --ff-only origin feature/recipe-wizard-handoff`, then **single** `bash scripts/temporary/p1-pre-a-readiness.sh`. Provide compact JSON `status`, `issues`, `p1_verify`, `p1_benchmark`, `historical_rc3`, `current_rc3`; script has no GPU inference or live-model mutation.
- [ ] If real `PRE_A_P1_REVIEW_READY` and `issues=[]`, review the operator's earlier conditional P3-A approval and refresh exact stage A plan; **do not execute stage A automatically or reuse expired plan**. Independently check downtime boundary and GPU/process ownership. D-034 post-B P1 retest and separately approved B/C remain mandatory. Keep Draft PR unmerged.

---

## 2026-11-06 — One tracked DGX wrapper after GitHub push/CI (D-016)

- [x] Original P1 numerical benchmark 3/3 PASS evidence supplied, including TTFT/latency/throughput, and 2026-11-06 inspect-only source/Hybrid/API READY; no pre-A rerun of P1 inference needed just to obtain metrics.
- [x] New `scripts/temporary/p1-pre-a-readiness.sh`, Python implementation, fake-DGX tests, workflow shell syntax and docs pushed under `feature/recipe-wizard-handoff`; [source CPU CI 435/435 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) at `75d22ce4303736ee84563a0f388a978379e4f228`.
- [x] Fix P3-C evidence gate and pre-A audit using REAL `identity.health` and `identity.models` output, not nonexistent `identity.status`; historical doctor rc3 raw checks still required and NOT assumed.
- [ ] **DGX operator only after GitHub fast-forward pull**: `bash scripts/temporary/p1-pre-a-readiness.sh` once; review printed `status`, `issues`, `historical_rc3`, `current_rc3`, `p1_verify`, `p1_benchmark` and `evidence_file`. The wrapper reads original P1 local reports and receipts; it does no GPU, inference, Docker lifecycle or model transitions. Do not repeat pasted Python snippets.
- [ ] Only if actual DGX evidence is `PRE_A_P1_REVIEW_READY` with empty issues, consider the operator's conditional pre-A approval and fresh stage A plan / scoped downtime, **without automatic execution**. A blocked result needs targeted diagnosis. Do not claim that pre-A implies production qualification or P3-C readiness.
- [ ] D-034: stage B independently approved, post-B P1 full functional and actual measured rebenchmark plus reviewed historical collision disposition, then independent C to 27B. Keep original service, :8000 and source preserved until authorized.
- [ ] Draft PR #1 stays Open/Unmerged. No auto PR merge or cache cleanup.

---

## 2026-11-06 — Use tracked temporary wrapper, not pasted DGX code (P1 pre-A reconciliation)

- [x] Actual P1 initial benchmark values shared: 3 samples / 192 tokens; latency P50=1.687357s/P95=1.780142s, TTFT P50=1.398707s/P95=1.751198s, mean 38.2968 tokens/sec; no repeat GPU benchmark needed just to obtain these numbers.
- [x] Actual P1 `--inspect-only` report shows source+Hybrid READY, API `qwen3.8-flash-next`, no active transfer, clean Git branch, both verify/benchmark plans READY; `actions.*.status=BLOCKED` because inspection-only is expected and **does not revoke earlier verify/benchmark PASS**.
- [x] Reaffirm D-016: temporary DGX logic goes through tracked `scripts/temporary/p1-pre-a-readiness.sh` → GitHub commit/CPU CI → operator `git pull --ff-only` → one wrapper execution → local private JSON evidence → reviewed handoff. No ad hoc pasted shell/Python code; script never does git pull, GPU tests, Docker mutation or model switch.
- [ ] Operator runs `bash scripts/temporary/p1-pre-a-readiness.sh` **after** CI and clean fast-forward pull. It reconciles historic 2026-11-05 and latest current 2026-11-06 doctor/inventory raw stdout, verifies current Flash image+API and original P1 functional/numeric receipts. If past/current reports are missing, use a new separately approved/read-only inspection report, not fabricated evidence. Return the small JSON.
- [ ] Check whether raw historical doctor/inventory rc3 was only expected own `qwen38-flash` / :8000 occupancy with `status=PASS`, `errors=[]`. If not, diagnose actual read failure and keep P3-A blocked. If pre-A baseline accepted, re-evaluate the operator's **conditional** P3-A downtime approval with a newly generated short-lived plan. No automatic stage execute.
- [ ] Post-B P1 functional verification, **numeric** full benchmark and reviewed diagnostic `p1-diagnostics.json` are still required by D-034 before final stage C. No initial P1 result substitutes for actual post-B proof.
- [ ] Draft PR #1 stays unmerged, Flash-Next host :8000 unchanged, no GPU/daemon mutation and no cleanup.

---

## 2026-11-06 — Conditional switch approval NOT MET; finish read-only P1 evidence review first

- [x] Check actual P1 historical evidence before P3-A: 2026-11-05 `verify=PASS` for baseline+extended completion/chat/tools/vision; `benchmark=PASS` bounded, original Flash source/Hybrid ready.
- [ ] Review actual prior local P1 benchmark JSON under `~/.local/state/blazux-wizard/p1/` and capture numerical TTFT, latency and usage-backed tokens/sec; historical summary had no numbers. **Do not rerun GPU benchmark merely to invent missing evidence.**
- [ ] Inspect actual read-only `doctor`/ `inventory-plan` JSON and earlier raw report, distinguish benign active `qwen38-flash`/port :8000 collision from Docker/socket/disk/cache observation failures. Exit 3 alone is not a fault diagnosis nor proof of benign collision. `bash scripts/temporary/p1-post-download.sh --inspect-only` captures these checks without GPU inference or service mutation; review output before any change.
- [x] Fix incompatible `P3-C` source gate that required both raw launch preflights to exit zero while the original model is already running. Only accept both rc3 under exact raw parsed/no-error same Flash-Next source-image and port ownership conditions. New negative tests forbid missing JSON, errors, wrong image/port or rc0 shortcut. [CI 418/418 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172127412).
- [ ] Treat operator's "**if no P1 outstanding, approve 27B**" as condition **currently NOT met**, NOT authorization for P3-A `--execute` or Flash downtime. No model change, PR merge, or auto progression.
- [ ] Preserve D-034 separate P3 stage A, B, post-B P1 verify/numerical rebenchmark, C order. Any P1 check now cannot replace genuine post-B receipts. Require fresh explicit authorization and current exact P3-A plan after a reviewed safe boundary.
- [ ] Preserve Draft PR, checkpoint/image/container, and :8000; no auto GPU benchmark or file cleanup.

---

## 2026-11-06 — Source hardening/CPU 413 PASS; P3-A runtime requires new explicit approval

- [x] Operator-supplied real DGX `sequence --plan` P2 receipt and P3-A read-only plan READY recorded below, including exact 14:40 KST expiry; **NOT_EXECUTED**.
- [x] Correct stale `sequence --plan` wording: staged source exists but actual DGX switch not qualified. Keep source implemented vs DGX acceptance explicit.
- [x] Add recovery-time foreign GPU-enabled Docker consumer guard (stop/restore collision fails closed) and focused CPU fake-Docker tests.
- [x] CPU 413/413 SUCCESS on tested source commit `02bf94c1628828ce22fa338dd5a8e5a0955f9179`: [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170050031), [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860).
- [ ] **No runtime P3-A action without explicit separately scoped operator downtime approval.** When such approval arrives, regenerate exact unexpired `stage-a --plan` and independently review source/target, :8000 ownership, GPU consumers, recovery readiness; old `79be6bf...` token expires 14:40 KST, never reuse it.
- [ ] After any separately authorized actual A run, verify independent live `qwen3.8-27b` API and complete A receipt before considering B. Stages B and C independently approved; P1 remediation/rebenchmark after verified B remains mandatory.
- [ ] Keep Draft PR unmerged; no unattended DGX operation, host Docker change, source cleanup or port service interruption.

---

## 2026-11-06 — Actual P3-A DGX read-only plan READY; next gate requires explicit downtime approval

- [x] Operator supplied real `./wizard.sh service manager status --json`: Flash-Next `LIVE_SERVICE_VERIFIED` on :8000, exact API ID `qwen3.8-flash-next`, `issues=[]`; **no mutation** and GPU/process exclusivity not independently qualified.
- [x] Operator supplied real `./wizard.sh switch flash-next-27b sequence --plan --json`: P2 successful private receipt SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9` observed, P3 separate-entry `BLOCKED` expected, not a failure.
- [x] Operator supplied real `./wizard.sh switch flash-next-27b stage-a --plan --json`: `READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, source exact ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, plan `79be6bf05cb02306ec9155ade317e06c457238de427417ebab8946e35449247a` expires 2026-11-06 **14:40 KST**. **Do not reuse this plan after expiry.**
- [ ] Request **separate explicit P3-A maintenance-window / downtime authorization**. Only then regenerate a fresh stage-A `--plan` on the actual DGX, independently review exact source/target IDs, foreign GPU consumers, current port ownership, fallback, and approval ID. No generic `continue` counts as authorization.
- [ ] Only after scoped explicit authorization execute stage A and independently verify `qwen3.8-27b` ACTIVE using fresh Manifest/API and stage-A local journal. Pause after A; stage B needs a *new* approval. P1 post-B remediation and final C remain blocked until preceding receipts exist.
- [ ] Do not merge Draft PR, touch model/cache, auto-advance P3 or restart the current service as a side effect of GitHub/docs/source activity.

---

## 2026-11-06 — P3 SOURCE/CPU gates ready; hold at operational approval boundary

- [x] P2 completed and recorded as `BENCH_PASS_RESTORED_VERIFIED`, original Flash-Next restored/verified. Do not run again.
- [x] D-034 source stages A/B/C implemented in `p3_persistent_switch.py`, read-only plans visible in Wizard CLI/TTY; source container restore and journal protections with fake Docker tests.
- [x] Post-B P1 `verify`, measured `benchmark` and historical rc=3 diagnostic proof gate implemented; **no actual P1 remedial evidence yet**, so final C is appropriately ineligible.
- [x] Source CI PASS 411/411 on `27728045907a1f2111dc4b8340fbea2cc365ff1d` ([PR run](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168524464)). Follow-up documentation commits are not additional GPU proof.
- [ ] Evaluate real P3 stage-A read-only `./wizard.sh switch flash-next-27b stage-a --plan --json` on DGX after non-destructive `git status -sb` and `git pull --ff-only`. Collect exact live source, pinned image/target, candidate plan and issue array.
- [ ] **NEW explicit approval needed** before executing A (Flash→27B) during a maintenance window. Separately confirm API ID and observed source/target IDs; do not chain B.
- [ ] Plan and separately approve B (27B→Flash); only after verified B obtain historical doctor/inventory-plan rc=3 root cause records, re-run P1 functional and numerical benchmark with fresh P1 approvals. Keep diagnostic status BLOCKED until reviewed.
- [ ] Only after P1 actual evidence verified, plan and separately approve C (Flash→27B). Verify 27B actually active; preserve Flash-Next and other model source assets.
- [ ] Before considering production release, perform controlled DGX fault-injection checks and validate actual rollback, port/GPU exclusivity and persistence after Docker restart. CI mock success is not enough.
- [ ] Keep PR #1 Draft/unmerged pending explicit merge request and production review. No Orcarouter/cleanup scope.

---

## 2026-11-06 — UPDATED NEXT ACTIONS: P2 COMPLETE; SOURCE-ONLY P3 engineering

- [x] P2 27B bounded **actual DGX** GPU/API/streaming benchmark: `BENCH_PASS_RESTORED_VERIFIED`, 3/3; original Flash-Next `RESTORED` and `LIVE_SERVICE_VERIFIED` (operator-supplied JSON). See EVIDENCE-LEDGER. **Do not rerun P2.**
- [x] P2 STOP boundary enforced; D-034 supersedes old D-033 two-roundtrip plan.
- [ ] Read latest GitHub HEAD/CI and existing manager code. Implement safe **separate P3 staged persistent switching** with per-stage current-state plan, exact scoped approval, fresh observed Docker/API/GPU source, target image/checkpoint/recipe, stop-before-start, port 8000, source-ID preservation, failure restore, append-only evidence and duplicate/stale block. CPU fake-backend tests BEFORE attempting any DGX execution.
- [ ] Integrate P3 phase evidence and **P1 remedial functional + actual rebenchmark evidence gate** into final stage C. Historical P1 doctor/inventory-plan rc=3 remains unexplained and P1 numeric metrics still unprovided; do not assume PASS. Retain existing P1 executor.
- [ ] Commit safe source/tests/docs into existing Draft PR #1, review CI. Keep PR unmerged.
- [ ] **Separate operational approval required** for each P3 transition A/B/C; no `--execute` on live DGX under this documentation/engineering instruction. A must verify 27B live, B Flash-Next live; after P1 remediation/rebench accepted, C must finish on 27B.
- [ ] Preserve original Docker images/containers, both pinned checkpoints, Orcarouter assets and :8000 external API. No deletion, redownload, image rebuild or parallel GPU models.

Earlier P2 checklist blocks below are historical and **superseded** by this completed result; never treat their unchecked P2 benchmark item as a current next action.

---

## 2026-11-06 — P2 then STOP; separate P3 entry; remediate/rebench P1 before final 27B

- [ ] **P2 first**: operator separately approves a new Flash-Next downtime plan; execute actual bounded NVIDIA 27B benchmark, record measured client TTFT/latency/decode/ingest proxies and restored original Flash-Next `LIVE_SERVICE_VERIFIED`; **STOP at P2 regardless of PASS**. No auto P3 plan or execute.
- [ ] Wait for explicit P3 entry authorization. Do not recycle the P2 benchmark plan ID; require fresh live Manifest/API and separate transition plan + approval.
- [ ] In P3, since P2 restores Flash-Next, separately activate 27B and verify `qwen3.8-27b` to establish the source for the next test.
- [ ] Separately switch **27B → Flash-Next**, verify `qwen3.8-flash-next` and preserve original container/rollback evidence.
- [ ] While Flash-Next is active resolve outstanding P1 `doctor/inventory-plan` nonzero reasons, repeat functional probes and **measure real P1 TTFT/latency/tokens/sec** with saved benchmark evidence. If not satisfied, block final transition.
- [ ] With P1 PASS, separately approve and perform final **Flash-Next → 27B**; verify API `qwen3.8-27b` and preserve safe rollback resources, record P3 outcome. **Final target 27B active**, not automatic Flash-Next restore.
- [x] Source-only: retire old P3 two-roundtrip executor, expose new read-only `sequence --plan`; persistent P3 switching executor **NOT IMPLEMENTED**, no new GPU actions.
- [ ] Retain existing Flash-Next API, original images and both caches; keep Draft PR unmerged. No Orcarouter/extra model scope.

---

## 2026-11-06 — Actual DGX P2 plan READY / P3 correctly BLOCKED; next is specifically approved P2 measured run

- [x] Actual DGX read-only `./wizard.sh model 27b benchmark --plan --json` returned `READY_TO_REQUEST_TRIAL_APPROVAL`, `issues=[]`, `executed=false`, correct model/image/source. Returned ID `2f76c3b03865b6a15a5c2fe8f316231f532fbf8b7fe178ffd00db8383edc3399` **expires 2026-11-06 12:20 KST** and must be regenerated.
- [x] Actual DGX read-only `./wizard.sh switch flash-next-27b roundtrip --plan --json` returned `BLOCKED`, `P2_BENCHMARK_RECEIPT_NOT_FOUND`; this is intended until a real P2 benchmark success receipt exists.
- [ ] After separately authorizing a Flash-Next :8000 downtime, create a **fresh** P2 benchmark `./wizard.sh model 27b benchmark --plan --json` and review `status=READY_TO_REQUEST_TRIAL_APPROVAL`, `issues=[]`, exact plan ID. During approved window execute via Wizard with fresh full ID and `I_ACCEPT_FLASH_NEXT_DOWNTIME`. Confirm `BENCH_PASS_RESTORED_VERIFIED`, actual TTFT/throughput proxy metrics, private benchmark evidence and Wizard Flash-Next restore identity before moving on. Any startup/restore failure => do not start P3.
- [ ] ONLY THEN generate the P3 two-cycle roundtrip plan; require separate explicit downtime approval and validated fresh P3 plan. No automatic P3 switching or model re-download.
- [ ] Keep original Flash-Next container, HTTP :8000, PR Draft and model caches untouched by preparatory plan queries.

---

## 2026-11-06 — REFOCUS on P2 actual benchmark and P3 repeated temporary roundtrip

- [x] First actual DGX NVIDIA 27B GPU text smoke and return-to-original `PASS_RESTORED`, plus independent manifest-led Flash-Next `LIVE_SERVICE_VERIFIED`.
- [x] **Source implementation** P2 exact-approved bounded benchmark, 3 sequential 64-token SSE prompts, client TTFT/latency/proxy throughput and point-memory sampling with private evidence, then same-original restore + Wizard check. Distinct approval from first smoke trial.
- [x] **Source implementation** P3 conditional two-cycle temporary roundtrip plan/executor, blocked absent successful current P2 `*.benchmark.json`; each cycle uses same original-recovery protections; two-cycle run does not qualify permanent switching.
- [ ] DGX **read-only**: `git status -sb` and `git pull --ff-only origin feature/recipe-wizard-handoff`; `./wizard.sh model 27b benchmark --plan --json`. Record status/plan parameters/issues. If BLOCKED, debug before requesting downtime; no repeated source-only import checks.
- [ ] When explicitly approved, run real P2 benchmark during maintenance with exact live plan and typed downtime acknowledgment. Share measured JSON/status; confirm `BENCH_PASS_RESTORED_VERIFIED`, metrics, original API, source ID and real `*.benchmark.json`. **No approval inferred from this handoff.**
- [ ] **Only after P2 DGX benchmark PASS**, read-only `./wizard.sh switch flash-next-27b roundtrip --plan --json`. Then separately obtain full P3 two-cycle downtime approval and test both cycles; record original-container and API identity after each.
- [ ] Full permanent Flash-Next ↔ 27B service switch, extended performance/profiles, abnormal-path fault recovery and rollback remain independently gated. Orcarouter work remains for P5, not current scope.
- [ ] Keep Draft PR #1 unmerged, original Flash-Next container and API :8000 intact until scoped actual test.

---

## 2026-11-06 — After real installed model inventory: preserve Orcarouter, advance P2 benchmarks

- [x] DGX ran `./wizard.sh model list --installed --json` and returned `READ_ONLY_INVENTORY`, `executed=false`; source snapshots Flash-Next **11/11**, NVIDIA 27B **3/3**, Orcarouter **17/17** with zero missing indexed shards.
- [x] **Actual legacy Orcarouter assets are preserved** at previous YSLAB HF cache revision `3a3b63161c0745390e5270179af42e46efc70799`; matching historical `orca-uncensored-bf16-mtp/ee5b6b553f1226d2` recipe directory observed. **No model removal or redownload needed** for source discovery; no GPU/recipe qualification yet.
- [x] Current Flash-Next API confirmed by manifest-led live status (`LIVE_SERVICE_VERIFIED`); 27B remains inactive after prior `PASS_RESTORED` first GPU trial.
- [ ] **Read-only future Orcarouter qualification:** inspect legacy recipe directory's exact manifests, referenced files, symlinks and model provenance without moving/modifying legacy files; distinguish original NVFP4 cache versus BF16 PLE recipe view and avoid claiming ready based on directory presence.
- [ ] Continue **P2 27B benchmark** in a separately approved, bounded GPU maintenance window with strict stop→test→restore; measure TTFT, prefill/decode tokens/s, memory and functional behavior. Never silently restart 27B based on file availability.
- [ ] P3 repeated Flash-Next ↔ 27B transition, P5 Orcarouter run/benchmark and P6 Orcarouter ↔ 27B transitions remain separately gated. Keep production service, legacy model caches, and 4 unregistered snapshots untouched.

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

## 2026-11-06 — After real GPU PASS_RESTORED: check live status ONLY through Manifest Wizard

- [x] Real DGX NVIDIA Qwen3.8-27B ModelOpt GPU startup, API ready and one bounded inference **PASS**. Normal-path original Flash-Next return `RESTORED`, issues=[]; overall `PASS_RESTORED`. Private evidence file `/home/inlc/.local/state/blazux-wizard/p2/20261105T230229Z-a4fc14cf8079.json` (not read independently). Never confuse normal restore with exceptional rollback tests.
- [x] Create unified read-only Manifest + API Wizard service status. `./wizard.sh service manager status --json` combines actual Docker/socket, `runtimes/service-policy.json`, expected exact `/v1/models` served ID, and `/health`. Keep `inventory`, `health` and `logs` distinct diagnostics; all read-only, no activation.
- [ ] Operator on DGX: `git status -sb`, `git pull --ff-only origin feature/recipe-wizard-handoff`, `./wizard.sh service manager status --json`. Confirm `status=LIVE_SERVICE_VERIFIED`, `observed_model=flash-next`, `expected_served_id=qwen3.8-flash-next`, all `checks` true and `issues=[]`. If BLOCKED, provide JSON and investigate, never silently bypass. No raw Docker/curl as main user workflow.
- [ ] Design P2 functional and timed benchmark probes that run **while Qwen3.8-27B is temporarily serving**, capturing real TTFT, prefill/decode tokens/sec, peak memory and short/mid context behavior. Keep one-model GPU policy and mandatory original Flash-Next restore; require **new** explicit interruption approval for another GPU trial.
- [ ] Then qualify repeated Flash-Next ↔ 27B permanent switching, transition journal + rollback, and separately Orcarouter. No unstated production model switch or PR merge.
- [ ] Record new status command's actual DGX JSON and benchmark results in evidence ledger/hand-off as separate fresh observations.

---

## 2026-11-06 — One-shot actual NVIDIA 27B trial next; explicit operator outage approval required

- [x] DGX CPU-only Qwen3.8 internal Qwen3_5 loader/ModelOpt registry checks **9/9 true, issues=[]**, `modelopt_mixed` registered. No GPU/weights tested.
- [x] Deliver exact-approved **temporary** 27B GPU trial with original Flash-Next rollback. 354/354 CPU regression tests PASS at source commit `ea28b0c0`. No model switch or running service change yet.
- [ ] Operator updates clean branch then runs `./scripts/serve_27b.sh --trial-plan` (read-only). Verify `status=READY_TO_REQUEST_TRIAL_APPROVAL`, original container ID and local pinned image identity, other GPU containers absent. If `BLOCKED`, investigate and **do not bypass**.
- [ ] **Only during approved maintenance interruption**, operator may opt into `./scripts/serve_27b.sh --trial-execute --approve-plan FULL_64_HEX_SHA --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME`. This directly interrupts live Flash-Next :8000 and can cause an outage if rollback fails. No approval implied by CPU PASS, user preference to try soon, or earlier download permission. Keep terminal attached; do not use `nohup` or background execution. The exact plan expires within 10 minutes.
- [ ] Record local trial JSON and bounded target log paths (no raw logs uploaded automatically). Distinguish trial API PASS, inference PASS, restored Flash-Next API PASS. If `RECOVERY_FAILED`, **do not start old while new GPU container may still run**; manually inspect Docker and GPU ownership.
- [ ] Based on first GPU error, adjust ModelOpt/GB10 kernel image separately if needed; do not introduce Unsloth compressed-tensors flags into official NVIDIA ModelOpt checkpoint. Future MTP, long context and production switching remain distinct follow-ups.

---

## 2026-11-06 — Re-run corrected 27B registry name audit (minimal next DGX step)

- [x] Initial DGX isolated CPU import passed module/class presence (five checks). `modelopt_mixed` check initially reported TypeError due to incorrect class-level call to `get_name(self)`; not evidence the model cannot run.
- [x] Correct `p2_27b_loader_import_audit.py` to use public `get_quantization_config("modelopt_mixed")` registry/class-identity resolution without instantiating a quant config; source CI `0a14f189`, 336/336 PASS.
- [ ] Clean fast-forward DGX to latest `feature/recipe-wizard-handoff`, execute `./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only` and capture full JSON. Expected keys `quant_registry_module_imported`, `quant_registry_factory_present`, `modelopt_mixed_registry_class_matches`, `modelopt_mixed_cli_name`. A future PASS is a CPU import/registry PASS only, **not** GPU qualification. If registry wrong, investigate actual installed image rather than guessing flags.
- [ ] Confirm true runtime CUDA/C++ extension and loader in an **independently approved** GPU plan before service stop/27B model load; preserve the live original Flash-Next and single :8000 service.
- [ ] Keep Draft PR #1, no merge, no start/switch, no manual execution of `command_preview`.

---

## 2026-11-06 — Next controlled 27B loader import evidence after successful DGX serve split

- [x] DGX ran both dedicated entrypoint `./scripts/serve_27b.sh --status` and `--plan` after fast-forward to `99dde4c`; correct read-only outputs, no 27B start or service modification. Existing Flash-Next `qwen38-flash` API identity **confirmed**, original image ID equals candidate 27B local image ID, and ModelOpt source mix is 208 FP8 + 193 NVFP4.
- [x] Implement isolated CPU-only import probe `p2-27b-loader-import-audit.sh` and 8 unit regressions; source `834c750` CI 333/333 PASS.
- [ ] DGX: after clean `git status -sb` and `git pull --ff-only origin feature/recipe-wizard-handoff`, execute `./scripts/temporary/p2-27b-loader-import-audit.sh --plan`. Optional separately opted-in CPU container `--execute-cpu-only` may test installed vLLM Qwen3.5 and ModelOpt import/class/name with 2GiB/2CPU/no network/GPU/cache/ports. Report structured JSON only. A restricted CPU sandbox import failure is **not** a GPU incompatibility verdict.
- [ ] Reconcile actual ModelOpt name/import facts with candidate `--quantization modelopt_mixed`; verify 27B image provenance, vLLM real loader and GB10 kernels, memory/context and original Flash-Next restore before any approved GPU transition. Keep P2 startup, service stop/switch and rollback blocked until scoped approval.
- [ ] Keep Draft PR #1 unmerged. Do not execute `command_preview` by hand; no duplicate active inference models.

---

## 2026-11-06 — Model-specific serving scripts delivered

- [x] Split legacy `scripts/serve.sh` into default-compatible dispatcher + `scripts/serve_flash-next.sh` (existing executable) + `scripts/serve_27b.sh` (read-only plan/status). `./flash serve` explicitly uses Flash-Next file.
- [x] Preserve old startup behavior/test fixtures and add 10 new CPU tests covering permissions, shell syntax, dispatcher, direct Flash-Next invocation, NVIDIA 27B environment override rejection and absence of a 27B start bypass. CI `67a54afc`: 325/325 PASS.
- [ ] After clean `git pull --ff-only`, operator may run **only read-only 27B** `./scripts/serve_27b.sh --plan` or `--status`; this returns `status=BLOCKED` even when metadata/source PASS. Avoid running `scripts/serve.sh` or `./flash serve` without realizing those default to an actual Flash-Next start, and **do not manually run the returned command_preview**.
- [ ] Review actual P2 source image provenance, ModelOpt vLLM/GPU import/weight load, 27B memory/context, original Flash-Next recovery/rollback, approved DGX transition scope; only then implement a guarded executable `serve_27b.sh` backend with complete start/wait/verify/benchmark and safe recovery.
- [ ] Preserve single active GPU model and `:8000/v1`. Keep PR #1 Draft until evidence/approval gates pass.

---

## 2026-11-06 — P2 dedicated 27B launch preview; GPU acceptance still blocked

- [x] Actual pinned DGX quant audit: modelopt `MIXED_PRECISION`, FP8 **208**, NVFP4 **193**, total **401**, no metadata issues.
- [x] Actual installed image AST audit: **4/4 checks true**, `SOURCE_SURFACES_PRESENT_UNQUALIFIED`; no GPU model load or kernels tested.
- [x] Build dedicated 27B **start-preview** with exact snapshot SHA, local image ID, `modelopt_mixed`, conservative initial GPU settings, no Flash-Next-specific PLE/MTP, source container image and local API identity audit. Source-only `ae4490d6` CI **315/315 PASS**. Does not enable `start --execute`.
- [ ] After clean fast-forward, run `./wizard.sh model 27b plan --for-action start --launch-preview --json` on DGX. This reads local Docker and `/health` plus `/v1/models` on existing `127.0.0.1:8000`, not a GPU model inference request; compare returned original container image and served API ID. Report `issues` and `observed_source`. **Do not run `command_preview`**.
- [ ] Verify runtime vLLM 0.32 CLI `modelopt_mixed`, quant loader import/GPU kernels, VRAM/context 8192/SSM dtype, image provenance/pinned-recipe acceptance, verified Flash-Next recovery before enabling an executable P2 transaction. Keep per-action source identity and explicit approval ID, revalidate immediately before any future stop/start.
- [ ] Only with separately approved DGX GPU/port 8000 maintenance window: stop old, verify port and GPU freed, start isolated 27B, wait, test exact API ID/text/tools/vision + bounded benchmark and restore on failure. Keep PR #1 Draft until those tests pass.

---

## 2026-11-06 — P2 CPU-source qualification next operator evidence

- [x] Add immutable-source ModelOpt layer-algorithm auditor and integrate `quantization_audit` in Wizard; CI `cd63f25` 303/303 CPU PASS.
- [ ] With checkout clean, `git pull --ff-only origin feature/recipe-wizard-handoff`, then rerun `./wizard.sh model 27b status --inspect-runtime --json` and review `quantization_audit` actual pinned local values; do not load model or stop Flash-Next.
- [ ] Inspect local image source with `./scripts/temporary/p2-27b-image-audit.sh --plan`, then explicit `--execute-cpu-only` for isolated runc source AST checks (CPU-only temporary container). Return JSON without secrets; this is NOT GPU model loading.
- [ ] Reconcile ModelOpt per-layer algorithm set against actual installed vLLM registry/loader. Only then design/qualify 27B-specific pinned launcher, image ID vs registry digest, memory/context profile and start/wait/verify/benchmark; no reuse of Flash-Next PLE/MTP defaults.
- [ ] Operational GPU/start/switch/rollback requires separate scoped approval and verified original Flash-Next recovery assets. Keep PR #1 Draft.

---

## 2026-11-06 — Actual image source audit for 27B next

- [x] Operator DGX actual `status --inspect-runtime` confirms NVIDIA pinned 27B source, correct architecture/modelopt/context, ARM64/Linux v0.32 local image ID and protected live Flash-Next.
- [x] Add bounded installed-image source AST auditor and explicit no-GPU/no-network temporary Docker wrapper, plus eight CPU unit tests. `acf5d64` CI: 294/294 PASS.
- [ ] **DGX read-only follow-up:** after `git status -sb` and clean `git pull --ff-only`, run `./scripts/temporary/p2-27b-image-audit.sh --plan`; review, then `./scripts/temporary/p2-27b-image-audit.sh --execute-cpu-only`. This transient runc container does not use GPU, host port or inference service. Return JSON, especially registry/modelopt checks and blocker messages.
- [ ] Audit exact `hf_quant_config.json`, mixed FP8/NVFP4 per-layer support and pinned snapshot tokenizer, verify executable image registry and real memory budget; do not confuse static source presence with GPU loading.
- [ ] Finish isolated 27B launcher/recipe and bounded P2 lifecycle executor with immutable image identification, transaction approval and full original Flash-Next restore. Actual 27B start and `:8000` switchover require a *separate* explicit user-approved transition window; until then no operation may touch inference service/GPU.
- [ ] Run GPU/model/API/benchmark/rollback acceptance only with approved DGX plan. PR #1 stays Draft.

---

## 2026-11-06 — NVIDIA 27B source downloaded; runtime qualification pending

- [x] Record user-provided DGX NVIDIA pinned download 19/19, exit 0, `SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, with exact evidence path; prior transfer-in-progress checklist is historical.
- [x] Implement source-only read-only `status --inspect-runtime` audit of exact source revision, model config, Docker image/platform/label and current service, with CPU fault tests. No GPU allocation, service stop or auto approval.
- [ ] After clean `git pull --ff-only` (download has completed), operator may run `./wizard.sh model 27b status --inspect-runtime --json` and return sanitized JSON, to ground actual cache/config/image/service assertions. Do not launch 27B.
- [ ] Inspect exact pinned config / hf_quant_config and vLLM 0.32 model registry+ModelOpt loader in image, ARM64 support, memory budget and validated image digest. Complete a 27B-specific non-Flash serve recipe and guarded start/wait/verify/benchmark adapter.
- [ ] Obtain a separate exact plan approval before any Flash-Next stop, 27B GPU start or P3 cutover. Preserve and verify rollback source, health and `:8000` API identity.
- [ ] After source CPU/CI, verify actual runtime in approved DGX window, including failures, latency/TTFT/TPS, model identity and rollback. Keep PR #1 Draft until end-to-end acceptance.

---## 2026-11-06 — full Wizard SOURCE / incremental P2–P7 debug

- [x] Build complete model-first TTY menu and machine workflow/roadmap, expose all ten model lifecycle actions for Flash-Next/NVIDIA 27B/Orcarouter.
- [x] Build service menu for status/health/bounded logs and guarded start/stop/restart/rollback/proxy/gateway; P3/P4/P6/P7 advanced plan actions and readiness dashboard are accessible.
- [x] Preserve P1 exact approval and 27B pinned downloader; block P1 guided when another inference model is active or service inventory unknown; add regression.
- [x] Add no-Docker/no-GPU CPU matrix to GitHub CI and update docs/decisions/handoff. Check final HEAD test counts and Draft PR #1 status.
- [ ] While operator-owned 27B download remains active, leave DGX checkout, qwen38-27b-dl, source image/cache and Flash-Next :8000 untouched; **do not ask git pull while downloading**. On completion, obtain exact return code/evidence, then review `./wizard.sh model 27b status --inspect-cache --expected-revision 482ca0f3832238542f8f5295dde86b5f22711d80 --json`.
- [ ] Begin real P2 runtime adapter qualification on source/CPU (vLLM 0.32 single GB10 ARM64, ModelOpt NVFP4, image digest, PLE/MTP) before any live GPU trial; model conversion/stop/switch requires separate approval.
- [ ] Implement/start fault-injected service transaction and symmetric rollback when approved; P3 bidirectional proof, P4 optional no-deletion default, Orcarouter adapter from reviewed parallel branch, P6 switch, P7 acceptance. Keep shared host API 8000.

## 2026-11-05 — after model-first Batch A/source-only B

- [x] Implement root model selection, read-only lifecycle plans and in-flight download suppression, preserving P1 and existing CLI.
- [x] Add bounded GET-only service health/model identity observer and preview-only atomic stop/port-free/start/verify/rollback order.
- [x] Add mock CPU tests and workflow coverage for model cases, API failures and transition gates.
- [ ] At completion of **operator-owned** NVIDIA download, collect return code, `~/.local/state/blazux-wizard/p2/evidence/*.json` path and exact pinned cache inspection before calling P2 downloaded; do not touch current DGX worktree during transfer.
- [ ] Next source batch: validate NVIDIA 27B vLLM 0.32 ARM64/GB10 loader+image, build start/wait/verify/bench adapter and real manifest-based service handover with scoped approval and recovery; do not enable live switching from preview alone.
- [ ] On user-approved DGX validation window after receipt, verify model start/rollback and 27B API/bench; keep Flash-Next model weights/image intact.

## 2026-11-05 — model-first unified Wizard source continuation

- [x] Record accepted D-020 UX design and source/acceptance gates; retain Flash-Next P1 backend.
- [x] Implement root 3-choice menu and read-only `select MODEL --json`; model plans for active, missing, in-flight, source-only, unknown and Orcarouter cases. Show only the relevant downloader or existing P1 guided backend behind explicit separate prompts.
- [x] Expose `qwen38-27b-dl` live container state in observed service manifest; suppress second download; add Orcarouter registry placeholder with no launch permission.
- [x] Add CPU regression matrix and GitHub CI job; preserve all legacy P1–P7 command routes and destructive refusal behavior.
- [ ] **Operator-owned DGX transfer still in progress at last evidence (`16/19` files).** Do not pull updates, restart Flash-Next, interrupt/alter download or run a second transfer. After download exits, collect Wizard receipt/evidence first and only then update DGX checkout.
- [ ] Batch B: actual /v1/models + GPU observation, bounded health/logs, immutable recipe/runtime qualification, and source-only stop→free :8000→start→verify→rollback transition plans with fault injection tests.
- [ ] Batch C: separately approve a live DGX service handover window; validate 27B vLLM 0.32 image/loader/ARM64 before any GPU start. Keep Orcarouter separate branch unmodified.

## P2 download approval unblock (2026-11-05)

- [x] Diagnose user-reported exact approval rejected by mutable preflight fingerprint; fix hash scope to stable safety fields. All storage/Docker/inode preconditions still rerun under download lock.
- [x] CPU regressions for lock inode creation, uptime/free-space drift, actual approved execution, low disk rejection, and service/image identity change requiring reapproval.
- [ ] Check final-HEAD GitHub Actions and PR. On DGX operator's next run: `git pull --ff-only origin feature/recipe-wizard-handoff`, then `./wizard.sh model 27b download --guided` and input the **new** full plan ID. Never reuse pre-fix ID `b190c936...`. Report evidence path / any new blockers.
- [ ] Actual NVIDIA 27B full checkpoint receipt and verification remains `NOT_RUN` until the operator reports results; single model at host `:8000` policy unchanged.

## P2 immediate operator download and parallel source development (2026-11-05)

- [x] Confirm NVIDIA exact model revision `482ca0f3832238542f8f5295dde86b5f22711d80` from authoritative source and add immutable SHA to invalid (not runtime-qualified) recipe.
- [x] Implement guarded Wizard `download --guided` and `download --execute --approve-plan` with no GPU and no API/Docker service mutation; add mock CPU tests and pinned-without-refs audit.
- [x] Commit one-GPU-model/host `:8000` service policy, read-only live manifest and generation-checked transition journal primitives.
- [ ] After latest CI PASS, **operator**: `git pull --ff-only`, then `./wizard.sh model 27b download --guided`. If plan BLOCKED (capacity/image/cache/name/transfer), return the exact issues; do not force the download or delete Flash-Next. Download is **NOT_RUN** until actual DGX evidence is returned.
- [ ] While 27B downloads, implement tested service-switch executor (stop Flash-Next, verify port release, start 27B at :8000, API verify and rollback); preserve original Flash-Next and require separately approved live transition.
- [ ] Qualify vLLM 0.32 ModelOpt loader and single GB10/ARM64 compatibility, then Wizard wait/verify/benchmark and P2 runtime acceptance.

## P2 NVIDIA acquisition and service-manager follow-up (2026-11-05)

- [x] User DGX read-only NVIDIA status: `NO_PINNED_LOCAL_SNAPSHOT`, 0 indexed shards, no local revision in inspected cache. Historical RadixArk evidence retained separately.
- [x] Add Wizard top-level Service management menu and 27B `download` planning action; all stateful actions remain fail-closed.
- [ ] Implement live read-only service/port/inode/disk/download-container inventory, immutable NVIDIA source pin and exact SHA256 plan with freshness and explicit approval.
- [ ] Implement and CPU-test guarded resumable 27B download (without `flash setup`, active model replacement or deletion); then schedule/approve actual DGX download separately.
- [ ] Qualify vLLM 0.32 single GB10 runtime and implement start/wait/verify/bench + rollback as a distinct action from downloading.

## P2 NVIDIA target selection (2026-11-05)

- [x] Replace P2 active model ID and local HF cache directory with `nvidia/Qwen3.8-27B-NVFP4`; retain RadixArk DGX result as historical evidence only.
- [ ] After Git pull, operator runs read-only `./wizard.sh model 27b status --inspect-cache --json` for **NVIDIA cache**, not the previously inspected RadixArk checkpoint.
- [ ] Verify NVIDIA immutable full SHA and actual local source files; qualify pinned vLLM 0.32 runtime/image and single GB10 memory before any download/start. No reuse of RadixArk revision.

## P2 source qualification update — 2026-11-05

- [x] Add bounded config fact discovery (architecture, model type, quant method, context and vision metadata), strictly **unqualified** for vLLM/GB10, with malformed/oversized config regressions.
- [ ] Check current CI after implementation and inspect real DGX read-only `./wizard.sh model 27b status --inspect-cache --json` output; never infer actual model availability from test fixtures.
- [ ] Source-check immutable model revision and vLLM 0.32 loader/GB10 support, then implement guarded 27B recipe planning and runtime steps without allowing unapproved download/start/replacement.

# Next actions — ordered work queue

## Current transition: P1 bounded GPU tests PASS → P2 27B inventory/qualification

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

- [x] P1: actual Wizard baseline, chat, tools, vision and bounded bench PASS.
- [ ] P1: obtain benchmark evidence metrics (TTFT, latency, tok/s) from the already existing operator file; review `doctor`/`inventory_plan` issues and confirm Wizard-driven install/start if required by full P1 lifecycle.
- [x] P2: source-only, fail-closed read-only HF cache inventory in Wizard; unit tests/CI required before DGX operator command.
- [ ] P2: operator runs `./wizard.sh model 27b status --inspect-cache --json` (no downloads, GPU, Docker or API changes).
- [ ] P2: source-verify pinned immutable 27B revision, image digest, vLLM 0.32/model architecture, memory/disk and baseline API expectations before changing placeholder recipe. Candidate stays deliberately invalid until verified.
- [ ] P2: guarded prepare/start/verify/benchmark **not yet implemented**; do not authorize service swap merely because P1 passed.



## 2026-11-05 — Restore default Blazux P1 acceptance semantics

**Latest operator DGX result (2026-11-05):** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` summary from `--auto-gpu` at `805f8e3e`: source checkpoint and Hybrid are both READY, `source_issues=[]`, `hybrid_issues=[]`, 11 indexed source and Hybrid shards resolved, `api_model_ids=["qwen3.8-flash-next"]`, verify and benchmark plans each READY, yet **verify action returned FAIL** and benchmark BLOCKED by verification gate. Original console suppressed the Wizard's failure evidence location because it parsed the JSON outcome only on returncode 0, even though Wizard writes evidence for returncode 2. This is an actual attempted API/GPU verification with FAIL outcome, not evidence of a broken default Blazux model. Exact failing subprobe/error still unconfirmed until raw report is examined.

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

**SOURCE/CI validation (not DGX):** `391a2844f4c8549e282eae3e266806c89801ad1a`, GitHub push and PR checks 2/2 SUCCESS, each 15 manifest + 10 inventory + 13 launcher + 1 mode + 102 P1 + 32 router = **173/173 CPU tests PASS**. Real DGX execution against this fix has NOT_RUN; prior verify FAIL remains unresolved until this new code runs.

- [x] Source: split standard /v1/completions + chat baseline from optional tool/vision probes, preserve exact per-probe failure classes and HTTP status without raw outputs, retain Wizard evidence on rc=2; let baseline PASS through to the short benchmark even if optional probes are PARTIAL.
- [x] CI/source unit and fake DGX regressions: 2/2 SUCCESS, 173 CPU tests per job.
- [ ] Operator can FIRST read the **existing** `20261105T103738Z-c4eb4031/result.json` at `actions.verify.command.stdout/stderr` to identify the original failure without re-running GPU work. Be careful of raw output before sharing.
- [ ] Only after that, `git pull --ff-only origin feature/recipe-wizard-handoff` and one `bash scripts/temporary/p1-post-download.sh --auto-gpu` to obtain per-subprobe baseline/extended status, actual evidence URI, benchmark metrics if baseline passes.
- [ ] Treat default P1 baseline and full extra feature acceptance as distinct gates; do not claim P1 complete if tools/vision or benchmark remain PARTIAL. Never restart servers or re-download assets as a response to a Wizard probe failure.


> Updated 2026-11-05 KST. **Draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) open, unmerged; current source CI at `43f5131` 2/2 SUCCESS (103 CPU tests/job).** Status terms are scoped. Tasks are not achieved merely because listed in a plan.

## 2026-11-05 — Completed download reported; P1 validation disagreement

**DGX operator update, 2026-11-05:** The operator explicitly confirms the NVIDIA Flash-Next download has finished. Their submitted terminal output after `git pull` to `dea7c5aa183da770b6b467288f2f6eedf8e94946` shows `bash scripts/temporary/p1-post-download.sh` produced report `/home/inlc/blazux-p1-reports/20261105T052545Z-1e6ec592/result.json`; current branch and clean tracked worktree checks PASS; no setup process found in the process scan. HTTP `/health` and `/v1/models` command exit codes are 0 **but actual served model ID was not included in the console summary**. Wizard doctor and inventory plan returned exit code 3; both P1 verify/benchmark plans BLOCKED: `checkpoint_downloading_or_incomplete`, `hybrid_not_prepared_or_incomplete`; no Wizard GPU/bench requests executed. The `checkpoint_downloading_or_incomplete` string is a **generic validation failure**, not proof that the download continues. The apparent mismatch needs read-only evidence before any setup, repair, download, switch or deletion.

- [x] SOURCE/CPU CI 2/2 SUCCESS, 138/138 tests each at `4c0041d`; previous fixture incompatibility fixed. Commit read-only `scripts/temporary/p1_cache_diagnosis.py` and invoke it from the existing one-command temporary P1 script; add synthetic tests, including master-ref fallback diagnostic and completed shards with leftover incomplete blob names. The current main-only Wizard check is deliberately left fail-closed pending evidence.
- [ ] Operator should `git pull --ff-only`, run `bash scripts/temporary/p1-post-download.sh --inspect-only` once and return the report's `cache_diagnosis` and actual `checks.models.stdout`; no `setup`, `prepare`, `serve` or automated benchmark until the discrepancy is understood.
- [ ] If diagnostics prove an auditor mismatch, fix the *specific* source predicate with CPU fixtures and rerun CI; otherwise identify genuinely missing Hybrid preparation without any competing download. Confirm the expected API model ID and actual image identity before Wizard verify/bench.

## Latest P1 checkpoint investigation — file-level facts required

**2026-11-05 P1 regression analysis:** NVIDIA's default `nvidia/Qwen3.8-Flash-Next-NVFP4` is supported by Blazux. The official `fc694b5` snapshot distributes `model.safetensors.index.json` (~31.3 MB) and `tokenizer.json` (~12.8 MB). Our new P1 audit erroneously rejected an otherwise-valid index above 16 MiB; code changed to a bounded 64 MiB maximum. **However the operator's specific issues** `model.safetensors.index.json` and `tokenizer.json` arise at the initial `_good_file` stage, *before* parsing/size checks. Thus the artificial size cap does not by itself explain the reported failures. The Hybrid marker exists, but Hybrid `tokenizer.json` also fails. Do not conflate claimed download completion with all snapshot symlinks resolving correctly; investigate metadata file existence, symlink resolution, size and repository containment first.

- [x] Fix 16MiB index-size bug, retaining 64MiB safety cap, with 17MiB-valid and >64MiB-rejected regression tests.
- [x] Expand `scripts/temporary/p1_cache_diagnosis.py` to return for each affected source/Hybrid metadata file: missing vs dangling HF symlink vs outside repo vs zero bytes vs valid, file size, and whether it exceeds the obsolete 16MiB cap. Add fixture tests for each class.
- [x] Existing single-command wrapper now reports API `/v1/models` **model IDs**, plus a distinct inspection-only vs Wizard-not-ready reason. No GPU, cache, model or Docker mutation from those source changes.
- [x] **Source/CI accepted:** `66c6c448c1922f958886fa4696c403a4b6227685`, GitHub Actions 2/2 SUCCESS, each 145/145 CPU tests PASS (15 manifest + 10 Inventory + 13 launcher + 1 executable mode + 74 P1 tests + 32 Wizard router). This is NOT DGX runtime acceptance.
- [ ] On DGX after operator's existing shell command chain finishes, `git pull --ff-only` then `bash scripts/temporary/p1-post-download.sh --inspect-only`; return **`cache_diagnosis.snapshots[*].source_metadata/hybrid_metadata`**, `api_model_ids`, and new evidence path. Only then decide if missing metadata should be repaired from its exact official revision and whether Hybrid snapshot needs a non-destructive repair. **Never re-download the 124GiB checkpoint or run `setup` as a guessed fix.**

## D-017 — Resolve false P1 audit block and exercise existing GPU service

**Operator DGX facts (2026-11-05):** The latest post-download diagnostic returned `api_model_ids=["qwen3.8-flash-next"]`, `refs/main=fc694b54fb0174e0913e6adf86691ef85a4ead47`, 0 incomplete HF blobs, a source index and tokenizer that are **existing nonempty symlinks whose targets resolve outside the model repository**, and a Hybrid tokenizer with the same layout. The Hybrid index is a normal 31,907,813-byte file and the `.prepared` marker exists. These observations show the previous `TARGET_OUTSIDE_REPOSITORY` reason is a **new P1 checker policy stricter than Blazux's original `os.path.exists`-based policy**; they do not establish that any metadata is missing. Previous plans were blocked before actual GPU verification or benchmark. The user explicitly allows non-disruptive GPU compute tests to run without separate per-step approvals, provided the actual target service is confirmed. The presence of an API response means some server is listening; do NOT assume there are literally no processes running or stop/replace any service.

- [x] Restore compatibility for confirmed existing metadata symlinks without weakening shard containment; add synthetic source/Hybrid and dangling/shard escape regressions.
- [x] Add scoped `--auto-gpu` to the existing one-command temporary runner. The operator may exercise the GPU without typing any plan-hash approvals. Still require actual model identity, current successful Wizard plan + double-checked plan ID, and verify PASS before benchmark. It never starts/stops a container, repairs Hybrid, changes model, or downloads anything.
- [x] GitHub SOURCE/CPU CI verified at `0063b0e004902408f980c155076c098d49d4569e`: push and PR jobs both SUCCESS, 155/155 CPU tests per job. No GPU PASS claim until operator results.
- [ ] Operator: `git pull --ff-only`, then `bash scripts/temporary/p1-post-download.sh --auto-gpu`. Return `~/blazux-p1-reports/.../result.json` summary including `plans`, `actions`, `api_model_ids` and new `cache_diagnosis`. If still BLOCKED, diagnose *new explicit issues*; no blind `./flash setup` or cache purge.

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

- [x] **W0 — Modular menu and headless CLI routing (SOURCE/CI).** P1 delegates to existing tested P1 flow; P2–P7 have per-stage status/plan interfaces and fail-closed execution. Source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe` produced 2/2 CI success, 101/101 tests/job. Follow-up source/docs commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b` GitHub CI verified **2/2 SUCCESS, 103/103 CPU tests each**, including P1 JSON guided guard.
- [ ] **W1 — Complete shared execution service and model adapters.** Add stage-specific schema/recipes/provenance checks, guarded prepare/start/verify/bench/rollback controllers as phases qualify; do not enable unverified P2–P7 operations. Exercise P1 against the actual DGX **only after the current setup and queued commands finish**, with per-action approval.
- [ ] **W2 — Real Wizard baseline acceptance.** P1 measured API and benchmark, rollback and evidence; then implement and validate P2, P3, optional P4, P5, P6, P7 in the previously locked order. P4 is conditionally skipped if capacity is sufficient.

**Direct CLI examples:** `./wizard.sh list --json`; `./wizard.sh p1 status --json`; `./wizard.sh --stage p3 --action switch --from-model flash-next --to-model 27b --json` (BLOCKED by design). Detailed contract: `docs/WIZARD-CLI-CONTRACT.md`.

## UI organization decision — domain-based menus (D-015)

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

- [x] Rename source `wizard/menus/p1.py`–`p7.py` into descriptive submodules under models/switching/storage/operations; update routing, legacy aliases, two-level interactive navigation, JSON catalog and direct CLI, plus CPU regressions. **SOURCE+CI 112/112 PASS/job twice** at `571e1c2`.
- [ ] Next model-specific implementation remains P1 actual DGX Wizard API/benchmark/rollback, then P2/P3/conditional P4/P5/P6/P7 in the existing runtime acceptance sequence. **File/menu grouping does not change stage acceptance order.**

## D-016 — User-run single-script temporary batch

- [x] Design and stage `scripts/temporary/p1-post-download.sh`, `p1_post_download.py`, source-only test `tests/test_p1_temporary_cpu.py`, README and CI. One script collects P1 diagnostic status, uses the existing Wizard for separate explicit verify/benchmark plans, and writes a consolidated report. Never runs a competing `setup`, automatic `serve` or cleanup.
- [x] New runner GitHub CPU CI VERIFIED at `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b`: both jobs SUCCESS; each ran 131 unique CPU tests. CPU CI is not DGX qualification.
- [ ] Once the operator-owned original setup/serve/wait/test process **fully ends**, operator runs `git pull --ff-only` and the one temporary wrapper. Start with `--inspect-only` if the live model state is uncertain; then use interactive TTY for independent current plan hashes if readiness is confirmed. Return reviewed `result.json` path/results; never upload secrets automatically.
- [ ] Review real P1 API/bench data (and any BLOCKED status) and update evidence/next actions before advancing. Temporary script is retired only by a later reviewed commit, not by running itself.

**Permanent rules:** `handoff/OPERATING-RULES.md` R1D and `scripts/temporary/README.md`; decision D-016.

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
