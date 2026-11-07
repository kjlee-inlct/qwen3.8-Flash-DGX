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

## 2026-11-07 — P2-FINAL protected Native Tools V1 SOURCE implementation (no DGX operations)

Created distinct `qwen38-27b-native-tools-v1` source candidate and deliberately unqualified pinned recipe; implemented read-only source/original/fallback/port/GPU inspection with no execute, plus strict SSE auto tool-call parsing with bounded data/time and HTTP/error guard. New offline regressions cover original immutability, variant collisions, other GPU users, source image/port/cache drift, malformed/truncated streaming/JSON and model mismatch. Extended `scripts/serve_27b.sh` CLI. Documented isolated cutover, independent approval, journal and rollback contract as **future implementation gates**; do not confuse SOURCE/CPU with actual DGX acceptance. Existing P3-C, original 27B/Flash, cache, operating journal and normal Wizard production gate untouched. P2-FINAL remains OPEN.

---

## 2026-11-07 — Latest DGX operational reverse postcheck VERIFIED; P2-FINAL Tool Calling HTTP 400 confirmed

Operator fast-forwarded to `09c6780`; verified real running `qwen38-27b`, `:8000` `LIVE_SERVICE_VERIFIED`, sole `qwen3.8-27b`, `issues=[]`; independent operating journal `VERIFIED/COMMITTED`, 14 events. Direct Docker `Config.Cmd` confirms absence of all tool-auto/parser/reasoning flags from preserved 27B, while source opt-in tool profile displays expected candidate flags. Real bounded local `--tools-probe` returns `BLOCKED/LOCAL_API_HTTP_ERROR_400` with no structured call/continuation; no destructive or lifecycle actions. This **closes the earlier reverse-postcheck gap** while keeping **P2-FINAL Native Tool Calling NOT_QUALIFIED**. Original P3-C historic PASS unchanged, normal main Wizard production gate OFF. New task: protected tool-enabled 27B variant and separately approved transition/rollback design; Open WebUI Native and streaming tests pending.

---

## 2026-11-07 — P2 final tool-calling opt-in source / P3-C completed-history freeze

Per operator ordering, created dedicated final P2 item for 27B Native Tool Calling. Verified official Qwen3.8-27B vLLM flags `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`; implemented opt-in candidate argv flag (legacy P2 launch remains unchanged), source-only profile and bounded localhost structured auto tool-call/continuation probe (no real tool execution, no Docker mutation), plus 27B dedicated entrypoint flags and Fake-DGX regression suite. Historical P2 GPU/benchmark passed and P3-C Stage A/B/C passed on DGX unchanged; appended P2 Tool Calling requires real parser/migration/Open WebUI tests before full P2 closure. Last actual ordinary reverse Flash→27B trial PASS, independent final status/audit still not supplied. Production main Wizard remains release gated; no P3-C rerun, no asset deletion or PR merge.

---

## 2026-11-07 — Independent post-switch Flash service and journal VERIFIED; reverse 27B plan ready

Operator subsequently read live DGX service: `flash-next` ACTIVE / `LIVE_SERVICE_VERIFIED`, sole `qwen3.8-flash-next` on :8000, `issues=[]`; operating journal `VERIFIED`, `COMMITTED`, 7 events, no issues. Separate read-only ordinary reverse plan `flash-next→27b` `READY_FOR_SEPARATE_TRIAL_APPROVAL`, issues none, **not executed**. First 27B→Flash physically accepted switch is now corroborated by independent read-only after-checks. Reverse still needs fresh explicit downtime consent and manual exact approvals. No new model transfer/cleanup or PR merge in this documentation update.

---

## 2026-11-07 — First REAL DGX normal Wizard switch PASS: NVIDIA 27B → Flash-Next

Operator supplied terminal showing source fast-forward to `4054eb2`, current 27B API `LIVE_SERVICE_VERIFIED`, independent operating journal `EMPTY`, exact fresh operating acceptance plan ready, and four human TTY approvals. The tracked new `operational-switch-acceptance.sh --target flash-next --execute` returned `Live transition result: PASS`, `Observed model: flash-next`, and new immutable private completion receipt. This proves first **ordinary** backend physical transfer, not one-off P3 replay. The independently verified source CI remains 671/671 CPU Fake-DGX. No reverse action, real rollback trial, production menu release, model deletion, Tool Calling recipe work or PR merge. The current last observed model is now Flash-Next, superseding prior 27B-active claims.

---

## 2026-11-07 — End-to-end source implementation of ordinary model-switch Wizard, independently gated DGX trial

Implemented existing `./wizard.sh` model-first main entry and target selector; separate guided review and eventual three-input production action flow, source gate still OFF; strict domain-separated execution SHA vs preview; trial-only `operational acceptance` CLI with four exact TTY acknowledgments and tracked wrapper; extra expiry/TTY/JSON cancel gates. Hardened new operating executor's pre-stop cancellation (no downtime on stale source), foreign-GPU post-start check, bounded target chat inference, terminal immutable receipt and journal audit before PASS. New read-only `operational_audit` checks event-log hash chain vs snapshot and missing committed receipt to fail closed after crash. Added multi-direction Fake-DGX acceptance, rollback, mismatch, expiry, noninteractive cancellation and journal corruption CPU tests, workflow wiring, main menu, roadmap and runbook. No ACTUAL DGX operating switch or recovery was attempted; no active 27B changes, model cleanup, P3 replay or Draft PR merge. Deferred Open WebUI Tool Calling.

---

## 2026-11-07 — Restore Wizard ordinary operating switch priority; release-gated UX/backend link (SOURCE)

Created `scripts/manager/operational_wizard.py` for target-first switch review, source-safe independent authorization fingerprint, three exact approvals and fake-only backend dispatch. Wired into existing `./wizard.sh` interactive model option 6 and grouped CLI `switch flash-next-27b operational guided --target ...`. Updated existing independent executor to reject preview-only SHA; Fake-DGX unit/integration tests and CI workflow. Production gate false, no real Docker/GPU switch; P3 immutable historical stages untouched. WebUI Tool Calling and 27B recipe support **deferred** per operator correction, not current focus.

---

## 2026-11-07 — WebUI native tools mismatch; 27B no-thinking exact output PASS

Real operator direct 27B curl with per-request `enable_thinking=false` returned exactly `DGX_OK` (4 tokens), while Open WebUI emitted vLLM tool-choice auto configuration error. Read-only Git source review identified missing `--enable-auto-tool-choice` / `--tool-call-parser` in 27B candidate launcher, unlike Flash; actual current Docker command still not observed. Added `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`, recommended WebUI Builtin Tools-off workaround and separate future startup-profile/parser qualification gate. No source executor changes, DGX restarts, model switch, deletion or PR merge.

---

## 2026-11-07 — Real DGX 27B curl verification PASS, formatting anomaly isolated

User supplied successful actual localhost /health, single /v1/models identity and two chat-completion probes (direct raw request and tracked shell smoke); tracked script emitted `27B_CURL_SMOKE_PASS`. Recorded actual active 27B pinned NVIDIA revision, vLLM 0.32.0 and 26-token direct reply. Reply contains reasoning-like prose and literal `</think>` in `content` despite `reasoning=null`: distinguish healthy inference from failed exact-format compliance, no speculative server-side repair. Follow-up `FORMAT_PASS` / `FORMAT_DEVIATION` classifier and offline fake-curl tests source-only. Maintained Draft PR, 27B state, Flash preservation and unqualified general operating switch.

---

## 2026-11-07 — Separate current 27B curl inference smoke from identity-only switch preview (source only)

