> **2026-11-07 LIVE ATTEMPT UPDATE:** Operator executed wrapper `--plan`: `READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL/issues=[]`, current Flash-Next, original 27B preserved, POST-B P1 evidence PASS; operator report `reports/transitions/flash-next--to--27b/p3-c-operator-20261107T004635Z-d9b59611f918.json`. Then `--execute` began prompting, but the first typed SHA included the prompt's leading `[`: `[56a30be...`. Exact comparison failed and emitted `CANCELLED`, `approval_accepted=false/executed=false/execution_dispatched=false`, report `p3-c-operator-20261107T004649Z-8bcc2d8a64fc.json`. No Docker stop/start or Stage-C service transition. **Important UX:** type ONLY the 64 lowercase hexadecimal characters, WITHOUT either displayed bracket. Old SHA and expiry cannot be reused. User additionally requested storing public benchmark metrics in Git: sanitized snapshots under `benchmarks/published/`; this does not authorize C or change original P1/P2/P3 runtime evidence.

---

# NVIDIA Flash-Next → NVIDIA 27B: final Stage-C operator runbook

**Date:** 2026-11-07 (KST)  
**Source branch:** \`feature/recipe-wizard-handoff\` / Draft PR #1  
**Entrypoint:** \`bash scripts/temporary/p3-stage-c-operator.sh\`

## Actual source evidence and scope

The operator's DGX read-only stage-C output from 2026-11-07 shows:

- \`status=READY_TO_REQUEST_TRANSITION_APPROVAL\`, \`issues=[]\`, \`executed=false\`, \`approval_accepted=false\`.
- Active current source \`flash-next\` / served \`qwen3.8-flash-next\` on port 8000, original Flash container \`90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5\`.
- Preserved 27B target container \`6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d\`.
- Both original stage-A/B success receipts preserved in \`~/.local/state/blazux-wizard/p3/\`.
- \`p1_evidence.status=PASS\` with distinct immutable post-B Verify, Benchmark and diagnostics SHA256 digests; preserved P2 benchmark receipt hash verified.
- Image digest \`sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137\` is **identical** for both existing Docker containers, not evidence that they serve the same model.
- Old Stage-C \`plan_id=d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7\` is historical, **expires after its original short window**. Never paste or reuse it.
- Operator ran \`evidence migrate --guided\` but typed \`COPY\`, so the migration returned \`status=CANCELLED/copied=0\`. The copy-only evidence import is optional and unrelated to C's approval. Do not re-run import to enable C.

**Actual P3-C transition has NOT run.** This source modification and CPU CI are not any additional DGX trial, port transition, or user authorization. Do not merge the PR or modify the live Flash service from source work.

## Final C script and approval boundaries

\`scripts/temporary/p3_stage_c_operator.py\` + \`scripts/temporary/p3-stage-c-operator.sh\` provide a tracked, temporary, human-oriented controller of the **existing canonical** \`./wizard.sh switch flash-next-27b stage-c\` interface. It never substitutes its own Docker transition engine. Default \`--plan\`:

- Reads original immutable private \`stage-a.json\` and \`stage-b.json\` from the legacy state directory (0600). Checks stage/provenance IDs, images, P2 hash, timestamps and live current Flash service.
- Calls only \`./wizard.sh service manager status --json\` and \`./wizard.sh switch flash-next-27b stage-c --plan --json\`.
- Requires exact canonical READY/empty issues, correct current/preserved container identities, P1 post-B Verify, measured Benchmark, diagnostics hashes, and current future-expiring SHA.
- Records an *operator summary* under ignored project \`reports/transitions/flash-next--to--27b/p3-c-operator-<UTC>-<nonce>.json\` with private 0700 dirs, exclusive 0600 file creation. This report is NOT the canonical immutable stage receipt or service journal.
- **Never stops/starts Docker, infers consent, runs GPU Verify/Benchmark or advances stages by default.**

\`--execute\` is reserved for the operator's **new explicit downtime approval**. It requires a real TTY, >2 minutes left on the fresh C SHA before prompting, and three independently typed inputs:

1. New **current** 64-character Stage-C \`plan_id\` printed literally as \`Type exactly [<CURRENT_SHA>]\`.
2. \`I_ACCEPT_FLASH_NEXT_DOWNTIME\` — explicit stop of the live original Flash-Next on port 8000.
3. \`I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C\` — independent final target acknowledgement, no automatic switch back.

An Enter alone, the word \`COPY\`, P3-A/B acknowledgement, wrong string, stale ID or TTY absence cancels or blocks. The wrapper re-fetches live status and stage-C plan after manual inputs and insists the **typed** plan still matches. Only then it invokes the canonical Wizard via:

\`\`\`text
./wizard.sh switch flash-next-27b stage-c --execute --approve-plan <FRESH_64_SHA> --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME --json
\`\`\`

Note: the **third human input is wrapper-only** and intentionally is **not** sent as \`--enter-p3\`; canonical C requires that field to be null. Canonical Wizard itself rechecks the plan under its P3 transition lock and retains the original service recovery/journal logic.

## Operator commands, in order

On the actual DGX only **after the new source CPU CI PASS**:

\`\`\`bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p3-stage-c-operator.sh --plan
\`\`\`

Expected in a safe, unmodified Flash source state:

\`\`\`text
status: READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL
issues: []
executed: false
execution_dispatched: false
approval_accepted: false
plan_id: <NEW CURRENT 64-character SHA>
expires_at_kst: <current short-lived time>
\`\`\`

If \`BLOCKED\`, stop. Inspect \`issues\` and the appended private \`evidence_file\`. Do not force, auto-retry or run A/B again. A status of READY only permits **asking for a new, separate service downtime approval**.

For the **actual final switch**, only after that new explicit operator decision to interrupt Flash-Next:

\`\`\`bash
bash scripts/temporary/p3-stage-c-operator.sh --execute
\`\`\`

The script prints all three exact strings, including an entirely new current SHA, and performs the switch only after matching every manual input and one more fresh plan check.

### Success

Expected only after genuine live validation:

\`\`\`text
status: P3_C_PASS_FINAL_27B_ACTIVE
executed: true
approval_accepted: true
execution_dispatched: true
post_switch_observed_model: 27b
wizard_result: {status: PASS, stage: c, executed: true, active_model: 27b, live_verified: true}
\`\`\`

\`~/.local/state/blazux-wizard/p3/stage-c.json\` is the authoritative **canonical immutable stage-C receipt**; the project-local operator report is supplemental. The wrapper independently rechecks live \`:8000/v1\` identity, original target image and original stage-C receipt fields. A successful C intentionally leaves NVIDIA 27B ACTIVE on port 8000. The Flash-Next original container/image/HF cache remain preserved for an independently approved return if needed.

### Blocked, interrupted, or recovery failure

A stale or rotated plan must block **before** Docker mutation. Any post-dispatch uncertainty, missing final API identity, lost immutable receipt, host crash, Docker daemon outage or interrupted operation returns \`OPERATOR_REVIEW_REQUIRED\` or another explicit failure, never a fabricated success.

Do **not** invoke \`--execute\` again, remove any container/lock/attempt marker or start Flash independently without reviewing the canonical journal, current live service status, immutable receipt and rollback state. The canonical Wizard's rollback is best effort, not a guarantee against host/daemon failure. No automatic rollback after a successfully committed final stage C.

## Preservation and CPU verification

- The Stage-C operator script does NOT move or edit original P2/P3 state, lock, journal, stage-A/B receipts or prior evidence. It does NOT execute optional evidence-import or repeat P1 benchmark.
- New wrapper reports are model-direction-specific, append-only, under the Git-ignored repository \`reports/\` tree. The prior \`~/blazux-p3-reports/\` and \`~/.local/state/blazux-wizard/p3/\` are retained.
- \`tests/test_p3_stage_c_operator_cpu.py\` uses fake DGX responses. It covers actual-shaped A/B lineage and P1 evidence gates, live Flash and preserved 27B identity, exact typed strings and Enter cancel, TTY/downtime gate, changed/expired plan ID, fake actual stage-C success and final live proof, canonical receipt mismatch, stale core approval, recovery uncertainty, and 0600 private report/symlink protections.
- The source flow does not exercise CUDA/Docker at development time. After GitHub CI PASS, the operator tests in real DGX using the commands above and shares the report.
