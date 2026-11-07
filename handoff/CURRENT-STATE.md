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

## LATEST SOURCE 2026-11-07 — P2-FINAL protected Native Tools V1 candidate added; REAL DGX unchanged

On existing Draft PR #1 / `feature/recipe-wizard-handoff`, added separate protected `qwen38-27b-native-tools-v1` source-only variant, intentionally incomplete YAML recipe, read-only `--tools-variant-plan`, strict SSE `--tools-stream-probe`, and offline CPU tests. The existing P2/P3 default `qwen38-27b` argv, service-policy, operational executor and production release gate are unchanged. The variant source is NOT executable; no parser-audited tool-enabled container has been created, no migration/rollback executor released, and no actual DGX tests run in this update. P2-FINAL remains OPEN/NOT_QUALIFIED. Latest operator-observed real DGX evidence still: original NVIDIA 27B on port 8000 LIVE_SERVICE_VERIFIED; journal VERIFIED/COMMITTED 14; old Docker Cmd missing auto-tool flags; local probe HTTP 400. Historical P3-C PASS/CLOSED, recurring switch both actual directions PASS; Wizard production menu still locked. Read `docs/P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md` before advancing.

---

## LATEST ACTUAL DGX 2026-11-07 — 27B ACTIVE / ordinary journal 14 COMMITTED / P2-FINAL HTTP 400

Operator fast-forwarded local `feature/recipe-wizard-handoff` source from `4054eb2` to `09c6780`, and the subsequent **REAL DGX, non-disruptive** checks returned:
- `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, `observed_model=27b`, sole `observed_model_ids=["qwen3.8-27b"]`, `expected_served_id=qwen3.8-27b`, `active_container.name=qwen38-27b`, `:8000`, all 8 reported API/manifest checks true, `issues=[]`. The field `gpu_exclusivity_verified=false` means **this status command has not established GPU exclusivity**, not that a second GPU model was observed.
- `python3 -m scripts.manager.operational_audit --json`: `status=VERIFIED`, `phase=COMMITTED`, **`event_count=14`**, `issues=[]`, final event SHA `ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e`. Independently confirms completed ordinary Flash→27B reverse switch after previous 27B→Flash PASS; no blind retry or P3 stages run.
- `docker inspect qwen38-27b --format '{{json .Config.Cmd}}'`: original pinned NVIDIA snapshot `482ca0f3832238542f8f5295dde86b5f22711d80`, served `qwen3.8-27b`; `--quantization modelopt_mixed`, `--dtype bfloat16`, `--max-model-len 8192`, `--max-num-seqs 1`, `--gpu-memory-utilization 0.70`, `--enforce-eager`; **no** `--enable-auto-tool-choice`, `--tool-call-parser`, `--reasoning-parser`.
- `bash scripts/serve_27b.sh --tools-profile`: `SOURCE_PROFILE_ONLY_DGX_NOT_QUALIFIED`, candidate flags `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`, `production_enabled=false`; no container created/modified.
- `bash scripts/serve_27b.sh --tools-probe`: **`BLOCKED`, `issues=["LOCAL_API_HTTP_ERROR_400"]`**, `structured_tool_call=false`, `tool_result_continuation=false`, `reasoning_separation=false`. Exact HTTP response body was not captured; absence of required flags from Docker inspect is separately established. No actual tool was executed or external service changed.

**Latest observed live model: NVIDIA 27B at :8000.** Original P2 download/runtime/benchmark and historical P3-C one-off stages = REAL PASS/CLOSED. New ordinary 27B↔Flash both directions = REAL PASS and read-only journal corroborated; production `./wizard.sh` main guided switch execution still source gated (`PRODUCTION_EXECUTION_RELEASED=False`); real failure/rollback and actual main-menu click-to-execute acceptance NOT_RUN. **P2-FINAL Native Tool Calling = BLOCKED ON CURRENT PRESERVED CONTAINER / NOT QUALIFIED**, source profile candidate only. Next: design protected tool-enabled variant and separately approved migration + rollback, then live structured auto call, continuation, streaming, reasoning separation, Open WebUI Native acceptance. No in-place container replacement or P3-C re-run, no PR merge.

---

## LATEST SCOPE DECISION — 2026-11-07: P2 final native Tool Calling added; P3-C historical CLOSED

**Current last user-reported LIVE model = NVIDIA 27B**, after independent ordinary Flash-Next→27B trial with fresh SHA, four human approvals, `Live transition result: PASS`, `Observed model: 27b`, private `completed-a811068f…json`. This is NOT old P3-C. Prior ordinary 27B→Flash had PASS and independent Flash status/journal verified. Separate post-reverse `service manager status --json` and operating journal `operational_audit --json` have NOT been provided yet. The **normal `./wizard.sh` switch menu is still `PRODUCTION_EXECUTION_RELEASED=False`**, despite backend bidirectional real PASS; do not claim live main menu UX release.

**User approved plan ordering:** P2 final pending item is official **Native Tool Calling** on pinned NVIDIA `nvidia/Qwen3.8-27B-NVFP4`, served `qwen3.8-27b` (internal architecture `Qwen3_5` is NOT a new model ID). vLLM 0.32 official Qwen3.8 recipe flags: `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`. New opt-in `_candidate_argv(..., tool_calling=True)` and source/local harmless probing via `scripts/serve_27b.sh --tools-profile|--tools-probe`. **Existing real 27B preserved container startup arguments do not change from Git source edits**. Tool Calling real DGX trial, structured tool-call, streaming, reasoning separation and Open WebUI native complete cycle remain NOT_QUALIFIED. Migration must preserve P3/P2 receipts and original containers, port 8000 and single active model. Do not mark P2-FINAL PASS without real proof.

**P3-C** one-off stage already REAL DGX PASS on 2026-11-07 and is **CLOSED/IMMUTABLE**; never rerun stage C. Preserve Draft PR #1 and HF cache; no GPU change or PR merge from this source update. Main contract: `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.

---

## LATEST REAL DGX POST-SWITCH CHECK — 2026-11-07: Flash-Next live VERIFIED, journal COMMITTED, reverse plan READY

**New operator read-only evidence after the earlier real 27B→Flash ordinary `PASS`:**
- `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, `observed_model=flash-next`, `expected_served_id=qwen3.8-flash-next`, only `observed_model_ids=["qwen3.8-flash-next"]`, active `qwen38-flash` (Up 18 minutes), host port 8000, all eight API/manifest checks true, `issues=[]`. The field `gpu_exclusivity_verified=false` only means the status command does not independently claim GPU exclusivity; do not present it as GPU qualification.
- `python3 -m scripts.manager.operational_audit --json`: `status=VERIFIED`, `phase=COMMITTED`, `event_count=7`, last event SHA `575197bd7fedcadf39751da4becdf7ca052943f37115b33b9398d736fa43a66a`, `issues=[]`. This independently corroborates the first ordinary switch's complete journal/receipt chain.
- `scripts/temporary/operational-switch-acceptance.sh --target 27b --plan --json`: `READY_FOR_SEPARATE_TRIAL_APPROVAL`, `source_model=flash-next`, `target_model=27b`, `served_id=qwen3.8-27b`, `issues=[]`, `executed=false`, `approval_accepted=false`, `production_release=false`, `seconds_remaining=276` at the instant of this observation, plan SHA prefix `c2fed6bf`; expiry `1794023400` epoch. **That preview is temporary and is not permission to reuse its SHA after expiry.**

**Acceptance now:** First operating 27B→Flash ACTUAL PASS including separately confirmed live API and committed audit. Reverse Flash→27B `READY` preview only, **ACTUAL REVERSE NOT RUN**. Normal production switch menu still hard gated, recovery fault-injection not run. **Last observed running model remains Flash-Next**. Do not execute reverse until separately approved live Flash downtime; any trial requires a new fresh plan and four manual TTY approvals. Old P3 A/B/C not rerun, original model/cache preserved; Open WebUI tool calling deferred.

---

## LATEST ACTUAL DGX — 2026-11-07: ordinary operating switch 27B → Flash-Next PASS (first physical acceptance)

**This operator-provided REAL DGX result supersedes earlier statements that all ordinary operating switches are NOT_RUN and that 27B remains active.** After clean Git fast-forward from `05c1968` to source commit `4054eb2`, operator independently checked `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, only served model `qwen3.8-27b`, active container `qwen38-27b`, port 8000, issues `[]`; `python3 -m scripts.manager.operational_audit --json` returned `EMPTY`, `event_count=0`, issues `[]`. The new acceptance read-only plan reported `READY_FOR_SEPARATE_TRIAL_APPROVAL`, 27B → Flash-Next, `issues=[]`, `seconds_remaining=242`, fresh 10-minute approval expiry, independent execution SHA.

Operator then ran the NEW tracked `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` with four **independently manually typed** exact approvals (trial authorization, fresh SHA, downtime consent, Flash target activation). Result **`Live transition result: PASS`**, **`Observed model: flash-next`**, and an immutable private operating completion receipt in `~/.local/state/blazux-wizard/operational-switch/completed-72e0941f…json`. This is **NOT historical P3 stage B**: it exercises the distinct normal operating executor on real DGX. The executor only reports PASS after target Docker/API served identity, bounded chat response, preserved original container and final operating journal verification. Original receipt bytes were not uploaded or independently opened by the assistant; evidence is the operator's terminal output.

**Last observed active inference model is now Flash-Next**, not 27B. There is NO automatic reverse switch; do not tell operators to run a 27B smoke until 27B is actually active. The separate reverse **Flash→27B ordinary acceptance has NOT_RUN**, and real failure-injection/restore acceptance is also NOT_RUN. Normal everyday Wizard remains `PRODUCTION_EXECUTION_RELEASED=False` and **NOT RELEASED**. Next safe DGX commands: recheck `service manager status --json`, `operational_audit --json`, then get a fresh **read-only** `--target 27b --plan --json` (separate user approval before 27B activation). Preserve both original containers/images/HF cache, immutable old P3 receipts, API port 8000, Open WebUI and Portainer. Open WebUI Tool Calling remains postponed; Draft PR #1 still Draft/unmerged.

---

## LATEST 2026-11-07 — Routine Flash↔27B Wizard source candidate / independent DGX acceptance pending

User explicitly directed: **finish existing Wizard ordinary operating switching UX and backend; defer Open WebUI Tool Calling.** Existing `./wizard.sh` now has a direct main **4. Switch active model** and model-specific **6. Guided operating switch**, plus `operational guided --target` read-only review and a distinct one-off trial route `operational acceptance --target ... --plan|--execute`. Production `PRODUCTION_EXECUTION_RELEASED=False` means normal menus cannot stop GPU; trial-only execute requires four exact new TTY acknowledgments, current SHA and separate physical downtime consent. Source `operational_executor.py` rechecks immutable P3 lineage, Docker image/container, single-GPU exclusivity, lock and dynamic plan; stops old before starting preserved new, verifies API model ID plus bounded chat, appends private journal and immutable completion, and best-effort restores on failure. Source `operational_audit.py` verifies journal-event hash chain vs snapshot and committed receipt, blocking crash divergence and ambiguous outcomes. Source-only Fake-DGX tests and GitHub CI are distinct from ACTUAL DGX runtime.

**ACTUAL DGX operating trial NOT_RUN**, original P3 A/B/C historical PASS retained. Last user-observed NVIDIA 27B `:8000` active under vLLM 0.32 and actual chat PASS, no new model stop/start. Original Flash preserved. Do not run old stage A/B/C, P1/P2 benchmark or any cleanup. Approval for source development is not blanket downtime consent. Do not mark Wizard production-accepted or flip release gate without actual separately approved DGX bidirectional/rollback evidence. Details: `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`. Draft PR #1 remains Draft/unmerged.

---

## 2026-11-07 — Highest-priority ordinary operating switch Wizard integration SOURCE; real execution STILL GATED

Operator corrected priority: **DEFER Open WebUI 27B Tool Calling/recipe work.** Return to existing `./wizard.sh` interface linking model-first target selection, read-only live preflight, explicit fresh independent approval and guarded ordinary switch/rollback backend. New `scripts/manager/operational_wizard.py` is wired through `wizard/console.py` model option 6 and `wizard/menus/switching/flash_next_27b.py` `operational guided --target` CLI. The preview candidate SHA is never a valid execution consent; independent domain-separated `operational_executor.execution_plan_id` required. Fake-DGX end-to-end guided flows are tested in `tests/test_operational_wizard_cpu.py`. Production `PRODUCTION_EXECUTION_RELEASED=False` hard-locks actual dispatch; manual plan/ack or CLI cannot bypass it. Historic P3 A/B/C receipts preserved and 27B on :8000 remains active; no Docker/GPU service mutation or user-authorized recurrent switch performed by this change. Additional real DGX bidirectional/rollback qualification remains **NOT_RUN**. Docs: `docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md`.

---

## 2026-11-07 — New real DGX: 27B strict chat-format PASS with thinking off; Open WebUI auto tools BLOCKED

Operator confirmed direct `qwen3.8-27b` Chat Completions with `chat_template_kwargs.enable_thinking=false` returns **exactly `DGX_OK`** (finish stop, reasoning null, 4 output tokens), no restart. Open WebUI 27B chat fails with `"auto" tool choice requires --enable-auto-tool-choice and --tool-call-parser to be set`. **Direct chat inference PASS is not Open WebUI native tool calling PASS.** Current source `scripts/manager/p2_27b_launch_preview.py::_candidate_argv` omits both auto-tool flags, while `scripts/serve_flash-next.sh` includes `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`. Live Docker `Config.Cmd` has not been separately inspected. Recommended first action: Open WebUI model-specific Builtin Tools OFF and remove attached/chat tools, retest plain chat **without changing DGX service**. Full native tool parser qualification/replacement needs an independently approved downtime plan and model-specific tests; no Docker stop/restart/create/delete, P3 replay, PR merge. See `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`.

---

## 2026-11-07 — ACTUAL DGX 27B CURRENT FUNCTIONAL INFERENCE PASS; output formatting deviation retained