Added one-command non-disruptive localhost `curl` 27B smoke with explicit /health, /v1/models and one bounded /v1/chat/completions verification; Fake-CPU failure modes and CI; Wizard ordinary-switch hint; operating switch UX doc and permanent handoff updates. Does **not** enable ordinary switch dispatch, perform real DGX curl, repeat P3 A/B/C or alter Docker/GPU service state. Await operator's actual 27B smoke output.

---

## 2026-11-07 — Ordinary model-switch preview, source-only transaction and Fake-DGX tests

- Added \`scripts/manager/operational_switch.py\`: strict independent read-only candidate (historical P3 provenance, fresh API, pinned Docker identity, foreign GPU and journal blockers), rotating non-executable fingerprint.
- Added \`scripts/manager/operational_executor.py\`: guarded backend source for independent exact plan and two acknowledgments, separate lock/journal/attempts, stop-before-start, port/model identity, post-switch verification and best-effort restoration. **Not routed to any CLI or TTY execute; not DGX qualified.**
- Updated model-first TTY \`wizard/console.py\` and P3 switching adapter to display an ordinary read-only switch preview without recommending replay of one-off stages.
- Updated \`wizard/roadmap.py\` to separate local historical P1/P2/P3 evidence, current API, general switching, interactive UX and release qualification.
- Added fake-DGX preview/transaction tests \`test_operational_switch_cpu.py\` and \`test_operational_executor_cpu.py\`; enrolled in \`.github/workflows/recipe-manifest-cpu.yml\`.
- Created \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`. Actual DGX 27B remains untouched, assets and P3 receipts preserved; Draft PR #1 still open/unmerged.

---

## 2026-11-07 — P3-C 실제 최종 PASS, 새로운 P1–P7 수용 현황 및 대화 시작 프롬프트 최신화

