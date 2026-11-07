## LATEST 2026-11-07 — User selects SINGLE canonical 27B recipe replacement (not variant switching); benchmark then delete verified old backup ONLY after PASS

Supersedes previous proposed persistent `qwen38-27b`↔`qwen38-27b-native-tools-v1` service-switch feature: user clarified to change **original 27B recipe**, stop existing service, **recreate the same canonical `qwen38-27b` name** with already DGX-proven native-tool flags, run NEW bounded benchmark, **replace latest active benchmark result**, then **remove the exact old backup Docker container only when every test PASSES**. Old benchmark evidence, model images, checkpoint cache and P3 A/B/C records must NOT be deleted/re-written. The separate unqualified persistent-switch prototype was removed from branch (not deployed). Native Tools 1-shot real DGX `PASS_RESTORED` remains prior proof and trial variant `qwen38-27b-native-tools-v1` remains stopped; its 9 chained events and receipt preserved.

**New Git source (NOT YET RUN on DGX):** `recipes/qwen38-27b.runtime.json` (single pinned 27B canonical source, vLLM 0.32.0, exact local image `sha256:9479fc92...`, revision `482ca0f...`, Jinja SHA `c3cf9e34...`, native-parser flags), desired `runtimes/service-policy.json` registration, `scripts/manager/p2_27b_recipe_migration.py` (read-only plan, independent exact-TTY execution, backup rename, canonical recreation, ordinary chat/structured tools/stream/SSE 3-sample fresh benchmark, private immutable receipts, atomic latest benchmark pointer, remove verified stopped old container only after all PASS, restore pre-change on precommit failure), and `scripts/temporary/p2-27b-native-recipe-migrate.sh` (`--plan`, `--execute`, `--status`). Permanent runbook: [docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md). **Per user request, do NOT block Git Pull on Fake-DGX CI**, but no source change alone authorizes downtime. User runs `git pull --ff-only` and `--plan` first; `--execute` still needs new independently accepted SHA + downtime acknowledgement + explicit verified-backup-deletion acknowledgement. Pull does not mutate Docker.

**CAUTION:** Original P3 receipts pin the PRE-MIGRATION 27B Docker ID. When user explicitly approves deletion after successful promotion, that old ID becomes historic, NOT active. Existing generic operating Flash↔27B code must remain fail-closed until later lineage-aware revision; ordinary service status sees canonical `qwen38-27b` by name but doesn't check tool flags, thus use new `--status` check to verify post migration actual flags / benchmark. Do NOT rewrite historical P3 receipts or indiscriminately delete caches or Docker images. Model stays `qwen3.8-27b` at `:8000`, ONE_ACTIVE_MODEL_ONLY, no SGLang.

**Current real DGX:** user most recently showed `qwen38-27b-native-tools-v1` `Exited (0)`, original `qwen38-27b` operating, 9 one-shot events, and validated `PASS_RESTORED`. **Canonical recipe migration, its new benchmark, backup cleanup, and new `--status` PASS are NOT_RUN.** The new action runs real Docker only on operator-approved TTY, not via connector or Fake-DGX. If `--plan` BLOCKED or execute reports `FAIL_RESTORED`, `RECOVERY_FAILED`, `COMMITTED_CLEANUP_PENDING`, stop and reconcile; never retry blindly.

---

## LATEST REAL DGX — 2026-11-07 P2-FINAL native tool_calls + streaming PASS_RESTORED

**Actual operator-provided DGX run, not CPU simulation:** fresh TTY-approved `scripts/temporary/p2-final-native-tools-operator.sh --execute` completed with `status=PASS_RESTORED`, `trial=PASS`, `structured_tool_call=true`, `tool_result_continuation=true`, `streamed_tool_call=true`, `structured_probe_status=LOCAL_STRUCTURED_TOOL_CYCLE_PASS`, `stream_probe_status=LOCAL_STREAMED_TOOL_CALL_PASS`, `issues=[]`, `original_restored=true` / `restoration.status=RESTORED`. Operator then independently verified original `qwen38-27b` serving sole API ID `qwen3.8-27b` at `:8000`, `LIVE_SERVICE_VERIFIED`, `issues=[]`. Ordinary operating journal still `VERIFIED`/`COMMITTED`, **14 events**, `issues=[]`, last event hash `ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e`. Docker running list contains original 27B, Open WebUI (healthy), Portainer; no second running model shown.

