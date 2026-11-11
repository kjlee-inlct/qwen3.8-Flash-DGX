# P5-D Read-Only Process Ownership / P6-E Generic Journal V2 (2026-11-10)

## 2026-11-12 KST — Actual DGX P5-D ownership-capture supersession

**Evidence origin and time.** This section records the **operator-provided actual DGX terminal transcript**, not a fresh GitHub-side host probe. The related `measurements inventory` receipt was captured at
`2026-11-11T21:12:57.019880+00:00` (**2026-11-12 06:12:57 KST**) on source
`5a48e9ca417b939b1cc51b2933c3086472033b6a`; the P5-D transcript was collected in the same operator session. Transient PID values below must not be reused as live identities.

### Independent command results and precise acceptance level

| Probe | Actual observed result | Acceptance interpretation |
| --- | --- | --- |
| `./wizard.sh service manager status --json` | `LIVE_P5_TRIAL_API_VERIFIED`, `issues=[]`; :8000 published and responding; declared served ID `qwen3.8-flash-next-orca-uncensored-bf16`; all service checks true | API/service observed healthy **at sampling time**; DEVELOPMENT_TRIAL, not production release |
| P5-C `observation-capture --model orcarouter` | `SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE`, `issues=[]`, full Docker ID correlated | Consistent sequential source evidence, not independently authenticated GPU/port ownership |
| P5-D `ownership-capture --model orcarouter` | `BLOCKED_PARTIAL_PROCESS_EVIDENCE`, one issue `PORT_8000_HOST_LISTENER_PID_UNAVAILABLE_OR_NAT` | **Partial evidence**, not a demonstrated service incident |
| Docker inspect vs P5-C | `docker_identity_match=true`; same exact full ID and image | Identity matched in this set of sequential probes |
| `docker top` vs `nvidia-smi` | `gpu_pid_subset_of_container=true`, GPU compute PID set is a subset of Docker host PIDs | Process-set consistency; **not** GPU exclusivity or authenticated GPU kernel ownership |
| `ss -H -ltnp sport = :8000` | `host_port_8000_listener_pids=[]`; `host_port_pid_to_container_verified=false` | Could reflect Docker NAT / docker-proxy / insufficient host inspection permissions / observability limits. **Root cause not established** |
| Gate flags | `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `real_dgx_verified=false`, `production_released=false` | Deliberately fail-closed, no release or transition authorization |

Observed running container:
`qwen38-orcarouter-qsa62318-lmhead-v3` (role `DEVELOPMENT_TRIAL`, not canonical `qwen38-orcarouter`), Docker full ID
`9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`;
image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`.
At the captured instant: init PID `4016083`, Docker host PID set
`{4016083, 4016529, 4016530}`, GPU compute PID set `{4016530}`,
listener PID set `{}`. **These are historical, volatile process IDs.**

**Exit-code contract.** Both `OBSERVED_PID_SETS_CONSISTENT_NOT_AUTHORIZED` (PID sets consistent but not authorizing) and
`BLOCKED_PARTIAL_PROCESS_EVIDENCE` (missing independent evidence) are **observation outcomes**.
The generic Wizard may return **exit code 3** for a non-authorizing/blocked review;
the provided shell transcript did not capture `$?` separately. Never interpret a
possible 3 as proof that the running service failed. Determine service health
separately using fresh `service manager status`, API identity and actual Docker
health. Conversely, API health is not proof of port PID attribution.

### Related measurement receipt (not part of P5-D ownership acceptance)

The separately invoked read-only `operations measurements inventory --model orcarouter --save --summary-only --json` stored a private, local receipt at:

`~/.local/state/blazux-wizard/model-measurements/orcarouter--20261111T211258936797Z--edbda9c9286e.json`

Observed: `max-model-len=8192`, `max-num-seqs=1`, GPU memory utilization `0.7`, PLE mmap enabled, PLE prewarm off, 16 PLE workers, KV memory log `9.83 GiB`, reported KV pool `197352 tokens`. GPU utilization sampled at 0%, memory PSI some avg10 at 0%. **This is idle/configuration evidence**, not MTP2/long-context performance, independent GPU memory allocation or PLE residency proof. Model weight-load memory and PLE resident bytes remain `NOT_OBSERVED`; no loaded benchmark was invoked. The private receipt is not committed and should not be treated as a durable repository artifact.