실제 DGX 운영자가 새로운 P3-C 계획/3개 독립 승인으로 전환했고, canonical Wizard가 `status=PASS/stage=c/executed=true/live_verified=true/active_model=27b`를 반환했다. wrapper `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `issues=[]`; 원본 `stage-c.json` 증거 보존. 이 결과는 10분 경계에서 승인 부족으로 BLOCKED되었던 과거 시도를 supersede하며, **현재 마지막 관측 모델은 NVIDIA 27B ACTIVE :8000**. 최신 Git 모델별 벤치 2개도 actual DGX private source와 VERIFIED.

모든 핵심 doc 경로를 재조회하여 필수 핸드오프/마스터 플랜/운영 계약/Manifest/벤치/단계별 P3 runbook의 **파일 미존재 없음**을 확인. 다만 기존 `handoff/SESSION-START-PROMPT.md`, `README.md`, `CHANGELOG.md` 및 일부 이전 계획의 첫 문단이 과거 P3-C NOT_RUN으로 시작하는 문서 최신화 누락을 발견. 새 시작 프롬프트를 P3-C 완료 이후 UX 작업 기준으로 갱신하고, `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md`를 추가하여 실제 DGX P1-P3 백엔드 PASS와 일반 Wizard 메뉴 UX 수용 미완료를 분리했다. 원본 증거·GitHub Draft PR·활성 27B 서비스는 변경하지 않았다. `wizard/roadmap.py` P3 정적 상태와 `wizard/console.py` P3 plan-only 메뉴는 **다음 소스 개발의 확인된 갭**, 이번 문서 작업에서는 실행 코드 변경 없음.

---

## 2026-11-07 — Fixed P3-C 10-minute plan-boundary operator refusal, source only

Actual operator runs at 10:08:14 and 10:09:30 KST, both ending in `P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS` with `executed=false/execution_dispatched=false`, revealed the canonical expiring plan window UX issue while Flash remained active. No real Stage-C transition occurred. New `scripts/temporary/p3_stage_c_operator.py` bounded 150s **read-only** refreshes stage-C plan and live Flash source until a NEW, fully provenance-qualified SHA with >=120s remains; rejects early unexpected SHA change, foreign current model, missing P1/P2 evidence, dirty Git, timeout/interrupt. Old plan and approvals never reused. Still requires three fresh exact manual inputs and independently calls unchanged canonical guarded Wizard. `--plan` stays immediate/non-mutating. Added fake DGX virtual-clock and newly authorized SHA execution regression tests. Operator pulls latest branch after CI and can run `bash scripts/temporary/p3-stage-c-operator.sh --execute` under existing explicit operator Flash downtime consent. No model deletion, no PR merge, no GPU activity in source changes.

---

## 2026-11-07 — Git-public benchmark snapshots, source-only exporter and post-C cancellation evidence

Published **two** model-named, Git-tracked, metric-only benchmark JSON files in `benchmarks/published/` with original receipt SHA256 and standardized metadata. Original user-observed Flash-Next post-B throughput 37.9527 tokens/s, and 27B trial-with-Flash-restore E2E 7.9002 tokens/s / decode proxy 11.1801 tokens/s; both 3 sequential requests max64 tokens. Numeric source values are grounded in supplied operator logs, not newly run models or normalized performance comparisons. Original private `~/.local/state/blazux-wizard` JSON, `reports/`, host paths, approval IDs, prompt/output and Docker logs remain Git-ignored/unpublished. Added allowlist-safe deterministic `scripts/manager/benchmark_publication.py` with `--plan`, `--verify-published`, exact original-SHA-gated `--write` and 12 fake-CPU tests, and read-only `scripts/temporary/verify-published-benchmarks.sh` checking published results against original DGX receipts. `--write` never stages/commits/pushes. Actual DGX original-to-public verifier NOT_RUN yet; request operator pull and run.

P3-C previous `--execute` output `CANCELLED` before dispatch because SHA was typed with leading `[`. No model transition occurred in that attempt. New C SHA and separate explicit live downtime confirmation required if proceeding. PR #1 Draft/unmerged.

---

## 2026-11-07 — Final P3-C tracked operator, actual C read-only plan READY

User's latest actual DGX dump shows C canonical `--plan` status READY/no issues/P1 post-B evidence PASS with original Flash active and preserved 27B offline; optional P2/P3 historical evidence import was CANCELLED/copied=0 (typed `COPY`, not SHA). No service changes. Added D-016 `scripts/temporary/p3_stage_c_operator.py` and `scripts/temporary/p3-stage-c-operator.sh`: default read-only plan, new P3-C-specific three exact TTY confirmations, action-bound fresh replan, canonical Wizard only for `--execute`, final 27B `:8000/v1` and immutable `stage-c.json` checks, Git-ignored private report `reports/transitions/flash-next--to--27b` and fail-closed recovery uncertainty. Added isolated fake-DGX `tests/test_p3_stage_c_operator_cpu.py` + GitHub workflow. Success intentionally leaves 27B active; original Flash model/image/container preserved. Actual C still NOT_RUN/NOT_AUTHORIZED; separate human downtime consent remains mandatory. [Operator instructions](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md). No PR merge.

---

## 2026-11-07 — Wizard model history and P2/P3 non-destructive consolidation

New `scripts/manager/evidence_catalog.py` reads model-centric historical Verify/Benchmark, 27B GPU trial/benchmark, P3 stage transitions and Flash diagnostics from existing private `~/.local/state/blazux-wizard` paths and new project `reports/`. Main Wizard adds model option **4** for categorized read-only history, Advanced option **8** to request a guarded copy-only import; CLI `./wizard.sh evidence list --model ... --kind ...` and `evidence migrate --plan|--guided`. Current SHA is repeated in guided approval prompt like P3. Copies use 0600 O_EXCL, 0700 directories, byte-identical SHA256 dedup, and legacy P2/P3 live state/journal/locks/attempt markers remain canonical/unmoved. P3 stage-B historically misnamed operator report classified by stage content, not filename. Additional CPU-only fake evidence tests, no CUDA/Docker inference performed. See [contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md). P3-C next step is **read-only** `./wizard.sh switch flash-next-27b stage-c --plan --json`, NOT a user-approved switch. Draft PR unmerged.

---

## 2026-11-07 — Model-centered Wizard / post-B real GPU receipts / evidence path contract

User's original DGX ZIP shows Flash-Next post-B Verify baseline+extended PASS and separate bounded Benchmark PASS (mean 37.9527 tokens/s, TTFT P50 1.384594 s). Distinct exactly approved original receipts remain in `~/.local/state/blazux-wizard/p1`; latest P1 diagnostic rc3 issue disposition PASS and P3-B stage-B PASS are immutable. Code updated for exact P3-style approval prompt, one selected action, output of Verify and numeric Benchmark, no P1-number UX, and new Git-ignored repo `reports/models/qwen3.8-flash-next` for all **future** P1 execution receipts. P3 stage-C evidence gate now reads both paths and ranks by finished timestamp; a newer failure must block. New CPU tests include prompts, no duplicate menu, and migration safeguards. Source CI at [workflow 42313905291](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42313905291) passed **508/508 tests** across 23 groups at source commit `287c81d4a9225ef6e27e5641dda15890ea98ca28`; later label/docs commits require rechecking latest CI. No actual DGX UX re-execution, P3-C or PR merge. See [contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

## 2026-11-07 — FINAL SOURCE CI / DRAFT PR REVIEW CHECKPOINT

Source, regressions, permanent docs and read-only DGX audit workflow have been committed to existing `feature/recipe-wizard-handoff` and Draft PR #1. Source-tested HEAD `67ff9cc2e4ece0c89c911513673f7d5d55c98fa4`: GitHub Actions [push 42310408411](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42310408411) **SUCCESS, 501/501 CPU tests across 23 groups**; PR run 42310415255 also checked separately. Explicit [Draft PR review #5808289782](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) recorded, with live DGX P1/ P3-C blockers, not approved/merged. The subsequent handoff documentation commit does not authorize runtime work; latest branch HEAD/CI must always be rechecked. Only permitted next operator check is `bash scripts/temporary/p1-post-b-audit.sh` after fast-forward pull and CI pass.

---

## 2026-11-07 — P3-B actual completion reconciliation and POST-B read-only audit

- Received user-supplied DGX actual P3-B success: canonical stage-B `PASS/executed=true/live_verified=true`, wrapper `P3_B_PASS_FLASH_NEXT_ACTIVE`, active `qwen3.8-flash-next`. Original wrapper report historically misnamed `p3-a-operator-20261106T223124Z-14861d75.json` and contains stale `approval_accepted=false`; preserve it unchanged.
- Source commit `23cf10de47ab85417e646a06245d8a70e0b2e849`: stage-aware operator evidence prefix, correct manually accepted approval vs execution dispatched fields, regression tests; no actual P3-B replay.
- Source commit `ea1a4ca1629acfd519fbfa839b615f45dd91c86e`: GitHub-tracked P1 POST-B audit (read-only only), exact raw rc3 diagnosis, private append-only receipts, latest-attempt P3-C evidence gate and fake-DGX tests. Initial CI reported SUCCESS; subsequent hardening commit `94622bc100a6f34b26603ac736b8b672ba26d24e` requires latest CI outcome check.
- Reconciled handoff CURRENT-STATE/NEXT-ACTIONS/EVIDENCE-LEDGER/DECISIONS and operating docs. Old records preserved below for chronology.
- Actual user-reported P1 post-B inspect-only PASS/Verify+Benchmark plan READY at `/home/inlc/blazux-p1-reports/20261106T224010Z-d2095867/result.json`. This is NOT a fresh post-B functional or performance execution. Full post-B rc3 evidence remains pending a **new DGX read-only audit**.
- P3-C NOT_RUN/NOT_AUTHORIZED. No Docker, GPU inference, service stop/start, model/cache deletion, PR merge, or old receipt overwrite performed by GitHub-only source work.

---

## 2026-11-06 — P3-B real read-only inspection PASS; implement independent 27B downtime/entry gate (489 CPU PASS)

Actual user DGX B inspector after P3-A returned `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`; verified running 27B API ID and container and preserved original Flash CID/image, P2/A hashes, `executed=false`. B originally inherited wrong Flash downtime ACK from shared canonical core; now B-specific `I_ACCEPT_27B_DOWNTIME` + `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`, A/C unaffected. Created `p3-stage-b-operator.sh` and Python with default read-only, gated real B `--execute` requiring separate user scope approval + three exact terminal inputs, replan/expiry, independent Flash API check, no auto P1/C. Fake-DGX CPU PR [42190159738](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) SUCCESS **489/489** tests, source `59046c4e17a5094f2c80a84025a763c2a767edcb`. No GPU/Docker effects or user B consent from GitHub work; 27B remains live as of provided DGX evidence.

---

## 2026-11-06 — DGX P3-A real PASS; 27B active, prepare B read-only inspection

Actual operator-run persistent P3-A with exact latest plan and independently typed downtime/P3 entry acknowledgments succeeded: Wizard stage-A PASS/executed/live-verified; wrapper `P3_A_PASS_27B_ACTIVE`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, no issues. Receipts `~/.local/state/blazux-wizard/p3/stage-a.json` and `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. 27B remains running. D-039 explicitly distinguishes this from prior stale-plan refused attempt and withholds B/C permission. Added tracked source/CPU-tested **read-only** B inspector verifying actual A receipt and preserved Flash identity through canonical Wizard API/plan; zero service mutation, no B execute mode, D-016 GitHub→DGX pull→single wrapper workflow. Post-B P1 verify and numeric benchmark + final C still pending; Draft PR not merged.

---

## 2026-11-06 — Fix P3-A exact confirmation UX and expired 10-minute plan refusal (459/459 CPU PASS)

User entered all three correct stage-A approvals, but plan `94b4deda...` expired at 16:30:00 KST (report 16:30:49 KST), Wizard refused `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT` with `executed=false`, no actual transition. Updated GitHub-tracked D-016 `p3_stage_a_operator.py` to display actual full required SHA/ACK literal at each terminal prompt, plan expiry KST and seconds left, fail before prompting with <120s left, replan read-only after manual input, and classify canonical stale refusal as `BLOCKED` rather than `OPERATOR_REVIEW_REQUIRED`. New fake-DGX tests assert exact prompts, short-window refusal, changed SHA refusal, no hidden retry. [CPU PR CI 459/459 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236) at code `fb34ce0ce985824cecd9c63159bf6f1eed408279`. No model switching, service lifecycle, GPU or cache mutation from GitHub. D-016 operator fast-forward pull and single wrapper, fresh exact approvals still required.

---

## 2026-11-06 — P1 pre-A real DGX PASS; first persistent P3-A D-016 operator runner SOURCE tested

User ran the fixed GitHub-tracked P1 pre-A script on actual DGX HEAD `834f823a76556a37a982e3dbf7f243db3edad6df` and supplied `PRE_A_P1_REVIEW_READY`, no issues; historical/current expected own Flash collision 2/2, original verify PASS and measured benchmark PASS (3 samples, mean 38.2968 tok/s). Original condition for P3-A now satisfied for **eligibility**. Added GitHub-tracked `p3-stage-a-operator.sh` Python wrapper: default read-only, separate `--execute` with TTY and exact typed stage A plan ID, downtime and P3 entry acknowledgment; canonical Wizard does actual stop→start→observe, wrapper verifies 27B live model/image independently and writes 0600 local report. Fake DGX tests cover wrong IDs, foreign service, missing P1, expired plan, no TTY, cancel, success postcheck and failure/no retry. D-034 B→Flash, full post-B P1 rebenchmark and C→27B remain separately approved steps; no P3 actual GPU run or GitHub PR merge here.

---

## 2026-11-06 — Correct P1 pre-A cache diagnosis persisted JSON location (439 CPU PASS)

Operator's real pre-A audit with both historical/current rc3 exact own-model collisions and P1 verify+numeric benchmark PASS returned `BLOCKED` on asset audit and revision drift. Found both arose because temporary script read console-only `cache_diagnosis` rather than persisted `checks.cache_diagnosis.stdout`. Fixed to reuse original JSON reader, classify unobservable revision separately from actual mismatch, and fake-DGX test actual persisted schema and negative evidence paths. [CI 439/439 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898) on code `9adc9ab282a91c02e959dcb5c62f98527b556391`. No DGX model, GPU or :8000 mutation; await D-016 single script recheck after pull.

---

## 2026-11-06 — P1 pre-A tracked audit / genuine identity schema fix, 435 CPU PASS

D-016 operator correction honored: GitHub tracked pre-A wrapper and unit tests first, DGX fast-forward pull then one wrapper; no ad hoc pasted Python. Wrapper reconciles local original P1 verify/bench receipts (3 samples, actual 38.2968 tok/s etc) with 2026-11-05/06 doctor/inventory raw outputs and fresh Flash service API; outputs private 0600 evidence with no GPU/Docker lifecycle. Corrected pre-A and post-B P3 P1 identity gate to match `require_model`'s real `{"health":"PASS","models":[...]}` rather than nonexistent `identity.status`. [Latest tested PR CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) **435/435 CPU PASS** at `75d22ce4303736ee84563a0f388a978379e4f228`. No actual DGX wrapper execution or P3-A transition occurred.

---

## 2026-11-06 — P1 numeric evidence received; D-016 script-first workflow restored

User supplied actual P1 benchmark receipt 3/3 PASS, 192 completion tokens, TTFT P50/P95 1.398707/1.751198s, latency P50/P95 1.687357/1.780142s and 38.2968 tokens/s mean. New actual 2026-11-06 P1 `--inspect-only` report source/Hybrid READY and API original ID; inspect-only BLOCKED actions are non-execution by design, not P1 failure. Doctor/inventory rc3 raw not yet available. D-016 mandates temporary script → GitHub push/CI → DGX pull → one wrapper, not pasted one-off terminal code. Added `p1-pre-a-readiness.sh` + Python and CPU fake DGX tests to reconcile both raw rc3 reports, original P1 receipts and fresh live API; writes private JSON, cannot perform actual model switching. Conditional P3-A approval remains pending evidence review; D-034 B then P1 rebenchmark then C still binding.

---

## 2026-11-06 — P1 pending audit / conditional P3-A approval unmet; correct active-service rc3 validation

Reviewed P1 operator proof: functional Flash-Next verify and bounded benchmark PASS, but numerical timing/tokens-per-second not supplied and doctor/inventory rc3 raw cause unresolved. User approval for Flash→27B is conditional on nothing remaining in P1, so no live switch. Audited `inventory.main`: an already running Flash container and occupied :8000 intentionally causes rc3 without read errors. Replaced post-B P1 diagnostic gate's impossible rc0 check with strict full doctor/plan JSON collision evidence for exact active Flash name/image/:8000, retaining historical reviewed disposition and new post-B verify and measured benchmark receipt prerequisites. Five negative CPU tests added (missing raw output, read errors, wrong image, wrong port, rc0 shortcut). [CI 418/418 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172127412) on source `26a6950`. No GPU or service action.

---

## 2026-11-06 — Correct P3 sequence-status wording; guard foreign GPU during rollback; 413 CPU PASS

Kept global P3 `sequence --plan` BLOCKED/no plan ID while displaying accurate existence of separately approval-gated A/B/C source adapters, not-yet-qualified DGX runtime. Hardened `p3_persistent_switch._restore` to abort original model restart if new unexpected GPU-enabled Docker containers appear after failed target stop; added bounded fake-Docker tests for collision and normal restoration. On source commit `02bf94c1628828ce22fa338dd5a8e5a0955f9179`, GitHub Actions [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170050031) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860) **413/413 CPU PASS**, 19 suites. An intermediate test fixture newline failure was resolved. No actual DGX P3 switch executed.

