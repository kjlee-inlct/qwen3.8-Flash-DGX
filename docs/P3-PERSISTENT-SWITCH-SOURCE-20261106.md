> **2026-11-07 SUPERSEDING ACTUAL DGX STATE:** P3-A and P3-B **BOTH PASSED on DGX**. Stage-B canonical Wizard receipt `~/.local/state/blazux-wizard/p3/stage-b.json` is `PASS/executed=true/live_verified=true`; wrapper `P3_B_PASS_FLASH_NEXT_ACTIVE` with post-switch `LIVE_SERVICE_VERIFIED` and API `qwen3.8-flash-next`. Old wrapper report `~/blazux-p3-reports/p3-a-operator-20261106T223124Z-14861d75.json` was misnamed due to A's persist function; the stale `approval_accepted=false` is bookkeeping, not a failed authorization. Preserve both records unchanged. P1 POST-B read-only inspect `~/blazux-p1-reports/20261106T224010Z-d2095867/result.json` PASS/plan READY does **NOT** execute Verify or Benchmark. Current full raw doctor/inventory rc3 disposition remains unqualified until the new D-016 `scripts/temporary/p1-post-b-audit.sh` is run. Newly developed P3-C evidence gate reads immutable latest diagnostics attempt and demands new actual P1 Verify+Benchmark with revision/image/numeric proof; C NOT_RUN/NOT_AUTHORIZED. Never repeat A/B, bypass approvals, or merge Draft PR. Old sections are preserved as historical evidence.

---

> **2026-11-06 ACTUAL P3-B INSPECT PASS, NOT EXECUTED:** DGX user ran tracked `scripts/temporary/p3-stage-b-inspect.sh`; `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, active `qwen3.8-27b`, original Flash container ID and P3-A/P2 provenance pinned. Report `~/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. This is permission to **review**, not to stop 27B. User has not separately approved B. Distinguish shared runtime Docker image from model API ID and preserved container IDs. Original B inspect plan `7af40f...` expires 17:50 KST and must not be reused.

> **Stage-B core ACK contract FIXED before actual B downtime:** former all-stage string `I_ACCEPT_FLASH_NEXT_DOWNTIME` is inaccurate because B stops active **NVIDIA 27B**. New B plan/executor require `I_ACCEPT_27B_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_P3_STAGE_B` plus exact newly generated current stage-B SHA. A/C contracts unchanged. D-016 tracked `scripts/temporary/p3-stage-b-operator.sh` is safe by default (`--plan`), with an independently approved `--execute` requiring three exact manual inputs and new plan+source checks, canonical Wizard guarded B and separate post-switch Flash API verification. No automatic P1 after B, no C. Source fake-DGX 489/489 CPU PASS; DGX B operator NOT_RUN, original 27B remains active. Stop on failed restore/unknown ID. See [D-040](../handoff/DECISIONS.md), [temporary wrapper runbook](../scripts/temporary/README.md).

> **2026-11-06 STAGE-A REAL DGX SUCCESS:** Operator executed P3-A with fresh plan `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4` and 3 manual ACK inputs. Canonical Wizard returned `stage=a,status=PASS,executed=true,live_verified=true`; tracked operator wrapper `P3_A_PASS_27B_ACTIVE`, `issues=[]`; independent after-switch Manifest/API `LIVE_SERVICE_VERIFIED`, `observed_model=27b`. Private evidence `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`, Wizard receipt `~/.local/state/blazux-wizard/p3/stage-a.json`. **27B deliberately remains active**. Previous A NOT_RUN lines below are historical, superseded. This is actual DGX execution evidence, not source CI alone.

> **B stage requires independent operator authorization:** newly tracked `scripts/temporary/p3-stage-b-inspect.sh` is exclusively **read-only**: actual A receipt, live 27B API and original preserved Flash ID/image plus canonical `stage-b --plan`. No `--execute` and no GPU/model lifecycle mutation. D-016 pull then inspector; B executable and downtime require a later fresh, separate operator decision and exact plan. Only after B success run full new P1 verify, measured benchmark and diagnostics, then independently approve C final 27B. Preserve original Docker/image/checkpoint, keep Draft PR unmerged and never auto-chain stages. See [D-039](../handoff/DECISIONS.md) and [temporary inspector procedure](../scripts/temporary/README.md).

> **2026-11-06 ACTUAL PRE-A P1 CLEARANCE:** DGX operator ran the tracked P1 pre-A wrapper after code fix: `status=PRE_A_P1_REVIEW_READY`, `issues=[]`, historical/current rc3 own-Flash collisions verified; original P1 functional and real measured benchmark PASS (3 samples, TTFT P50 1.398707s, latency P50 1.687357s, mean throughput 38.2968 tokens/s), Flash source API/image still live. Private evidence `~/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`. Earlier P1 initial blockers are closed for **pre-A**, not the mandatory **post-B** P1 retest. The operator's **previous conditional** Flash→27B approval is now eligible only for P3-A. No actual P3 transition has run.
>
> **D-016 stage-A tracked operator interface:** `scripts/temporary/p3-stage-a-operator.sh --plan` read-only; `--execute` requires interactive typed current full plan ID + exact downtime and separate P3 entry strings, then delegates only to the canonical Wizard stage-A executor with fresh-plan recheck and independently verifies the final 27B API/model/image. Single stage only; failure stops, recovery is best effort. Do not auto-run B or C, auto-merge PR or delete model assets. Host process GPU exclusivity/daemon failure recovery remain unqualified by CPU tests. See [temporary workflow](../scripts/temporary/README.md), [D-037](../handoff/DECISIONS.md).