**New operator-supplied REAL DGX evidence (after `git pull --ff-only` to `05c1968b55ab8ac7720b96630a952843f795c7cc`):** direct `curl` to localhost `:8000/health` succeeded; `/v1/models` returned **one** served ID `qwen3.8-27b` from the pinned NVIDIA `482ca0f3832238542f8f5295dde86b5f22711d80` snapshot (`max_model_len=8192`); and a direct `/v1/chat/completions` request succeeded with `model=qwen3.8-27b`, `finish_reason=stop`, `completion_tokens=26`, `system_fingerprint=vllm-0.32.0-bfe01fe9`. The tracked non-destructive `scripts/temporary/operational-27b-curl-smoke.sh` emitted **HEALTH_PASS / IDENTITY_PASS / INFERENCE_PASS / 27B_CURL_SMOKE_PASS**. Hence **current 27B API identity + actual user-visible text generation PASS** on DGX; not merely historical P2/P3 or Fake-CPU tests.

**Separate issue:** `choices[0].message.reasoning=null`, but `content` included reasoning-like prose, literal `</think>`, then `DGX_OK`. Thus the model generated a valid answer but FAILED a strict `content.strip() == "DGX_OK"` formatting check. Root cause unverified: possible chat-template/reasoning-parser separation; **do not** claim exact-response adherence, verified reasoning isolation, production release or switch/restore qualification. Source follow-up classifies `FORMAT_PASS` vs `FORMAT_DEVIATION` separately from inference PASS with offline CPU regressions; **that updated classifier has not been run on real DGX**, although raw actual response independently establishes the discrepancy.

**No model stop/start/switch, P3 stage A/B/C replay, deletion, or cache mutation.** The operator's only DGX change was source-only Git fast-forward. Last observed active model remains NVIDIA 27B; preserved original Flash container and assets must remain untouched. P3 historical PASS is unchanged; ordinary repeatable switch and guided approval UX still not qualified on real DGX.

---

## 2026-11-07 — Active 27B inference confirmation requested; curl smoke SOURCE added, real DGX NOT_RUN

Operator supplied `READY_FOR_OPERATOR_REVIEW_ONLY` for actual DGX 27B→Flash preview: historical P3 A/B/C receipts verified, `LIVE_SERVICE_VERIFIED`, issues=[], `executed=false`, `execution_supported=false`, no downtime. Operator correctly requested **a separate actual curl text-generation test** before treating the active 27B as functionally verified. Added `scripts/temporary/operational-27b-curl-smoke.sh` using localhost-only health + /v1/models + one bounded chat completion, with offline fake-curl CPU tests and optional Wizard menu instruction. Actual DGX script result **NOT_RUN/NOT_OBSERVED** until operator sends output. Continue preserving active 27B and Flash fallback; no ordinary switch execution, P3 rerun, PR merge or deletion. See `docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md`.

---

## 2026-11-07 — NEW: source-only general operating switch preflight and guarded executor (NOT DGX QUALIFIED)