---

## 2026-11-06 — Actual P3-A read-only readiness observed on DGX; no transition executed

2026-11-06 DGX operator read-only observation: current Flash-Next `qwen38-flash` on :8000/v1, `LIVE_SERVICE_VERIFIED`, served ID `qwen3.8-flash-next`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, exact container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Manifest/API check array 8/8 true, `issues=[]`, `executed=false`; **GPU exclusivity and process ownership remain unverified**, and current identity is not historical rollback proof. `sequence --plan`: `status=BLOCKED` with only `P3_SEPARATE_OPERATOR_ENTRY_REQUIRED` by D-034 (expected), with successful local P2 receipt SHA-256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, evidence path `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`. `stage-a --plan`: `status=READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, source `flash-next`, target `27b`, `plan_id=79be6bf05cb02306ec9155ade317e06c457238de427417ebab8946e35449247a`, expiry epoch `1793943600` (2026-11-06 14:40 KST), target image equal to preserved local Docker image ID, expected target container ID null (not yet created), `executed=false` and `operations_enabled=false`. **This was a plan only, not scoped downtime approval or P3 entry**; plan IDs must be regenerated when stale and must never be reused across stages. No GPU/Docker/service mutation was performed by these read-only queries.

Documentation-only evidence receipt; source P3 stages and CI are separate. No operational approval inferred from `READY_TO_REQUEST_TRANSITION_APPROVAL`.

---

## 2026-11-06 — Implement P3 A/B/C persistent switching source and P1 evidence gate; CPU CI green

Introduced `scripts/manager/p3_persistent_switch.py` with distinct guarded P3 phases A/B/C, fresh observed Docker/API source and preserved target identity checks, short-lived exact approval plan, safe stop-before-start, rollback attempts, private stage receipts, attempt lock and append-only service journal. Added `scripts/manager/p3_p1_evidence_gate.py` to require new post-B P1 functional, numerical benchmark and reviewed historical rc=3 root-cause proof before C. Wired `wizard/menus/switching/flash_next_27b.py`, interactive `wizard/console.py` **plan-only** stage choices and `wizard/main.py` help. Preserved legacy read-only `sequence --plan`, blocked retired `roundtrip`. Extended CPU regression in `tests/test_p3_persistent_cpu.py` and added it to CI YAML.

CI after fixes: [push 42168518712](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168518712) and [PR 42168524464](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168524464) SUCCESS, **411/411 CPU tests**, 19 groups. Recorded failed interim runs and their corrected syntax/mock fixture causes in Actions history, no test weakening. New [P3 source runbook](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md) details approval and known limitations. **No actual DGX P3 transition or P1 rerun.**

---

## 2026-11-06 — Record actual P2 27B benchmark PASS and Flash-Next restored, close P2 stage

From operator-supplied DGX execution result: NVIDIA 27B model/API/inference and three bounded streaming requests succeeded (`BENCH_PASS_RESTORED_VERIFIED`); original Flash-Next was restored and independently observed by the Wizard as `LIVE_SERVICE_VERIFIED`. Recorded precise latency, TTFT, client throughput proxies and private DGX evidence paths in CURRENT-STATE and EVIDENCE-LEDGER. This corrects earlier plan-only `NOT_RUN` reporting without claiming direct inspection of private DGX files. No Docker/GPU state changed while editing sources. **P2 finished; P3 not auto-started; D-034 governs all future P3 stages.**

---

## 2026-11-06 — User changed P3 sequence; P2→P3 no-auto boundary enforced in source

Per D-034, retire old 2x temporary Flash-Next→27B→Flash-Next P3 plan/execute (now fail-closed even with past approval IDs). Add `scripts/manager/p3_transition_sequence.py` and `./wizard.sh switch flash-next-27b sequence --plan --json`: read-only, no executable plan, no automatic transition. P3 must be entered separately, establish verified active 27B, switch 27B→Flash-Next, resolve P1 deficiencies + real benchmark while Flash-Next running, then separately switch Flash-Next→27B as final state. The source code/CPU tests do NOT implement or verify permanent switching. P2 actual benchmark still awaited, and no operational Docker/GPU calls made while editing. D-033 superseded.

---

## 2026-11-06 — P2 exact-approved 27B benchmark and P3 gated two-roundtrip source implementations

Created `scripts/manager/p2_27b_benchmark.py` with separate benchmark plan/ack, 3 bounded streaming requests, client metrics and private final success+restore evidence, delegating all GPU/container transitions to existing approved one-shot executor. Wired `./wizard.sh model 27b benchmark --plan/--execute` and `scripts/serve_27b.sh --bench-*`. Added `scripts/manager/p3_27b_roundtrip.py` with plan blocked until real P2 benchmark PASS, exact separate approval and two sequential, original-ID-checked return-to-original cycles. Wired `./wizard.sh switch flash-next-27b roundtrip --plan/--execute`. Added CPU fake-backend tests and CI. **Source only: no new DGX GPU benchmark, P3 cycle or permanent service switch executed.** See [P2/P3 procedure](../docs/P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md).

---

## 2026-11-06 — Real DGX installed-model scan confirms preserved original Orcarouter

User ran Wizard `model list --installed --json` and supplied `READ_ONLY_INVENTORY`: 3 registered model snapshots (Flash-Next 11/11 shards, 27B 3/3, original Orcarouter 17/17; no missing weight shards), and 4 unregistered HF cache snapshot sightings. Legacy Orcarouter BF16/MTP recipe directory **present**. Current Flash-Next API `LIVE_SERVICE_VERIFIED`. No changes to GPU/service/weights. Orcarouter source presence is empirical; recipe/runtime qualification remains unverified. Record separately from prior actual 27B GPU `PASS_RESTORED` and from yet-to-run 27B benchmark.

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

## 2026-11-06 — REAL Qwen3.8-27B GPU PASS_RESTORED and unified Manifest-led Wizard status

Operator supplied actual DGX `--trial-execute` result: `executed=true`, `target_api_ready=true`, `inference_ok=true`, `trial=PASS`, `restoration.status=RESTORED`, `issues=[]`, `status=PASS_RESTORED`. This supersedes earlier source-only `NOT_RUN` statements. User requested canonical Manifest-based Wizard read-only status rather than ad hoc Docker/curl. Implemented `scripts/manager/service_status.py` and unified `./wizard.sh service manager status --json`; added CPU fake-backend tests and updated routing. Kept old `inventory`, `health`, `logs` non-mutating. Combined status NOT_RUN on real DGX until operator invocation; no further actual GPU model or service changes made during this source update. See `handoff/P2-27B-GPU-TRIAL-PASS-20261106.md`.

---

## 2026-11-06 — Qwen3.8-27B experimental GPU trial (explicit approval, restore original)

After actual DGX 9/9 CPU import/ModelOpt registry PASS, implemented `scripts/manager/p2_27b_gpu_trial.py` with exact 64-character fresh plan approval, downtime acknowledgment, bounded initial 27B launch (NVIDIA ModelOpt mixed, no MTP), health/model ID + tiny generation test, private logs and exact original Flash-Next `:8000` container restoration. Added `--trial-plan`/`--trial-execute` to dedicated `serve_27b.sh`. Unknown Docker state or competing GPU container blocks start/restoration; trial never removes original. CPU regression CI `ea28b0c0` 354/354 PASS. **Actual 27B GPU trial and rollback NOT_RUN yet**. Compared MiaAI-Lab/Unsloth, NVIDIA forum GB10 recipe, eugr and NVIDIA guide; checkpoint formats not interchangeable.

---

## 2026-11-06 — Resolve 27B CPU import check false-negative

Observed the operator's actual isolated CPU import with Qwen3.5 and ModelOpt classes all present, but TypeError when our test incorrectly invoked vLLM `ModelOptMixedPrecisionConfig.get_name()` without `self`. Replaced with public vLLM quantization factory lookup under `modelopt_mixed` and exact returned class identity, without constructing quant config or model. Added 3 extra CPU tests plus instance-method regression; CI `0a14f189` **336/336 PASS**. Test must be re-run on DGX; runtime/launch still blocked.

---

## 2026-11-06 — Post-split DGX accepted read-only 27B entrypoint; new opt-in CPU import probe

Reconciled real DGX fast-forward and actual `serve_27b.sh --status/--plan` JSON, including verified original Flash-Next API identity and identical original/target local vLLM 0.32 image IDs. Added isolated `scripts/manager/p2_27b_loader_import_audit.py`, `scripts/temporary/p2-27b-loader-import-audit.sh`, and 8 CPU tests. It imports installed vLLM Qwen3.5 and ModelOpt class and verifies `get_name()=modelopt_mixed` under restricted CPU runc (opt-in; not run on DGX yet); no inference/weights/GPU/cache/network/ports. Source CI `834c750` **333/333 PASS**; 27B GPU/service stop/start/switch remains blocked.

---

## 2026-11-06 — Separate dedicated Flash-Next/27B server entrypoints

Moved existing Flash-Next launch implementation into executable `scripts/serve_flash-next.sh` and routed `./flash serve` directly to it. Replaced `scripts/serve.sh` with compatible default Flash-Next dispatcher and explicit 27B selection; added executable `scripts/serve_27b.sh` exposing only `--plan`/`--status` (read-only) while GPU start/switch remains blocked. Added 10 CPU regressions, executable-mode checks and CI workflow coverage for both new files. Source CI `67a54afc`: 325/325 PASS. No inference service changes, commits/merges to main or 27B GPU launch.

---

## 2026-11-06 — Operator DGX 27B source PASS and separate blocked launch-preview

Recorded actual exact pinned ModelOpt layer counts FP8 208 + NVFP4 193, and installed image source 4/4 checks true from CPU-only runc. Added `scripts/manager/p2_27b_launch_preview.py` + 12 CPU tests and `--launch-preview` Wizard CLI, returning proposed explicit `modelopt_mixed` vLLM argv and source/API fingerprints. This is not approval/execution, includes immutable pinned revision, prohibits Flash-Next PLE/MTP inheritance, and keeps transition/rollback/GPU gates closed. CI `ae4490d6` 315/315 PASS. No DGX GPU or inference service mutation performed.

---

## 2026-11-06 — Immutable NVIDIA ModelOpt mixed precision audit in P2 runtime preflight

Added `scripts/manager/p2_27b_quant_audit.py` + nine CPU regressions. Existing Wizard runtime-preflight now reads bounded exact-pin `hf_quant_config.json`, reports producer/quantization mode/layer counts and blocks unexpected or unparseable mixes while preserving all prior image/host/runtime gates. GitHub source commit `cd63f25`: CI 303/303 PASS; no model, GPU, Docker service, download or cache mutations performed.

---

## 2026-11-06 — Audit installed vLLM 0.32 image source using CPU-only runc

Based on the new DGX preflight result, authored `scripts/manager/p2_27b_image_audit.py`, `scripts/temporary/p2-27b-image-audit.sh` and 8 CPU regressions to audit the exact local image's registered Qwen3.5 model class and ModelOpt NVFP4/FP8 source without importing vLLM/CUDA. The wrapper defaults to plan-only and requires an explicit CPU-only run flag; image ID pinned and Docker isolated with runc, no GPU or network. SOURCE commit `acf5d64` CI 294/294 PASS. Actual operator CPU-only image probe, GPU/27B service/bench and rollback NOT_RUN.

---

## 2026-11-06 — P2 download completion evidence and guarded runtime preflight

Reconciled operator's actual NVIDIA 27B 19/19 exit-0 download with stale handoff. Added read-only `p2_27b_qualification.py` for pinned source/config, host ARM64, Docker image/platform/label and current service observation, plus `model 27b status --inspect-runtime` command and isolated CPU regressions. Kept the candidate recipe intentionally invalid, GPU start/switch blocked, and Flash-Next service unchanged. NVIDIA 27B `SOURCE_FILES_PRESENT_PINNED_CANDIDATE` does not establish loader, GPU/API, benchmark, or rollback qualification. CI needs validation at new HEAD.

---## 2026-11-06 — Complete P1–P7 Wizard console and lifecycle source (D-021)

Added `wizard/console.py` (three primary screens, model Continue/all actions, full service and advanced P3/P4/P6/P7 plans), `wizard/workflow.py` (P1/P2/P5 action slots for inspect/download/prepare/start/wait/verify/benchmark/switch/rollback/recipe), `wizard/roadmap.py` (all seven release gates), and `scripts/manager/service_logs.py` (bounded opt-in read-only service logs). Wired CLI `workflow` and `roadmap`, extended service `logs` route and CPU CI tests; preserved original P1 guarded engine and P2 approved downloader. Corrected P1 shortcut routing so another active GPU model or unknown service observation cannot enter P1 guided startup. All new P2–P7 mutation adapters remain blocked until runtime/recovery qualification. No DGX operations performed.

## 2026-11-05 — Read-only local API health and stop-before-start/rollback preview

Added `scripts/manager/service_health.py` (fixed loopback :8000 GET /health and /v1/models, bounded response and timeout, served-ID match) and `scripts/manager/service_transition_preview.py` (fail-closed atomic handover preview and explicit recovery). Wired health into existing service CLI and simple root Service choice; attached transition preview to model selection when other model observed. Extended CPU unit tests and CI. No actual service/DGX/API/GPU calls in this development session. Download is user-owned and in progress per last evidence; not verified complete.

## 2026-11-05 — Model-first Wizard UI and read-only automatic lifecycle planner (D-020)

Created `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`; changed `wizard/main.py` TTY root to 3 choices and introduced machine `select MODEL --json` / `model choose MODEL --json`. Added `wizard/quickstart.py`: safe consolidated download/monitor/P1-guided/switch-blocked plans from actual service + pinned checkpoint observations. Updated live `service_manifest.py` to classify in-flight `qwen38-27b-dl` without triggering new downloads; added unqualified Orcarouter service policy entry. Preserved old stage CLI and Flash-Next P1 backend. Added new CPU regression suite and refreshed canonical docs/CI/DECISIONS. User-owned NVIDIA 27B download started; receipt and runtime **not verified**. No service/API/GPU or DGX worktree actions performed in this coding session.

## 2026-11-05 — Fix P2 guided download falsely expiring under its own lock

After a user entered the correct plan ID, the second preflight rejected the request because raw inode counts, floor free GiB and Docker uptime were hashed. Created `_approval_facts` containing stable model/revision/cache/image/host running-state/port occupancy plus time window. Retained all live minimum-disk, inode, transfer and Docker checks on revalidation. Added mock CPU tests reproducing the change while state lock is created and guarding safety-relevant image/state drift. No DGX download or service mutation was performed by this change.

## 2026-11-05 — P2 pinned NVIDIA downloader and single active model manifest foundations

Operator confirmed one active GPU model per DGX Spark, both NVIDIA Flash-Next and 27B on host port 8000. Added `runtimes/service-policy.json`, `service_manifest.py`, `service_journal.py`; service menu read-only inventory uses actual Docker/socket. Added exact-revision `p2_27b_download.py` Wizard download plans with live revalidation/lock/approval and bounded evidence, no GPU/port/service effects. Added interactive `download --guided`, CPU regressions and pinned snapshot recognition without refs/main. Source and CI separate from actual DGX download/GPU/switch. No service interrupted.

## 2026-11-05 — Service management UI and NVIDIA 27B download planning

Added independent `service manager` Wizard menu/CLI (source-only) while retaining `operations system` for P7. Added `download` action to NVIDIA 27B planning, default BLOCKED. CPU router tests cover menu/catalog and refusal of unapproved mutation. Documented NVIDIA DGX `NO_PINNED_LOCAL_SNAPSHOT`; no download, restart, Docker/GPU work run.

## 2026-11-05 — P2 model choice changed to NVIDIA

Operator selected `nvidia/Qwen3.8-27B-NVFP4` instead of RadixArk. Switched read-only Wizard cache inventory, fixture cache path, invalid candidate recipe and current documentation. Preserved RadixArk 3/3-shard DGX result as historical evidence; NVIDIA local presence and DGX/GPU acceptance NOT_RUN. No runtime mutation or download.

## 2026-11-05 — P2 bounded config metadata audit

Added read-only `config.json` model facts (architecture, model type, quantization, context, vision marker) to 27B Wizard inventory. Source inspection remains unqualified for vLLM 0.32 and never authorizes runtime mutations; malformed and >1MiB config are explicitly not source-ready. Added CPU fixtures. GitHub CI results must be recorded separately; no DGX command executed in this session.

# Handoff changelog (append-only)

## 2026-11-05 — H-018 — Observed P1 GPU PASS; begin P2 source-only read inventory

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

- Distinguish high-level benchmark PASS from performance metric thresholds; operational doctor/inventory-plan exits remain 3, no P1 service lifecycle exit asserted. P2 candidate remains invalid/unpinned, operations blocked. No DGX action by assistant.


## 2026-11-05 — H-017 — Default Blazux baseline separated from optional Wizard probes

**Latest operator DGX result (2026-11-05):** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` summary from `--auto-gpu` at `805f8e3e`: source checkpoint and Hybrid are both READY, `source_issues=[]`, `hybrid_issues=[]`, 11 indexed source and Hybrid shards resolved, `api_model_ids=["qwen3.8-flash-next"]`, verify and benchmark plans each READY, yet **verify action returned FAIL** and benchmark BLOCKED by verification gate. Original console suppressed the Wizard's failure evidence location because it parsed the JSON outcome only on returncode 0, even though Wizard writes evidence for returncode 2. This is an actual attempted API/GPU verification with FAIL outcome, not evidence of a broken default Blazux model. Exact failing subprobe/error still unconfirmed until raw report is examined.

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

