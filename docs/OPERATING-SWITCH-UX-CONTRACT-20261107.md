## Addendum — 2026-11-07: REAL DGX 27B smoke PASS; strict format deviation

**Actual operator result, newer than the previous source-only NOT_RUN note below:** local `/health` and sole `/v1/models` ID `qwen3.8-27b` PASS; actual model `qwen3.8-27b` chat completion `finish_reason=stop` and 26 completion tokens under `vllm-0.32.0-bfe01fe9`. `bash scripts/temporary/operational-27b-curl-smoke.sh` emitted `HEALTH_PASS`, `IDENTITY_PASS`, `INFERENCE_PASS`, `27B_CURL_SMOKE_PASS`. This is **real hardware functional inference** (not mock). No Docker/service mutation.

However, the direct response's `message.content` contained reasoning-like prose, a literal `</think>` marker, then `DGX_OK` while `message.reasoning=null`; an **exact-response assertion must fail**, even though generation completed normally. `FORMAT_PASS` / `FORMAT_DEVIATION` classification was subsequently added in source; it does not retrospectively claim new real DGX runtime testing of that updated script. Exit 0 and `27B_CURL_SMOKE_PASS` continue to mean **functional inference only**, not exact-format compliance. An inferred misconfigured reasoning parser is a hypothesis, not proven; investigate per-request chat-template controls separately and do not restart live vLLM solely on this observation.

