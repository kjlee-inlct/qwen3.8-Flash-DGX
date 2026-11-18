# P3–P5 one-turn scoped closeout and remaining operational acceptance (2026-11-18)

## Verdict

**P3-A/B/C/G are already real-DGX historical PASS/CLOSED; P3-D read-only PASS; P3-E/F are completed only within source/host-read-only and CPU handoff.** P3-E canonical Flash reinstallation and new generalized transition release are not qualified and remain assigned to the separately gated P8 production lifecycle. Do not rerun previously successful operating transitions to manufacture a fresh P3 PASS.

**P4-A and P4-B/C are already real-DGX read-only PASS/CLOSED** with nine reviewed resource records, zero deletion candidates and zero approvals. Live deletion is **NOT_RUN / NOT_AUTHORIZED**, not a remaining mandatory action when storage is sufficient. Never infer reclaimable bytes from Docker category estimates.

**P5 Orcarouter v3 BF16PLE MTP0 real inference/API was observed as a DEVELOPMENT_TRIAL.** P5-C sequential correlation was collected. P5-D actual DGX observation on 2026-11-12 returned `BLOCKED_PARTIAL_PROCESS_EVIDENCE` because an independent host port-8000 listener PID was not available under Docker/NAT; Docker/GPU PID subsets were consistent. This **is not evidence of a failed service**. Fully qualified loaded TTFT/TTFC/TPS, calibrated context lengths, resource interval, file-specific PLE RSS, independent GPU/port ownership, MTP2 overlay and general production promotion are **NOT ACCEPTED**.

The selected P6-E-related CPU **45/45 PASS** was provided by the operator at source SHA `2f5240d` and does not cover newer P3–P5 closeout source, the full repository test suite or current-head Actions. GitHub Actions has no new runs after 2026-11-11; CI is `UNVERIFIED`. PR #1 stays Draft/Open/unmerged.

## New reusable source-safe collector

- `scripts/manager/p3_p5_closeout.py` only orchestrates established P3/P4/P5 read-only/CPU modules. It has **no** mode to enable inference, switch models, load GPU weights, delete cache, modify Docker, migrate operating Journal or trigger recovery.
- `--plan`: returns a non-authorizing plan without subprocess calls or filesystem writes.
- `--cpu-only`: P3-D/G source CPU runner, P4-A/P4-B+C regression files, P5 source CPU runner, and P5 measurements/session contract CPU regression files. Insists on actual test summary/zero return code; it cannot assert DGX or CI PASS.
- `--read-only`: P3-D/E/F/G read-only inspection, P4-A/B/C read-only inventory/rehearsal, P5 source plan, P5 model measurement inventory, and P5 bounded benchmark **plan**. P5 source plan intentionally returns status `BLOCKED`/code 3 because GPU trial authorization remains withheld; this is collected as an expected non-authorizing result, not falsely promoted to PASS.
- Optional `--read-only --with-p5-asset-hashes` invokes the existing heavier P5 read-only cache and donor shard audit. **Warning: this can read large checkpoint shards**, so schedule it as an explicit I/O operation, not as the default.
- `tests/test_p3_p5_closeout_cpu.py` adds nine mock CPU tests for plan-only, fake regression results, failure/dirty-tree denial, commands allowlist, invalid JSON and rejection of live flags. The workflow's Push/PR path filters and CPU job were updated. **These nine new tests and full CI remain unexecuted / unverified until a valid run receipt exists.**

### Operator execution on the existing development checkout (no live inference or service mutation)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only
git rev-parse HEAD
python3 -B -m scripts.manager.p3_p5_closeout --plan --json
python3 -B -m scripts.manager.p3_p5_closeout --cpu-only --json
echo "P3_P5_CPU_RC=$?"
python3 -B -m scripts.manager.p3_p5_closeout --read-only --json
echo "P3_P5_READONLY_RC=$?"
```

Review the JSON `tasks`, `source_head`, `clean_before_run` and `status`; an overall `READ_ONLY_COLLECTED_NOT_RELEASED` confirms **collection**, never end-to-end acceptance. No automatic report file is written; redirect outputs locally only if the operator chooses and redact sensitive metadata before sharing. `--cpu-only` may take multiple minutes because it executes the existing P3/P5 suites; `--read-only` also repeats the P3 CPU runner. Use `--plan` first when resources are uncertain.

### P5 loaded workload — separate operator action and consent

```bash
./wizard.sh service manager status --json
./wizard.sh operations measurements inventory --model orcarouter --json
./wizard.sh operations measurements benchmark-plan --model orcarouter --contexts-k 1,4,8 --max-output-tokens 128 --json
```

The above is read-only / planning. **Only after the operator separately approves bounded inference and confirms Orcarouter v3 is already the active model**, the existing opt-in command may collect (but never automatically qualify) loaded SSE metrics:

```bash
./wizard.sh operations measurements benchmark-execute --model orcarouter --contexts-k 1,4,8 --max-output-tokens 128 --ack-live-inference I_ACCEPT_ACTIVE_MODEL_INFERENCE --save --json
```

The benchmark executor never starts or switches a model; it requires exact live API ID and full Docker container identity. It may skip cases above the observed active model context limit and does not itself provide independently authenticated P5-D ownership or a synchronized P5-B resource session. Approval for inference is **not** approval for stop/switch, downtime, Journal migration, recovery, deletion or production release. PLE RSS needs file-specific measurements rather than engine log inferred KV capacity.

## Acceptance boundary and next action

| Area | Historical evidence | Accepted here | Still blocked |
| --- | --- | --- | --- |
| P3 | A/B/C/G real one-off PASS, D read-only PASS, E metadata / F 168 CPU | Historical scope preserved; P3 source-only closeout tooling | Canonical Flash reinstall, new generalized executor, full Wizard release; defer to P8 |
| P4 | A host inventory + B/C one-shot dry-run PASS | Read-only storage scope **CLOSED** | Deletion only if capacity mandates it and exact resource separately approved |
| P5 | Orcarouter v3 MTP0 inference; C correlation; D partial PID | Source-only prep and operator read-only/CPU collector | Loaded model session, true GPU/port ownership, PLE RSS, Tools/Vision, MTP2, promotion |
| CI | Last workflow success 2026-11-11 | New test registered in YAML | New source-head Actions job/result not generated |

P5 cannot be called `REAL_ACCEPTANCE_PASS` based on this source-only change. P6-E independent authority, P7 cross-component checks and P8 recovery/release continue blocked as documented. P1/2 accepted backend baseline, vLLM 0.32.0, ONE_ACTIVE_MODEL_ONLY, port 8000, OpenWebUI/Portainer and every existing cache/image/PLE asset are preserved.

**Decision:** `P3_HISTORICAL_SWITCH_CLOSED_P8_REINSTALL_PENDING / P4_READ_ONLY_CLOSED_NO_DELETE / P5_DEVELOPMENT_TRIAL_LOADED_PENDING / NEW_SOURCE_CPU_PENDING / CI_UNVERIFIED / PRODUCTION_BLOCKED`.