### Decision / disposition

- **P5-D result:** `DGX_READ_ONLY_CAPTURE_PERFORMED / PARTIAL_PID_EVIDENCE / NOT_AUTHORIZED`. No automatic retry, service restart, Docker NAT change, host PID privilege escalation or active-model switch is justified by this result.
- **Known residual:** a host-port PID-to-container chain and independent GPU exclusivity cannot be established from these probes. Treat this as an evidence limitation, not a production outage. Further collection/measurement completeness is **deferred to P8**, not a blocker to begin P6-E source development.
- **Next order:** **P6-E** durable Nonce/Replay Fence and Journal v2 safety contract → **P5** resource/benchmark session integration → **P7** independent Proxy/Gateway/Storage verification → **P8** loaded/fault/recovery acceptance and measurement completeness.
- Real inference load, switching, fault injection, release, and automatic recovery require **separate operator approval**; none occurred in this documentation update. Retain vLLM 0.32, ONE_ACTIVE_MODEL_ONLY, port 8000, current Orcarouter v3, and Draft/Open PR #1 without merging.
- This new DGX evidence **supersedes only earlier statements that P5-D had not yet been run**; historical CPU-only implementation and CI receipts remain valid in their original time context. No GitHub-side DGX runtime verification is claimed.

---

## Scope and immutable rules

Model-agnostic source changes, **not** production release. DGX Spark GB10 ARM64,
vLLM **0.32.0** only, SGLang prohibited; ONE_ACTIVE_MODEL_ONLY; API host **:8000**.
Preserve all running/stopped containers, images, PLE/model/HF caches, OpenWebUI
and Portainer. The current Orcarouter V3 is a DEVELOPMENT_TRIAL, **not** the
canonical `qwen38-orcarouter` container. No stop/start/switch, inference load,
port takeover, resource tuning, deletion, merge, or operating Journal migration.

## Evidence from operator (before this source change)

The operator's P5-C output on DGX reported:
- Trial container `qwen38-orcarouter-qsa62318-lmhead-v3`, Docker full ID
  `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`.
- Served ID `qwen3.8-flash-next-orca-uncensored-bf16` and
  `SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE`, issues empty.
- P6-D `BLOCKED_LIVE_EXECUTOR_NOT_QUALIFIED`; expected due to intentionally
  absent independent authorization, GPU/port PID ownership and generic executor.
These are dated observations, not future-state assurances.

## P5-D CLI

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff

# Fresh READ ONLY (not an inference benchmark). Can return exit 3 on
# GB10/NAT/permission limits, in which case treat as unverified, not failure
# of a running model.
./wizard.sh operations generic ownership-capture \
  --model orcarouter --json
```

Execution uses one P5-C observation followed by exact argv commands:
`docker inspect --format '{{json .}}' <observed-name>`,
`docker top <observed-name> -eo pid`,
`ss -H -ltnp sport = :8000`,
`nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits`.
They are sequential and bounded (6 s each), and never mutate containers.
An unsupported GPU process interface or Docker NAT with no visible listener PID
produces `BLOCKED_PARTIAL_PROCESS_EVIDENCE`. Even consistent host PID subsets
return `OBSERVED_PID_SETS_CONSISTENT_NOT_AUTHORIZED` and cannot prove host
port PID-to-container mapping or GPU exclusivity.

Offline review is available via
`ownership-review --model orcarouter --ownership-evidence /absolute/file.json --json`.
Bundle fields: `observation` (prior P5-C JSON), `docker_inspect` (Docker
inspect dict), `docker_top_stdout`, `ss_stdout`, `gpu_stdout`.
The bundle is untrusted and has no approval authority.

## P6-E planned Journal v2 fields and migration behavior

A synthetic `schema_version=2` event proposal contains explicit:
- Source/target registered model keys, both 64-digit full Docker IDs, and
  canonical-role requirement (Trial never silently promoted).
- Source/target plan ID, phase, index, previous hash and optional last
  verified V1 event hash *anchor*, event hash and record origin.
- API host port 8000, maximum GPU active-model count 1, mandatory
  revalidation, independent approval authentication, durable nonce ledger.

Code: `draft_v2_event`, `audit_v2_draft` and `migration_preview` in
`scripts/manager/generic_journal_v2.py`. Schema proposal bytes are untrusted,
in-memory only; no fsync, receipt, V2 live writer, signer, cross-process lease
or executor. Hash integrity alone does not confer authenticity.

V1 status mapping:
- EMPTY with event_count=0 and no issues: `REQUIRES_APPROVED_EMPTY_V2_BOOTSTRAP`.
- VERIFIED terminal and valid last hash: `REQUIRES_APPROVED_V1_ANCHOR_AND_READ_ONLY_RECONCILIATION`.
- Dirty, missing, partial, inconsistent: `FREEZE_UNTRUSTED_OR_UNRESOLVED_V1`.
All remain `BLOCKED_V2_MIGRATION_NOT_AUTHORIZED`, exit code **3**. Orcarouter
is explicitly unsupported by current V1 journal. No auto-migration or editing
historical records is allowed.

```bash
./wizard.sh operations generic journal-v2-preview \
  --from-model orcarouter --to-model 27b --json
