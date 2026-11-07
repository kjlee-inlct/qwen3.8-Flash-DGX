## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

**Execution update:** Initial no-execution state at the bottom of this historical authorization runbook has been superseded by the **actual forward PASS** documented above. Current next action is the **reverse** target `27b` with new plan and approvals; do not rerun `--target flash-next --execute` just to replay completed trial. The existing runbook's forward step remains historical context.

---

# P3-G — Operator-approved real DGX switch acceptance (2026-11-07)

**Authorization recorded:** In the ongoing conversation, after sharing a real `P3_D_G_DRAFT_ACCEPTANCE` JSON with no blocked stages and `P3_DG_EXIT=0`, the operator explicitly stated **“P3-G 허용”** and **“문서 업데이트 + 서비스 중단 허용.”** This authorizes the **scope of the P3-G one-off real switch acceptance and associated active API downtime**. The statement is **not** an exact live execution token, plan SHA, login credential, unattended automation instruction, deletion/reinstall approval, or production release. Each switch still requires the existing standalone **interactive TTY four-approval handshake**.

**Current source branch:** `feature/recipe-wizard-handoff`; PR #1 stays Draft/open/unmerged. **Actual service mutation from this chat was NOT dispatched**; only the operator can run a live test on the DGX terminal. No replay of historical P3-A/B/C, no shell pipeline of approval strings, no background execution.

## Verified actual DGX entry criteria (operator-provided)

| Gate | Observed status | Evidence scope |
| --- | --- | --- |
| P3-D | `READ_ONLY_PASS` | Privileged `ss` after the operator's explicit `sudo -v`; host IPv4/IPv6 :8000 proxy PIDs 2051487/2051502 mapped to live canonical 27B container; NVIDIA GPU compute PID 2051842; one GPU model |
| P3-E | `DRAFT_REVIEW_REQUIRED` | Preserved Flash FP8-hybrid snapshot source verified, source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED`, `issues=[]`. Canonical Flash *reinstall* recipe remains unqualified and unregistered; **not required** to start the *historically accepted preserved* Flash Docker container |
| P3-F | `SOURCE_CPU_PASS_NOT_RELEASED` | DGX-local 144/144 CPU/Fake-DGX tests passed; **no live rollback qualification** |
| P3-G | `PREVIEW_PASS_REAL_SWITCH_NOT_RUN` | Current Docker IDs and source canonical 27B/target P3 historical Flash provenance, journal VERIFIED/COMMITTED, `issues=[]`. Actual transfer NOT RUN |
| Aggregate | `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`, `blocked_stages=[]` | `P3_DG_EXIT=0`; **read-only checks only**, not permission to bypass the live acceptance handshake |

The Flash source draft SHA was `2511a952eb6b2f5bfd4355b3d2f5469c3e624284c05e113aca63bee792f3e2a1` in the real operator DGX report. **Do not** register the Flash draft as an executable lifecycle recipe or recreate its Docker container for this P3-G test.

## Authorized test scope and exclusions

- **Included:** First one-off `27b -> flash-next` transfer using *existing preserved Docker containers*, active API :8000 interruption, image/model identity and inference proof, exclusive GPU/service check, durable operating journal/receipt, and **separately manually approved** reverse `flash-next -> 27b` test. The forward test and reverse test have **distinct new plans and approvals**.
- **Excluded:** automatic two-step roundtrip from one approval, P3-A/B/C replay, recreation or deletion of either container, image cleanup, changes to HF cache, forced fault injection, production switch release, GitHub PR merge, app configuration/proxy/gateway changes, unattended retry. A dedicated controlled fault/rollback trial remains an outstanding separate P3-G acceptance item even after two PASS transfers.
- **Service-risk acknowledgement:** During the switch, Open WebUI and API clients may lose requests; 27B is stopped before starting Flash. Failure restoration is **best effort**, not guaranteed across machine faults, Docker daemon failure, power loss or inconsistent disk/journal state.
- **Durable evidence rule:** Source documentation is NOT proof of execution. Only exact *new* local receipts, API output, journal audit, service status and individual observed results can advance G acceptance.

## Safe preflight (no model change)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
bash scripts/temporary/operational-switch-acceptance.sh \
  --target flash-next --plan --json
```

