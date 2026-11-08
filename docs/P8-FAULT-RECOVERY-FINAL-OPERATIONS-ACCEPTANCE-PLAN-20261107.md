## 2026-11-09 P8 source/Fake-DGX readiness only — no live recovery or release

At source commit `21aa6c9`, `scripts/manager/p6_p8_fakedgx.py` provides an *in-memory* two-direction Orcarouter↔27B model-switch state machine with synthetic target-start, target-API and source-restore failure cases. `./wizard.sh operations recovery-acceptance fault-matrix --fake-dgx --json` can exercise those 8 simulated cases. GitHub CPU/Fake-DGX CI passed; the fake adapter does **not** use the production switch executor, Docker, GPU, localhost API or actual Journal persistence. It is not evidence of working automatic rollback, real DGX fault injection, outage acceptance, or `production_released=true`. Actual P8-R1/R2/R3 and P8-A/B/C/D live acceptance remain held for separate operator approval and verified evidence. The P6 non-authorizing live preflight cannot approve a switch, even if its current Docker/API identity appears consistent. [P5 technical](P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md) · [Full audit](HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md).

---

## 2026-11-08 — Actual P3 source-handoff evidence and P4-A-only capacity observation

P3-E host assets actual read-only PASS within **metadata/index/shard presence** scope: pinned FP8-hybrid view, index 31,907,813 bytes/299,845 entries, 11 shards size sum 129,771,270,410 apparent bytes, template/meta hashes; never full cryptographic shard integrity or fresh reinstall. P3-F actual local 7-suite 168/168 CPU PASS with production gate off; 27B API current 8/8 PASS. This completes P3's **source/CPU handoff** prerequisites to P8, not P8 runtime signoff.

P4-A begins as Wizard read-only capacity inventory. No measured real DGX P4-A storage output yet, and no deletion decision is implied. Preserve all Flash/27B/Orcarouter assets pending P8 acceptance and an explicit separate P4 disposal choice. P8-R0/R1/R2/R3 scope stays unchanged; real canonical reinstall, induced fault recovery and production release NOT_RUN.

---

## 2026-11-08 — Explicit P3-E/F handoff to P8; P4 is held

Operator directs P3 closeout, **P4 NOT_STARTED**. See `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`. P3-E source/read-only evidence and P3-F CPU/Fake-DGX evidence must not be mistaken for real fresh Flash reinstall or production lifecycle acceptance.

Add subtracks within the existing P8 stages (all NONEXECUTABLE until separately approved): **R0** canonical desired Flash Docker/image/env/cache/template/security/network/restart specification and Fake-DGX drift tests; **R1** exact-plan/TTY-approved fresh real Flash reinstall, 27B source preservation, port/GPU checks; **R2** functional API/tool/vision/benchmark/idempotence/journal and authorized return; **R3** independently approved fault injection, verifiable automatic original restoration and final Wizard UX/security/operations release after P5/P6/P7 prerequisites.

Latest DGX index: 31,907,813 bytes, 299,845 tensor-map keys. Source bounded cap 400,000 verified by [GitHub CPU CI 42392758148](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42392758148) 880/880 PASS; actual host read-only rerun pending. P3-F current local 7-suite rerun pending. Neither command authorizes Docker mutation, P8 fault trials or final release.

---

# P8 — Fault recovery, automatic rollback and final operational acceptance

**Decision:** Operator requested on 2026-11-07 that **“장애 발생 후 자동 복구 검증과 최종 운영 수용은 P8로 이동”**. This is the canonical milestone assignment. **P3-G is complete (REAL BIDIRECTIONAL DGX PASS)** based on two separately TTY-approved successful 27B→Flash-Next→27B transfers, verified served model IDs, `:8000` and committed journal; final 27B recipe `diff=[]`. The P3-G gate therefore no longer depends on controlled fault injection, automatic restoration validation or general production signoff. These requirements are **not waived**; they are **P8-only**.

## 1. Phase boundary

| Stage | Final scope | Current status | Excluded |
| --- | --- | --- | --- |
| P3-G | Real bidirectional Flash-Next↔27B switch, per-action approvals, source/target API identity and successful journal commits | **PASS / CLOSED** | Forced failure/rollback or final release |
| P4 | Optional Flash cleanup/recovery storage decision | **OPTIONAL** | No mandatory model deletion |
| P5 | Orcarouter runtime / API / benchmark | **PENDING** | No implicit G regression |
| P6 | Orcarouter↔27B successful live transfer | **PENDING** | P8 deliberate failure injection |
| P7 | Service, proxy, gateway, storage/manifest integration and numerical/CI qualification | **PENDING** | Final operations go-live authorization |
| **P8** | **Deliberate bounded fault injection + observed automated source restoration + final Wizard operational UX/security/release acceptance** | **NOT_RUN / NOT_RELEASED** | No silent approval or unattended destructive trials |

