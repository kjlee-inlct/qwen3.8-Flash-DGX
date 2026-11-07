## LATEST DGX CONFIRMATION — 2026-11-07: missing auto tool/parser CLI flags + real HTTP 400

The previously missing **actual preserved 27B `docker inspect Config.Cmd`** was supplied. It contains the pinned NVIDIA modelopt_mixed launch but **none of** `--enable-auto-tool-choice`, `--tool-call-parser`, `--reasoning-parser`. The source-only `--tools-profile` correctly advertises `qwen3_coder` and `qwen3`, but did NOT modify the Docker command. Actual localhost `--tools-probe`: **`BLOCKED/LOCAL_API_HTTP_ERROR_400`**, no structured tool result. Do not assume the exact HTTP 400 response text because that body was not captured. Current 27B otherwise `LIVE_SERVICE_VERIFIED`, and operating journal `VERIFIED/COMMITTED/14`. Open WebUI Native full tool cycle remains unqualified. Root cause for the earlier auto-tool-choice error is **strongly supported by the missing launcher switches**; adding flags requires a separately approved, preserved-container-safe **new variant** and parser compatibility testing, not a restart of the original. P2-FINAL is pending. See `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.

---

## 2026-11-07 — Promoted to P2-FINAL qualification item (not yet DGX accepted)

User selected formal Qwen3.8-27B Native Tool Calling as final P2 item. **Official Qwen3.8-27B vLLM recipe** specifies `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3` (the model uses internal `Qwen3_5` config, but installed checkpoint/API is `nvidia/Qwen3.8-27B-NVFP4` / `qwen3.8-27b`). Implemented opt-in, isolated `tool_calling=True` candidate argv and `scripts/serve_27b.sh --tools-profile`/ `--tools-probe` with bounded localhost API test. **Nothing automatically changes preserved 27B Docker Cmd**; Open WebUI Native full tool cycle, parser compatibility and safe 27B migration still NOT_QUALIFIED. Earlier erroneous P3-C NOT_RUN statements are obsolete: P3-C one-off already **REAL PASS/CLOSED**. Ordinary two-way backend operator trials also both REAL PASS; normal menu production execution remains source-gated. Full detailed gate: `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.

---

# Open WebUI 27B automatic tool-choice incompatibility — 2026-11-07

## Observed actual DGX (operator-provided)

- Active NVIDIA pinned `qwen3.8-27b` on vLLM 0.32 and :8000; direct `/health`, `/v1/models` and `/v1/chat/completions` **PASS**.
- `chat_template_kwargs.enable_thinking=false` on direct non-tool chat returns **exactly `DGX_OK`**, `finish_reason=stop`, `reasoning=null`, 4 generated tokens. This is **REAL DGX** and resolves the direct text-format anomaly for that request only.
- Selecting 27B in Open WebUI and asking a question yields: `"auto" tool choice requires --enable-auto-tool-choice and --tool-call-parser to be set`. WebUI exact version, attached/builtin tools, raw request, live Docker `Config.Cmd` and current parser list are **NOT YET OBSERVED**. Do not claim the model itself failed.

## Evidence-backed source distinction

- `scripts/manager/p2_27b_launch_preview.py::_candidate_argv` builds the 27B Docker/vLLM command **without** `--enable-auto-tool-choice`, `--tool-call-parser` or `--reasoning-parser`. `p2_27b_gpu_trial.py::trial_command` derives from it; persistent P3 restored the preserved 27B container rather than rebuilding its arguments. This matches the error, but is **source inference, not a fresh inspect of running Docker arguments**.
- `scripts/serve_flash-next.sh` **does** include `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`. Do not infer that Flash's tested parser automatically qualifies this pinned NVIDIA 27B.
- vLLM 0.32 documents that `tool_choice=auto` requires auto-tool-choice enabled and a compatible tool-call parser. Open WebUI current documentation states built-in tools are injected by default in Native mode and can be disabled per-model.

## Immediate safe workaround: Open WebUI only, NO DGX lifecycle change

In Open WebUI **Workspace → Models → edit 27B → Capabilities → Builtin Tools: OFF**. Disable any workspace Tools attached to the selected model and chat-specific Integrations/Tools or injected features for that test. Start a new 27B chat and ask a plain text question. The exact UI may vary with Open WebUI version. This disables the associated autonomous built-in tools (memory, web, code, etc.); it is a test/workaround, NOT verified full WebUI agentic acceptance. **Do not change 27B Docker/service/port**.

To check the *actual* preserved 27B container command without stopping it:

~~~bash
docker inspect qwen38-27b --format '{{json .Config.Cmd}}' | python3 -m json.tool
~~~

The mere absence of parser flags is diagnostic; a `docker restart` **cannot add new startup arguments**. Do NOT manually `docker rm`, `docker run`, build, stop or replace the preserved container.

## Future qualified solution (source plan only, not executed)

For production Open WebUI Native Tool Calling, define and test a per-model vLLM **startup profile** that enables `--enable-auto-tool-choice` plus a parser matching the exact pinned NVIDIA checkpoint and its tokenizer/chat template. The upstream vLLM recipe for related Qwen3.5 27B lists `qwen3_coder` with `qwen3` reasoning parser, and the local Flash launcher also selects this combination. This is a **candidate**, not proof of Qwen3.8 NVIDIA 27B parser capability on the existing custom vLLM 0.32 image. Qualify parser availability, request `tools` schema, auto decision, tool_calls/arguments, tool-response continuation, streaming and reasoning separation using Fake-DGX source tests and an independently approved bounded DGX trial.

Any update of an existing Docker container's launch command requires a separately planned replacement/recreation or rollback-friendly migration, **new scoped operator downtime consent**, and fresh pinned-image/provenance/port/one-model checks. Preserve old P3 A/B/C receipts, 27B active service, Flash fallback, HF caches, containers and Draft PR. No environment or service changes authorized by this diagnosis.

## Source references

- https://docs.vllm.ai/en/v0.32.0/features/tool_calling/
- https://docs.openwebui.com/features/extensibility/plugin/tools/
- https://recipes.vllm.ai/Qwen/Qwen3.5-27B

## Acceptance gates

| Dimension | Scope | Status |
|---|---|---|
| Live 27B chat without tools | Real DGX | PASS |
| Exact reply with per-request thinking disabled | Real DGX | PASS for one request |
| Open WebUI native `tool_choice=auto` | Real DGX | ERROR / BLOCKED |
| Builtin Tools-off WebUI workaround | Real WebUI | NOT_RUN |
| Verified live Docker `Config.Cmd` | Real DGX read-only | NOT_RUN |
| 27B auto tool parser on pinned runtime | SOURCE/CPU + DGX | NOT_QUALIFIED |
| General 27B ↔ Flash operating switch | DGX | NOT_QUALIFIED |
