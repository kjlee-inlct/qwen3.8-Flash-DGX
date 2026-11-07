# P2-FINAL — Protected NVIDIA 27B Native Tools V1 (SOURCE ONLY, 2026-11-07)

## Status and provenance

- Runtime target: DGX Spark GB10, vLLM **0.32**, model `nvidia/Qwen3.8-27B-NVFP4` revision `482ca0f3832238542f8f5295dde86b5f22711d80`, OpenAI served ID `qwen3.8-27b`, port **8000**, **ONE_ACTIVE_MODEL_ONLY**.
- Preserved original containers: `qwen38-27b` and `qwen38-flash`; preserve their Docker IDs, image objects, labels, pinned HF cache and immutable P2/P3/P3-C/ordinary-switch receipts.
- Operator's last actual DGX post-reverse observation: `qwen38-27b` LIVE_SERVICE_VERIFIED at :8000, journal VERIFIED/COMMITTED with 14 events. Current original Docker Cmd has **none** of `--enable-auto-tool-choice`, `--tool-call-parser`, `--reasoning-parser`; local `--tools-probe` returned **HTTP 400**. The HTTP body was not captured.
- New distinct variant identity: `nvidia-27b-native-tools-v1` / `qwen38-27b-native-tools-v1`. It uses the **same** pinned source and served ID but would run **instead of**, never alongside, the original 27B. **No such new Docker container has been created by source work.**
- The new candidate recipe `recipes/qwen38-27b-native-tools-v1.candidate.yaml` is intentionally **SCHEMA-INCOMPLETE** pending verified local image digest/source Git SHA/parser proof. It is **not** registered in `runtimes/service-policy.json`; the ordinary Wizard executor does not understand this third variant. Never promote it by merely changing YAML or copying a generated command.
- Source-only guards exist in `scripts/manager/p2_27b_tool_variant.py` and `scripts/manager/p2_27b_tool_streaming.py`, with offline tests. No approval or executable cutover path exists. Historical P3-C remains **PASS, FINAL, IMMUTABLE** and must NOT be rerun.

## Official parser candidate, not live validation

The upstream vLLM Qwen3.8-27B recipe lists:

```text
--enable-auto-tool-choice
--tool-call-parser qwen3_coder
--reasoning-parser qwen3
```

References: https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-27B.yaml and https://docs.vllm.ai/en/v0.32.0/features/tool_calling/ .

These published defaults **do not prove** that the exact local NVIDIA image's vLLM parser registry, pinned tokenizer/chat template and installed libraries support them. The candidate uses the original exact vLLM 0.32 Docker image SHA observed from the original `docker inspect`, same modelopt_mixed loader settings, same pinned snapshot and read-only cache mount, but a *different* container name and provenance labels. Verify the SHA against runtime provenance prior to any approval. No image updates, dependency installs, SGLang, or alternate API port are authorized.