Latest source work adds the model-centered read-only ordinary switch preview (\`scripts/manager/operational_switch.py\`, \`wizard/console.py\`, \`wizard/menus/switching/flash_next_27b.py\`) and an **unexposed, unqualified** independent transaction backend (\`scripts/manager/operational_executor.py\`). Historical P3-A/B/C receipts are validated as provenance **only**, never reused as a new operating approval. The executor's exact-plan/two-ack/lock/attempt marker/append-only journal/stop-before-start/rollback paths remain inaccessible from the Wizard CLI/TTY until a separate scoped actual DGX acceptance authorizes release. Source-only Fake-DGX suites and CI are tracked in \`tests/test_operational_{switch,executor}_cpu.py\` and the CPU workflow. Read-only dashboard distinguishes P3 historical receipts, live API, CPU CI, general switch qualification and Wizard UX acceptance; no static PASS is invented. See \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`.

**Actual DGX is unchanged by these GitHub commits.** Last operator-confirmed observation remains NVIDIA 27B served as \`qwen3.8-27b\` on :8000 after P3-C PASS. Never re-run P3-A/B/C or P1/P2 benchmark; never stop 27B or prune original Flash/27B assets without separately approved actual operating test. Existing Draft PR #1 unmerged. A green CI demonstrates CPU simulation only; do not infer release-qualified operating transition or integrated user acceptance.

---

## 2026-11-07 10:19 KST — ACTUAL DGX P3-C FINAL PASS, NVIDIA 27B ACTIVE (AUTHORITATIVE)

**This new REAL DGX operator evidence supersedes every previous statement below that P3-C is NOT_RUN, not approved or that Flash-Next is the currently active model.** The operator pulled the source with 565/565 fake-CPU regression PASS, independently approved the live downtime, and ran `bash scripts/temporary/p3-stage-c-operator.sh --execute` on the actual DGX. Initial read-only result `status=READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL/issues=[]/current_model=flash-next`, current C SHA `cb88d3be38a4fe1fd965a57aee402c76d53d746fe1cac76640d5b0a4fb6293ad`, expiry 2026-11-07 10:20:00 KST, `plan_refreshed=false` (the new rollover mechanism was **not** needed in this successful invocation). Operator independently typed that exact current SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, and `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C` in a TTY. Canonical Wizard result:

- `wizard_result.status=PASS`, `stage=c`, `executed=true`, `live_verified=true`, `active_model=27b`, `execute_command_exit_code=0`.
- Wrapper `status=P3_C_PASS_FINAL_27B_ACTIVE`, `approval_accepted=true`, `execution_dispatched=true`, `executed=true`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `issues=[]`. Wrapper rechecked `stage-c.json` and final active API/port/service identity; verified target is preserved original 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d` and original Flash source CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, shared runtime image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. Final served API identity was verified by wrapper's final status guard, based on `qwen3.8-27b` at port 8000.
- Canonical immutable receipt `/home/inlc/.local/state/blazux-wizard/p3/stage-c.json`; operator private report `/home/inlc/Workspace/llm/blazux-orcarouter/reports/transitions/flash-next--to--27b/p3-c-operator-20261107T011939Z-5f26a6ff25a2.json`. Both stay local/private, not committed. Under original rules: NVIDIA 27B **remains active**, NO automatic Flash switchback, and original Flash assets/container/cache must be preserved. The wrapper `current_model=flash-next` and `current_model_ids` are **pre-switch initial-state fields**; the final `post_switch_observed_model=27b` is the actual final state.

**Actual qualification outcome:** P1 NVIDIA Flash-Next functional Verify PASS (completions/chat/tools/vision) and benchmark PASS, including post-P3-B P1 measurements; P2 NVIDIA 27B pinned download, GPU trial and bounded benchmark with restored-original receipt `BENCH_PASS_RESTORED_VERIFIED`; P3-A Flash→27B PASS, P3-B 27B→Flash PASS, post-B P1 gate PASS, and now P3-C Flash→27B PASS. Each uses real DGX evidence, not merely CPU CI. Both published Git benchmark summaries were independently source-reconciled on DGX (`VERIFIED` x2). There is **no need** to repeat P1/P2 or P3 A/B/C or stop 27B for requalification without a new scope and separate approval.

**User-facing Wizard UX is NOT end-to-end qualified:** `wizard/console.py` P3 stage menu entries call `module.run([stage, "--plan"])` ONLY; they do not launch a guided interactive execution. The operator successfully used a tracked temporary shell/Python wrapper that called the **canonical** `./wizard.sh switch flash-next-27b stage-c --execute ...` route, which calls `scripts/manager/p3_persistent_switch.py`. Thus the real engine and CLI P1/P2/P3 are qualified, but an ordinary one-screen selectable model-switch UX and recurring routine Flash↔27B switch flow remain to be designed/implemented/tested. Do not describe UI selection as validated or equate P3-C one-off acceptance with general repeatable operations; service/proxy/gateway/Orcarouter and cleanup are outside the confirmed scope.

---

## 2026-11-07 — P3-C OPERATOR PLAN WINDOW ROLLOVER FIX IS SOURCE-ONLY

Actual DGX `--execute` twice near 10:10 KST canonical 10-minute plan expiration (10:08:14, 10:09:30 KST) returned `BLOCKED` solely due `P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS`, with `approval_accepted=false/executed=false/execution_dispatched=false`. No Stage C transition, GPU operation or downtime. Active model observed remained original Flash-Next; preserved NVIDIA 27B target unchanged, original P1/P2 evidence PASS. Canonical plan window end `2026-11-07 10:10:00 KST`; old SHA `30b2b29bb715e2393b65152ea8d1da2db61956d631efce2248aee2e9690610de` has expired and cannot be reused.

Updated **only** the tracked `scripts/temporary/p3_stage_c_operator.py` flow: near expiry, wait a bounded <=150 seconds for a **different fully READY read-only canonical plan** with >=120 seconds left; if source/API/P1/P2/container/provenance changes, SHA rotates unexpectedly before boundary, time limit/TTY/interrupt fails, or git becomes dirty, BLOCK before dispatch. Once freshly READY, it requests fresh exact current SHA, separate Flash downtime ack and separate final-C ack; then still repeats plan/live check and uses unchanged canonical switch guard. `--plan` unchanged. New virtual-clock CPU tests; docs `docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md`. Source+CI cannot claim actual DGX Stage C execution. No auto approval, no model deletion, no PR merge. P3-C still NOT_EXECUTED pending actual operator command.

---

## 2026-11-07 — PUBLIC BENCHMARK REPORTS VERIFIED AGAINST ORIGINAL REAL DGX PRIVATE RECEIPTS

User ran `bash scripts/temporary/verify-published-benchmarks.sh` on actual DGX after pulling branch changes. Both Flash `f506db4c76430674.json` and NVIDIA 27B `80f109dbd7c97460.json` returned `status=VERIFIED/issues=[]/executed=false`, with raw original SHA256 values respectively `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db` and `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. Thus the previously pending REAL-DGX private-to-public benchmark reproducibility check **is complete** (not merely mock CI). Published summaries are now source-reconciled, not unverified manual transcriptions. They remain narrow 3-request benchmarks using distinct Flash E2E and 27B E2E/decode-proxy definitions.

No GPU inference or service transition was performed by this check. **P3-C remains NOT_RUN, NOT_AUTHORIZED for live Flash downtime**; the previous actual `--execute` was CANCELLED prior to dispatch. Read-only benchmark verification does not re-prove current API readiness. For next actual step run `bash scripts/temporary/p3-stage-c-operator.sh --plan` with latest code for a fresh live check, and require independent exact current plan SHA/downtime/target acknowledgments before any `--execute`. No A/B repetition or P1 retest. PR remains Draft, unmerged.

---

## 2026-11-07 — GIT-PUBLISHED METRIC-ONLY BENCHMARKS / C CANCELLED BEFORE DISPATCH

Original operator evidence contains actual DGX Flash-Next post-P3-B benchmark PASS (mean 37.9527 tok/s, TTFT p50/p95 1.384594/1.779602 s, latency p50/p95 1.724560/1.813754 s, 3x64-token requests, concurrency1) and actual NVIDIA 27B bounded bench `BENCH_PASS_RESTORED_VERIFIED` (mean E2E 7.9002 tok/s, mean decode proxy 11.1801 tok/s, TTFT p50/p95 0.179349/28.977990 s, latency p50/p95 5.818283/34.609889 s, 3 requests). Published **sanitized** copies of this metric metadata only to tracked `benchmarks/published/`, with original private SHA256 digests and pinned model revisions; raw JSON evidence, plan IDs, host paths and logs stay LOCAL and `/reports/` remains Git-ignored. `scripts/manager/benchmark_publication.py` + CPU tests allow future original-private → public allowlist export. One-command cross-check `bash scripts/temporary/verify-published-benchmarks.sh` is READ ONLY; DGX original-file verification pending operator execution. These values are from user logs, not new benchmark invocations; 27B E2E vs decode proxy are not the same metric.

Actual P3-C operator `--plan` READY and P1 gate PASS. User's P3-C `--execute` submitted `[56a30...` instead of exact `56a30...` (the leading `[` is only prompt decoration), got **CANCELLED**, `approval_accepted=false/executed=false/execution_dispatched=false`. No Docker stop/start or Stage-C receipt. P3-C remains NOT_RUN; no automatic retries. Reissue new plan SHA and separate downtime/final C confirmations only at operator's direction.

---

## 2026-11-07 — NEW STAGE-C WRAPPER READY IN SOURCE; DGX C PLAN READY, NO SWITCH YET

Operator DGX independently ran `./wizard.sh switch flash-next-27b stage-c --plan --json`: **READY_TO_REQUEST_TRANSITION_APPROVAL / issues=[] / executed=false / approval_accepted=false**, POST-B P1 verify+benchmark+rc3 diagnostics gate PASS with SHA256 hashes, P2 trial benchmark receipt hash unchanged, original running Flash CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5` and stopped preserved 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`, shared image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. Old short-window SHA `d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7` expired by design and must never be reused. Optional P2/P3 evidence import prompt received literal `COPY` instead of SHA: `CANCELLED/copied=0/executed=false`; no P2/P3 records copied or migrated.

NEW GitHub source: `scripts/temporary/p3_stage_c_operator.py`, `scripts/temporary/p3-stage-c-operator.sh`, fake-DGX `tests/test_p3_stage_c_operator_cpu.py` provide a tracked D-016 Stage C operator. Default `--plan` checks original immutable A/B receipts, pinned P2, P1 post-B PASS evidence and live Flash without service mutation. `--execute` would require a **new** exact current C SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C` manually typed in TTY, then fresh preflight and canonical Wizard recheck. Third literal is wrapper-only; core C uses null `--enter-p3`. C pass additionally requires live 27B API and canonical `stage-c.json` proof. Per-model direction report under `reports/transitions/flash-next--to--27b/`, no changes to original state/journal/locks. Source CI is not actual DGX C execution; **P3-C NOT_AUTHORIZED/NOT_EXECUTED**. No PR merge. Runbook: [C operator](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## 2026-11-07 — HISTORICAL EVIDENCE VIEW AND GUARDED P2/P3 COPY ADDED (SOURCE ONLY)

Latest source adds a **read-only model-indexed history** for original Flash Verify/Benchmark, 27B GPU trials/benchmarks, stage A/B model transitions, diagnostics and optional operator reports. The service-policy manifest supplies human-facing model IDs; the UI hides internal P-codes. It distinguishes Flash-Next direct throughput from 27B E2E and decode-proxy throughput. History reads both old `~/.local/state/blazux-wizard/p1,p2,p3` and new ignored repo `reports/`, deduplicates byte-identical SHA256, and sorts by UTC event time. CPU-only synthetic fixtures test this.

Stage 1 copy-only consolidation: `./wizard.sh evidence migrate --plan` / `--guided` or main Wizard `3 Advanced → 8` generates and revalidates a digest-bound fresh copy plan, requires the literal full SHA in prompt, writes private 0600 append-only files under `reports/models/<served-id>`, `reports/transitions/<direction>`, `reports/diagnostics/<served-id>`; no source deletion. P2/P3 original state/journal/locks and original trial/transition evidence remain authoritative; no change to their live writers or restore mechanics. Stage 2 native writer mirrors and stage 3 full state relocation are **not implemented**, by design until later real-DGX review. Source approval tests are not evidence of a DGX import.

**P3-C next:** Actual operator-provided P3-B and post-B P1 PASS; fresh stage-C read-only plan on DGX NOT_RUN. Request `./wizard.sh switch flash-next-27b stage-c --plan --json` after source CI+ff-only update, then evaluate its exact live source/target/receipt gates. C downtime NOT_AUTHORIZED and no switch performed. See [migration document](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md) and [next actions](NEXT-ACTIONS.md).

---

## 2026-11-07 — OPERATOR POST-B P1 ACTUAL PASS / MODEL-CENTERED WIZARD UX SOURCE UPDATE

The operator supplied `blazux-wizard.zip`, confirming DGX **P1 Verify PASS** (baseline/extended + text/chat/tools/vision, UTC 2026-11-06T23:26:27Z) and **P1 Benchmark PASS** (UTC 23:30:31Z, 3 requests, 64 tokens, concurrency 1, seed 1234; 37.9527 tokens/sec; TTFT p50 1.384594 s, p95 1.779602 s; latency p50 1.724560 s, p95 1.813754 s). Both have distinct typed exact plan IDs and immutable old-path receipts under `~/.local/state/blazux-wizard/p1`. P3-B stage-B canonical state PASS, existing original NVIDIA Flash-Next serving :8000 and post-B read-only diagnostics PASS with expected own name/port collision rc3. **P3-C NOT_AUTHORIZED/NOT_RUN**; no automatic phase transition. Original historical receipts must never be rewritten.

Source branch now changes Flash interactive UX to one chosen action, P3-style `Type exactly [SHA]` with the current SHA visible, and Verify/Benchmark metrics on screen. New Flash evidence writes into Git-ignored project `reports/models/qwen3.8-flash-next`; P3 evidence gate reads this and the legacy path without allowing old PASS to mask newer failed attempts. All operational changes were source-only GitHub edits; **no further GPU/runtime/transition/merge took place**. Review [operator UX/evidence contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md), confirm current HEAD and CI, then a clean operator fast-forward pull before using the updated Wizard. Do not rerun real GPU checks without separate operator authorization.

---

## 2026-11-07 — CPU SOURCE VALIDATION CHECKPOINT

GitHub source+documentation as of commit `67ff9cc2e4ece0c89c911513673f7d5d55c98fa4`: **501/501 CPU PASS, 23 test groups** ([Actions run 42310408411](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42310408411)). Draft PR #1 reviewed with COMMENT (review ID `5808289782`), remains OPEN/DRAFT/UNMERGED. This validates only source/CPU regressions, not new real DGX post-B P1 or C. Newest handoff-only commit SHA/CI must be checked live at next session. D-016 next: clean fast-forward pull then exactly one `bash scripts/temporary/p1-post-b-audit.sh`; no unapproved GPU call, model switch or cache cleanup.

---

## 2026-11-07 — LATEST AUTHORITATIVE STAGE: P3-B ACTUAL DGX PASS; Flash-Next ACTIVE

**This section supersedes older `P3-B NOT_RUN` / `27B ACTIVE` sections below.** Actual DGX outputs supplied by the operator, NOT inferred from CPU CI:

- P2 27B initial GPU benchmark/restoration: **PASS / COMPLETE**, do not repeat.
- P3-A Flash-Next → 27B: **ACTUAL_DGX_PASS** (`stage-a.json`, `P3_A_PASS_27B_ACTIVE`).
- P3-B 27B → original Flash-Next: **ACTUAL_DGX_PASS**, `stage-b.json`, `P3_B_PASS_FLASH_NEXT_ACTIVE`, `executed=true`, `wizard_result.status=PASS`, `wizard_result.live_verified=true`, `issues=[]`, `post_switch_status=LIVE_SERVICE_VERIFIED`.
- Last operator-verified model: **flash-next**; API served ID **`qwen3.8-flash-next`**, port **8000**. New live runtime observation during this GitHub source-only work: **NOT_PERFORMED**.
- Original Flash CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. P3-A-created 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`. Runtime image shared `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; identical image does NOT imply identical served model.
- Actual B operator report `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T223124Z-14861d75.json` (historically misnamed); canonical `/home/inlc/.local/state/blazux-wizard/p3/stage-b.json`. Historical `approval_accepted=false` in old operator report is a wrapper bookkeeping error, not evidence of missing core execution consent. Do not modify old evidence.
- P1 POST-B READ-ONLY PREFLIGHT: **PASS**: `/home/inlc/blazux-p1-reports/20261106T224010Z-d2095867/result.json`, API ID correct, branch+clean+plan checks READY, source/Hybrid ready. `actions.verify/benchmark=BLOCKED` with `reason=inspection_only` means **NOT_RUN**, not failed.
- P1 POST-B Verify: **NOT_RUN**; Benchmark: **NOT_RUN**. Post-B raw doctor/inventory `rc=3` disposition: **NOT_YET_QUALIFIED** (prior pre-A expected collision is not new post-B evidence).
- P3-C: **NOT_RUN, NOT_AUTHORIZED**, ineligible until separately approved actual new P1 Verify, numeric Benchmark, valid post-B diagnostics.

**Current source work:** stage-B filename/approval-state fixes and append-only `scripts/temporary/p1-post-b-audit.sh` with fake-DGX tests and latest-evidence P3-C gate. No GPU/service mutation or PR merge. D-016: commit/CI first, then operator fast-forward pulls and runs ONE tracked read-only audit, stops on BLOCKED, and separately approves any later GPU action.

---

## 2026-11-06 — P3-B separate downtime permission GRANTED; actual DGX transition pending

Operator explicitly replied **"승인"** when asked the unambiguous scoped question "P3-B(현재 NVIDIA 27B 중단 → 원본 Flash-Next 복귀)를 승인하시겠습니까?" following real DGX `READY_FOR_SEPARATE_P3_B_APPROVAL` (`issues=[]`, saved `~/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`). **P3-B entry permission now granted** for this one stage only; does not authorize another action. No new actual B DGX output exists: **P3-B NOT_RUN**, 27B last verified running. Tracked GitHub `scripts/temporary/p3-stage-b-operator.sh --execute` is ready, CPU [489/489 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) with exact stage-B-only `I_ACCEPT_27B_DOWNTIME` + `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`, fresh full current plan SHA and typed three-step terminal confirmation. Do not pre-fill approvals or use expired B inspection plan SHA. D-016: agent commits docs; operator fast-forward pulls and runs one tracked wrapper. Wizard must verify live source/target containers and restore on failure when possible; return `P3_B_PASS_FLASH_NEXT_ACTIVE` and independently verified `qwen3.8-flash-next` before any P1 work. No automatic post-B P1 or C, no PR merge/cleanup.

---

## 2026-11-06 — Real DGX P3-B INSPECT PASS, 27B still LIVE, separately approved stage B NOT_RUN

Operator ran D-016 tracked `scripts/temporary/p3-stage-b-inspect.sh` after pulling HEAD `e5d4171d07838e565510b1127f4a0b27dcd8423f`. ACTUAL DGX result `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`, `operations_enabled=false`, `approval_accepted=false`, saved to `/home/inlc/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. API current model `27b`, ID `qwen3.8-27b`; running 27B container ID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`; preserved original Flash ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`; both share runtime image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. P2 benchmark evidence hash unchanged. Canonical B stage plan generated with no issues (`7af40f009dd67975c77b98c03183833dd4997e16f9c9443bd11ea880f6d8162c`, expires 17:50 KST Nov 6); this SHA is inspection-only and must not be reused after expiry.

**Actual staged state:** P1 initial PASS / P2 trial+bench PASS / **P3-A DGX PASS (27B ACTIVE)** / **P3-B read-only inspect PASS, NO B execution or B permission** / post-B P1 verify+numerics NOT_RUN / C NOT_RUN. User's log is not an additional downtime approval. No assistant-side GPU/Docker mutation was performed.

Source work after receipt: fixed wrong all-stage Flash downtime ACK in core: B now has exact `I_ACCEPT_27B_DOWNTIME` + independent `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`; A/C retain original ACK contracts. Added `scripts/temporary/p3-stage-b-operator.sh` default read-only and explicit `--execute` protected by three typed B-specific exact approvals, active source/API and A receipt safeguards, plan expiry/rotation guard, independent returned Flash API, private 0600 evidence, no auto P1/C. Fake DGX CI [489/489 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) on source `59046c4e17a5094f2c80a84025a763c2a767edcb`; actual updated B operator DGX NOT_RUN. Do not instruct `--execute` until separate B user approval; 27B kept live. Draft PR #1 open/unmerged, no cache/image cleanup.

---

## 2026-11-06 — P3-A actual DGX PASS: NVIDIA 27B LIVE; stop before B, B source inspector CPU-tested

User actually executed `bash scripts/temporary/p3-stage-a-operator.sh --execute` after a fast-forward pull to Git HEAD `a3945bdc5cfec467478978c47b3a27bdafee84bd` and typed the current plan hash `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`, Flash downtime ACK and separate P3 entry ACK. The Wizard returned `stage=a,status=PASS,executed=true,live_verified=true` and durable `~/.local/state/blazux-wizard/p3/stage-a.json`. The tracked wrapper independently observed `post_switch_observed_model=27b`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `status=P3_A_PASS_27B_ACTIVE`, `issues=[]` and exit code 0. Private evidence `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. As of actual user report, **27B active**, original Flash original image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137` and original container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5` are stage-A identity anchors; independently inspect still-preserved/stopped status before B. P2 receipt hash remains `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`.

**Stage ledger:** P1 initial pre-A evidence PASS / P2 GPU smoke+benchmark PASS / **P3-A ACTUAL PASS** / **P3-B NOT_RUN, NOT AUTHORIZED** / P1 post-B verify+measured benchmark NOT_RUN / P3-C NOT_RUN. P3-A being successful doesn't justify any subsequent downtime or automatic GPU workload. Existing stage-B canonical Wizard backend has independent exact plan/ack requirement; plan generation alone does not approve execute. To support the upcoming separate decision, added source-only D-016 `scripts/temporary/p3-stage-b-inspect.sh` and Python module with NO execute mode; it compares actual private A receipt, 27B live Manifest/API ID, stopped preserved Flash container ID/image and newly generated stage-B plan, writes local 0600 summary. It cannot run B. CPU mock-DGX cases validate false-identity/stale plans/no execute. Actual DGX B inspection is NOT_RUN pending operator pull. The original P3-A source test and latest source changes are GitHub/CI only; no change was made on the currently running 27B by assistant. Do not merge Draft PR, clean HF caches, or schedule background GPU activity.

---

## 2026-11-06 — Actual P3-A triple-ack attempt BLOCKED, zero Docker mutation; fixed approval UX and short plan boundary

User ran `bash scripts/temporary/p3-stage-a-operator.sh --execute` after fast-forward pull to HEAD `be6f3f9e6d757cc11c6299024900b637c7ca239d`. Real P1 proof `PRE_A_P1_REVIEW_READY`, live Flash `LIVE_SERVICE_VERIFIED`, P2 receipt hash `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, P3-A plan `94b4dedae21eb72b12443029257931e123e33404c32898d9ae2bad52954c064f`. Operator independently typed plan ID, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, and `I_SEPARATELY_AUTHORIZE_P3_ENTRY` correctly. Wizard returned `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT`, `approval_accepted=false`, `executed=false`, no stage transition. Local report `~/blazux-p3-reports/p3-a-operator-20261106T073049Z-4dc8be1b.json` has `status=OPERATOR_REVIEW_REQUIRED` **from old wrapper**, even though nested Wizard result was `BLOCKED` and no operation occurred. P3-A/B/C actual service transitions remain **NOT_RUN**; original Flash service was verified before the attempt. No proof of failure to restore: there was no stop/start.

**Stale plan root evidence:** plan `expires_at_epoch_seconds=1793950200` = **2026-11-06 16:30:00 KST**. Receipt is named at **2026-11-06 16:30:49 KST** (07:30:49Z). The 10-minute plan window expired before the final report; this strongly explains stale-plan refusal (the exact nested fresh-plan difference was not included in operator output). Do not reuse the old hash.

Operator requested exact typed strings to be displayed **in the terminal**, not generic prompts. Source updated `scripts/temporary/p3_stage_a_operator.py`: prints actual current plan full SHA and both exact literal acknowledgements beside each prompt, with KST expiry and seconds remaining. `--execute` refuses initiating prompts when fewer than 120 seconds remain; after all typed acknowledgments refreshes the stage-A read-only plan and blocks without invoking execution if SHA changed or expired. A stale Wizard refusal with `executed=false` reports `BLOCKED` rather than misleading recovery warning. Never auto replace a SHA, auto-retry, or auto-enter B/C. Fake DGX tests include all three strings, short window, rotated SHA, stale refusal. [Code push CI 42181851452](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181851452) and [PR CI 42181858236](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236) **SUCCESS 459/459 CPU, 20 groups** on code SHA `fb34ce0ce985824cecd9c63159bf6f1eed408279`. Actual DGX with updated wrapper **NOT_RUN** yet. D-016 GitHub→fast-forward pull→one wrapper; fresh triple-ack required if operator opts into a subsequent real P3-A attempt. Preserve original Flash containers/images/cache and Draft PR.

---

## 2026-11-06 — Actual DGX P1 PRE-A PASS, conditional 27B entry now eligible; guarded P3-A wrapper SOURCE only

Actual DGX `git pull` then `bash scripts/temporary/p1-pre-a-readiness.sh` on source HEAD `834f823a76556a37a982e3dbf7f243db3edad6df` wrote `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`: `status=PRE_A_P1_REVIEW_READY`, **`issues=[]`**, both current/historical `rc3=EXPECTED_ACTIVE_FLASH_COLLISION` (2 checks each), P1 Verify PASS, P1 numerical benchmark PASS with 3 requests, 192 completion tokens; TTFT P50/P95 1.398707/1.751198s, latency P50/P95 1.687357/1.780142s, mean throughput 38.2968 tokens/s. Current Flash-Next service image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137` verified. Earlier P1 numeric gaps, rc3 ambiguity and temporary cached-diagnosis parser issue are **closed for pre-A assessment**; post-B P1 full reverify+remeasurement remains NOT_RUN and required later.

User's original P3-A scope was **if P1 initial gaps all resolved, approve 27B transition**. D-037 records that the condition is now satisfied. The local `p3_a_execution_authorized=false` field simply means the **read-only P1 evidence command** never authorizes/executes service changes; live stage A still requires a new plan and independently typed exact ID / downtime / P3 entry confirmations. No actual P3-A/B/C has run; current model remains Flash-Next.

Source added `scripts/temporary/p3-stage-a-operator.sh` + `p3_stage_a_operator.py`, covered by fake-DGX CPU tests `tests/test_p3_stage_a_operator_cpu.py` and Actions workflow. Default is plan-only; `--execute` requires interactive three independent typed confirmations, verifies same Flash image and complete P2 receipt provenance and freshness, delegates live transition ONLY to canonical Wizard stage-A executor, then independently rechecks actual served `qwen3.8-27b` API/model/container/image. On failure show `OPERATOR_REVIEW_REQUIRED` and do not retry or auto-B; rollback by core executor is best-effort and can fail. No host-GPU exclusivity or live P3 recovery qualification is implied by source/CPU CI. D-016 GitHub push→CI→DGX pull→one wrapper remains mandatory. Draft PR #1 stays unmerged.

---

## 2026-11-06 — DGX pre-A P1 evidence showed *two parser-induced blockers*; source fix 439 CPU PASS, DGX rerun pending

DGX operator ran tracked `scripts/temporary/p1-pre-a-readiness.sh` from HEAD `3a59419305b31266f034fe4cbec2b384bb91d1f4`. Real local saved receipt `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T064009Z-70e9cef9.json` reported `status=BLOCKED` only on `P1_ASSET_AUDIT_NOT_READY` and `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. **Other actual checks passed:** historic and current doctor/inventory rc=3 independently confirmed `EXPECTED_ACTIVE_FLASH_COLLISION` 2/2 each, P1 functional `p1_verify.status=PASS`, numerical `p1_benchmark.status=PASS` (3 samples, latency P50 1.687357s, TTFT P50 1.398707s, mean throughput 38.2968 tokens/s), live model flash-next, expected preserved image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. `operations_enabled=false`, `p3_a_execution_authorized=false`, no P3 execute.

Source root cause verified from original `scripts.temporary.p1_post_download.session`: private persisted `result.json` retains `checks.cache_diagnosis.stdout` JSON but **does not store a top-level `cache_diagnosis` key**; that top-level key is printed only in the console summary. `p1_pre_a_readiness.assessment` previously read `current["cache_diagnosis"]["wizard_audit"]`, always missing for genuine saved files, then falsely labeled missing revision as `DRIFT`. Fixed to reuse canonical `p1_post_download.cache_diagnosis_summary(current["checks"])` to read stored data and distinguish `P1_CURRENT_CHECKPOINT_REVISION_UNAVAILABLE` from actual `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. Test fixture changed to exact real `checks.cache_diagnosis.stdout` structure; additional positive, corrupt/missing, and true-drift CPU regressions added. **Source commit `9adc9ab282a91c02e959dcb5c62f98527b556391`: [push CI 42176219970](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176219970) and [PR CI 42176224898](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898) SUCCESS, 439/439 CPU tests across 19 groups**. Source proof only, **no DGX rerun yet**. D-016: operator fast-forward pulls, invokes same tracked wrapper once, returns `issues` and `status`; do not run P3-A or disrupt Flash automatically. Original conditional entry approval is not independently validated until real re-evaluation.

---

## 2026-11-06 — GitHub-first D-016 P1 audit delivered, 435/435 CPU PASS; operator DGX step pending

New tracked wrapper `scripts/temporary/p1-pre-a-readiness.sh` is committed with CPU fake-DGX tests, runbook, private evidence output and no GPU/service operations. Pre-A initial P1 numeric evidence *already supplied* (2026-11-05 original benchmark): TTFT P50/P95 1.398707/1.751198 s; latency P50/P95 1.687357/1.780142 s; mean 38.2968 tokens/s from 192 tokens across 3 requests. P1 source+Hybrid READY and basic/extended Verify PASS; 2026-11-06 inspection `actions.*=BLOCKED/inspection_only` is intentionally non-executed, not regression. Only historical/current raw `doctor=3` /`inventory_plan=3` cause remains unreviewed from supplied **summary**, plus D-034's mandatory post-B P1 rebenchmark later.

Discovered and corrected impossible P1 identity receipt check: actual P1 Wizard identity result has `health=PASS` and `models` with served ID, not `identity.status=PASS`. This was fixed in both initial read-only wrapper and P3 final C P1 gate, test fixtures made real-shaped, wrong-ID negatives added. GitHub push [42173798547](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173798547) and PR [42173805888](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) on source commit `75d22ce4303736ee84563a0f388a978379e4f228` SUCCESS, **435/435 CPU PASS, 19 groups**. No actual DGX pre-A wrapper run yet, P3-A/B/C NOT_RUN, no automatic P3 authorization. After fast-forward pull, operator invokes **one** `bash scripts/temporary/p1-pre-a-readiness.sh` and supplies its small JSON result; do not paste custom terminal Python snippets.

---

## 2026-11-06 — P1 initial numerics now REAL; D-016 tracked pre-A evidence wrapper developed (DGX NOT_RUN)

Operator-reported genuine P1 benchmark JSON `20261105T113125Z-586b2b46d93e.json` status PASS: **TTFT P50 1.398707 s / P95 1.751198 s; latency P50 1.687357 s / P95 1.780142 s; mean 38.2968 tokens/sec; 3 samples, total 192 tokens**. This supersedes prior "metrics not supplied" only. Flash-Next inspect-only report `20261106T060941Z-e71a159c/result.json` returned clean branch, source/Hybrid ready and no incomplete blobs; 11/11 indexed shards present/resolvable (some compatible external symlinks), original source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, API `qwen3.8-flash-next`, plans verify/benchmark READY, no active setup process. `actions.verify/benchmark` show `BLOCKED/inspection_only` because operator selected read-only mode; **not** GPU verify/benchmark failure. Historical P1 functional verify PASS is retained. Current/historic doctor/inventory-plan return 3 cause still **not independently established from raw JSON** (pasted report summary only contains rc), so do not accept P3-A conditional approval yet.

D-016 temporary script rule was re-read. Added a tracked `scripts/temporary/p1-pre-a-readiness.sh` and Python entry, with CPU fake-DGX tests; it reads old + current private P1 reports, original P1 verify+benchmark receipts and fresh Wizard service manager status, writing a concise local 0600 evidence record; **never switches service, starts GPU inference, performs git pull or auto-generates an approval**. Next operator action after CI: clean DGX `git pull --ff-only`, then run this **single wrapper**, return its small JSON. `PRE_A_P1_REVIEW_READY` would mean initial pre-A evidence acceptable for reviewing conditional P3 entry, **not** automatic Flash downtime or post-B evidence. P3-A/B/C remain NOT_RUN, original Flash active.

---

## 2026-11-06 — Conditional P3-A consent NOT MET: P1 missing metrics/rc3 evidence; 418/418 CPU PASS for guard correction

User requested P1 remaining-work inspection before any P3-A Flash→27B interruption and explicitly granted **conditional** approval only if no P1 work remains. Latest recorded P1 actual DGX on 2026-11-05 has `verify=PASS`, baseline+extended `PASS`, default_completion/chat/tools/vision `PASS`, `benchmark=PASS`, Flash image/source/Hybrid ready; **P1 numeric TTFT/latency/throughput values have never been shared or independently reviewed, doctor and inventory-plan rc=3 raw reasons unexamined, and required post-B P1 rerun NOT_RUN**. Condition is not met. P3-A NOT_RUN, no new service-change approval; original Flash service retained.

Source audit shows both `wizard/00-doctor.sh` and `wizard/10-plan.sh` delegate to `scripts.manager.inventory`; its CLI returns 3 when `collision_free=false`. When the expected `qwen38-flash` is already running on :8000, collision is expected even if inventory's `status=PASS` and `errors=[]`. Previous post-B P1 gate required both return codes zero, contradictory to active source service. Corrected to accept only raw-proven exact owned active Flash collision (both rc3, parsed doctor+inventory JSON with no inventory errors, correct image/name/API port/launch preview), not merely any rc3; genuine read errors or foreign containers fail closed. **Historic raw rc3 cause still UNKNOWN**, so it remains open. New post-B actual P1 verify/benchmark/diagnosis receipt requirement unchanged.

Source commit `26a69507983dbcb2a7ab4c569f9d8baa6162e25c`: [push 42172119698](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172119698) and [Draft PR 42172127412](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172127412) **SUCCESS**, 418/418 CPU tests over 19 groups. Actual DGX P3 A/B/C NOT_RUN, stage-A previous plan IDs must not be reused after expiry; Draft PR remains unmerged.

---

## 2026-11-06 — P3 read-only plan UX and recovery collision guard corrected (413 CPU PASS)

With actual DGX P3-A read-only READY evidence preserved below, SOURCE-only development continued without service interruption. Global `sequence --plan` now distinguishes staged switch code implemented from actual DGX qualification: `persistent_switch_source_implemented=true`, `persistent_switch_dgx_qualified=false`, and independent stage A/B/C read-only commands while retaining `status=BLOCKED`, no `plan_id` and `operations_enabled=false`. This corrects stale "no persistent switch executor" notice, without authorizing P3 entry or live execution.

The P3 recovery function now performs another Docker GPU-consumer inventory after stopping/removing the failed target and **before restarting the original model**. Unexpected GPU-enabled Docker consumer => `RECOVERY_FAILED` with `RESTORE_FOREIGN_GPU_CONSUMER`; original is not restarted onto another GPU service. CPU tests cover refusal and normal recovery. Host-level GPU processes outside inspected Docker inventory are not fully qualified; neither this patch nor `gpu_exclusivity_verified=false` implies global GPU exclusivity.

**Actual CI on source commit `02bf94c1628828ce22fa338dd5a8e5a0955f9179`:** [push 42170050031](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170050031) and [PR 42170056860](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860) SUCCESS; **413/413 CPU tests, 19 test groups**, no failures. Intermediate fixture serialization failure on commit `d82122f` was corrected; no production GPU calls occurred. P3-A/B/C actual transitions and P1 post-B benchmark remain NOT_RUN. Draft PR still unmerged.

---

## 2026-11-06 — New real DGX P3-A read-only readiness; Flash-Next still active (no P3 execution)

2026-11-06 DGX operator read-only observation: current Flash-Next `qwen38-flash` on :8000/v1, `LIVE_SERVICE_VERIFIED`, served ID `qwen3.8-flash-next`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, exact container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Manifest/API check array 8/8 true, `issues=[]`, `executed=false`; **GPU exclusivity and process ownership remain unverified**, and current identity is not historical rollback proof. `sequence --plan`: `status=BLOCKED` with only `P3_SEPARATE_OPERATOR_ENTRY_REQUIRED` by D-034 (expected), with successful local P2 receipt SHA-256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, evidence path `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`. `stage-a --plan`: `status=READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, source `flash-next`, target `27b`, `plan_id=79be6bf05cb02306ec9155ade317e06c457238de427417ebab8946e35449247a`, expiry epoch `1793943600` (2026-11-06 14:40 KST), target image equal to preserved local Docker image ID, expected target container ID null (not yet created), `executed=false` and `operations_enabled=false`. **This was a plan only, not scoped downtime approval or P3 entry**; plan IDs must be regenerated when stale and must never be reused across stages. No GPU/Docker/service mutation was performed by these read-only queries.

**Current stage:** P2 closed; P3-A `PLAN_READY` but **P3 entry / actual stage execution NOT APPROVED and NOT_RUN**. Only the independent first-stage request for operational approval is eligible for review. Preserve `qwen38-flash`, both model snapshots, Docker image and :8000. Do not auto-run B, P1 remedial benchmark or C. Last provided actual DGX service state remains Flash-Next.

---

## 2026-11-06 — P3 staged persistent switching SOURCE implemented; CPU CI 411/411 PASS; DGX P3 NOT_RUN

Existing D-034 remains binding: P2 actual limited NVIDIA 27B benchmark `BENCH_PASS_RESTORED_VERIFIED` and original Flash-Next `LIVE_SERVICE_VERIFIED` were recorded below; P2 is CLOSED. No P3 live service change has been authorized or executed.

New **source-only** P3 stage-specific adapter `scripts/manager/p3_persistent_switch.py` and Wizard `switch flash-next-27b stage-a/stage-b/stage-c --plan`: A Flash→27B; B 27B→Flash; C final Flash→27B. Each stage has live Docker/Manifest/API identity checks, target ID/label preservation, independent short-lived plan SHA, explicit downtime acknowledgment, stage A separate P3 entry acknowledgment, stop-before-start, port :8000 release, single-GPU Docker guard, private receipt and append-only service journal. Success leaves target model active and never auto-advances. Failure attempts exact source container recovery; recovery-failed journal blocks automatic replay. Older `roundtrip` remains RETIRED/BLOCKED; global `sequence --plan` remains non-executable.

New `scripts/manager/p3_p1_evidence_gate.py` blocks C until local P1 `verify` and `benchmark` PASS receipts are *newer* than stage B, include actual functional and numerical TTFT/latency/tokens/sec proof tied to original Flash-Next image, and actual reviewed resolution of historical `doctor/inventory-plan` rc=3. No fabricated P1 benchmark or rc=3 cause; **P1 REMEDIATION NOT_RUN / NO POST-B EVIDENCE**.

CI after code/Wizard changes: [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168518712) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168524464) **SUCCESS, 411/411 CPU tests, 19 groups** at code HEAD `27728045907a1f2111dc4b8340fbea2cc365ff1d`. CPU simulations include A/B/C successful transitions, target identity change rejection, failure recovery, explicit approvals and P1 acceptance gate; no actual DGX GPU, API switch or downtime. Some intermediate development commits had red CI (syntax and test doubles); these were corrected and preserved in Actions history. CI PASS does not certify production safety.

Read [P3 source operation contract](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md) before read-only planning. Next runtime step requires independent operator approval, actual current DGX preflight and fallback arrangement; P3 stage A/B/C status remains **NOT_RUN/NOT_QUALIFIED** and Draft PR stays unmerged.

---

## 2026-11-06 — Actual DGX P2 benchmark PASS (operator-supplied, supersedes earlier plan-only status)

**P2 COMPLETED within the approved bounded trial scope.** Operator-provided DGX execution output, not independent access to the private report bytes: `BENCH_PASS_RESTORED_VERIFIED`, executed=true, target API ready=true, inference=true, benchmark 3/3 streaming requests (64 max output tokens, concurrency=1, seed=1234), original Flash-Next `RESTORED` without issues, and fresh Wizard post-restore `LIVE_SERVICE_VERIFIED` for `qwen3.8-flash-next`. Original Docker image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. This **supersedes older sections below saying P2 benchmark NOT_RUN**; do not repeat P2/download/build.

Actual client metrics supplied: TTFT P50=0.179349s, P95=28.977990s; E2E latency P50=5.818283s, P95=34.609889s; mean E2E throughput=7.9002 tok/s; mean **client decode proxy**=11.1801 tok/s; mean **prompt-ingest proxy**=246.2744 tok/s. Per-request TTFT 32.177839/0.179349/0.178962s; latency 37.808956/5.818283/5.813945s, each 64 completion tokens. First-request cold overhead hypothesis is NOT confirmed. GPU memory/peak unavailable, engine decode/prefill throughput unmeasured, no extended concurrency/vision/tools acceptance for 27B.

DGX private evidence paths: `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`, `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.json`, `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.target.log`. These are operator-reported paths, not contents independently read by GitHub tools. Source revision `482ca0f3832238542f8f5295dde86b5f22711d80`.

**P2 STAGE CLOSED. P3 NOT STARTED** and not authorized for live changes. D-034 manual order: independent approval Flash-Next→27B (A), independent 27B→Flash-Next (B), resolve P1 doctor/inventory-plan rc=3 and functional/TTFT/tokens/sec evidence on Flash-Next, then independent final Flash-Next→27B (C); expected final 27B active. Old `roundtrip` executor is retired. Source-only P3 engineering is permissible but no GPU/service mutation, no auto progression, no PR merge.

---

## 2026-11-06 — REVISED P3 MANUAL sequence; P2 must STOP, never auto enter P3

User decision D-034 supersedes previous P3 two-cycle roundtrip. **P2 benchmark still NOT RUN** on DGX; previous latest actual DGX only `--plan READY_TO_REQUEST_TRIAL_APPROVAL` with `issues=[]`, and prior first GPU smoke `PASS_RESTORED` plus Flash-Next `LIVE_SERVICE_VERIFIED`. No change to live model. After separately approved actual P2 measured PASS, **terminate P2 workflow** and wait for explicit P3 instruction and a new separate scoped approval.

P3 revised order: explicit operator P3 entry; because P2 leaves Flash-Next running, separately approve **Flash-Next → 27B** to establish 27B source; verify **27B → Flash-Next**; address outstanding P1 issues/redo functional probes and actual benchmark on verified Flash-Next; only then approve **Flash-Next → 27B** and verify 27B as final active model. No phase auto-chaining. P1 pending: historic `doctor`/`inventory-plan` rc=3 causes unresolved, actual numeric TTFT/throughput metrics not supplied (despite earlier P1 smoke and bounded bench PASS). No P1 metrics invented.

Source changes: old `scripts/manager/p3_27b_roundtrip.py` plan/execute now **permanently BLOCKED**; Wizard `roundtrip` route retired. New `./wizard.sh switch flash-next-27b sequence --plan --json` provides read-only manual-entry plan and **never** an executable ID; new persistent P3 service-switch executor not yet implemented/qualified. This change is policy/source-only and does not alter P2's measured benchmark/restore executor. See `docs/P3-MANUAL-TRANSITION-SEQUENCE-20261106.md`.

---

## 2026-11-06 — Actual DGX P2 benchmark READ-ONLY plan READY; P3 prerequisite BLOCKED as designed

Operator ran `./wizard.sh model 27b benchmark --plan --json` on the actual DGX and received `status=READY_TO_REQUEST_TRIAL_APPROVAL`, `issues=[]`, `executed=false`, `gpu_verified=false`, benchmark profile `p2-27b-api-benchmark-v1` (3 requests, 64 max tokens, seed 1234, concurrency 1, model `qwen3.8-27b`, stream). Verified source exact Docker ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`; original image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. The plan ID `2f76c3b03865b6a15a5c2fe8f316231f532fbf8b7fe178ffd00db8383edc3399` expired **2026-11-06 12:20 KST** (epoch 1793935200), and MUST NOT be reused for execution. **This was read-only readiness, not actual P2 GPU benchmark PASS**.

Operator also ran `./wizard.sh switch flash-next-27b roundtrip --plan --json`: `status=BLOCKED`, `issues=["P2_BENCHMARK_RECEIPT_NOT_FOUND"]`, `plan_id=null`, `executed=false`, `cycles=2`. This is the **correct** P3 prerequisite guard; P3 cannot begin until actual approved P2 benchmark returns `BENCH_PASS_RESTORED_VERIFIED` and a private `*.benchmark.json` receipt exists.

**Next**: operator authorizes a fresh Flash-Next service downtime separately. During that maintenance window, regenerate the **new** P2 benchmark plan ID using the read-only Wizard, then explicitly execute with fresh `--approve-plan` and `--ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME`. Any nonempty issues/blocker prevents execution. An approved P2 run interrupts :8000 and must attempt original Flash-Next restoration. Read its actual metrics + evidence and independently verify restored model before any P3 plan/execute. Preserve original Flash-Next until authorized; no GPU test was performed merely by these two plan queries.

---

## 2026-11-06 — P2 bounded GPU benchmark and P3 gated two-cycle trial implemented in SOURCE; DGX NOT RUN

**Priority corrected:** stop feature drift into model inventory/Orcarouter; original target is **P2 27B benchmark, then P3 Flash-Next ↔ 27B verification**. Existing real DGX P2 first-launch `PASS_RESTORED` and latest live `LIVE_SERVICE_VERIFIED` remain valid. P2 timed benchmark **NOT_RUN**; P3 repeated roundtrip **NOT_RUN**; permanent production switch remains unimplemented.

Added `scripts/manager/p2_27b_benchmark.py`, Wizard `./wizard.sh model 27b benchmark --plan --json` and exact-scoped `--execute` route. P2 benchmark plans have a **different ID** from one-shot smoke. Execute reuses the real proven `p2_27b_gpu_trial.execute` original-container lock/restore; measures 3 bounded streaming text prompts, client TTFT/latency, e2e throughput and separate explicitly labeled prefill/decode **proxies** (not engine metrics), best-effort point GPU memory samples (not peak). Actual 27B text benchmark measures yet **not available**. Local private JSON `*.benchmark.json` records final result and fresh Wizard post-restore API identity.

Added `scripts/manager/p3_27b_roundtrip.py` and Wizard `./wizard.sh switch flash-next-27b roundtrip --plan --json`. It **fails closed until a real latest P2 benchmark receipt reports `BENCH_PASS_RESTORED_VERIFIED`**. Its optional separately approved `--execute` reuses the guarded trial executor exactly twice, requiring the original Flash-Next container ID and API service state to be verified after **every** cycle, aborting on failure. This is **two temporary forward-and-return cycles**, NOT a persistent model-switch implementation and NOT automatically qualified without actual DGX evidence. No GPU/service changed by source-only development.

Canonical new instructions: [P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md](../docs/P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md). The next DGX action is **read-only P2 benchmark --plan** after clean fast-forward; use no GPU execute until new explicit downtime approval.

---

## 2026-11-06 — ACTUAL DGX installed-model inventory PASS; legacy Orcarouter confirmed preserved

Operator executed **`./wizard.sh model list --installed --json`** on DGX after pulling the new Wizard. Actual result `status=READ_ONLY_INVENTORY`, `scope=CONFIGURED_CACHE_ROOTS_ONLY`, `service_status=LIVE_SERVICE_VERIFIED`, `active_model_observed=flash-next`, `active_api_identity_verified=true`, `executed=false`, `operations_enabled=false`, `other_cached_repos_truncated=false`, `service_issues=[]`.

The scanner checked `/home/inlc/.cache/huggingface` and `/home/inlc/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`. Registered original NVIDIA Flash-Next revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` has **11/11** indexed nonempty shards and `source_files_present=true` in the default cache; it is also the **only observed active/verified API model**. Registered NVIDIA Qwen3.8-27B revision `482ca0f3832238542f8f5295dde86b5f22711d80` has **3/3** indexed shards and `source_files_present=true` in the default cache, but is not currently serving. Previous actual 27B one-shot GPU trial separately returned `PASS_RESTORED`; scanner's individual `runtime_qualified=false` only means source inventory does not requalify GPU runtime.

**Crucial newly observed fact:** The original `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` revision `3a3b63161c0745390e5270179af42e46efc70799` is **still present** in the legacy `yslab-qwen38-bf16ple-dgx-spark/hf-cache`: **17/17** nonempty indexed shards, tokenizer/config/index true, `issues=[]`, `source_files_present=true`. Its existing `recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2` directory is **also present**. Therefore the source/recipe directory is **not deleted**, and redownload must not be performed merely because Orcarouter is inactive. **NOT** yet established: recipe file completeness/identity, BF16 PLE/MTP build/runtime compatibility, reinstallation feasibility, API functionality or benchmarks. Orcarouter remains inactive and runtime-unqualified.

Four **unregistered snapshot sightings only**, not verified full checkpoints: `maurienne-ai/Qwen3.8-27B-DFlash2-NVFP4-RTNcal` rev `bd7a934213c47a9e7ef69eef36bb3325f47fd1f1`; `RadixArk/Qwen3.8-27B-NVFP4` rev `52d1adc5f38aa5ebf099c29ed7025ba34cfbb854`; `dealignai/Qwen3.8-Flash-Next-ABLITERATED-NVFP4` rev `be794b990578ef3031eccf9f28e675a289a09ee9`; `RadixArk/Qwen3.8-Flash-Next-NVFP4` rev `7b719225242aacd3dbd3f9407468c2ee9a9d2594`. Do **not** automatically register, switch to or delete any of these.

This is actual DGX source-preservation and current-service evidence, **not** permission to move/delete files, switch models, benchmark GPU, or modify the operational Flash-Next container. It supersedes prior `NOT_YET_RUN` references to the installed-model CLI below.

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

## 2026-11-06 — ACTUAL P2 27B GPU PASS_RESTORED; manifest-led Wizard service status is canonical

**Latest actual DGX operator JSON:** one-shot NVIDIA Qwen3.8-27B GPU trial `executed=true`, `target_api_ready=true`, `inference_ok=true`, `trial=PASS`, `restoration={"status":"RESTORED","issues":[]}`, overall `status=PASS_RESTORED`. First real GPU load, bounded inference and normal successful original Flash-Next restoration now confirmed. Original private DGX evidence `/home/inlc/.local/state/blazux-wizard/p2/20261105T230229Z-a4fc14cf8079.json` and `.target.log` exist according to operator stdout; contents **not independently inspected**. Historical older NOT_RUN sections below are superseded by this result; this does not verify full benchmark, MTP, large contexts, tools/vision, permanent switching or failure-mode rollback.

**Service verification decision:** user prefers manifest-based Wizard over manual `docker ps`/`curl`. Implemented `./wizard.sh service manager status --json` to combine `runtimes/service-policy.json`, read-only fresh container/port Manifest and localhost `/health` + `/v1/models` exact expected served model ID in a **single** status response. New `scripts/manager/service_status.py` (source only) status `LIVE_SERVICE_VERIFIED` iff checks all pass, otherwise `BLOCKED` and explicit issues. `inventory`, `health`, `logs` retain individual read-only diagnostic commands. Status does not assert historical rollback provenance or GPU exclusivity outside managed models. **New unified-status command has NOT_RUN on actual DGX**; do not call it PASS until operator executes it.

Next: operator fast-forwards clean branch, runs `./wizard.sh service manager status --json`, expects `flash-next` and `qwen3.8-flash-next` with all checks true. Source code/CI stage and GPU run stage stay distinct. Keep Draft PR #1 unmerged; no further Flash-Next stop/27B restart without fresh explicit approval. Detailed run receipt: [P2-27B-GPU-TRIAL-PASS-20261106.md](P2-27B-GPU-TRIAL-PASS-20261106.md).

---

## 2026-11-06 — Qwen3.8-27B CPU registration PASS; explicit one-shot GPU trial prepared (NOT RUN)

Operator DGX returned **all nine import/registry checks true**, `issues: []`, `status: IMPORT_AND_REGISTRY_PRESENT_UNQUALIFIED`, `modelopt_mixed_cli_name: true`, `schema_version: 2`. These are real restricted CPU-only imports for installed Qwen3.8-27B checkpoint's internal `Qwen3_5ForConditionalGeneration` loader and vLLM ModelOpt mixed precision registry. They do **not** prove CUDA kernels or GPU model load. `nvidia/Qwen3.8-27B-NVFP4` remains the target model; `qwen3_5` is **only** the checkpoint's internal architecture key.

User requested moving to actual GPU startup rather than more source-only gates and provided comparative external references (MiaAI-Lab, NVIDIA DGX forum, eugr/spark-vllm-docker). Key distinction: MiaAI-Lab runs `unsloth/Qwen3.8-27B-NVFP4` with compressed-tensors; operator's pinned `nvidia/Qwen3.8-27B-NVFP4` uses ModelOpt MIXED FP8/NVFP4, so do NOT copy `--quantization compressed-tensors` or alternate images/quantization defaults. eugr supports NVIDIA checkpoint; GB10 community references require architecture-specific NVFP4 kernels, but do not prove this exact local vLLM 0.32 image.

New `scripts/manager/p2_27b_gpu_trial.py` and `scripts/serve_27b.sh --trial-plan` / `--trial-execute` implement **one-shot experimental GPU load and mandatory return to Flash-Next**, not a permanent model switch. Default/read-only plan checks pinned checkpoint, image, current source API identity, exact original container ID and restart policy, host :8000, target name available, no competing GPU-enabled Docker container. The **only** execute path requires the full SHA256 plan ID plus explicit typed `I_ACCEPT_FLASH_NEXT_DOWNTIME` acknowledgment within the approval time window and revalidates live state under local lock. On execution: stop existing `qwen38-flash` (never remove), launch NVIDIA ModelOpt 27B with 8k ctx/one seq/0.70 eager (no PLE/MTP), wait exact API ID, run one bounded inference, save local bounded trial logs, stop/rm ONLY own labeled trial container, docker start ORIGINAL Flash-Next and verify :8000 original served ID. If rollback cannot be proven, report `RECOVERY_FAILED` (manual recovery required); SIGKILL/power loss/Docker faults are not guaranteed to recover. **No DGX GPU trial has run yet.**

Source branch HEAD before handoff docs `ea28b0c0ddbe085782617cc1445c2fcaf613f2a4`; CI run `42124595787` **SUCCESS 354/354 CPU tests, 16 suites**. Draft PR #1 remains unmerged; original operational GPU service untouched by source work.

---

## 2026-11-06 — Actual DGX 27B Python import succeeded; ModelOpt name audit false negative fixed

**Real operator DGX** on branch HEAD `9db92f7` executed `./scripts/temporary/p2-27b-loader-import-audit.sh --plan` (correct local image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, no GPU/ports/weights/changes) and explicit `--execute-cpu-only` in restricted `runc`. The container reported `qwen3_5_module_imported=true`, `qwen3_5_class_present=true`, `modelopt_module_imported=true`, `modelopt_mixed_class_present=true`, `modelopt_nvfp4_class_present=true`. **All actual imports/class surfaces passed.** However `modelopt_mixed_cli_name=false` and `MODEL_OPT_NAME_LOOKUP_FAILED:TypeError` were caused by **our checker** incorrectly calling `ModelOptMixedPrecisionConfig.get_name()` on the class. The installed vLLM 0.32 has an instance method `get_name(self)`, not a static/classmethod. CPU container also printed nonfatal `vllm._C ModuleNotFoundError` and `No CUDA runtime is found` warnings; they do not establish GPU incompatibility or launch success. **No GPU, weights or inference were run.**

Fixed in source commit `0a14f189c4dae61827298fde46f3148d316f8c72`: now obtain `get_quantization_config("modelopt_mixed")` from the vLLM public quant registry and verify class identity against the imported `ModelOptMixedPrecisionConfig`; no instance construction or mis-bound `get_name(self)` call. Three additional tests plus regression for instance-method signature, wrong registry, exceptions; GitHub Actions run `42121160545` **SUCCESS 336/336 tests (16 suites)**. **Updated checker has NOT_RUN on real DGX yet**; actual quant-registry result remains pending, 27B GPU/launch and Flash-Next recovery remain unverified/blocked.

---

## 2026-11-06 — Real DGX after model-specific serve split; CPU-only Python loader import probe prepared

**Actual operator DGX evidence (new):** clean source pull `b1c9b2e..c44aa72`, then `c44aa72..99dde4c` (split `serve.sh` entrypoints into Flash-Next/27B). Operator ran `./wizard.sh model 27b plan --for-action start --launch-preview --json` before the split, then `./scripts/serve_27b.sh --status` and `--plan` **after the split**; both paths returned the expected read-only JSON, no errors. Latest `--status`: exact pinned NVIDIA 27B source/architecture ModelOpt FP8 208 + NVFP4 193, image ARM64 v0.32, `runtime_qualified=false`, six remaining GPU/start/rollback issues. Latest `--plan`: `observed_source.api_identity_confirmed=true`, source container `qwen38-flash`, original source image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, **identical to candidate 27B local image ID**; target `command_preview` includes pinned snapshot `482ca0f3832238542f8f5295dde86b5f22711d80`, `modelopt_mixed`, context 8192, max seqs 1, mem fraction 0.70, eager. Status `BLOCKED`, `executed=false`, `plan_id=null`, `operations_enabled=false`. Original Flash-Next API remains observed and identity-confirmed on :8000. This is **not** 27B GPU/loader/bench/rollback proof.

**New source-only follow-up:** `scripts/manager/p2_27b_loader_import_audit.py` and `scripts/temporary/p2-27b-loader-import-audit.sh` for isolated CPU-only actual installed module imports and `ModelOptMixedPrecisionConfig.get_name() == modelopt_mixed`. Default `--plan` only inspects Docker image; explicit `--execute-cpu-only` uses ephemeral restricted runc/no GPU/network/cache/ports. The new import probe **has not been run on real DGX**. Source commit `834c750fc966f73c885fcfc5d81d054a60ae419e` CI `42112730764` **SUCCESS 333/333 CPU tests**. Even import PASS cannot authorize 27B GPU start.

---

## 2026-11-06 — Model-specific serve entrypoints separated (Flash-Next behavior preserved)

Operator requested model-specific serving files rather than maintaining Flash-Next and 27B launch details in one `serve.sh`.

**Implemented**: the original full Flash-Next implementation lives at `scripts/serve_flash-next.sh` (same configuration/modes/guards and default behavior). `flash` directly calls this file. `scripts/serve.sh` is now a thin backward-compatible dispatcher: no args -> Flash-Next, explicit `flash-next` -> Flash-Next, `27b --plan` (or `--model 27b --plan`) -> `scripts/serve_27b.sh` with source-only preview. `scripts/serve_27b.sh` owns the P2 model-specific entrypoint but **only supports read-only plan/status**; direct GPU --execute/start/switch remains blocked until a verified separate approved runtime transaction. The Flash-Next runner refuses an attempted NVIDIA 27B checkpoint override, so PLE/MTP presets never silently reach 27B.

**CI:** source commit `67a54afc615e51f207f12238e8473200c62a1aad` GitHub Actions run `42111216055` SUCCESS, **325/325 CPU tests PASS** across 16 suites. Original Flash-Next live DGX service was not modified in this development step; no 27B GPU run, service stop/switch or rollback performed. New documentation commit CI to be verified.

---

## 2026-11-06 — DGX pinned 27B quant + image AST PASS; dedicated launch *preview* added

**New actual operator DGX evidence supersedes old checklists:**
- `./wizard.sh model 27b status --inspect-runtime --json` confirmed exact pinned source `482ca0f3832238542f8f5295dde86b5f22711d80`; `quantization_audit.status=PINNED_METADATA_PARSED_UNQUALIFIED`, `producer=modelopt`, `quant_algo=MIXED_PRECISION`, **FP8=208, NVFP4=193, 401 total**, `issues=[]`, CPU metadata only.
- `./scripts/temporary/p2-27b-image-audit.sh --plan` returned immutable local image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, no execution.
- Operator explicitly ran `--execute-cpu-only`: `SOURCE_SURFACES_PRESENT_UNQUALIFIED`, **four of four checks true**: 27B model registry architecture, `Qwen3_5ForConditionalGeneration` class, ModelOpt NVFP4/FP8 mixed algorithms and mixed config classes. Actual installed image source locations: `vllm/model_executor/models/registry.py`, `.../models/qwen3_5.py`, `.../layers/quantization/modelopt.py`. This test ran one CPU-only runc audit container; GPU `false`, launch authority `false`.
- Flash-Next remains observed on port 8000. **27B GPU loading, GPU kernels, API, benchmarks and rollback remain NOT_RUN**. Source PASS does not close those gates.

**New P2 implementation:** `scripts/manager/p2_27b_launch_preview.py` and `./wizard.sh model 27b plan --for-action start --launch-preview --json` implement an entirely read-only 27B-specific candidate argv and live-source API identity preview; **never execute** the candidate `docker run` argv. Initial **unvalidated** settings: `modelopt_mixed`, 8192 context, 1 sequence, 0.70 memory fraction, eager, PLE/MTP disabled. Source commit `ae4490d66d9c1b9306435165a9821253ee6f38d7`, GitHub Actions run `42110115101` **SUCCESS 315/315 CPU tests**. The new docs commit requires its own CI verification.

---

## 2026-11-06 — Exact pinned ModelOpt mixed-precision metadata audit added to Wizard

On the previous real DGX read-only preflight, source is pinned and configuration reports `quant_method=modelopt`, but **layer distribution has not yet been observed**. New SOURCE `scripts/manager/p2_27b_quant_audit.py` now parses only `hf_quant_config.json` in the immutable NVIDIA 27B snapshot, rejects oversized/malformed/unexpected algorithms, reports `MIXED_PRECISION`, exact per-algorithm counts, and adds `quantization_audit` to the existing `status --inspect-runtime` JSON. It does not inspect weights or approve runtime execution. Actual DGX run of this updated command remains **NOT_RUN**.

**Latest source/CI:** `cd63f25f0bf7282ea06dbb13c3499798394322b0` — GitHub Actions run `42065472163` **SUCCESS, 303/303 CPU tests PASS**, including nine additional quantization unit tests. Existing single active model and Flash-Next :8000 unchanged. Further documentation commit requires final HEAD CI verification.

---

## 2026-11-06 — DGX P2 runtime metadata verified; installed-image source audit developed

**New actual operator DGX evidence (2026-11-06 KST):** after clean fast-forward from `e99914c` to `edf0968`, `./wizard.sh model 27b status --inspect-runtime --json` returned `source_files_present=true`, `source_checkpoint_status=SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, pinned revision `482ca0f3832238542f8f5295dde86b5f22711d80`; `Qwen3_5ForConditionalGeneration`, `qwen3_5`, `modelopt`, context 262144, vision config present; host `aarch64`, Docker image ARM64/Linux with base label `v0.32`, local image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. Flash-Next observed running and port 8000 listening; download no longer running. `repo_digests=[]`, `gpu_verified=false`, `runtime_qualified=false`; `status=BLOCKED` with six unresolved runtime/transition gates. This is read-only host evidence, not 27B GPU support proof.

**Source work:** added `scripts/manager/p2_27b_image_audit.py` and `scripts/temporary/p2-27b-image-audit.sh`. Default `--plan` only reads local image ID; explicit `--execute-cpu-only` creates a short-lived, isolated runc container with no GPU, network, port, cache or service changes and AST-parses installed vLLM registry/Qwen3.5/ModelOpt source. Even `SOURCE_SURFACES_PRESENT_UNQUALIFIED` is not a 27B load PASS. GitHub Actions on source commit `acf5d64` PASS, **294/294 CPU tests**, invalid recipe still blocked. New documentation commit needs CI confirmation.

---

## 2026-11-06 — P2 NVIDIA 27B download PASS confirmed; read-only runtime qualification added

**Operator DGX evidence (2026-11-05 KST):** approved `./wizard.sh model 27b download --guided` completed **19/19** files, return code **0**. NVIDIA repo `nvidia/Qwen3.8-27B-NVFP4`, immutable revision `482ca0f3832238542f8f5295dde86b5f22711d80`, checkpoint result `SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, `issues=[]`, `gpu_verified=false`, runtime `NOT_RUN`, evidence `/home/inlc/.local/state/blazux-wizard/p2/evidence/20261105T150433Z-bd8cf46ef5.json`. This **supersedes** older 84%-in-progress and NOT_RUN download notes below; do not redownload without new corruption evidence.

**Current GitHub SOURCE addition:** `scripts/manager/p2_27b_qualification.py` and `./wizard.sh model 27b status --inspect-runtime --json` expose bounded, read-only pinned snapshot/config, modelopt architecture, host ARM64, exact Docker image metadata and actual service inventory, while retaining explicit blockers for unproven vLLM 0.32 loader, mixed NVFP4/FP8 GPU kernels, immutable recipe digest, memory/context and rollback. CPU regression cases added. **Neither a matching image tag nor downloaded files grant startup approval.** The existing Flash-Next on host :8000 remains protected; no GPU start, switch, cleanup or DGX command was run by the source session. Latest GitHub CI verdict requires post-commit check.

---## 2026-11-06 — full P1–P7 Wizard source implemented; P2–P7 adapters to debug

**Operator instruction D-021:** create the entire Wizard now, even if parts cannot yet execute; as actual P2 onward develops, debug/qualify individual backend adapters. Completed GitHub SOURCE:
- `wizard/console.py`: simple 3-choice primary TTY, per-model Continue + all ten actions, service status/health/bounded logs/start/stop/restart/rollback/proxy/gateway, advanced P3/P4/P6/P7 with explicit switch pair and guarded legacy menu.
- `wizard/workflow.py`: unified three-model action matrix, read-only machine `workflow MODEL --json` and `--for-action ACTION`; existing P1 guarded backend and P2 approved exact-revision downloader reused. Fixed a real P1 UX safety issue: never offer/invoke P1 guided start while another managed model is active or the inventory is unknown.
- `wizard/roadmap.py`: seven-stage P1–P7 evidence-scoped acceptance overview, CLI `roadmap --json`. No source-only result counts as GPU/benchmark PASS.
- `scripts/manager/service_logs.py`: bounded, opt-in read-only tail for exactly observed managed service; no Docker mutation, no automatic log upload.
- Added focused CPU regression suites and CI for full console/P1–P7 workflow, P7 dashboard and log limits. Docs/CLI/decisions updated. GitHub PR #1 remains Draft until DGX verification.

**DGX actual state:** user last supplied proof that the exact-revision 27B download began (`Fetching 19 files: 84%`). No later completion, evidence receipt, pinned shard audit, 27B vLLM-0.32 ARM64 start, API bench, P3/P6 switch or recovery have been observed; **do not claim these PASS**. The existing Flash-Next `:8000` deployment and download are untouched by this source-only work. User should not pull/interrupt until the active download exits. SOURCE/CPU CI verdict requires latest HEAD readback.

## 2026-11-05 — Batch A plus read-only service health/switch preview complete in SOURCE

Model-first Wizard UI, legacy-compatible selection CLI and in-flight 27B detection implemented. Additional GitHub SOURCE: bounded localhost `/health`+`/v1/models` API identity probe exposed via `./wizard.sh service manager health --json`, and fail-closed `service_transition_preview.py` attached to model selection if an alternate running model is observed. Preview specifies stop-old → port 8000 free → start-target → verify identity → journal commit and rollback, but **always BLOCKED/plan_id=null** until vLLM 0.32 target runtime, original recovery and approved executor are qualified. Existing P1 runner and 27B guarded downloader remain unchanged. Final CI still requires HEAD check; source-only API/preview tests do not constitute actual DGX execution.

DGX transfer: user reported `Fetching 19 files: 84%` after successful download plan approval. Started only; **no completion or integrity evidence yet**. Do not ask operator to pull new commits or disrupt active download. Existing Flash-Next :8000 remains protected.

## 2026-11-05 — model-first Wizard SOURCE implemented during user-owned 27B download (current)

**Operator DGX evidence:** on branch `feature/recipe-wizard-handoff`, `./wizard.sh model 27b download --guided` accepted a new full plan ID `e7d3ee776b65c3c5e3395fbeff5d0d739ef432028c030df8d604578412570c49` and printed `Fetching 19 files: 84% (16/19)`. This **establishes actual download started**; no process completion, receipt audit/evidence path, 27B vLLM-0.32 startup, GPU benchmark or switching results were supplied. Host preflight observed Flash-Next container `qwen38-flash` Up, bound `:8000`, approx 322 GiB free before download. **Do not recommend `git pull` or interfere with the operator's running download until it completes.**

Operator accepted **D-020 model-first primary UI**: `./wizard.sh` → 1 Select/run model, 2 Service, 3 Advanced, 0 Exit. The TTY selection and `./wizard.sh select 27b --json` share read-only `wizard/quickstart.py` planner. Model choices Flash-Next, NVIDIA 27B, Orcarouter. `service_manifest.py` now observes `qwen38-27b-dl` to suppress duplicate transfers. `runtimes/service-policy.json` registers Orcarouter as an **unqualified placeholder only**. Existing `p1_wizard.py` + P1 API/bench and P2 approved downloader untouched; old CLI aliases remain supported. UI never stops/starts a service by selection, and runtime transition is still BLOCKED until qualified. Definitive plan: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`. GitHub CPU CI verification pending final HEAD; no DGX execution from this coding session.

## 2026-11-05 — P2 guided approval false-positive fixed (source)

Actual DGX operator log: the exact 64-character plan ID `b190c936072038bc55c14c62dd2f9a63e3ddbf5c2e1ebbf0d1710551a7ec21ce` was entered at `./wizard.sh model 27b download --guided`, but execution returned `executed=false` and `PREFLIGHT_CHANGED_REPLAN_REQUIRED`. This **does not** establish that download started. Root cause in source: mutable `free_inodes` (changed by creating the lock/state folder), exact free GiB and Docker human uptime were included in SHA256 fingerprint and changed between approval and locked revalidation. Fixed to hash stable safety-critical identity while still rechecking all capacity/inode/collision conditions after lock. CPU regressions include real directory/lock, uptime/inode/disk drift, changed image and running-state authorization, and low disk fail-closed behavior. Current actual DGX download still `NOT_RUN`; operator must `git pull --ff-only` and use the **new** plan ID from `download --guided`. P1 active service untouched.

## 2026-11-05 — P2 pinned download ready in SOURCE; one-model API policy (supersedes earlier notes)

**Latest user decision:** one active GPU model per DGX; Flash-Next and NVIDIA 27B share host `:8000/v1`. A 27B GPU start requires approved Flash-Next stop → port release → 27B start → verified API → rollback on failure. **No live stop/start/switch is authorized or performed.** Committed `runtimes/service-policy.json` and live read-only `scripts/manager/service_manifest.py`; append-only, atomic, generation-checked `scripts/manager/service_journal.py` is source-only pending qualified executor. `service manager inventory` reports Docker observations with API/GPU verification explicitly false.

**P2 actual download status: NOT_RUN.** NVIDIA 27B was absent from operator-observed `~/.cache/huggingface` at previous HEAD. Official full SHA `482ca0f3832238542f8f5295dde86b5f22711d80` verified from Hugging Face listing. New `scripts/manager/p2_27b_download.py` is a Wizard-backed, exact-plan-approved, no-GPU/no-port download path. Plan requires image ID, >=35GiB free, inode/cache/name/process checks; CLI `./wizard.sh model 27b plan --for-action download --json`, interactive approval `./wizard.sh model 27b download --guided`. The source recipe remains invalid pending vLLM 0.32 loader/image digest qualification. CPU/CI results must be quoted only for the final checked HEAD; no DGX download or benchmark claims. Pinned snapshot audit no longer requires `refs/main`.

## P2 DGX NVIDIA cache absent; Wizard service menu source implementation (2026-11-05)

User-supplied DGX `./wizard.sh model 27b status --inspect-cache --json` after `git pull` to `3f4ef68` returned NVIDIA `nvidia/Qwen3.8-27B-NVFP4` `local_revision=null`, `source_files_present=false`, `indexed_shard_count=0`, `incomplete_blob_files=0`, `issues=[NO_PINNED_LOCAL_SNAPSHOT]`. The earlier RadixArk snapshot does not satisfy this NVIDIA checkpoint. No download has run. New Wizard top-level **service management** menu has a separate guarded `svc` handler; P7 operations remain integrated release acceptance, and 27B gains `download` planning. Both remain source-only/blocked for mutations; they cannot restart/stop the Flash-Next service or launch GPU. See `docs/P2-27B-WIZARD-OPERATIONS.md`.

## P2 operator decision — NVIDIA 27B replaces RadixArk candidate (2026-11-05)

**Current target is `nvidia/Qwen3.8-27B-NVFP4`** per operator instruction. Public NVIDIA model card establishes checkpoint listing and vLLM multi-GPU GB300 example, **not** vLLM 0.32 single-GB10 qualification. Previously supplied DGX read-only inspection returned RadixArk revision `52d1adc5f38aa5ebf099c29ed7025ba34cfbb854`, 3/3 indexed shards, 0 incomplete transfers, zero issues, and a parsed ModelOpt config; this is **historical RadixArk evidence only** and cannot establish NVIDIA cache presence. The Wizard now inspects the `models--nvidia--Qwen3.8-27B-NVFP4` cache and retains fail-closed runtime status. No P2 model download, GPU start, service cutover or cache deletion approved or performed.

## P2 source progress — 2026-11-05 (new session)

GitHub-linked source changes add a bounded, read-only 27B `config.json` inspector to `scripts/manager/p2_27b_inventory.py`: records reported model architecture, model type, quantization method, context length and presence of vision configuration without inferring vLLM 0.32, GPU fit or runtime acceptance. Invalid/oversize JSON is explicitly rejected from `source_files_present`. CPU regression fixtures cover valid, invalid and oversized model config. **SOURCE changes committed; CI must be checked at latest HEAD. DGX/GPU tests NOT_RUN.** No installation, model download, Docker or API changes authorized.

# Current state — active snapshot

## Newest confirmed DGX evidence: P1 API/GPU PASS; P2 source-only (2026-11-05)

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.


## Most recent 2026-11-05 update — baseline vs optional Wizard probes

**Latest operator DGX result (2026-11-05):** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` summary from `--auto-gpu` at `805f8e3e`: source checkpoint and Hybrid are both READY, `source_issues=[]`, `hybrid_issues=[]`, 11 indexed source and Hybrid shards resolved, `api_model_ids=["qwen3.8-flash-next"]`, verify and benchmark plans each READY, yet **verify action returned FAIL** and benchmark BLOCKED by verification gate. Original console suppressed the Wizard's failure evidence location because it parsed the JSON outcome only on returncode 0, even though Wizard writes evidence for returncode 2. This is an actual attempted API/GPU verification with FAIL outcome, not evidence of a broken default Blazux model. Exact failing subprobe/error still unconfirmed until raw report is examined.

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

**SOURCE/CI validation (not DGX):** `391a2844f4c8549e282eae3e266806c89801ad1a`, GitHub push and PR checks 2/2 SUCCESS, each 15 manifest + 10 inventory + 13 launcher + 1 mode + 102 P1 + 32 router = **173/173 CPU tests PASS**. Real DGX execution against this fix has NOT_RUN; prior verify FAIL remains unresolved until this new code runs.


**Snapshot written:** 2026-11-05 (KST) · **Status:** `WIZARD_P1_P7_ROUTER_SOURCE_IMPLEMENTED / P1_GPU_NOT_VERIFIED` · **Implementation:** Flash-Next default port 8000, N2 read-only Inventory and Wizard doctor/plan; **GPU:** `VERIFY_ATTEMPTED_FAIL`; new source fix `NOT_RUN_ON_DGX`.

## Latest DGX checkpoint update and P1 diagnostic blocker (2026-11-05)

**DGX operator update, 2026-11-05:** The operator explicitly confirms the NVIDIA Flash-Next download has finished. Their submitted terminal output after `git pull` to `dea7c5aa183da770b6b467288f2f6eedf8e94946` shows `bash scripts/temporary/p1-post-download.sh` produced report `/home/inlc/blazux-p1-reports/20261105T052545Z-1e6ec592/result.json`; current branch and clean tracked worktree checks PASS; no setup process found in the process scan. HTTP `/health` and `/v1/models` command exit codes are 0 **but actual served model ID was not included in the console summary**. Wizard doctor and inventory plan returned exit code 3; both P1 verify/benchmark plans BLOCKED: `checkpoint_downloading_or_incomplete`, `hybrid_not_prepared_or_incomplete`; no Wizard GPU/bench requests executed. The `checkpoint_downloading_or_incomplete` string is a **generic validation failure**, not proof that the download continues. The apparent mismatch needs read-only evidence before any setup, repair, download, switch or deletion.

**Diagnosis implementation validation:** SOURCE/CPU CI verified at `4c0041dd230e2abe22ba8379aca74068933ecece`: GitHub push and PR both SUCCESS, each **138/138 CPU tests PASS** (15 manifest + 10 inventory + 13 launcher + 1 executable-mode + 67 P1 + 32 Wizard router). The earlier `eb759ad` source attempt failed its tests because the optional new diagnostic key was absent from an old fake fixture; fixed in `4c0041d` without changing runtime assets. Real DGX evidence still pending.

**New read-only diagnosis:** `scripts/temporary/p1_cache_diagnosis.py` is called from `p1-post-download.sh`. It records `refs/main`, `refs/master`, actual snapshot and Hybrid file issues, remaining `.incomplete` names count and strict P1 Wizard audit. Source/CI evidence is separate; it cannot claim the weights actually need downloading. No automatic repair. Next action is operator `git pull --ff-only` and a single `bash scripts/temporary/p1-post-download.sh --inspect-only`; review `cache_diagnosis` and `checks.models.stdout` before planning any GPU test.

## Latest root-cause split: Blazux default support vs Wizard regression

**2026-11-05 P1 regression analysis:** NVIDIA's default `nvidia/Qwen3.8-Flash-Next-NVFP4` is supported by Blazux. The official `fc694b5` snapshot distributes `model.safetensors.index.json` (~31.3 MB) and `tokenizer.json` (~12.8 MB). Our new P1 audit erroneously rejected an otherwise-valid index above 16 MiB; code changed to a bounded 64 MiB maximum. **However the operator's specific issues** `model.safetensors.index.json` and `tokenizer.json` arise at the initial `_good_file` stage, *before* parsing/size checks. Thus the artificial size cap does not by itself explain the reported failures. The Hybrid marker exists, but Hybrid `tokenizer.json` also fails. Do not conflate claimed download completion with all snapshot symlinks resolving correctly; investigate metadata file existence, symlink resolution, size and repository containment first.

**Mitigation:** source commit `66c6c448c1922f958886fa4696c403a4b6227685` passes 145/145 CPU tests/job in 2/2 GitHub CI checks; **DGX field-level metadata evidence still pending**. Next operator use is a single `scripts/temporary/p1-post-download.sh --inspect-only` after Git Pull. No active model/container/cache mutation.

## 2026-11-05 — Blazux metadata-symlink parity / P1 GPU approval update

**Operator DGX facts (2026-11-05):** The latest post-download diagnostic returned `api_model_ids=["qwen3.8-flash-next"]`, `refs/main=fc694b54fb0174e0913e6adf86691ef85a4ead47`, 0 incomplete HF blobs, a source index and tokenizer that are **existing nonempty symlinks whose targets resolve outside the model repository**, and a Hybrid tokenizer with the same layout. The Hybrid index is a normal 31,907,813-byte file and the `.prepared` marker exists. These observations show the previous `TARGET_OUTSIDE_REPOSITORY` reason is a **new P1 checker policy stricter than Blazux's original `os.path.exists`-based policy**; they do not establish that any metadata is missing. Previous plans were blocked before actual GPU verification or benchmark. The user explicitly allows non-disruptive GPU compute tests to run without separate per-step approvals, provided the actual target service is confirmed. The presence of an API response means some server is listening; do NOT assume there are literally no processes running or stop/replace any service.

**Implementation:** P1 asset audit now accepts existing nonempty external metadata symlinks for just `model.safetensors.index.json` and `tokenizer.json`; referenced weight shards still cannot escape the model repository. Diagnostic reports `p1_metadata_link_compatible` and target size. The one-command temporary runner gets `--auto-gpu` for verify → benchmark, *with exact fresh Wizard plan IDs passed internally and independently rechecked*. No model lifecycle actions added. **SOURCE/CI verification:** commit `0063b0e004902408f980c155076c098d49d4569e`, 2/2 GitHub Actions SUCCESS, **155/155 CPU tests PASS in each job** (15 manifest + 10 inventory + 13 launcher + 1 mode + 84 P1 + 32 router). **Actual host GPU/API tests remain NOT_RUN** pending operator's new bundle output.

## Confirmed user goal — Wizard-first, P1 through P7

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

**Current P1 exit gate:** Wizard handles preflight → pinned recipe/image/checkpoint verification → explicit plan/approval → setup/prepare → model serve → /v1/models + reasoning/tool/vision smoke → reproducible benchmark (throughput, TTFT, peak resource, seed/config) → evidence export → safe failure/recovery. No GPU/benchmark exit claim is permitted before real DGX measurements.

**CI readback:** At `017319a5394155797bcb7e5c933ccef35080d669`, two GitHub Actions `manifest` jobs succeeded, 39/39 CPU tests per job (15 manifest + 10 inventory + 13 launch + 1 executable-mode). This is **CI PASS only**, not P1 acceptance. Actual HEAD must still be fetched per session.

## Repository/branch tracking

| Item | Last verified state |
|---|---|
| New fork | `kjlee-inlct/qwen3.8-Flash-DGX` |
| Upstream `main` baseline | `b0aa8b77604139557169387b2fa8386355d8b651` |
| Fork `main` baseline at branch creation | `b0aa8b77604139557169387b2fa8386355d8b651` |
| **Active work branch** | `feature/recipe-wizard-handoff` — created from fork `main` |
| Parallel Orcarouter branch | `feature/orcarouter-bf16-adapter@620598c30cfe3521af99a935caf0baf5b83556d8` (as last checked) |
| Parallel Orcarouter design | `docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md` on the parallel branch |
| Old Preview repository | `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark`; frozen preservation, historic `feature/blazux-phase6-runtime-gates@2e6a5794b0fe282ae4bf6f4852acd919fea6d55a` |
| New branch exact HEAD | **Read actual GitHub branch HEAD**. Do not embed a file's own eventual HEAD as authoritative; the branch commit changes when this file changes |
| Draft PR | [#1 — recipe wizard roadmap and handoff](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) against `main`; open, not merged |
| PR CI | New 2026-11-05 implementation commit 7e8f4a1: manifest 15/15 PASS, Inventory 10/10 PASS; **4 launcher tests FAIL (exit 126)** because executable mode lost. Follow-up commit restores script modes and adds regression; **recheck HEAD CI**. Prior verified HEAD `017319a` has two successful CI jobs (39/39 CPU tests each); live HEAD check required each session. |

## Operational environment — protect; verify fresh

**User report 2026-11-05:** prior operating services have all been deleted; requests Blazux default NVIDIA Flash-Next on the **same external :8000/v1 API port**. This is a user-reported change, not yet independently observed with current DGX Docker/ss/df commands. Historical prior-session values (not rechecked):
- Container `qwen38-flash-orca-uncensored-bf16-mtp`.
- Container ID `3fc5a3d5be1d52595602287acd87895220219bad050484251ac0408a163ffc45`.
- Original image ID `sha256:b0984c4b724b6f8c0745acb654994e1bd3a6c50b75c2c76078f1bfd6b395f39a`.
- OpenAI-compatible `:8000/v1`, model ID `qwen3.8-flash-next-orca-uncensored-bf16-mtp`, existing external clients.
- Legacy workspace `~/Workspace/llm/blazux-phase6-gates`, target new workspace `~/Workspace/llm/blazux-orcarouter`.

**Actual current running/stopped status, capacity, local Docker images, model snapshots and ports: `NOT_OBSERVED_THIS_SESSION`.** No stop/delete/launch performed by this development session. Do not infer that port 8000 or container name is free just because previous services were reported deleted.

**Target default service source configuration:** `MODEL=nvidia/Qwen3.8-Flash-Next-NVFP4`, `MODE=hybrid`, `MTP=2`, `YARN=1`, `CTX=500000`, `NAME=qwen38-flash`, `PORT=8000`, served model `qwen3.8-flash-next`, Docker internal 8000. This is desired/source state, **not a running API**. Existing Orcarouter model ID is not an alias for this different checkpoint.

**P1 checkpoint download (2026-11-05 11:46 KST, USER_REPORTED):** `nvidia/Qwen3.8-Flash-Next-NVFP4` is **DOWNLOAD_IN_PROGRESS** on the user's machine. This is **not** independently observed on DGX and has no verified completion percent, downloaded bytes, checkpoint revision, sha256, download command or cache path. **DOWNLOAD_COMPLETED=NOT_VERIFIED**, **HYBRID_PREPARED=NOT_VERIFIED**, **SERVICE/API/BENCH=NOT_RUN**. This session has not started, stopped, retried, removed or modified the download. Do not run a second download, `./flash setup default` (could download/build and mutate cache), hybrid preparation, model launch or cleanup while a write may still be in progress. Continue with P1 Wizard implementation and mock CPU tests independently of download, and inspect completed snapshot/index/shards after the user reports completion.

## New evidence and P1 Wizard source batch

**2026-11-05 operator-provided DGX terminal log (not directly observed through an SSH tool):** GB10/aarch64, Docker 29.6.2, 121 GiB unified memory (117 GiB available then); read-only Wizard Inventory showed no host :8000 collision and no `qwen38-flash` container, and initially 580,134,281,216 bytes free. The existing OpenWebUI and Portainer containers were running; preserve both. `./flash setup default` finished building `qwen38-flash-dgx:v0.32` (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`). The final log line showed **model download 9/25 = 36%**, NOT completed weights/Hybrid. The user's shell also entered `./flash serve default`, `./flash wait`, `./flash test` after setup, so these may run automatically after download/preparation. Do not compete with, modify or restart this running operator setup chain. Port availability and download progress can change after the log timestamp.

**New P1 SOURCE implementation at `c625a49276272e90d19ab6367f580a0230754890`:** `wizard/p1.sh`, `scripts/manager/p1_assets.py`, `p1_wizard.py`, `p1_bench.py`, new CPU tests and CI coverage. Wizard supports read-only inventory/snapshot/image proof, deterministic plan SHA, explicit per-action approval, guarded Hybrid prepare/start/wait, API health/model/text/tool/vision probes, bounded SSE benchmark and JSON evidence. **SOURCE IMPLEMENTED, CPU CI 2/2 PASS (80/80 per job), DGX Wizard/API/bench NOT_RUN.** It never automatically runs `setup`, downloads, deletes containers or caches or switches services.

## P1–P7 unified Wizard architecture (2026-11-05)

- User requested **build the entire Wizard navigation/CLI framework up front**, then incrementally connect and debug real P1–P7 model/runtime adapters. One stage file per menu: `wizard/menus/models/`, `switching/`, `storage/`, and `operations/`, shared `wizard/menus/common.py`, dispatcher `wizard/main.py`, executable root `./wizard.sh`, legacy `wizard/p1.sh`.
- `./wizard.sh` offers the interactive stage menu. The same handlers support direct noninteractive CLI, `--stage`, `--action`, `--json`, `--dry-run`, `--execute`, `--approve-plan`. The P1 adapter reuses `p1_wizard.py` and current exact-plan approval. P2–P7 have typed source-only status/plan interfaces; **execution remains hard-BLOCKED** until each model adapter, recipe, GPU evidence and rollback gate is actually implemented.
- Initial modular source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`: 2 GitHub CI checks SUCCESS, **101/101 CPU tests per job** (80 previous + 21 router tests). Follow-up full source/docs commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b`: GitHub CI **2/2 SUCCESS**, **103/103 CPU tests per job** (15 manifest, 10 inventory, 13 launch, 1 script mode, 41 P1, 23 Wizard router). No actual DGX actions performed by this batch.
- `./wizard.sh p1 status --json` and `./wizard.sh p1 plan --for-action verify --json` are read-only. `./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json` returns BLOCKED until P3 qualifies. No model switching or deletion feature was secretly enabled.
- **Current DGX source-of-evidence remains** the prior user-supplied log: image built, Flash-Next download 36% last observed, queued original setup/serve/wait/test; current live service still unverified. Do not update the live worktree while that shell chain may be running. See `docs/WIZARD-CLI-CONTRACT.md`.

## Descriptive Wizard menus, grouped by capability

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

**Source evidence:** `571e1c204d76bcb66b9e02cb1315ac775013a130` refactor, GitHub Actions push/PR **2/2 SUCCESS**, **112/112 CPU tests per job** (15 manifest + 10 inventory + 13 Flash launch + 1 script mode + 41 P1 + 32 router). No real DGX model operations performed or authorized by this rename.

## Temporary one-command DGX P1 handoff workflow (D-016)

- New `scripts/temporary/` is the canonical place for **single-invocation, short-lived, Git-committed operator bundles**. `p1-post-download.sh` dispatches `p1_post_download.py` with source-safe diagnostics → explicit independent Wizard verify/benchmark approvals → JSON evidence collection. `--inspect-only` is safe and can run unattended; on a TTY, each real action requires the full current 64-character plan hash. Script never calls `./flash setup`, downloads, starts/stops a service, removes images/cache, changes the active worktree or performs `git pull`.
- Operator must complete the **already entered** original `setup/serve/wait/test` shell chain **before** Git Pull; do not infer from the old 9/25 download log that current operations have finished. Operator local entrypoint: `git pull --ff-only origin feature/recipe-wizard-handoff`, then `bash scripts/temporary/p1-post-download.sh` (interactive) or `... --inspect-only`. Non-TTY with no explicit plan hashes executes only inspection. Logs stored with restricted permissions under `~/blazux-p1-reports/`, outside Git/HF cache. Wizard-generated evidence remains under `~/.local/state/blazux-wizard/p1/`.
- This code is **SOURCE+CPU CI verified at `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b` (2/2 jobs SUCCESS, 131/131 tests/job); actual DGX/API/GPU/bench still NOT_RUN pending operator evidence**. 27B/Orcarouter runtime phases remain gated; P2–P7 are not executable. See `scripts/temporary/README.md` and `handoff/OPERATING-RULES.md#r1d--git-tracked-temporary-script-batches-for-user-operated-dgx-d-016`.

## Stage matrix

| Stage | Source/plan | CPU/CI | DGX/GPU | Release |
|---|---|---|---|---|
| P0 inventory + recipe/wizard architecture | `N1 schema + N2 inventory + default 8000 SOURCE_IMPLEMENTED`; N3 doctor/plan partial | N1 15 + N2 10 CPU PASS at 7e8f4a1; launch 4 FAIL from permissions; **CI_RECHECK_REQUIRED** after mode fix | `NOT_RUN` | `NOT_APPLICABLE` |
| P1 Flash-Next **Wizard** implementation + DGX bench | `WIZARD_SOURCE_IMPLEMENTED / CI_VERIFY_REQUIRED` | Existing 39/39 previous PASS, new P1 CPU suite 41/41 PASS; total 80/80 CPU tests PASS per CI job (2 successes) | `IMAGE_BUILD_USER_LOG_PASS`, download last seen 36%; **Wizard GPU/API/BENCH NOT_RUN** | `BLOCKED` |
| P2 27B **Wizard** implementation + DGX bench | `PLANNED/COMPAT_UNKNOWN` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P3 Flash-Next ↔ 27B **Wizard** switching/rollback | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P4 Flash-Next **Wizard** optional removal, only if capacity requires | `PLAN_ONLY/EXACT_APPROVAL_REQUIRED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P5 Orcarouter-Flash-Next **Wizard** implement + DGX bench | `PARALLEL_DESIGN_ONLY` | `NOT_RUN_THIS_FORK` | `NOT_RUN` | `BLOCKED` |
| P6 Orcarouter ↔ 27B **Wizard** switching/rollback | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P7 **Wizard**/service/proxy/gateway/storage operations acceptance | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |

**Outstanding historic release blocker:** same-checkpoint strict max logprob delta `<=1e-4` not satisfied in old Preview baseline, therefore do not claim Orcarouter numerical qualification.

## Current deliverables

- `docs/MODEL-RECIPE-WIZARD-PLAN.md` — stage roadmap and architecture.
- `docs/MANIFEST-CONTRACTS.md` — manifest schema intent, switch/rollback/deletion gates.
- `handoff/*` — persistent entrypoint, rules, decisions, evidence, action list and starter prompt.
- N1 SOURCE IMPLEMENTED: schema, bounded YAML validator, intentionally invalid 27B candidate, synthetic fixture, 15 CPU tests, new GitHub Actions CPU workflow. See schemas/recipe.schema.json, scripts/manager/manifest.py, recipes/, tests/test_manager_manifest_cpu.py.
- Default Blazux `flash` + `profiles/default.env` + `scripts/serve.sh` now target host port 8000 and refuse implicit Docker name replacement. The built-in model is NVIDIA Flash-Next. This path requires image/model assets and explicit operational go-ahead on DGX.
- `scripts/manager/inventory.py` and `wizard/00-doctor.sh`/`10-plan.sh` provide read-only Docker/ss/disk/cache inspection. N3 is partial (no interactive or execute path).
- No pinned, launchable **manifest**; no service controller, proxy/gateway or 27B runtime adapter. Synthetic recipe SHA values are fake fixture data.

## Blockers / approvals

- Need fresh read-only DGX inventory **execution** before operational choices; the code now exists, but DGX observations do not.
- Need vLLM 0.32 source check for Qwen3.8-27B architecture, quantized `lm_head`, GDN, tokenizer and speculative support. SGLang is excluded.
- User requested implementation for Flash-Next on port 8000; no local GPU/model loading was performed and no command was executed against DGX. Obtain scoped operator confirmation and preflight evidence before actually running setup/serve; explicit deletion approval remains required for P4.
- Need plan for sufficient free disk. Do not delete existing images/cache or checkpoint automatically.

## Immediate dependencies and next safest actions

1. Verify new GitHub Actions CPU checks on `c625a492…`, remedy any failures and preserve failure evidence.
2. Let operator's existing `./flash setup default` download/Hybrid preparation and queued `serve/wait/test` commands finish **without restarting or changing the worktree mid-run**. Once done, use `bash wizard/p1.sh status`; if container is already running, do not rerun `start`.
3. Obtain fresh Wizard `plan --for-action verify`, explicit action approval, run Wizard API text/tool/vision verify; then separately plan/approve a bounded 3-request benchmark and save local JSON evidence. Do not claim P1 PASS until real DGX data proves it. P2 remains next after P1.

## Immediate next actions

1. **P1 Wizard end-to-end implementation first:** add guided/noninteractive `prepare/serve/verify/benchmark/evidence` flow, approvals, idempotent state + fail-closed plan with mock CPU tests. Existing `doctor/plan` are only partial; no launch without gated operator action.
2. Read-only DGX `wizard/00-doctor.sh` and `./flash doctor default`; establish current port 8000 availability, checkpoint/image provenance, HF cache mounts and disk capacity. No claims of service running until observed.
3. After scope-specific operational go-ahead and rollback plan, execute **P1 via Wizard** on DGX, collect actual API/benchmark evidence, then advance to P2 (27B Wizard), not directly to Orcarouter.

See [NEXT-ACTIONS.md](NEXT-ACTIONS.md), [EVIDENCE-LEDGER.md](EVIDENCE-LEDGER.md) and [../docs/MODEL-RECIPE-WIZARD-PLAN.md](../docs/MODEL-RECIPE-WIZARD-PLAN.md).
