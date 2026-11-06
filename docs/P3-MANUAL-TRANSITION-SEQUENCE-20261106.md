# P3 revised contract — manual entry, Flash-Next P1 remediation, final 27B

Date: 2026-11-06 (KST). **Overrides the older two-temporary-roundtrip procedure** in [P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md](P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md). This is the accepted user-specified operating sequence. **This document does not authorize live service changes.**

## Required execution order (strict gates)

| Order | Operator-approved phase | Required evidence / next step |
| --- | --- | --- |
| P2 completion | NVIDIA Qwen3.8-27B GPU benchmark + restore original Flash-Next | `BENCH_PASS_RESTORED_VERIFIED`, actual metrics, local `*.benchmark.json`, `LIVE_SERVICE_VERIFIED` `qwen3.8-flash-next`. **STOP. Never enter/launch P3 automatically.** |
| P3 entry | **Separate intentional operator decision and approval** | Verify live manifest and P2 evidence, acquire a separate scoped plan/ack for any service transition. No stale P2 ID can approve P3. |
| P3 stage A | Flash-Next → 27B, ONLY to establish a verified 27B source state | Since P2 restored Flash-Next, establishing 27B before attempting 27B→Flash-Next requires a separately approved transition. Exact `/v1/models` ID `qwen3.8-27b` + `/health` + one GPU model/port :8000. If failed, restore pre-transition Flash-Next. |
| P3 stage B | **27B → Flash-Next** | Independent scoped transition approval; check API `qwen3.8-flash-next`, image/container identity, service health, exclusive ownership. This stage must PASS before P1 remediation and benchmark. |
| P1 corrective work | **While Flash-Next is active**, resolve P1 shortcomings, rerun verification/benchmark | Audit earlier P1 `doctor` and `inventory-plan` exit 3 causes (exact reasons not supplied), verify functional `default_completion/chat/tools/vision` probes and normal API, capture real measured latency, TTFT and token throughput with source/seed/profile and local evidence. Prior P1 `verify=PASS` and `benchmark=PASS` are NOT sufficient without measured numbers and unresolved exit-code disposition. If P1 remains incomplete, **do not start final 27B switch**. |
| P3 stage C | **Flash-Next → 27B**, intended final active model | New dedicated approval. Verify final served ID `qwen3.8-27b` and host :8000, original rollback assets retained, `LIVE_SERVICE_VERIFIED`, record append-only transition journal and exact source/target image/container identities. Do not automatically restore Flash-Next after successful final switch. |
| Acceptance | P3 final completed ONLY after stage C, not merely a roundtrip | Actual P2 benchmark receipt, verified stage A/B evidence, P1 gap-closure and measured P1 rebenchmark, verified final 27B API, and safe fallback plan. Any missing evidence => BLOCKED / partial, not PASS. |

All state-changing operations require fresh observed facts, exact plan ID, scoped downtime acknowledgment and existing approved recovery policy. Each transition shall stop only the exact authorized source, verify port released, start exact target, verify model identity, append evidence, and on failure restore the source. Protect original Docker containers, checkpoints and image; never auto-delete/convert/re-download. Unexpected GPU consumers or API identity mismatch => BLOCKED. Host crash/Docker daemon failure can defeat automatic rollback.

## Read-only operator interface (source implemented)

```bash
./wizard.sh switch flash-next-27b sequence --plan --json
```

The response always keeps `plan_id=null`, `executed=false`, `operations_enabled=false`. Without successful local P2 evidence, returns `P2_BENCHMARK_RECEIPT_NOT_FOUND` (or another explicit P2 evidence issue). With P2 evidence present and original Flash-Next still verified, returns `P3_SEPARATE_OPERATOR_ENTRY_REQUIRED`. This read-only plan is **not** authorization and has no GPU, Docker or service mutation.

**Retired unsafe old interface:** `./wizard.sh switch flash-next-27b roundtrip --plan/--execute` and direct `python -m scripts.manager.p3_27b_roundtrip execute` are both now permanently `BLOCKED` with `P3_LEGACY_ROUNDTRIP_RETIRED`. A successful prior P2 benchmark does NOT unlock it.

## Current implementation status

- **P2**: exact-approved benchmark script prepared and CPU-CI tested. Latest DGX operator supplied **read-only** P2 plan `READY_TO_REQUEST_TRIAL_APPROVAL` with no issues; at the time this document was created **no actual measured P2 benchmark output had been supplied**.
- **P3**: revised phase sequence is represented read-only and old executor disabled, with unit tests. **Full durable bidirectional service-switch executor and stage journal validation are NOT IMPLEMENTED or GPU qualified** under this new sequence. The canonical next real step remains the separately approved P2 benchmark, not P3.
- **P1**: previously provided DGX functional verify/benchmark `PASS`; numerical performance metrics not yet supplied, prior `doctor` and `inventory_plan` results 3 need analysis. Preserve baseline and do not invent remedial results.

See [handoff CURRENT-STATE](../handoff/CURRENT-STATE.md), [OPERATING-RULES](../handoff/OPERATING-RULES.md), [DECISIONS](../handoff/DECISIONS.md), and [NEXT-ACTIONS](../handoff/NEXT-ACTIONS.md).