> **2026-11-06 pre-A P1 review:** User supplied actual original P1 numeric metrics (TTFT P50 1.398707 s, latency P50 1.687357 s, mean 38.2968 completion tok/s from 3 requests) and inspect-only source/Hybrid/API READY. Outstanding historic and current doctor/inventory raw rc3 evidence is collected via the GitHub-tracked `bash scripts/temporary/p1-pre-a-readiness.sh` after DGX fast-forward pull; do not substitute ad hoc code or rerun initial P1 GPU benchmark needlessly. The D-016 wrapper never executes P3 or grants downtime. Its `PRE_A_P1_REVIEW_READY` result would confirm **only pre-A initial P1 evidence**, not the D-034 required post-B verify/rebenchmark and separate C approval. P3 final C evidence gate also corrected to validate real P1 Wizard `identity.health=PASS` and `models` list (not missing `identity.status`). [CPU CI 435/435 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) source only; actual DGX wrapper and P3 still NOT_RUN.

> **2026-11-06 P1 pre-A audit / current operator conditional instruction:** Flash-Next actual P1 baseline+extended functional and bounded benchmark PASS recorded on 2026-11-05, but numerical TTFT/latency/throughput evidence and raw historic `doctor/inventory-plan` rc3 explanation remain missing, plus post-B P1 retest is not yet possible. The operator's "approve 27B **if** no P1 outstanding" is **NOT MET**, not a live P3-A authorization. Keep current Flash service untouched.
>
> **Source fix to post-B P1 gate (CI 418/418 PASS):** `wizard/00-doctor.sh` and `wizard/10-plan.sh` are dry-run launch preflights: when `qwen38-flash` is active on :8000 they return **3** despite valid `inspect_host.status=PASS` and `errors=[]`, because `collision_free=false`. The old requirement for both rc0 during an already-active Flash service was contradictory. `p3_p1_evidence_gate.py` now checks **both exit codes 3 plus the complete parsed `doctor_output` and `inventory_plan_output`** for exact `qwen38-flash`, matching immutable image ID, active Up status, :8000 published mapping, `status=PASS`, `errors=[]`, `scope=SOURCE`, `dry_run=true`, correct proposed name/port/served ID and expected name/port collision flags. Generic rc3 is NOT enough; inventory failure or foreign image/port blocks. Requires still a reviewed `historical_rc3_disposition` and `finished_at_utc` newer than stage B, private 0600 receipt and fresh post-B functional/numeric P1 evidence. This is **source-only**; no actual historical rc3 cause or P3 transition proved.

> **2026-11-06 source hardening:** P3 sequence plan now explicitly reports source-staged adapters available but `persistent_switch_dgx_qualified=false`; it remains `BLOCKED` and no `plan_id` or automatic progression. Failed-target rollback also rechecks for newly appearing GPU-enabled Docker containers before restarting original source; unexpected consumer causes `RECOVERY_FAILED`, not a dual GPU start. [GitHub CPU CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860) **413/413 PASS** on tested source commit `02bf94c`, but **no actual DGX switching/failure recovery is validated**. Host processes outside Docker are still not conclusively accounted for and require separate preflight review.

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

P1 diagnostics JSON at `~/.local/state/blazux-wizard/p3/p1-diagnostics.json` is a **reviewed evidence receipt** (private mode 0600). Its required fields are `status=PASS`, **both `doctor_exit_code=3` and `inventory_plan_exit_code=3` for the verified *already-running* source**, full parsed `doctor_output` and `inventory_plan_output` JSON showing `status=PASS`, `errors=[]`, `name_conflict=true`, `port_conflict=true`, `collision_free=false`, `scope=SOURCE`, `dry_run=true`, exact proposed `qwen38-flash` / port 8000 / served ID, and one active `qwen38-flash` container with the immutable Flash image and published :8000. It also requires a detailed `historical_rc3_disposition` and `finished_at_utc` later than stage B. A genuine observation failure or a foreign image cannot be accepted as a benign collision. Do not fill this receipt by assuming rc=3 was harmless; investigate the exact historical logs and live checks before accepting it. Detailed P1 verify/benchmark receipts come from the original `scripts/manager/p1_wizard.py` approval workflow and must contain actual measured values.

Historical P2 27B benchmark record: `handoff/EVIDENCE-LEDGER.md`. No private DGX evidence/logs are uploaded to GitHub automatically.
