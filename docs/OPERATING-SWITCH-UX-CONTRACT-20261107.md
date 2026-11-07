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
