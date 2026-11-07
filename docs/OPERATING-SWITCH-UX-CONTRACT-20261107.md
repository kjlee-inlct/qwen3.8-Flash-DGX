## 2026-11-07 — Latest operating Wizard source candidate: model-first UX, transaction, source-only trial (DGX NOT_RUN)

This newest section supersedes earlier notes saying the operating executor is not wired to Wizard. User priority is **the existing `./wizard.sh` ordinary Flash-Next ↔ NVIDIA 27B operating switch**, NOT the postponed Open WebUI Tool Calling / 27B recipe work.

**Wizard source now links all stages:** `./wizard.sh` main choice **4. Switch active model**, or model-centered screen choice **6. Guided operating switch** → fresh guarded preflight → preview / source-target image and preserved container facts → independent executable SHA (strictly different from preview SHA) → three exact human acknowledgements **once production is separately qualified** → independent locked backend stop-before-start → target `:8000` HTTP/model ID **and a real bounded chat** → final pinned container and journal receipt confirmation; failure triggers best-effort original restoration and reports `FAIL_RESTORED`, `RECOVERY_FAILED`, or committed evidence uncertainty, never automatic repeated stages.

**Journal integrity hardening:** `scripts/manager/operational_audit.py` verifies full append-only event SHA chain, current snapshot and last committed immutable receipt. A crash between event append and snapshot update or a missing completion receipt blocks any new plan. `OLD_STOPPING` is entered only after an extra source identity recheck; pre-stop drift closes `PLANNED→CANCELLED` without Docker downtime. Target API verification is followed by a small real chat, separate post-start GPU conflict check, and final journal audit.

**Safely separated execution:** Ordinary production menu still has `PRODUCTION_EXECUTION_RELEASED=False` in the source; normal CLI `--execute` fails closed. One-off, separately authorized **physical acceptance** is available through `./wizard.sh switch flash-next-27b operational acceptance --target flash-next --plan --json` (read-only) and the explicitly opt-in `... --execute` requiring **four exact manually typed TTY approvals**, no automated approval, source/state recheck, and no automatic return. Tracked wrapper: `scripts/temporary/operational-switch-acceptance.sh`. See **`docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`**. Every direction requires a new plan and independent consent, especially while 27B is live.

Offline Fake-DGX tests cover both directions, cancellation/no TTY, expiry, execute/JSON refusal, identity drift, rollback, inference failure, attempt replay, journal divergence, record integrity and UI route. **Actual DGX ordinary switching, rollback and integrated live production UX are NOT YET VERIFIED or RELEASED.** The operator has not separately approved new live 27B downtime; the code alone never modifies their running service. P3 original A/B/C receipts, Flash and 27B original model assets, Portainer/Open WebUI and API port 8000 are preserved. Draft PR #1 remains unmerged.

---

## 2026-11-07 — Priority restored: Guided model switch UX → independent executor (SOURCE, release gated)

**Immediate engineering priority is recurring Flash-Next ↔ NVIDIA 27B model switching from the EXISTING `./wizard.sh` interface.** Open WebUI auto tool calling, `qwen3_coder` parser configuration, NVIDIA 27B recipe tool changes, P4 cleanup and P5/P6/P7 are **DEFERRED**, not prerequisites for this source iteration. Do not change the working DGX 27B service.

New operator navigation:

- `./wizard.sh` → **Select / run model → target NVIDIA Flash-Next or NVIDIA 27B → 6. Guided operating switch (release gated)**.
- `./wizard.sh switch flash-next-27b operational guided --target flash-next` opens the same review-only guided path. Existing option 5 and `operational --target ... --plan --json` remain read-only previews.
- This is not P3 stage A/B/C execution. Original stage receipts, image IDs and container IDs are evidence only.

**Source connection:** `scripts/manager/operational_wizard.py::guided` reads a fresh `operational_switch.make_plan` with current model/target/port/P3 lineage, displays any blockers, and derives a **domain-separated execution approval SHA** from the immutable source/target IDs, images, preview hash and expiry with `operational_executor.execution_plan_id`. The read-only preview fingerprint is NOT itself a valid execution approval: the backend explicitly rejects it. The source-only test path obtains three distinct exact inputs: new execution SHA, separate downtime consent, and target-specific activation consent, then calls the independent `operational_executor.execute` which rechecks live state under the private lock; the success/failure result is rendered including private evidence path. No approval value is accepted through a legacy P3 path.

**Production safety gate:** `PRODUCTION_EXECUTION_RELEASED = False` in `operational_wizard.py`. It is **not** configurable by TTY prompt, CLI flag or environment; `--execute`, `--approve-plan` etc are blocked before preflight by the public guided CLI. The source-only suite temporarily patches the gate **within CPU Fake-DGX test process** and injects a fake Docker/HTTP backend. No actual DGX switching is authorized by this source work; user-facing guided mode stops at `RELEASE_GATED`. Release requires crash/ambiguous recovery review and a separate operator-approved real DGX trial; it cannot be inferred from CPU tests or historical P3 A/B/C.

**Required remaining work:** harden the recurring executor's crash/port/unknown-state recovery gates, independently qualify exact backend/multiclient behavior, perform scoped operator-approved bounded DGX trial for both directions/rollback, decide release activation process, then switch production gate only via code review. A one-screen target selection alone does not establish end-to-end operator acceptance.

---

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