P1/P2 results and immutable historical P3-A/B/C receipts are unchanged. Active service at last actual DGX observation is canonical NVIDIA **27B**, API ID `qwen3.8-27b`, port 8000, recipe `diff=[]`, audit `VERIFIED/COMMITTED`, journal event_count=28. Latest real P3-G roundtrip acceptance source: `docs/P3-G-LIVE-BIDIRECTIONAL-SWITCH-PASS-20261107.md`.

## 2. P8 sub-stages (no execution authorized)

### P8-A — Recovery and fault matrix design (source only)

Define bounded failures against an **existing preserved target**, without corrupting model checkpoints, deleting containers, or writing into HF caches. Include start-time failure before API readiness, target API identity mismatch, target inference failure, missing target/port conflict precondition, and interruption/crash windows where retry safety is uncertain. Identify exactly which tests can safely run via Fake-DGX only and which are allowed real-DGX experiments, based on a later explicit approval.

Specify: original model identity and Docker ID, preserved alternate image, single active GPU model, port 8000 ownership, lock and append-only journal, pre-switch service snapshots, observability, hard watchdog/timeout, explicit bounded restoration path, and abort/stop criteria. Do not claim automatic recovery from power loss or Docker daemon failure without actual proof.

### P8-B — Fake-DGX recovery and journal integrity matrix

CPU-only automation must exercise stop-before-start, target start failure, failure after target start, API mismatch, failed chat probe, exception/interrupt boundaries, journal consistency, rollback success and rollback failure, duplicate SHA attempts, stale plans, non-TTY execution, missing ownership proofs and foreign GPU consumers. Require deterministic source/original model recovery on simulatable failures and correct `FAIL_RESTORED` vs `RECOVERY_FAILED` distinction. No real Docker/GPU/API mutation. All tests must PASS, and CI must be tied to a specific code HEAD.

### P8-C — One specifically approved actual DGX fault-recovery trial

**NOT APPROVED by the user's prior P3-G service downtime permission**. The operator must separately authorize the exact failure mechanism, target model, downtime, expected recovery action, rollback deadline, stop conditions and evidence capture. Do not use the ordinary P3-G two-switch success SHA or `--execute` route as a failure-injection permission.

On explicit approval only: independently verify active source (expected canonical 27B), protected operating journal, current model ID, GPU/PID + :8000 ownership; fault only an isolated bounded target-start/verify step; record injected failure; prove the actual **automatic source restoration** through Docker/runtime/API/model ID, inference/chat response, single GPU owner, :8000 listener and terminal `RESTORED`/`FAIL_RESTORED` journal + receipt consistency. An uncertain or failed restore is **FAIL**, not success. Manual recovery and renewed approval required before retry.

### P8-D — Final integrated Wizard release / operational signoff

After P5, P6, P7 and P8-C prerequisites are met, conduct final UX and operational acceptance for model install/reinstall/removal (when approved), model recipe/manifest drift handling, unique containers and backup cleanup, proxy/gateway routing and preservation, safe switch/cancel/error handling, private journal integrity, restart behavior, API/TUI/OpenWebUI service observations, source-pinned version manifests, logs, numerical and CI thresholds. Decide routine production release **separately** and explicitly; no source-only status or successful P3-G pair unlocks it.

## 3. Current Wizard P8 interface and safety

P8 has been registered as **source-only** under `./wizard.sh operations recovery-acceptance status --json` and `./wizard.sh roadmap --json`. The P8 `preflight`, `fault-matrix`, `recovery`, `audit`, `ux`, `signoff` plans are **INTERFACE_ONLY / BLOCKED**, including when supplied `--execute` and a fake SHA. No real fault injection adapter or production release function has been implemented in this step.

P7 continues to cover integration verification of service/proxy/gateway; **final operational signoff solely belongs to P8**. The original `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md` remains a historical document; the current canonical milestone register is `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`.

## 4. Acceptance evidence and dispositions

P3-G operator-forward receipt `completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json` and reverse receipt `completed-a909a1470760613b3d8e1f588dada06a41205ceac7e07c5ff464eac01884ed8b.json` remain immutable, along with the latest journal `VERIFIED/COMMITTED` and reverse 27B `diff=[]`. Paths are reported by operator; not independently read as bytes here.

**P3-G = PASS/CLOSED by operator-defined scope. P8 = NOT_RUN / NOT_RELEASED. P7 = integration only. Routine model-switch and generic lifecycle release remains gated.** No host process or container is modified by adding this roadmap and source interface.
