> **Actual DGX read-only observation, 2026-11-06:** Flash-Next `LIVE_SERVICE_VERIFIED` at :8000; qualified P2 benchmark receipt hash `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9` detected; P3 `sequence --plan` correctly `BLOCKED` by separate entry; `stage-a --plan` reported `READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, expiring 14:40 KST. **Actual P3 A/B/C transitions remain NOT_RUN, no new downtime approval.** These are operator-provided observations, not independent DGX runtime access. See [EVIDENCE-LEDGER](../handoff/EVIDENCE-LEDGER.md).

# P3 persistent Flash-Next ↔ NVIDIA 27B switching — source contract

**2026-11-06 (KST). Development status: SOURCE IMPLEMENTED; CPU regression required; DGX P3 actual switch NOT_RUN; production qualification NOT_GRANTED.** Binding decision: [D-034](../handoff/DECISIONS.md) and [manual transition sequence](P3-MANUAL-TRANSITION-SEQUENCE-20261106.md). P2 bounded NVIDIA 27B benchmark **COMPLETED** with `BENCH_PASS_RESTORED_VERIFIED`; original Flash-Next was verified after restoration. P2 completion does **not** authorize P3 runtime changes.

## Implementation

- `scripts/manager/p3_persistent_switch.py`: independent `stage-a`, `stage-b`, `stage-c` plan/execute adapters. `--plan` gathers fresh localhost Manifest+API/Docker inventory, validates the successful local P2 receipt, exact source and target images, preserved container IDs and source/target state, verifies no additional GPU-enabled Docker container, and returns short-lived action-specific SHA-256 plan ID **only if all checks succeed**. Plan does not call Docker stop/start, GPU inference, or network inference.
- `scripts/manager/p3_p1_evidence_gate.py`: final stage C requires operator-local P1 `verify` and `benchmark` PASS receipts created **after** successful stage B and matching the preserved Flash-Next image, plus reviewed historical `doctor` and `inventory_plan` rc=3 remediation evidence. P1 benchmark must include numerical TTFT/latency/tokens per second and at least three samples. Old PASS labels or missing numbers cannot qualify C.
- `scripts/manager/service_journal.py`: existing atomic append-only state machine and manifest snapshots. P3 uses private `~/.local/state/blazux-wizard/p3/` stage receipts, nonblocking transition lock, one-time attempt markers and journal. Interrupted / recovery-failed stage is **not** automatically resumed or treated as successful.
- `wizard/menus/switching/flash_next_27b.py`: introduces independent P3 stage routes while preserving existing `sequence --plan` as a **read-only global sequence**, and keeping obsolete `roundtrip --execute` blocked. `wizard/main.py` remains the common CLI entrypoint.
- Existing P2 one-shot 27B trial's candidate Docker command and source/image checks are reused **only** for the first-stage target creation; the P2 one-shot restore executor itself is **not** used as the persistent switch because it would always return to Flash-Next.

## Stages and no-auto-transition boundary

| Stage | Required running source | Intended target left active on success | Prerequisite |
|---|---|---|---|
| P3-A | Flash-Next | NVIDIA 27B | Qualifying P2 receipt, separate explicit P3 entry and fresh A approval |
| P3-B | NVIDIA 27B | Flash-Next | Immutable P3-A PASS receipt, fresh B approval |
| P1 correction | Flash-Next | Flash-Next | Investigate historical rc=3 and repeat P1 functional and measured benchmark; no implicit switch |
| P3-C | Flash-Next | NVIDIA 27B | Immutable P3-B PASS, accepted post-B P1 diagnostics/functional/numeric receipts, fresh C approval |

Every stage is a single stop→port-release→start→exact `/health` and `/v1/models` verification→journal event→receipt transaction. Stage results never launch the next stage. Successful stage C retains **27B**, not Flash-Next.

## Operator read-only inspection (safe source contract)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
./wizard.sh switch flash-next-27b sequence --plan --json
./wizard.sh switch flash-next-27b stage-a --plan --json
```

After stage A has actually been approved, executed and verified, B may be planned read-only with `./wizard.sh switch flash-next-27b stage-b --plan --json`. After stage B and genuine P1 remedial proof, C may be planned with `./wizard.sh switch flash-next-27b stage-c --plan --json`. These examples are **NOT permission to execute**. Source-only CI cannot establish runtime safety.

Live execution syntax (documentation only; **do not run without separately approved maintenance window, current plan ID and recovery agreement**):

```bash
./wizard.sh switch flash-next-27b stage-a --execute \
  --approve-plan "$P3_A_PLAN_ID" \
  --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME \
  --enter-p3 I_SEPARATELY_AUTHORIZE_P3_ENTRY --json

./wizard.sh switch flash-next-27b stage-b --execute \
  --approve-plan "$P3_B_PLAN_ID" \
  --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME --json

# ONLY AFTER post-B P1 corrective/functional/rebenchmark evidence is accepted
./wizard.sh switch flash-next-27b stage-c --execute \
  --approve-plan "$P3_C_PLAN_ID" \
  --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME --json
```

**Never reuse a P2 plan ID, stage-A approval for B/C, old roundtrip approval, or an expired plan.** Each plan contains stage, source/target identity, immutable P2 receipt SHA-256, previous P3 stage receipt SHA-256, P1 acceptance evidence (when needed), :8000 and ten-minute time bucket; recheck on execute. Do not invent plan IDs.

## Recovery and limits

The runner stops only the expected Docker source by exact verified ID/image and leaves it intact; verifies :8000 released; starts the intended target. On failure, it attempts to stop only its owned A target or the exact previously recorded B/C target, then restart the **same original source container** and recheck the correct model ID/API. Stage receipts are private and non-overwriting. Foreign Docker IDs, changed image/labels, unexpected GPU consumers, missing P1 evidence and inconsistent journal state block operation.

**Limitations:** SIGKILL, Docker daemon/host failure, OOM or power loss can prevent automatic recovery. True arbitrary GPU process exclusivity, complete HF mount provenance, profile compatibility under all loads, and fault-injection validation are not established by CPU tests. Real DGX P3 steps A/B/C remain `NOT_RUN`; neither `SOURCE IMPLEMENTED` nor CI SUCCESS is production acceptance.

P1 diagnostics JSON at `~/.local/state/blazux-wizard/p3/p1-diagnostics.json` is a **reviewed evidence receipt** (private mode 0600). Its required fields are `status=PASS`, `doctor_exit_code=0`, `inventory_plan_exit_code=0`, a detailed `historical_rc3_disposition` and `finished_at_utc` later than stage B. Do not fill this receipt by assuming rc=3 was harmless; investigate the exact historical logs and live checks before accepting it. Detailed P1 verify/benchmark receipts come from the original `scripts/manager/p1_wizard.py` approval workflow and must contain actual measured values.

Historical P2 27B benchmark record: `handoff/EVIDENCE-LEDGER.md`. No private DGX evidence/logs are uploaded to GitHub automatically.
