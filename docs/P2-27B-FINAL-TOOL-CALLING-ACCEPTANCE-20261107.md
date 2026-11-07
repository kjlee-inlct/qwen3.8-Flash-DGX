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