**SOURCE/CI validation (not DGX):** `391a2844f4c8549e282eae3e266806c89801ad1a`, GitHub push and PR checks 2/2 SUCCESS, each 15 manifest + 10 inventory + 13 launcher + 1 mode + 102 P1 + 32 router = **173/173 CPU tests PASS**. Real DGX execution against this fix has NOT_RUN; prior verify FAIL remains unresolved until this new code runs.


## 2026-11-05 — H-016 — Preserve default Blazux shared-metadata layout and preauthorize bounded P1 GPU tests

- Operator's latest actual DGX report showed expected API model ID `qwen3.8-flash-next`; original index/tokenizer and Hybrid tokenizer are symlinks resolving to existing files **outside** the model repo. 31,907,813-byte Hybrid index and `.prepared` exist, incomplete blob count=0. Older P1 checker falsely treated these metadata links as missing. This is a P1 source compatibility defect; no evidence that the full checkpoint needs re-downloading.
- New asset verifier accepts only nonempty **metadata** symlinks (`model.safetensors.index.json`, `tokenizer.json`) across the model-repo boundary; weight shards remain root-pinned, JSON index still parsed with 64MiB cap. Source/Hybrid symlink, dangling link and escaped shard regression fixtures added. Diagnostic records compatibility flag and target size without copying model files.
- User explicitly authorized GPU compute for non-disruptive P1 testing without per-action typed consent. Added `--auto-gpu` to the existing temporary wrapper. It checks expected served ID and health, takes current verify and benchmark hash IDs, invokes the original Wizard's same second-preflight protection, and never touches lifecycle/cache. P1 verify must PASS before bounded bench.
- This is source-only implementation; do not claim actual P1 GPU PASS until new DGX operator evidence. D-017, R1E added to permanent rules; P2–P7 and destructive actions remain separately blocked.
- **CI/source confirmation:** commit `0063b0e004902408f980c155076c098d49d4569e`, [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978150843/job/127081754127) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978155433/job/127081768853), both **SUCCESS**. Each job ran 15 + 10 + 13 + 1 + 84 + 32 = **155/155 CPU tests PASS**. No actual DGX GPU/API/benchmark result has been observed for the fixed Wizard yet.