**Qualification update:** The actual bounded 27B Native Tools `tool_choice=auto` + synthetic tool-result continuation + SSE + original restoration **subgate is now REAL PASS**. Earlier “not run” / original API HTTP-400 historical entries below remain chronological evidence, **not current milestone status**. This run does NOT verify real Open WebUI Native end-to-end, production Wizard native-tools switching, crash/forced-error rollback, comprehensive generated reasoning leakage, physical GPU process exclusivity or host port process ownership. The ordinary status fields `manifest_status=OBSERVED_UNQUALIFIED`, `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `operations_enabled=false` remain unqualified scopes rather than observed conflicts. Do not declare complete P2-FINAL production acceptance; ordinary Wizard `PRODUCTION_EXECUTION_RELEASED=False`, old P3-C immutable, original containers/images/HF cache retained, vLLM 0.32, port 8000, ONE_ACTIVE_MODEL_ONLY. **No repeat trial with the same SHA**; private attempt marker blocks blind repetition.

**Evidence detail and remaining acceptance gates:** [docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md](P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md). Next: private one-shot evidence/stopped variant inventory audit (read-only); design safe long-lived variant-aware service identity and production rollout (separately approved); live Open WebUI Native application end-to-end only during an independently approved maintenance period. No new service downtime authorized by this report.

---

## 2026-11-07 — REAL DGX NVIDIA 27B pinned-template CPU rendering PASS (P2-FINAL subgate CLOSED)

Operator fast-forwarded `1295f30..a137e27` and ran `bash scripts/serve_27b.sh --tools-template-audit` on the actual DGX Spark. Actual **operator-provided** JSON (do not confuse with GitHub CI) reported `status=CPU_TEMPLATE_RENDER_VALIDATED_ONLY`, `issues=[]`, all five markers **TRUE**: `tool_prompt_rendered`, `tool_result_rendered`, `non_tool_prompt_rendered`, `no_thinking_rendered`, `thinking_prompt_rendered`. `tokenizer_auto_template_present=true`, local Transformers `5.19.0`, expected and observed SHA-256 exactly `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`, pinned NVIDIA `chat_template.jinja` revision `482ca0f3832238542f8f5295dde86b5f22711d80`. Prior real DGX registry import audit independently confirmed vLLM `0.32.0`, tool `qwen3_coder` and reasoning `qwen3` registered.

**Evidence boundary:** This closes the **CPU parser-registry presence + pinned tokenizer/Jinja prompt-render** subgates, not actual `--enable-auto-tool-choice` serving, structured tool_calls, streaming, reasoning separation in generated API output or Open WebUI Native, and not production cutover acceptance. Original `qwen38-27b` remains the most recently observed active model, original `qwen38-flash` preserved, API :8000, `ONE_ACTIVE_MODEL_ONLY`, HF cache, original Docker IDs and old P2/P3/P3-C plus ordinary-switch receipts/journal untouched. This last test reported `docker_state_mutated=false`, `gpu_inference_executed=false`, `execution_enabled=false`, `approval_accepted=false`, `plan_id=null`.

**Next development:** Implement and Fake-DGX-test distinct **variant-aware service inventory/identity policy, crash-safe independent journal/rollback and separate operator approval** before any live Native Tools cutover. Keep original service manifest semantics and `PRODUCTION_EXECUTION_RELEASED=False` until explicitly reviewed. The existing Fake-DGX simulation is NOT a real executor. No operator downtime consent is given by this CPU PASS; DO NOT run the inert Docker candidate, manually stop the original or replay P3. Draft PR #1 remains open/unmerged.

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

## SOURCE UPDATE 2026-11-07 — Protected Native Tools V1 candidate, SSE probe; P2-FINAL still OPEN

Added isolated source candidate `qwen38-27b-native-tools-v1` in `scripts/manager/p2_27b_tool_variant.py` and intentionally schema-incomplete recipe `recipes/qwen38-27b-native-tools-v1.candidate.yaml`. `--tools-variant-plan` performs read-only source/container/GPU inventory and ALWAYS refuses execution; do not run its command preview. New `--tools-stream-probe` validates bounded local streaming SSE tool-call structure but is **not** actual DGX acceptance. Full design and unresolved execution/rollback/manifest gates: [protected variant contract](P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md). Existing original Docker Cmd lacks tool flags and its HTTP 400 stays the latest actual evidence. P3-C remains closed. No actual DGX Docker or service change, no normal Wizard production unlock.

---

## NEW ACTUAL DGX EVIDENCE — 2026-11-07: P2-FINAL Native Tool Calling NOT PASS on original 27B

Operator local source updated to `09c6780`; **27B service `LIVE_SERVICE_VERIFIED`** at port 8000 with only `qwen3.8-27b`, original `qwen38-27b` active, `issues=[]`. Independent ordinary operating journal `VERIFIED/COMMITTED`, 14 events after actual 27B→Flash→27B normal transfers; **reverse operating postcheck no longer pending**.

Direct inspect of the running preserved NVIDIA 27B Docker `Config.Cmd` confirms original `modelopt_mixed`/BF16, context 8192/seq 1/GPU mem 0.70/eager, **no** `--enable-auto-tool-choice`, `--tool-call-parser`, or `--reasoning-parser`. The opt-in `scripts/serve_27b.sh --tools-profile` shows correct source candidate `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`, `SOURCE_PROFILE_ONLY_DGX_NOT_QUALIFIED`, and does not retrofit the original container. **Actual localhost** `--tools-probe` returns `status=BLOCKED`, `issues=["LOCAL_API_HTTP_ERROR_400"]`, and structured tool call/tool continuation/reasoning separation all false. HTTP response body was not supplied; do not misquote it. This is not a model-load issue: regular chat and API identity remain verified.

**P2-FINAL remains NOT QUALIFIED.** Next work: implement **separate, versioned, immutable tool-enabled 27B variant** and safe approved cutover/restore contract; the existing `qwen38-27b` Docker image/ID/P3 provenance are relied on by the ordinary switch and MUST NOT be casually replaced. Source/test/CI first; actual DGX model downtime only with separately scoped consent. Validate parser compatibility, non-tool chat, structured auto calls, JSON arguments, fixed test-tool response continuation, streamed tool calls, reasoning separation, Open WebUI Native, and complete rollback evidence. Do not mark P2 full complete before real acceptance. Historical P3-C stage C already completed PASS, remains frozen.

---

# P2 LAST acceptance item — NVIDIA Qwen3.8-27B Native Tool Calling, vLLM 0.32

**Accepted ordering (2026-11-07):** P2 original pinned download, GPU loader/trial/benchmark and source restore had already passed on actual DGX. Add **P2-FINAL: structured Native Tool Calling and Open WebUI tool-use integration** as the last P2 acceptance requirement. P3-C historic one-off A/B/C has ALREADY passed on actual DGX and MUST NOT be re-run, modified, reopened or represented as a current pending transition.

## Actual DGX baseline and historical evidence

- Official checkpoint **`nvidia/Qwen3.8-27B-NVFP4`**, revision `482ca0f3832238542f8f5295dde86b5f22711d80`, OpenAI served ID `qwen3.8-27b`, **vLLM 0.32**, API port **8000**, fixed single-model operation.
- Its internal architecture/registry string `Qwen3_5ForConditionalGeneration` reflects implementation ancestry; do **not** silently rename the checkpoint or API to Qwen3.5-27B.
- The DGX operator previously observed 27B normal text inference PASS and **Open WebUI Native automatic tool request ERROR**: `"auto" tool choice requires --enable-auto-tool-choice and --tool-call-parser to be set`. Correct plain-text inference does not prove Tool Calling.
- More recent, independent ordinary switching live acceptance: 27B→Flash **PASS**, then Flash→27B **PASS** with four exact TTY approvals; latest user-provided final operating result `Observed model: 27b`. **Independent post-reverse `service manager status` and `operational_audit` outputs are not yet supplied**. Original P3-C acceptance (2026-11-07) remains permanently PASS; no stage C replay.
- The **running preserved 27B Docker container's exact `Config.Cmd` has not yet been supplied**. Source launch profile prior to this change omitted the auto tool/reasoning flags. Do not confuse new source flags with the existing container's immutable startup command.

## Official vLLM recipe and source-only candidate

vLLM Qwen3.8-27B recipe and vLLM 0.32 tool-calling documentation support:

~~~bash
--enable-auto-tool-choice \
--tool-call-parser qwen3_coder \
--reasoning-parser qwen3
~~~

References: https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-27B.yaml and https://docs.vllm.ai/en/v0.32.0/features/tool_calling/ .

**Implemented source, NOT live deployment:**
- `scripts/manager/p2_27b_launch_preview.py`: `_candidate_argv(cache, image, tool_calling=True)` opt-in emits all five argument tokens. Default `False` intentionally leaves every historical P2 trial/planner/startup argument unchanged.
- `scripts/manager/p2_27b_tool_calling.py`: `profile` reports source flags and explicit remaining acceptance gates; `probe` performs a bounded **localhost-only** tool roundtrip (GET sole active ID, POST `tool_choice=auto`, validate structured function call and JSON arguments, send fixed simulated tool result and require non-thinking final answer). It does not execute any actual function or alter Docker.
- `scripts/serve_27b.sh --tools-profile` and `--tools-probe` expose these read-only/source-only checks through the existing dedicated 27B entrypoint.
- Fake-DGX CPU regression tests check flags, defaults, schema, auto tool choice, tool-message continuation, malformed/HTTP-400 safe failures. CPU CI proves source safety only.

## Operator read-only checks (before any new downtime approval)

~~~bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
docker inspect qwen38-27b --format '{{json .Config.Cmd}}' | python3 -m json.tool
bash scripts/serve_27b.sh --tools-profile
~~~

The following is a **small, explicit local inference probe**; it may return `BLOCKED/LOCAL_API_HTTP_ERROR_400` on the existing container, and such failure is expected if auto tool parser flags were not present when that container was first created. It does **not** change the service:

~~~bash
bash scripts/serve_27b.sh --tools-probe
~~~

No operation above changes container start args. A `docker restart` cannot enable different Docker Cmd flags.

## Strict acceptance and migration boundary

**P2-FINAL is NOT YET PASS** until ALL of these are evidenced:

1. Real image vLLM **0.32** parser `qwen3_coder` and reasoning `qwen3` are present and compatible with the pinned NVIDIA checkpoint and its chat template.
2. A separately designed migration plan safely preserves immutable P2/P3 original 27B and Flash containers/assets/receipts. **Do not edit/recreate/delete the original `qwen38-27b` in-place**: its container ID/image and old P3 provenance are pinned in the ordinary switch preflight. New tool-enabled profile needs its **own separately identified service/recipe variant** and an explicitly reviewed stop-before-start, port-8000, ONE_ACTIVE_MODEL_ONLY and original rollback path.
3. Under new, separately scoped DGX downtime approval, an actual tool-enabled runtime serves the **same** `qwen3.8-27b` identity and passes `tool_choice=auto`, correct structured function ID/name/arguments, tool response continuation, **streamed** tool-call chunks, reasoning separation and non-tool chat/health.
4. Open WebUI **Native** mode actually calls the tool and handles the tool response; disabled Builtin Tools workaround is not acceptance. Record versions/config and sanitized results in private reports; do not publish sensitive prompts.
5. After controlled rollback and final API status/journal audit, source configuration, manifests, and UX/proxy gateways pass tests. Do not flip the normal operating Wizard release flag until these independent service/migration gates are qualified.

**P3-C completed historical acceptance stays FINAL PASS** while P2's newly appended Tool Calling integration is still OPEN. This new acceptance gate does not invalidate past P2 GPU/benchmark PASS or historical P3-C real execution, and never authorizes repeating completed stage tests.

## Phase status

| Milestone | Status |
|---|---|
| P2 pinned download, loader, actual 27B trial and bounded benchmark | REAL DGX PASS (historical) |
| P2-FINAL source opt-in flags and safe local tool-cycle probe | SOURCE IMPLEMENTED / CPU CI pending or PASS after run |
| P2-FINAL actual 27B Native Tool Calling + streaming + Open WebUI | NOT_RUN / NOT_QUALIFIED |
| P3-C original one-off Flash→27B completion | REAL DGX PASS — IMMUTABLE/CLOSED |
| Ordinary 27B↔Flash switching backend | BOTH DIRECTIONS operator-reported REAL PASS; reverse postcheck pending |
| Normal interactive Wizard menu production switching | RELEASE GATED / ACTUAL MENU UX NOT ACCEPTED |