# Expected: BLOCKED_V2_MIGRATION_NOT_AUTHORIZED, exit 3

python3 -m unittest discover -s tests -p 'test_p5d_p6e_cpu.py' -v
```

## Acceptance and open requirements

P5-D/P6-E SOURCE CI VERIFIED: implementation commit `61effbd25a856a1736bb01098f2f87742b0248e0` (initial failed only because document inventory excluded new runbook); inventory correction commit `c697c7474550e1703f4f68daf857582e66292eec` passed **9/9 new CPU tests**, full Push [42739085075](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42739085075) and PR [42739090964](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42739090964) both **SUCCESS**. At that historical 2026-11-10 source-only milestone, DGX P5-D had **NOT** yet been run; its actual 2026-11-12 operator-captured result is documented above. P6-E migration remains source-only, not a production write.

CPU and CI outcome must be checked against the source commit before marking
pass. Do not conflate read-only inventory with independent atomic observation
of Docker ID, host PID, :8000 listener forwarding and GPU kernel context.
P5 live performance under load, V2 migration, real operator approval, durable
nonce/receipt and rollback, P7 verified proxies/gateway/storage, P8 live
fault handling and production acceptance are **not yet implemented or qualified**.

## 2026-11-10 read-only hardening supersession

P5-D now rejects externally supplied P5-C evidence when the requested model,
served API ID, canonical container, fixed port, unresolved issue list, or
runtime role/container pairing is inconsistent. These are untrusted source
checks only, never proof of Docker/port/GPU ownership.

P6-E in-memory Journal v2 auditing now fails closed for malformed JSON field
types (boolean indexes, list phases, non-string hashes) without exceptions.
Draft extension checks the prior event hash and type; a boolean V1 event count
cannot be treated as an empty journal. New CPU negative fixtures cover these
cases. No operating Journal migration, writer, execution or release enabled.

## P7 model-first TTY integration (source-only; 2026-11-10)

In `./wizard.sh` select a model, then "P5–P8 common model qualification".
Menu items 8/9 perform explicit P5-C/P5-D sequential read-only host probes
and label the resulting observation as **not live acceptance**. Items 10/11
select a target from the manifest registry and display the permanently blocked
P6-D operating-gate / P6-E Journal migration preview with explanatory issues.
They do **not** invoke a switch, approval, inference, actual Journal write,
persistent replay fence or recovery. CPU tests mock both host probes and confirm
that P6-D/P6-E menu paths never invoke external runtime commands.

## P7 registry-first selector (source-only)

The interactive model selector now reads registered model keys from the
service-policy manifest. Existing P1/P2/P5 model-specific action adapters
retain their guarded behavior and display order. Newly registered models
appear with a **source-only** label and enter only the model-independent
P5–P8 qualification menu. Unavailable/invalid registry state blocks the
selector without attempting a model launch or legacy lifecycle action.
Two CPU regression tests cover registry-only models and invalid registry.