**Do not proceed to execute** unless the last command returns `READY_FOR_SEPARATE_TRIAL_APPROVAL`, source `27b`, target `flash-next`, no `issues`, expected port 8000 and both preserved containers still present/current. Fresh plan lifetime is short; the `--execute` command calculates a NEW independent execution SHA and prints it. Never copy a read-only ordinary switch `plan_id` in place of the **separate execution approval SHA**.

## Real P3-G step 1 — operator-controlled 27B -> Flash-Next

```bash
# MUST run directly in a real terminal (TTY), not with --json or input pipes:
bash scripts/temporary/operational-switch-acceptance.sh \
  --target flash-next --execute
```

The existing acceptance Wizard displays the **exact plan SHA generated for this run** and prompts for **FOUR** inputs, in order:

1. `I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL`
2. The **fresh displayed 64-character execution plan SHA** (no stale copied SHA)
3. `I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME`
4. `I_APPROVE_FLASH_NEXT_AS_ACTIVE_MODEL`

Typing Enter, a mismatched value, an expired/changed SHA, non-TTY execution or a changed current Docker/service state **cancels or blocks** dispatch. These are deliberate additional live safeguards; conversation permission never bypasses them. This step **does not** auto-return to 27B on success.

## Step-1 postchecks — before allowing another live transfer

```bash
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
bash scripts/temporary/operational-switch-acceptance.sh \
  --target 27b --plan --json
```

Verify all of: live API identity `qwen3.8-flash-next`; container `qwen38-flash` running and `qwen38-27b` stopped; one GPU-model container / :8000 owner; **first acceptance result `PASS` with `executed=true` and `live_verified=true`**, private `completed-<new_sha>.json` receipt and journal `VERIFIED/COMMITTED`; new reverse plan `READY_FOR_SEPARATE_TRIAL_APPROVAL` with source `flash-next` and target `27b`. `operational_executor` already includes a bounded target API wait, local API ID check and chat inference probe; do not infer full multimodal/tool-quality/benchmark qualification from this smoke alone.

If result is `BLOCKED`, `FAIL_RESTORED`, `RECOVERY_FAILED`, `COMMITTED_EVIDENCE_INCOMPLETE`, journal mismatch, or live identity inconsistent: **STOP; do not run the reverse command or blindly retry.** Existing executor attempts bounded rollback, but review the actual current state first.

## Real P3-G step 2 — fresh independently approved Flash-Next -> 27B

Only after successful step-1 evidence and a fresh `READY_FOR_SEPARATE_TRIAL_APPROVAL` reverse plan:

```bash
bash scripts/temporary/operational-switch-acceptance.sh \
  --target 27b --execute
```

Four new interactive inputs (same first three, **NEW SHA** and different fourth):

1. `I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL`
2. The new SHA displayed by the second execution
3. `I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME`
4. `I_APPROVE_27B_AS_ACTIVE_MODEL`

Then run:

```bash
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
./wizard.sh model 27b recipe-diff --cache-source /home/inlc/.cache/huggingface --json
```

Expected final stable model = canonical `27b`, model ID `qwen3.8-27b` on :8000, `diff=[]`, one model active, last journal `VERIFIED/COMMITTED`, both separate real receipts present. No delete/recreate/bench or production release in this two-switch test.

## Acceptance and next actions

- **Step 1 PASS alone** proves only one direction. **Step 1 + Step 2 PASS** proves two approved actual transfers with local API/chat/journal postchecks, not forced failure/restore. Stop between them for evidence review.
- Forced safe failure simulation, recovery receipt integrity and Wizard UX proof are **separate P3-G criteria** and must not be fabricated as complete. Production routine switching remains locked pending reviewed release decision.
- Document every result in `handoff/CURRENT-STATE.md`, `EVIDENCE-LEDGER.md` and `NEXT-ACTIONS.md` with exact actual receipt paths and result status. **Never claim a live switch occurred on the basis of this authorization document alone.**

## Current execution state (at document creation)

`P3-G_REAL_SWITCH_27B_TO_FLASH=NOT_RUN`; `P3-G_REAL_SWITCH_FLASH_TO_27B=NOT_RUN`; `P3-G_FORCED_FAILURE_RECOVERY=NOT_RUN`; `PRODUCTION_RELEASED=false`. The user has authorized *downtime scope*, NOT supplied the four exact TTY approvals of either real operation.
