# P3-G — First actual DGX 27B → Flash-Next ordinary operating switch PASS (2026-11-07)

**Evidence source:** operator-supplied actual DGX terminal output after the separately approved maintenance/downtime scope. This records a **real one-way switch**, not a preview or CPU simulation. The operator executed the established `scripts/temporary/operational-switch-acceptance.sh` guarded TTY entry. Do not rerun or overwrite the historical P3-A/B/C stage receipts.

## 1. Independent one-switch approval and execution

| Observation | Value |
| --- | --- |
| Trial scope | `ONE_OFF_REAL_DGX_OPERATING_ACCEPTANCE` |
| Preflight | `READY_FOR_SEPARATE_TRIAL_APPROVAL`, no issues |
| Source / target | `27b` → `flash-next` |
| API port | `8000` |
| Trial execution SHA | `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654` |
| Plan expiry | Unix epoch `1794057600` |
| Human approval | All four TTY inputs were supplied: `I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL`, exact fresh SHA, `I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME`, `I_APPROVE_FLASH_NEXT_AS_ACTIVE_MODEL` |
| Actual executor | `Live transition result: PASS` |
| Executor's observed active model | `flash-next` |
| Private completed receipt (reported path, not independently opened by GitHub) | `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json` |

No second transfer was requested or automatically triggered by this acceptance invocation. The SHA is historical evidence only; **never reuse it for a reverse plan**.

## 2. Operator's real DGX postchecks

`./wizard.sh service manager status --json` returned:

- `status: LIVE_SERVICE_VERIFIED`; `observed_model: flash-next`, `expected_served_id: qwen3.8-flash-next`, `observed_model_ids: ["qwen3.8-flash-next"]`, `api_health_status: API_IDENTITY_CONFIRMED`.
- Active container `qwen38-flash`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, status `Up 6 minutes`, published `0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp`.
- All eight service status checks were `true`: manifest/container alignment; port 8000 publishing; HTTP health; API model identity; listener present; expected served ID defined; manifest/live observation valid; one managed model running. `issues=[]`.
- `manifest_status: OBSERVED_UNQUALIFIED` is not canonical Flash reinstall recipe qualification.
- `gpu_exclusivity_verified:false`, `port_process_ownership_verified:false` and `previous_trial_provenance_verified:false` are **scope limits of this status command**, not affirmative negative measurements; real GPU/PID provenance is not separately retested post-switch by these outputs.
- `operations_enabled:false` remains; no ordinary production model-switch release.

`python3 -m scripts.manager.operational_audit --json` returned `status: VERIFIED`, `phase: COMMITTED`, `event_count:21`, `issues:[]`, `last_event_hash:4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`.

**Conclusion:** **P3-G direction 1, real 27B→Flash-Next: PASS**, corroborated by live Flash API identity and verified committed journal. This is **not** P3-G final acceptance, not full Flash recipe qualification, not an independently verified GPU-process audit after switch, not a forced failure/rollback test.

## 3. Current state and separately approved next action

**Last observed live active model: Flash-Next**; 27B is expected to be preserved and stopped by the guarded executor, but the user-facing service status only listed the active container. Verify the current actual Docker/source state in a fresh read-only reverse preflight before any reverse action. No automatic switch-back on forward PASS.

**Next stage: a separate real `flash-next` → `27b` trial, with new approval SHA and human TTY consent.**

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff

./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json

# Read-only: must say source=flash-next, target=27b, issues=[]
bash scripts/temporary/operational-switch-acceptance.sh \
  --target 27b --plan --json
```

Proceed only if status is `READY_FOR_SEPARATE_TRIAL_APPROVAL` and source/target/port/identity are correct. In a **real operator TTY**, issue one new scoped approval:

```bash
bash scripts/temporary/operational-switch-acceptance.sh \
  --target 27b --execute
```

The existing executable asks **four** inputs: `I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL`, the **fresh 64-hex execution SHA printed by this invocation**, `I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME`, and `I_APPROVE_27B_AS_ACTIVE_MODEL`. Do not pipe approvals or reuse the earlier SHA. This **interrupts Flash's port 8000 service**, attempts to activate preserved canonical 27B, and performs bounded API/chat/journal checks. Auto-recovery on failure is best-effort; unhandled host/Docker/disk failures may require manual recovery.

After the new execution, collect **the full displayed result**, receipt path, `./wizard.sh service manager status --json`, and `python3 -m scripts.manager.operational_audit --json`. If any status is `BLOCKED`, `FAIL_RESTORED`, `RECOVERY_FAILED`, `COMMITTED_EVIDENCE_INCOMPLETE`, journal invalid or API identity uncertain, **STOP—do not blindly retry, remove/recreate containers or execute an automatic roundtrip**.

## 4. P3-G acceptance accounting

| Gate | Evidence as of this report |
| --- | --- |
| Read-only D GPU/port process proof before first switch | `READ_ONLY_PASS` (prior operator explicit `--sudo-ss`) |
| E observed Flash FP8-hybrid and source draft | Documented fields match, **canonical install/reinstall NOT QUALIFIED** |
| F CPU/Fake-DGX | DGX local `144/144 PASS` before this one-off trial |
| G real 27B→Flash-Next | **PASS** |
| G real Flash-Next→27B | **NOT_RUN**, fresh approval necessary |
| G deliberate safe failure and successful rollback | **NOT_RUN**, separate test/permission |
| General Wizard production release | **NOT_RELEASED** |
| P3-A/B/C prior real one-off historic evidence | **PASS/CLOSED**, immutable |

The user authorized service downtime for P3-G acceptance, **not deletion, reinstall, forced fault injection, automatic dispatch, or GitHub PR merge**. Active Flash remains the last confirmed model pending reverse evidence.
