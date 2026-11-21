# P4-A — Actual DGX Spark read-only capacity and model-state inventory (2026-11-08)

## Evidence provenance and scope

- Source: operator-provided console output from the real DGX Spark, after clean `git status --short`, `git pull --ff-only origin feature/recipe-wizard-handoff` and `git rev-parse HEAD`.
- **Operator-observed checkout HEAD**: `a29cd6e62fed930b7f3e248e0fdf9c0c94e78f18`.
- Executed **read-only** command: `./wizard.sh storage flash-next inventory --json`.
- Actual response: `stage=P4-A`, `status=READ_ONLY_INVENTORY_COMPLETE`, `issues=[]`, `scope=DGX_READ_ONLY`, `approval_accepted=false`, `executed=false`, `operations_enabled=false`, `production_released=false`, `removal_plan_id=null`, `reclaimable_bytes_verified=false`.
- The evidence is the operator's console report, not a fresh Docker/API probe executed by GitHub CI or an independent third-party attestation. Raw mount paths/secrets and foreign container names are not in the report.

## Service / container state

| Observation | Reported value |
|---|---|
| `observed_active_model` | `27b` |
| `active_api_verified` | `true` |
| `managed_containers.27b` | present, running, image ID observed, canonical recipe registered |
| `managed_containers.flash-next` | present, **stopped**, image ID observed, canonical recipe **not registered** |
| `managed_containers.orcarouter` | container absent, canonical recipe **not registered** |
| `gpu_running_container_count` | 1 |
| `port_8000_owner_count` | 1 |
| `other_container_count` | 2 |

`LIVE_SERVICE_VERIFIED` and container ownership were determined by the Wizard's existing Docker/API probes. They do **not** independently prove kernel-level PID attribution, large model weight integrity, new Flash installation, or a full P8 rollback qualification.

## Disk measurements — same total/free reported for both cache roots

| Measurement | Bytes | Approximate decimal GB |
|---|---:|---:|
| File-system total (reported at root #1 and #2) | 982,819,848,192 | 982.82 |
| File-system free (reported at root #1 and #2) | 324,880,961,536 | 324.88 |
| File-system used (total minus free) | 657,938,886,656 | 657.94 |
| Allocated `du` — cache root #1 | 267,995,971,584 | 268.00 |
| Allocated `du` — cache root #2 | 192,507,006,976 | 192.51 |

File-system free percentage is approximately **33.056%**, used approximately **66.944%**. Both roots report **identical total/free**, suggesting a shared underlying file system, **not proven** without device/mount identity. **Never add the two `filesystem_total_bytes` or `filesystem_free_bytes` observations.** Cache-root `du` measurements are independent path observations and may not be additive if hardlinks, mount topology, shared blobs or nested roots overlap.

## Known model-repository allocated `du` bytes

| Root | Model | Present | Allocated bytes | Decimal GB |
|---|---|---|---:|---:|
| #1 | NVIDIA 27B | yes | 21,932,584,960 | 21.93 |
| #1 | NVIDIA Flash-Next | yes | 75,967,504,384 | 75.97 |
| #1 | Orcarouter | no | — | — |
| #2 | Orcarouter | yes | 177,686,446,080 | 177.69 |
| #2 | NVIDIA 27B | no | — | — |
| #2 | NVIDIA Flash-Next | no | — | — |

The difference between a root's `du` amount and its listed known-model repository amounts **does not uniquely identify unknown model data or deletion candidates**. No content hash, hardlink relation, snapshot/blob graph, derivative checkpoint provenance or actual reclaimable bytes was measured here. In particular, historical P3-E Flash FP8-hybrid **129,771,270,410 apparent bytes** counts 11 index-referenced shard sizes, **not** the same metric or necessarily the same directory as today's NVIDIA Flash repository **75,967,504,384 allocated bytes**. Neither missing weights nor a reclaim saving can be inferred from the difference.

## Docker `system df` displayed estimates

| Category | Total | Active | Docker Size | Docker Reclaimable |
|---|---:|---:|---|---|
| Images | 3 | 3 | 28.74GB | 0B (0%) |
| Containers | 4 | 3 | 416.7MB | 182.7MB (43%) |
| Local Volumes | 1 | 1 | 34.16kB | 0B (0%) |
| Build Cache | 180 | 0 | 7.364MB | 2.088MB |

All four Docker categories are present; `docker_disk_usage.status=OBSERVED_DOCKER_ESTIMATES`. The reported container/build-cache reclaimable display values total approximately 184.788 MB **as an arithmetic sum of provider estimates only**: this does **not** establish safe reclaimable bytes, target ownership, or deletion approval. Docker shared layers and dependencies are not independently audited.

## Acceptance and remaining boundary

- **P4-A actual DGX read-only collection: PASS / COMPLETE**, with no reported observation issues and no destructive action.
- No observed immediate disk-pressure condition is established by a reported **324.88 GB free** (about one-third of the reported volume). This is an assessment of the presented snapshot only, not ongoing monitoring or a guaranteed free-space threshold.
- Preserve active 27B, stopped Flash reference, Orcarouter source, other HF caches/models, Docker images, Open WebUI, Portainer and historical receipts. `preservation` flags are intent/policy, not a content-integrity assertion.
- **P4-B** shared asset/candidate assessment: **NOT_STARTED / NOT_APPROVED**. **P4-C** cleanup: **NOT_STARTED / NOT_APPROVED**. The operator has not requested any actual deletion or plan.
- **P8** canonical Flash reinstall, deliberate fault injection/automatic restoration, generic lifecycle and production release: **NOT_RUN / NOT_RELEASED**.
- **P3-A/B/C/G** previous actual transfers remain PASS/CLOSED; this P4-A run does not repeat them.
- P4-A was run with source checkout `a29cd6e`, which had GitHub source-only CI **889/889 PASS / 40 groups**. This operational output constitutes the separate real-DGX inventory evidence.

Next action: report P4-A evidence and await a separate operator decision before **any** P4-B evaluation, P4-C mutation, or P8 runtime work. No further DGX probe is required to acknowledge the P4-A read-only result supplied here.
