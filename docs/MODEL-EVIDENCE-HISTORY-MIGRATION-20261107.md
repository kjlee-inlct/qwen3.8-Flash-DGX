# Model-centric Wizard history and safe evidence consolidation (2026-11-07)

## Scope and operator UX

**This implementation does not start/stop any model.** Current verified DGX service stays NVIDIA Flash-Next on :8000/v1 with vLLM 0.32 and ONE_ACTIVE_MODEL_ONLY. Nothing in source CI grants stage C downtime approval.

The model identity, name and served ID come from \`runtimes/service-policy.json\`; P1/P2/P3 are compatibility/source rollout aliases and are not used as user-facing model history headings. The read-only Wizard history requires no separate API health check, Docker call or inference request:

\`\`\`text
./wizard.sh
  1. Select / run model
  1. NVIDIA Flash-Next   (or 2. NVIDIA 27B)
  4. Past Verify / Benchmark / transitions (read only)
     1 All, 2 Verify, 3 Benchmark, 4 transitions,
     5 trials, 6 diagnostics, 0 back
\`\`\`

Machine-readable read-only examples:

\`\`\`bash
./wizard.sh evidence list --model flash-next --kind verify
./wizard.sh evidence list --model flash-next --kind benchmark
./wizard.sh evidence list --model 27b --kind benchmark
./wizard.sh evidence list --model 27b --kind transition
./wizard.sh evidence list --model flash-next --kind all --limit 20
\`\`\`

The catalog reads legacy and new report folders, returns most recent bounded records, deduplicates **exact identical bytes by SHA-256**, reports unreadable/untrusted files as issues and never writes to them. Date comes from record UTC completion or source filename's UTC when available, not the time of importing the copy.

For Flash-Next, show baseline/extended Verify status and functional probes, and TTFT, latency and mean completion tokens/sec for benchmark. For NVIDIA 27B, the old bounded GPU benchmark reports **mean end-to-end throughput** separately from its **decode proxy**; neither is incorrectly relabeled as the Flash benchmark's measurement. Both from/to models can find their transition history. The historically misnamed \`p3-a-operator-20261106T223124Z-14861d75.json\` contains a P3-B receipt and is classified by its **stage field**, not its filename. No old record is rewritten.

## Multi-phase evidence paths

| Phase | Current state / design | Safety rule |
| --- | --- | --- |
| 0: legacy read compatibility | \`~/.local/state/blazux-wizard/p1/p2/p3\`, \`~/blazux-p3-reports\` | Leave original records unchanged, preserve operational P2/P3 state and journals |
| 1: model history | \`reports/models/<served_id>/\`, \`reports/transitions/<from>--to--<to>/\`, \`reports/diagnostics/<served_id>/\` plus old paths | Read-only catalog, hash deduplication |
| 1: operator-authorized copy | Copy immutable JSON to \`reports/\`; never move or delete originals | Exact copy-plan SHA, fresh recheck, new O_EXCL 0600 files and private 0700 directories |
| 2: future P2/P3 writers | After separate real DGX validation, write new **report** mirror/snapshot at commit while canonical state remains legacy | No silent modifications to safety-critical code during phase 1 |
| 3: possible full state relocation | Future explicitly proposed migration of trial locks, P3 attempt markers, stage receipts, journal and recovery readers | Requires separate design, crash/recovery/rollback tests; NOT INCLUDED |

Project \`/reports/\` is ignored by Git. It is **not** a remote backup: take a separate secure backup if needed. The copy tool does not import \`.lock\`, \`*.target.log\`, \`service-state.json\`, \`service-events.jsonl\`, or \`attempt-*.json\`. These original files still bind service recovery, replay protection and identity.

Operator copy-only workflow:

\`\`\`bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh evidence migrate --plan
# Review status=READY_TO_REQUEST_COPY_APPROVAL, issues=[], copy_count and destination list.
./wizard.sh evidence migrate --guided
# Type exactly [CURRENT_64_HEX_PLAN_ID] to COPY, or just Enter to cancel.
\`\`\`

Or from the interactive Wizard: \`3 Advanced → 8 Copy historical reports into project → y → Type exactly [current SHA]\`.

Migration treats source files as private JSON objects (<=1MiB, no group/world access or symlinks), calculates their SHA256 and copies bytes unchanged. Reuses the same content digest and original filename in the new filename. If a source changes between plan and execution, the entire stale plan is rejected before copy. If a source changes during the copy loop, the tool stops with \`PARTIAL_REVIEW_REQUIRED\`, never overwrites originals or prior target files. Retry only after reviewing a **new** plan. A copy that already exists with matching bytes is reported as \`ALREADY_COPIED\`. The P3 stage-C gate continues to read original canonical A/B receipts and diagnostics, plus legacy and project-local Flash Verify/Benchmark; do not change its gate inputs based on a copied display record.

## Current actual DGX qualification and stage C

User-provided original DGX ZIP confirms P3-A/B actual PASS and post-B Flash Verify + Benchmark actual PASS with distinct manually entered SHA approvals. The measured Flash 3-request mean was **37.9527 tok/s**, TTFT p50 **1.384594s**, latency p50 **1.724560s**; diagnostics identified the original own-container name/port conflict behind raw rc3 rather than a foreign service. Latest active model in supplied output was **flash-next**. These observations are NOT a new live state check, and source/CI changes are not a fresh GPU qualification.

**P3-C can be the very next independently approved live transition.** It does **not** require an unconditional repeat of P1 GPU benchmark, nor completion of the broader P2/P3 state relocation (phase 3). After source CPU CI and user fast-forward pull, operator runs exactly this read-only preflight:

\`\`\`bash
./wizard.sh switch flash-next-27b stage-c --plan --json
\`\`\`

Require \`status=READY_TO_REQUEST_TRANSITION_APPROVAL\`, \`issues=[]\`, \`p1_evidence.status=PASS\`, a non-null **fresh** \`plan_id\`, correct current Flash-Next source and preserved original 27B target image/container IDs, verified :8000 API identity and still-pinned P2 trial receipt. \`BLOCKED\` means STOP and report the issues, not force, retry stage A/B, start 27B independently or delete model files. This plan is **not authorization** to stop the service.

After a separate explicit operator decision to accept Flash-Next downtime, the exact stage-C plan and downtime acknowledgment must be supplied through the pre-existing guarded Wizard executor, preferably via a separately reviewed P3-C guided operator wrapper for parity with stages A/B. Never reuse A/B plan IDs or approvals. Successful C ends with 27B active on :8000 and live model identity verified; the original Flash cache/image/container must be retained for rollback. No automatic switch-back after C.

## CPU/source acceptance

\`tests/test_evidence_catalog_cpu.py\` covers mixed legacy/project history, real-shaped P1/P2 summary metrics, both transition directions in history, historical misnamed B report, exact copy-plan SHA and cancellation, deduplication, stable UTC timestamps, no lock/journal copies, permission/symlink fail closed and non-mutating Wizard routes. Tests use temporary files and fake data only; no live GPU, Docker or network inference.
