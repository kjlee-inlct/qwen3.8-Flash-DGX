> **2026-11-07 ACTUAL DGX STAGE UPDATE (supersedes pending B language below):** P3-A Flash-Next→27B PASS; **P3-B 27B→original Flash-Next PASS**, independently checked `LIVE_SERVICE_VERIFIED` and `qwen3.8-flash-next` served at :8000. The next step is **NOT another model switch**: collect verified post-B raw doctor/inventory diagnostics using new read-only D-016 `scripts/temporary/p1-post-b-audit.sh`, followed only under fresh individual approvals by actual post-B P1 Verify and measured Benchmark. P3-C Flash-Next→27B remains blocked/not authorized until all new evidence passes. Do not reuse old stage plans or assume source CI is DGX runtime evidence. Original old B report name `p3-a-operator-20261106T223124Z-14861d75.json` is a known historical bug; immutable canonical B receipt is `stage-b.json`.

---

> **2026-11-06 update (D-037):** Initial P1 pre-A evidence now `PRE_A_P1_REVIEW_READY`, `issues=[]` on actual DGX; old claims of unprovided initial Flash P1 numbers and unresolved historical rc3 are superseded **for initial P1**, not post-P3-B P1. User conditional authorization permits considering **stage A only** after fresh plan and interactive full SHA/downtime/separate P3-entry acknowledgments. D-016 tracked `scripts/temporary/p3-stage-a-operator.sh` defaults read-only and may invoke canonical stage-A only after all three inputs in `--execute` mode. B, post-B P1 functional+measured rebenchmark and C require their own gates. Actual P3 transitions NOT_RUN and rollback remains best-effort. See [source and safety](P3-PERSISTENT-SWITCH-SOURCE-20261106.md) and [handoff decision D-037](../handoff/DECISIONS.md).

> **Source implementation update — 2026-11-06:** P2 bounded NVIDIA 27B benchmark is now **BENCH_PASS_RESTORED_VERIFIED** (3/3 actual DGX API requests); Flash-Next post-restore `LIVE_SERVICE_VERIFIED` observed in operator output. The former 'P2 benchmark not run' section below is HISTORICAL, superseded by this update. New `scripts/manager/p3_persistent_switch.py` implements distinct stage A/B/C approval-gated persistent switching **in source** with CPU mock tests and append-only local stage journal. New `scripts/manager/p3_p1_evidence_gate.py` blocks final C until P1 functional, numerical benchmark and rc=3 diagnosis evidence. **Actual P3 DGX/GPU switching remains NOT_RUN, NOT_PRODUCTION_QUALIFIED.** See [persistent switch source operations](P3-PERSISTENT-SWITCH-SOURCE-20261106.md), and live P2 measurements in [EVIDENCE-LEDGER](../handoff/EVIDENCE-LEDGER.md). This update is not live-operations approval.

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
