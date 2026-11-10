# P5-D Read-Only Process Ownership / P6-E Generic Journal V2 (2026-11-10)

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

CPU and CI outcome must be checked against the source commit before marking
pass. Do not conflate read-only inventory with independent atomic observation
of Docker ID, host PID, :8000 listener forwarding and GPU kernel context.
P5 live performance under load, V2 migration, real operator approval, durable
nonce/receipt and rollback, P7 verified proxies/gateway/storage, P8 live
fault handling and production acceptance are **not yet implemented or qualified**.
