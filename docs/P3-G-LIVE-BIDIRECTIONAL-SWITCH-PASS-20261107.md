# P3-G — Actual DGX bidirectional operating-switch acceptance PASS (2026-11-07)

**Evidence source:** Two separate operator-provided DGX console transcripts. These were real one-off executions through `scripts/temporary/operational-switch-acceptance.sh` with four exact TTY approvals **per direction**, not a source/CI simulation and not the read-only P3-D–G aggregator. This report records the observed results, not independent retrieval of the private receipt files.

## 1. Real one-off switch results

| Test | 27B → Flash-Next (previous operator trial) | Flash-Next → 27B (latest operator trial) |
| --- | --- | --- |
| Preflight | `READY_FOR_SEPARATE_TRIAL_APPROVAL`; `issues=[]` | `READY_FOR_SEPARATE_TRIAL_APPROVAL`; `issues=[]` |
| Approval mode | Four separate exact TTY inputs and fresh SHA | Four separate exact TTY inputs and NEW SHA |
| Executable SHA | `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654` | `a909a1470760613b3d8e1f588dada06a41205ceac7e07c5ff464eac01884ed8b` |
| Executor result | `Live transition result: PASS` | `Live transition result: PASS` |
| Observed active model | `flash-next` | `27b` |
| Service postcheck | `LIVE_SERVICE_VERIFIED`; `qwen3.8-flash-next`; :8000 | `LIVE_SERVICE_VERIFIED`; `qwen3.8-27b`; :8000 |
| Journal postcheck | `VERIFIED/COMMITTED`, events 21, issues=[] | `VERIFIED/COMMITTED`, events 28, issues=[] |
| Private receipt path | `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json` | `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-a909a1470760613b3d8e1f588dada06a41205ceac7e07c5ff464eac01884ed8b.json` |

Reverse direction explicitly supplied the four expected inputs: `I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL`; fresh `a909a147...` SHA; `I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME`; `I_APPROVE_27B_AS_ACTIVE_MODEL`. The reverse `--plan --json` identified `source_model=flash-next`, `target_model=27b`, `served_id=qwen3.8-27b`, `api_port=8000`, `issues=[]`, `scope=ONE_OFF_REAL_DGX_OPERATING_ACCEPTANCE`.

**Observed completed operating journal for reverse:** `event_count=28`, `status=VERIFIED`, `phase=COMMITTED`, `issues=[]`, `last_event_hash=213670149ca6ef36eabda3fe2d5b6f13ac7ec5851f12b535373a84af46efc311`.

## 2. Canonical 27B final live state

Operator's real `./wizard.sh service manager status --json`:

- `active_container.name=qwen38-27b`, `active_container.status=Up 8 minutes`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`.
- Published port `0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp`; `api_health_status=API_IDENTITY_CONFIRMED`.
- `observed_model=27b`, `expected_served_id=qwen3.8-27b`, `observed_model_ids=["qwen3.8-27b"]`, `status=LIVE_SERVICE_VERIFIED`, `issues=[]`.
- All eight `checks` entries were `true`, including `single_managed_model_running=true`. This is the manifest-led managed-service check **not** a post-switch independent `nvidia-smi`+PID audit.
- `manifest_status=OBSERVED_UNQUALIFIED`; `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` are explicitly outside this status command's confirmation scope, **not detected GPU or port conflicts**.
- `operations_enabled=false`: routine production switching and generic lifecycle release remain **disabled**.

Operator's real `./wizard.sh model 27b recipe-diff --json` returned:

- `active_model=27b`, `installed=true`, `running=true`, `status=READ_ONLY_STATUS`, `diff=[]`, `issues=[]`, `decision=OBSERVE_ONLY`.
- `container_id=00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`, recipe SHA `301c9c7980690b97e357db5fb57090fc82c507ab9c1116c8e154739e360bbbbb`, pinned NVIDIA 27B revision `482ca0f3832238542f8f5295dde86b5f22711d80`.
- `advisories=["HOST_HF_CACHE_SOURCE_NOT_PINNED_IN_RECIPE"]`. This explicitly reflects that the host bind path is deployment-specific; it is **not** a runtime recipe difference or an acceptance failure. The observed host cache is `/home/inlc/.cache/huggingface`, mounted read-only at `/hf`.
- Desired/observed match for canonical 27B vLLM 0.32 runtime (8K context, BF16 compute path, `modelopt_mixed` quantization, native tool/reasoning flags), Docker GPU/IPC/cache settings and port 8000.

## 3. Acceptance classification (evidence-scoped)

| Area | Classification after latest actual DGX trial |
| --- | --- |
| Historical P3-A/B/C transfers | Prior **PASS/CLOSED**, unchanged and never replayed |
| P3-D | Prior independently proven **READ_ONLY_PASS** for GPU and :8000 ownership; no separate new post-reverse PID query |
| P3-E | Flash Hybrid candidate and documented source-draft fields matched; **canonical Flash reinstall remains DRAFT_REVIEW_REQUIRED** |
| P3-F | Earlier operator local CPU tests **144/144 PASS**; no production lifecycle release |
| **P3-G real 27B → Flash** | **PASS** |
| **P3-G real Flash → 27B** | **PASS** |
| **P3-G actual two-way transfer acceptance** | **PASS** — separate exact TTY plans, transitions, live API checks, committed journal, canonical recipe diff |
| P3-G deliberate safe target failure + automatic source restoration | **NOT_RUN** (not inferred from successful transfers) |
| P3-G operator UX / final integrated release | **PENDING** as a separate acceptance decision |
| Routine production model switching | **NOT_RELEASED**, `operations_enabled=false` |

**Final last-observed active model = canonical 27B.** Both one-off completed SHA values are historical and must not be reused for additional live operations. Failure injection, deletion/reinstall, cache/image cleanup, re-execution of P3 A/B/C and routine production release are outside this evidence and do not become authorized merely because two switches PASSed.

## 4. Next safe work

1. Preserve both actual one-off receipts and the append-only event journal; do not manually edit, truncate or replay them. New switch plans must re-observe current Docker/API and use a new SHA.
2. Source/Fake-DGX first: select a bounded **failure injection design** (e.g., target start failure with successful original-source restoration) and verify full Fake-DGX tests, journal terminal state, no blind retry, single-model constraint. This **does not count** as an actual DGX failure/restore test.
3. Run a real bounded failure/rollback acceptance **only with its own new, explicit operator approval** that states the method, downtime, rollback guards, abort criteria and evidence. The previous permission for successful transfers did not authorize purposeful failure.
4. Review Wizard UX and source/CI/release gates separately; do not set `production_released=true` from a successful pair of manual tests.
5. Optional P4 disposition, and P5/P6/P7 remain on the roadmap and are not silently completed.

**Evidence qualifier:** Private receipt paths are operator-reported. GitHub documentation can record their paths and the observed result but cannot attest to independently reading their bytes. No new code changes or CI qualification are implied by this documentation-only update.