## 2026-11-05 — H-015 — P1 metadata audit bug corrected and file-level diagnosis added

- Blazux default NVIDIA checkpoint remains supported. NVIDIA Hugging Face `fc694b5` index is 31.3 MB; our P1 Python audit invented a 16 MiB JSON size ceiling, causing a false rejection for *otherwise valid indexes*. Changed to a bounded 64 MiB cap; added realistic >16MiB and still-over-limit regression tests. This is our new code defect, not an upstream Blazux limitation.
- The actual DGX `source_issues=[model.safetensors.index.json, tokenizer.json]` are from the **earlier `_good_file` predicate** and therefore do not prove that this size gate caused the user's failure. New read-only diagnostics now identify file absent/dangling symlink/empty/outside repo, size, source vs Hybrid, and report parsed API model IDs.
- `66c6c448c1922f958886fa4696c403a4b6227685` source commit CI 2/2 **SUCCESS**, 145/145 CPU tests per job. No GPU/bench re-run, download/repair or service change by assistant; real DGX file evidence still required.


## 2026-11-05 — H-014 — Download completed (operator report), P1 audit disagreement

- Operator confirms NVIDIA Flash-Next download finished. First actual DGX wrapper run on branch `dea7c5a`: Git clean, process scan no active setup, `/health` and `/v1/models` exit code 0; Doctor/inventory plan exit 3; Wizard verify/bench both BLOCKED on generic checkpoint incomplete and Hybrid unready. No Wizard GPU/benchmark calls made.
- Root cause **unknown**: P1 audit currently reads `refs/main` only, whereas `./flash` accepts `refs/master` or an alternate snapshot; it also treats any remaining `.incomplete` blob as blocking even when indexed files are present. A full copy of the raw report has not been supplied; do not assert either explanation as proven.
- Added read-only `scripts/temporary/p1_cache_diagnosis.py`, wired into the one-command wrapper, plus CPU fixtures. First CI run failed due an optional diagnostic missing in the pre-existing report fixture; follow-up makes the field optional and adds tests. GitHub CI fix commit `4c0041dd230e2abe22ba8379aca74068933ecece` 2/2 SUCCESS, 138/138 CPU PASS per job. No DGX changes executed by assistant.