Qwen/vLLM background: [vLLM reasoning outputs](https://docs.vllm.ai/en/stable/features/reasoning_outputs/) and [Qwen vLLM deployment](https://github.com/QwenLM/Qwen3/blob/main/docs/source/deployment/vllm.md). Check version/model-specific compatibility before configuring `--reasoning-parser qwen3` or request-specific `chat_template_kwargs.enable_thinking=false`.

**P3 A/B/C remain history only; general 27B↔Flash execution/rollback and Wizard approval UX are NOT yet qualified.** Preserve 27B active, Flash fallback and original private receipts.

---

## Addendum — 2026-11-07: 27B real-generation curl smoke (DGX execution NOT_RUN)

The operator correctly highlighted that `LIVE_SERVICE_VERIFIED` only proves running container, HTTP `/health` and `/v1/models` **identity**, not successful token generation. Before concluding NVIDIA 27B is functionally healthy **now**, run the one-shot, non-disruptive script from the actual DGX when 27B remains the current active model:

~~~bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/operational-27b-curl-smoke.sh
~~~

This invokes **curl** against 127.0.0.1:8000, requiring: HTTP 200 /health; exactly `qwen3.8-27b` in /v1/models; and a non-empty final chat reply with matching model ID from one /v1/chat/completions request, bounded to max 256 output tokens and an HTTP timeout. No docker lifecycle, switch, network target override, file deletion, API key or benchmark. A 27B thinking response that emits no final message fails closed for this **user-visible completion** criterion and requires operator review (not a launch/rollback instruction). Output markers: `HEALTH_PASS`, `IDENTITY_PASS`, `INFERENCE_PASS`, then `27B_CURL_SMOKE_PASS`; on failure nonzero exit, do NOT infer successful inference from existing P3 receipts. Paste stdout/stderr for verification. The Wizard ordinary switch preview *displays* this optional smoke instruction but never runs it implicitly. `tests/test_operational_curl_smoke_cpu.py` uses an offline fake curl binary to test PASS/wrong IDs/empty completion/HTTP/transport errors and verifies no non-local target is accepted.

**Source-only script and Fake-CPU tests are not proof of fresh real-DGX execution.** Existing 27B active status is last operator reported, not live observed from this assistant. General operating switch, its execution UX and real rollback remain unqualified/unreleased; P3 A/B/C never rerun.

---

## Addendum — 2026-11-07: independent guarded transaction SOURCE now present, still NOT RELEASED

The independent \`scripts/manager/operational_executor.py\` source has now been added, using a fresh plan recheck, two exact operator acknowledgments, private lock and single-use attempt marker, append-only journal separate from P3, stop-before-start, port release, exact container/image IDs, 27B label, target API served ID and original-container preservation, with best-effort restoration and explicit failure outcomes. It is **NOT routed through Wizard CLI/TTY** and is not authorized for live DGX use. CPU Fake-DGX tests in \`tests/test_operational_executor_cpu.py\` cover both directional successes, cancellation/invalid IDs, failure/recovery branches and one-time plan attempts. This updates the "required executor" portion below: **source implementation exists, but release qualification, guided approval flow and independently approved real DGX validation are still outstanding**. No running 27B service was altered, no P3 stage rerun or real operating transition occurred. CPU success never authorizes downtime.

---

# Ordinary model-switch preflight — Wizard source iteration (2026-11-07)

**Source-only / read-only. Not a GPU or service acceptance certificate.** Historical P3-A/B/C passed on actual DGX but recurring operating switches and interactive UX have NOT passed acceptance. Do not replay completed one-off stages. Last observed DGX remains NVIDIA 27B on port 8000.

## Operator path and CLI

Open **./wizard.sh → Select / run model → NVIDIA Flash-Next or NVIDIA 27B → Review ordinary model switch (read only)**. The advanced P3 menu offers the same ordinary-switch preview instead of recommending replay of old P3 stages. Historical P3 CLI stage routes remain backward compatible and keep their own authorization gates.

Equivalent CLI (read-only):

~~~bash
./wizard.sh switch flash-next-27b operational --target flash-next --plan --json
./wizard.sh switch flash-next-27b operational --target 27b --plan --json
~~~

All requests with --execute, --approve-plan, or --ack-downtime fail closed immediately. The candidate fingerprint is NOT an executable approval token, even if a SHA256 candidate is present. No operation will stop/start a service or make an API inference. No operational downtime consent is requested in this source iteration.

## Preflight contract

**scripts/manager/operational_switch.py** builds a preview only after:

1. Fresh manifest-led LIVE_SERVICE_VERIFIED API / model ID observation, with the source model matching the service policy.
2. Three immutable permission-checked P3 A/B/C receipts proving historical directed stage success, pinned image/container identities, consistent P2 receipt SHA and chronological finishes. They do NOT authorize a new switch.
3. Read-only Docker checks: exact source running, preserved target stopped, pinned image IDs and 64-hex container IDs, port 8000 bindings, safe restart policy, P3 A provenance for the preserved 27B container and zero foreign GPU-enabled containers.
4. The independent operational-switch journal has no unresolved phase. No old P3 state or new operating journal is modified by preview.
5. The requested target is a different supported model (Flash-Next or NVIDIA 27B). Orcarouter remains unqualified.

Passing produces **READY_FOR_OPERATOR_REVIEW_ONLY** while still setting executed=false, execution_supported=false, operations_enabled=false and approval_accepted=false. Blockers never authorize service changes.

## Readiness dashboard

**./wizard.sh roadmap --json** distinguishes locally readable P1/P2 historical Verify/Benchmark records; strictly checked P3 A/B/C receipt lineage; independently measured current API health and served ID; source, CPU CI and operational switch scope; interactive UX acceptance; and P7 release readiness. Private receipts may not exist on CI, in which case historical local receipt availability is UNKNOWN/UNAVAILABLE, not fabricated PASS. Current API presence does not by itself prove P3 historical execution, general rollback readiness or benchmark validity.

## Required before executable operating switch

- Independently qualified guarded operating-switch executor with a NEW scoped exact-plan approval (not a P3 A/B/C plan ID), bounded expiry and live state recheck.
- Single-active-GPU lock, stop-old-before-start, port 8000 free check, exact Docker/image IDs, immutable attempt/receipt, append-only separate journal, target API ID and post-switch verification.
- Best-effort source restore with explicit RESTORED versus RECOVERY_FAILED, fail-closed on unknown state, no automatic retry after ambiguous outcomes.
- Complete Fake-DGX rollback/crash state machine, repeated bidirectional flow tests, and a separately approved actual DGX end-to-end trial. Existing operational NVIDIA 27B must remain untouched until explicit new consent.

## Test scope and deployment

**tests/test_operational_switch_cpu.py**, included in source-only GitHub Actions, exercises the preview, both directions, missing/altered receipts, foreign GPU conflicts, container ID drift, stale journal, wrong API status, model already active, rotating SHA, read-only menu/CLI and immediate execute rejection. Existing P1/P2/P3 mechanisms are not changed, and the running DGX is not accessed.

After review and a green CI, the operator can optionally fast-forward Git source and run the read-only preview. Source update does not imply permission to switch, restart, delete containers or files, or run P1/P2 benchmarks again.