## Implemented read-only and bounded inference checks

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
bash scripts/serve_27b.sh --tools-profile
bash scripts/serve_27b.sh --tools-variant-plan
```

The **variant-plan intentionally exits 3** even if all current source/container evidence checks pass, because its parser and live acceptance gates are unfulfilled. It checks the observed sole 27B API identity, preservation and startup flags of the original 27B, stopped Flash fallback identity, :8000 mapping, read-only /hf bind, occupied target name, and running Docker GPU users. It reports an **inert** candidate command and fingerprint; neither is an execution authorization. An incomplete inventory or identity drift fails closed. Use this only on the actual DGX; it is not an API verification by the assistant.

```bash
# Optional LATER, only after separate approved tool-enabled runtime deployment:
bash scripts/serve_27b.sh --tools-probe
bash scripts/serve_27b.sh --tools-stream-probe
```

These generate bounded local inference API requests; neither changes Docker state nor executes a real tool. The new streaming probe validates OpenAI SSE deltas, single tool index/name/id, incremental JSON arguments, `finish_reason=tool_calls`, `[DONE]` and absence of leaked `<think>` tags. It rejects truncated/oversized/malformed SSE, wrong model identity, HTTP errors and mismatched argument JSON. It does not by itself validate tool-result continuation, non-tool chat or WebUI. Existing `--tools-probe` validates one structured auto call and a *fixed simulated* tool result continuation.

## Required safe cutover execution contract — NOT IMPLEMENTED / NOT APPROVED

The following **must be implemented and Fake-DGX tested separately** before a new executable command or the ordinary Wizard release may be exposed:

1. **Audit/preflight:** immutable source/target/fallback IDs, images, labels, vLLM 0.32 registry/parser availability, pinned tokenizer revision/chat template, cache mount, single GPU Docker inventory, no variant name collision, exact source `:8000` API/Chat identity. Inspect both original containers and their immutable P3 lineage; preserve original P3 receipts.
2. **Independent human approval:** short-lived, domain-separated SHA binding complete source/target images, container IDs, recipe version and time window; TTY with explicit fresh plan, downtime acknowledgment and target acknowledgment. No hidden auto-ack or reuse of historic P3 approvals.
3. **Transactional lock/journal:** distinct namespace `~/.local/state/blazux-wizard/p2-final-tools-v1/`; mode 0600; one-use marker and append-only hashed events/immutable receipts, with full source/target/API identities. A crash or ambiguous prior attempt must **block** retries until manual inspection.
4. **Stop-before-start:** stop only the exact, approved original `qwen38-27b`; assert it stopped, confirm no other GPU-bound model and confirm host port 8000 is free; ONLY THEN create/start `qwen38-27b-native-tools-v1` under its own name. Do **not** remove/recreate/rename the original.
5. **Post-start qualification:** verify Docker ID/image and sole GPU active model, exact `:8000` served ID `qwen3.8-27b`, bounded non-tool chat, structured `tool_choice=auto` function name/ID/JSON arguments, fixed tool response continuation, streaming, reasoning isolation including `enable_thinking=false`, and WebUI Native end-to-end.
6. **Commit or restore:** record success only after all required checks; on failure, stop **only variant-owned** container and restart original `qwen38-27b`, verify image/API/Chat, commit `FAIL_RESTORED` receipt. If rollback is uncertain or fails, report `RECOVERY_FAILED`, block retries and require manual operator intervention. No unconditional delete/prune.
7. **Manifest/UX integration:** add explicit variant identity/lineage policy and variant-aware status/audit/rollback before any executor release. Current `runtimes/service-policy.json`, `operational_switch.py`, `operational_executor.py` and ordinary Wizard expect only original `27b` and `flash-next`; activating the variant without new integration would cause identity audits to fail. Never weaken `PRODUCTION_EXECUTION_RELEASED=False` as a shortcut.

## Test matrix and acceptance

| Area | Current source / real outcome |
|---|---|
| Original 27B completion, chat, GPU loader, benchmark | Historical actual DGX PASS |
| Historical P3-A/B/C | Actual DGX PASS; do not rerun |
| Ordinary recurrent 27B↔Flash | Actual DGX both directions PASS, latest journal 14 COMMITTED |
| Source isolated variant recipe and read-only inspection | Implemented source, CPU CI only |
| Streaming parser and malformed stream regressions | Implemented source, CPU CI only |
| Exact vLLM image parser + pinned tokenizer audit | NOT_RUN |
| Variant cutover, failure injection, original restore | NOT_IMPLEMENTED / NOT_RUN |
| Actual structured auto, continuation, streaming, reasoning | NOT_QUALIFIED (original HTTP 400) |
| Open WebUI Native Tools | NOT_QUALIFIED |
| Main Wizard production execution | `PRODUCTION_EXECUTION_RELEASED=False` |

**P2-FINAL remains OPEN.** Publish no private Docker IDs, raw logs, request/response bodies, approval SHA values or private receipts to Git. Actual service mutations require a NEW separately scoped downtime authorization. Work on P4–P7 does not override these gates.