## 2026-11-05 — H-013 — Temporary operator bundle safety and final CPU CI

- Fix commit `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b` checks an operator-owned setup/serve process again just before test execution, blocks report output under HF cache, adds two CPU regressions, and removes duplicated CI invocation (temporary test suite is included under `test_p1_*_cpu.py`).
- GitHub Actions **2/2 SUCCESS**, each with 15 manifest + 10 inventory + 13 Flash launch + 1 executable-mode + 60 P1 (41 earlier and 19 temporary) + 32 Wizard router = **131/131 unique CPU tests PASS**. [Push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970955588/job/127058833280), [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970960007/job/127058848658).
- This is SOURCE/CI evidence, not a DGX runtime observation. Download, model service, GPU benchmarks and existing user processes were untouched by the assistant.

## 2026-11-05 — H-012 — Git-first temporary operator script rule and first P1 bundle

- User requested grouping post-download steps 1–3 into one script, committed in GitHub so the DGX operator only needs a Git Pull and single script invocation, with a separate temporary scripts directory. Follow-up explicitly requested that this **become a permanent documented project rule**.
- Added D-016 and OPERATING-RULES R1D: use `scripts/temporary/` for scoped tested throwaway wrappers; source commit + CPU checks → operator's own `git pull --ff-only` after preexisting processes finish → one wrapper for inspect → individually approved Wizard verify/bench → structured evidence. No implicit setup/download/stop/start/cleanup, no logs in Git/HF cache, no secret upload, no self-removal.
- Staged `scripts/temporary/p1-post-download.sh`, `p1_post_download.py`, README and mocked `tests/test_p1_temporary_cpu.py`; CI workflow and executable-bit test extended. **Runtime DGX operations NOT_RUN** in this GitHub-only session; result/CI to be verified at exact new HEAD.


## 2026-11-05 — H-011 — Rename numbered Wizard stages into capability groups

- User clarified that model P1/P2/P5 belong to one **Model management** menu with descriptive model submodules; P3/P6 belong to one **Model switching** menu with transition submodules; P4 storage and P7 operations are separate domains.
- Source commit `571e1c204d76bcb66b9e02cb1315ac775013a130`: move `wizard/menus/p1.py`–`p7.py` to `models/flash_next.py`, `models/qwen_27b.py`, `models/orcarouter_flash_next.py`, `switching/flash_next_27b.py`, `switching/orcarouter_27b.py`, `storage/flash_next_cleanup.py`, `operations/system.py`; update grouped two-level menu, CLI router, flat compatibility alias registry, 32 router CPU tests.
- **CI 2/2 SUCCESS**, 112/112 CPU tests per job; historical P1–P7 CLI flags and `wizard/p1.sh` remain compatible. No assistant DGX Docker, GPU, checkpoint/download, model switching or cleanup operation. Source-only P2–P7 still blocked.
- Active docs updated; D-015 supersedes D-014 numbered filename architecture, while original roadmap order P1→P7 remains unchanged.


## 2026-11-05 — H-010 — P1 JSON-mode hardening and final CPU CI

- Follow-up commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b` hardened P1: no guided prompt in `--json` mode, verified guided default for TTY, added two router regression tests, committed modular CLI contract/handoff.
- GitHub Actions push and PR `manifest` jobs both **SUCCESS**; per job 15 manifest + 10 inventory + 13 Flash launcher + 1 script mode + 41 P1 + 23 Wizard router = **103/103 CPU PASS**. [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961837000/job/127029761586); [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961842431/job/127029780582).
- No actual DGX Wizard GPU/API/benchmark operations, model switching, cleanup or gateway changes occurred. P2–P7 menu skeleton SOURCE_ONLY and execution BLOCKED. Original user download/setup/serve chain not interrupted.



## 2026-11-05 — H-009 — Build P1–P7 Wizard menu/router before operational phases

- User requests complete up-front Wizard **architecture** and per-stage/menu source modules rather than one monolithic file; direct CLI/JSON automation in addition to guided menu for user-mediated DGX operations.
- Added root executable `wizard.sh`, `wizard/main.py`, `wizard/menus/{common,p1,p2,p3,p4,p5,p6,p7}.py`; existing `wizard/p1.sh` retained as compatibility shim. P1 reuses existing guarded source workflow, P2–P7 status/plan interfaces explicitly `BLOCKED` for execution pending pinned recipes/source/runtime/rollback acceptance.
- First source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`, two GitHub Actions SUCCESS, **101 CPU tests per job** (21 new routing tests and 80 previous).
- Follow-up source hardens P1 JSON mode and adds two regression tests; verify final branch CI before release claim.
- No DGX Docker/GPU/service interaction, model download or deletion by assistant. User-supplied previous download/queued setup chain preserved. Actual P1–P7 runtime acceptance remains incomplete.


## 2026-11-05 — H-008 — P1 Wizard code batch and operator build/download evidence

- Operator-provided DGX log: Docker image `qwen38-flash-dgx:v0.32` built (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`), port :8000 free at earlier read-only scan, model download 9/25 = 36% in last visible line. OpenWebUI/Portainer kept running. Shell has queued `serve/wait/test` after `./flash setup default`.
- Added `scripts/manager/p1_assets.py` (read-only shard/index/cache/image integrity), `p1_wizard.py` (guarded actions, approval plan hashes, API smoke, immutable JSON evidence), `p1_bench.py` (bounded streaming TTFT/latency/tokens), `wizard/p1.sh` (guided and noninteractive), isolated mock CPU tests and GitHub Actions coverage.
- First source commit `c625a49276272e90d19ab6367f580a0230754890` applied; two GitHub Actions runs SUCCESS with 80/80 CPU tests each (41 new P1 + 39 baseline). No assistant-executed Docker, HF cache, GPU or API action. P1 runtime remains `NOT_RUN`. Do not start a duplicate download or interfere with existing operator setup.


## 2026-11-05 — H-007 — User reports NVIDIA Flash-Next checkpoint download in progress

- At 11:46 KST user reports `nvidia/Qwen3.8-Flash-Next-NVFP4` download is **still running**. This is USER_REPORTED, not independently inspected on DGX. Completion percentage, cache path, revision and storage remaining unknown.
- Recorded `DOWNLOAD_IN_PROGRESS` in CURRENT-STATE, priority guard in NEXT-ACTIONS and E-20261105-04 in evidence ledger. `DOWNLOAD_COMPLETE`, `HYBRID_READY`, GPU, API and benchmarks remain **NOT_VERIFIED / NOT_RUN**.
- Do not launch a competing download, `./flash setup default` or hybrid preparation while it may modify active weights/cache. P1 Wizard code and synthetic CPU tests can proceed while assets download.
- GitHub documentation change only: no Docker, image, download, cache or GPU operations performed by this session.

## 2026-11-05 — H-006 — Confirm all P1–P7 stages must be Wizard-driven

- User explicitly confirmed exact sequential target: Wizard Flash-Next install/run/bench → Wizard 27B install/run/bench → Wizard Flash-Next ↔ 27B switching → optional approved Flash-Next cleanup if storage insufficient → Wizard Orcarouter-Flash-Next install/run/bench → Wizard Orcarouter ↔ 27B switching → integrated Wizard operations release.
- Clarified `P4=SKIPPED_NOT_NEEDED` when disk allows; no automatic deletion. External port :8000 is the desired stable API entrypoint; actual DGX occupancy and activation remain NOT_OBSERVED.
- Promoted the sequence into `handoff/README.md`, `OPERATING-RULES.md`, `NEXT-ACTIONS.md`, `CURRENT-STATE.md`, `DECISIONS.md`, `SESSION-START-PROMPT.md` and master plan. First unfinished implementation remains **P1 Wizard end-to-end**, not merely manual `flash serve`.
- Documentation-only GitHub commit; no DGX, GPU, Docker operations, benchmark, deletion or model switch. Previously verified code HEAD `017319a`: 39/39 CPU tests in each of two successful GitHub Actions runs; recheck new commit checks separately.

## 2026-11-05 — H-005 — Restore executable bits and record CI failure

- Commit `7e8f4a109a04c130a5dba0d73e3ece0881d85478` had a real **CI FAIL**: manifest 15/15 PASS; inventory 10/10 PASS; shell launcher 9/13 PASS and 4/13 FAIL, exit 126 because `flash`/`scripts/serve.sh` lost executable permissions in GitHub tree update.
- Restored executable mode `100755` for both scripts; added a CPU regression test asserting launch scripts are executable and `bash -n` workflow checks. Rerun CI on new HEAD; preserve failed evidence instead of rewriting.
- No DGX, Docker runtime, GPU, API port or model state changed.

## 2026-11-05 — H-004 — Flash-Next on legacy :8000 and source-safe inventory

- User reports previous operating services deleted; current Docker/ports/images/weights on DGX **NOT OBSERVED**. Do not treat past Orcarouter container or model ID as current deployment state.
- Updated `flash`, `profiles/default.env`, `scripts/serve.sh` so NVIDIA Flash-Next default profile exposes host port 8000 and served name `qwen3.8-flash-next`. The upstream profile continues Hybrid+YaRN+MTP2; no SGLang.
- Replaced implicit `docker rm -f "$NAME"` with refusal to replace any existing exact Docker container name. No automatic removal on failed launch.
- Removed historical hard-coded 8000/name manifest bans. Added `scripts/manager/inventory.py` (read-only Docker/ss/disk/cache/mount reconciliation), Wizard `00-doctor.sh`/`10-plan.sh` wrappers, deterministic synthetic CPU tests, CI workflow coverage.
- This commit is SOURCE-only; tests CI verification to follow actual commit. No DGX GPU, cache mutations, download, Docker actions or API benchmark. Updated rules, decisions, contracts and runbook.

## 2026-11-04 — H-003 — N1 source-only manifest validation

- Added YAML recipe JSON Schema Draft 2020-12, CPU-only validator, pinned SHA/digest constraints, historical protected name/port denial, no approval bypass.
- Added deliberately invalid 27B candidate, synthetic fixture, 15 isolated CPU tests and new GitHub Actions CPU workflow. No Docker, GPU, actual DGX or model/cache/port changes.
- Ran: python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -q -> **15/15 PASS**; 27B candidate -> expected FAIL (exit 2); synthetic fixture -> schema PASS (exit 0) with launch_authorized=false.
- Updated CURRENT-STATE, NEXT-ACTIONS, EVIDENCE-LEDGER, DECISIONS and planning contracts. Draft PR #1 still requires CI readback and review; N2 and all operational testing remain outstanding.

## 2026-11-04 — H-002 — Documentation committed and draft PR opened

- Verified the new planning branch was 1 commit ahead of `main`, 10 tracked doc files, all under `docs/` and `handoff/`.
- Commit `76cd8dae16b0f34e47c353b56b6e9dbcc5fcde25` created the initial document set.
- Opened [Draft PR #1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1); no merge. At original commit check, GitHub showed 0 check-runs/0 PR workflow runs; **not CI PASS**.
- Corrected illustrative 27B recipe to keep PLE semantics `UNVERIFIED_FOR_27B` rather than assuming no PLE; still no runtime/CPU tests.
- Updated live handoff state, next actions and evidence. All work was GitHub-only.

## 2026-11-04 — H-001 — Recipe/Wizard migration planning initialized

- Confirmed user preference: **vLLM 0.32 only**, no SGLang, one large target at a time by default.
- Created planning branch `feature/recipe-wizard-handoff` from fork `main@b0aa8b77604139557169387b2fa8386355d8b651`.
- Preserved parallel `feature/orcarouter-bf16-adapter` design branch.
- Defined P0→P7 roadmap, manifest separation, wizard steps, protected runtime boundaries, gated checkpoint deletion and switch/rollback semantics.
- Added a standard entrypoint, living current state, evidence ledger, decisions, next tasks and new-conversation prompt under `handoff/`.
- **Tests:** documentation/source review only. No new CPU/CI/GPU/benchmark runs; no Docker, HF weights, model or service changes.
- PR/CI state should be read from GitHub; do not infer a merge.

## Future entry template

`YYYY-MM-DD — H-NNN — Subject`: exact changes, files, branch/commit, PR, test outcomes, external effects, remaining blockers. Newer entries should be placed **above** older entries while preserving them.
