# P5-D — One-turn DGX read-only result and evidence-bound diagnosis (2026-11-19 KST)

## 2026-11-20 KST — new P5-D DGX read-only audit: EACCES 13 on 3/3 PIDs

**New operator-provided exact-SHA audit:** `fd338efa549a8c3bb54e65e5e033d2334d9e96e1` (documentation-only child of prior CPU-verified `7c11d0d`). Manifest validation PASS and Wizard `p5d-source-binding-review` PASS for `orcarouter-bf16-ple` (declarative BF16 / DISK_MMAP source pin). Actual `p5d_live_audit --save --json` returned `BLOCKED_PARTIAL_PROVENANCE`, `P5D_READONLY_RC=3` with `SMAPS_ACCESS_DENIED` / **`errno=13` on all three host PIDs** `4016083`, `4016529`, `4016530`. Thus 0 mapped candidates does not mean 0 RSS, PSS or PLE residency. Docker IPv4+IPv6 wildcard port declarations now classify `DOCKER_DECLARATION_CONSISTENT_NOT_HOST_VERIFIED`; actual kernel NAT owner remains unobserved. PID namespace identity unqualified (`container_netns=""`), LISTEN FD owner absent, pinned snapshot aliases unreadable, host NAT `UNAVAILABLE`. Exact outcome and safe permission preflight documented in [P5-D procfs blocker](P5-D-PROCFS-PERMISSION-BLOCKER-20261120.md).

**Decision:** P5-D source/Wizard/manifest acceptance remains CPU-supported at prior `7c11d0d` **138/138 operator PASS**, but live PLE RSS/PSS/inode/PID/NAT qualification remains BLOCKED. No repeat GPU workload, service mutation, sudo, Docker exec, live Journal write, CI dispatch, main change, PR merge or production release. A future non-elevated procfs access preflight must first refresh the PID ownership snapshot; historical PIDs can be recycled. `RC3` denotes unqualified evidence, not a running service failure. Full private receipt is not attached to this documentation update.

---



## 2026-11-19 KST — operator CPU regression 50/50 PASS at 08d03b1

**Evidence type: operator-provided terminal transcript (not independently run by GitHub connector).** On DGX host `lc-gx10-pc` under `~/Workspace/llm/blazux-orcarouter`, the operator reported `git rev-parse HEAD = 08d03b182c3a1be78a698312d1abcb5b2cef571e` and three selected CPU-only unittest completions: `test_p5d_live_audit_cpu.py` **22/22 OK (0.013s)**, `test_p5_readonly_attribution_cpu.py` **9/9 OK (0.000s)**, and `test_p5d_p6e_cpu.py` **19/19 OK (0.012s)**. **Total 50/50 selected tests PASS**, based on that exact supplied transcript. The previously expected 44 was a mistaken projection: there were 40 historical selected tests at old SHA `4366f3b`; the latest three modules report 50, an increase of 10 across that historical baseline. There is no claim of full repository test-suite execution or GitHub-run CI.

**Qualification:** The source and unit-test files on this code SHA (`scripts/manager/p5d_live_audit.py`, `tests/test_p5d_live_audit_cpu.py`) received the new fail-closed namespace/limited enumeration/errno handling patches. This observed CPU execution verifies selected synthetic regressions, **not a new live P5-D probe**. The original private read-only receipt remains `BLOCKED_PARTIAL_PROVENANCE / RC3`, with 3/3 unreadable smaps, absent namespace identities, unbound LISTEN inode↔PID FD and independently unverified NAT owner. No per-PLE unique RSS/PSS, pinned tensor identity, GPU exclusivity or production authority is established.

**Independent CI check after operator report:** for `08d03b182c3a1be78a698312d1abcb5b2cef571e`, GitHub workflow-runs API returned `[]` and combined commit statuses `[]`. Latest observed workflow run remained on historical `8b118c8` (2026-11-12 KST). **CPU_TESTED=OPERATOR_REPORTED_SELECTED_50_OF_50; CI_VERIFIED=NO; DGX_LIVE_AUDIT_NEW_HEAD=NOT_RUN; PRODUCTION_RELEASED=NO**. Source-only follow-up documentation may advance the repository HEAD beyond the tested SHA; that does not create new CPU or live-DGX evidence, and must retain this exact tested-source SHA. PR #1 stays Draft/Open/Unmerged. No new live service intervention authorized.

---


## 2026-11-19 KST — follow-up SOURCE hardening after base HEAD `141df9fdd562`

Code review found two fail-closed gaps: `pid_identity_continuous` could accidentally accept a PID identity dictionary **omitting** any namespace key (empty iterator passes `all()`), and pinned-snapshot directory entries were fully materialized before applying the 256-file cap. The revised source explicitly requires positive integer start ticks plus **all three** valid `net:[N]`/`mnt:[N]`/`pid:[N]` identifiers; snapshot entry enumeration is capped at 257 including the one overflow sentinel. It also bounds container `/proc/PID/net/tcp{,6}` reads at 5,000,001 chars and records numeric `smaps_errno` per PID in the private receipt and compact summary (without copying raw exception text).

Four new CPU-only regression methods cover omitted/empty/wrong namespace evidence, bounded scandir iteration, errno 13/2/5, and an oversized container TCP listing. The tests are **SOURCE_ADDED / NOT_EXECUTED** in this GitHub-only update: no local repository checkout or new workflow run is available for the updated HEAD. The historical **40/40** result applies only to DGX SHA `4366f3b` and must not be reused. GitHub branch had no newer workflow runs since 2026-11-12 07:00 KST, and `main` had no `.github/workflows/` directory at inspection; the root cause remains **UNVERIFIED** (default-branch registration, workflow settings, event semantics and runner state require separate checking).

**Gate:** `SOURCE_IMPLEMENTED` (once committed) / `CPU_TESTED=NOT_RUN_ON_NEW_HEAD` / `CI_VERIFIED=NO` / `DGX_OBSERVED=HISTORICAL_RECEIPT_ONLY` / `OPERATION_AUTHORIZED=NO` / `PRODUCTION_RELEASED=NO`. PLE-specific RSS/PSS, inode content authenticity, NAT kernel owner and production admission remain unqualified. `RC=3` signifies evidence gaps, not a service outage. No sudo, GPU workload, DGX probing, Docker mutation, live Journal or PR merge was performed.

---


## 2026-11-19 KST — uploaded ORIGINAL 9,661-byte P5-D private receipt reviewed (later evidence)

Operator uploaded the **actual saved** `orcarouter--20261119T004619880648Z--bd848453cb4f.json`, not only the compact terminal summary. It is an operator-supplied receipt originally captured from **DGX source SHA `4366f3b1476105c6f556e0e93c4f5e1da64f68fa`** between 2026-11-19 00:46:16.550982 and 00:46:19.879156 UTC; this upload/review is later than the original audit. No new host audit, GPU inference, model switch, service restart or privilege escalation was performed while reviewing this file.

### Evidence-by-evidence reclassification

| Field | Original JSON | Supported interpretation |
| --- | --- | --- |
| `initial_ownership.docker_host_pids` and `final_ownership.docker_host_pids` | `[4016083, 4016529, 4016530]` both; exact Docker ID stable | Same Docker ID and reported host PID set in this short sequential capture |
| `gpu_compute_pids` | `[4016530]`, subset of Docker PID set | Positive process-set correlation only; independent GPU exclusivity still false |
| `file_mappings[*].cgroup_exact_container_id_present` | `true` for all three PIDs | Concrete cgroup text contained the Docker ID as checked by old collector, but no independent kernel security attestation |
| `file_mappings[*].sampled_smaps_bytes` | **0 bytes for all three**; each `NOT_OBSERVED`, `SMAPS_UNREADABLE`, `mapped_files=[]` | **Failed to read smaps**, NOT proof that there are zero memory-mapped file pages. Old collector did not retain errno, so cannot distinguish `EACCES`/`EPERM` vs missing file or other I/O cause |
| `pinned_snapshot.filesystem_inode_aliases_observed` | 0; `PINNED_SNAPSHOT_DIRECTORY_UNREADABLE` + `PINNED_SNAPSHOT_FILES_NOT_OBSERVED` | The candidate pinned HF snapshot cannot be stat-verified; cannot prove path missing versus permission or mount alias problems; expected revision is a **declared** source value |
| `pid_identity_before/after` | start ticks: 4016083=159946344, 4016529=159948383, 4016530=159948383 before/after; **netns, mntns, pidns all empty strings for all three PIDs** | Nonempty namespace identity was **NOT verified**. The original `pid_identity_continuous=true` only checked equality of the same empty strings and is **not acceptable** as validated namespace continuity. Later source correctly requires nonempty namespace format |
| `port.container_listener.listening_inode_count` | 1; `container_netns=""`; matched Docker FD-owning PIDs=[] | The Linux `/proc/PID/net/tcp*` read exposed a :8000 LISTEN inode, but FD↔PID mapping was **NOT confirmed**. Old `PID_NETNS_DRIFT` was triggered by an empty namespace and is **not evidence of a real network namespace transition** |
| `port.publication` | `declared_host_port_8000=true`, `effective_host_port_8000=true`, `network_mode=bridge`, but `docker_port_declarations_consistent=false` | The old equality comparator labelled `DOCKER_DECLARATION_MISMATCH`; **actual raw HostConfig and NetworkSettings port binding entries are absent from receipt**, so cannot determine whether Docker appended IPv6 wildcard or there was a substantive IP/port mismatch. Later source normalizes *only* IPv4 wildcard plus IPv6 wildcard, not all mismatches |
| `port.iptables_nat` and `host_listener_pid_observed` | `status=UNAVAILABLE`, `matching_rule_found=false`, host listener PID absent | NAT tables and host listener PID **unobserved**, not proof of absent DNAT or service outage. No kernel NAT path attribution |
| `service_api_model_id_confirmed` | `true` | Existing API was responsive for expected served ID at sampling time; not a port owner or authenticated PLE-residency guarantee |
| `executed_inference`, `service_mutated`, `production_released` | `false` for all | This was read-only observation (plus separate private JSON persistence), not operating release |

**Required corrections:** `SMAPS_UNREADABLE` must be displayed as **UNKNOWN_ACCESS_CAUSE** (the old receipt does not expose errno); `pid_identity_continuous=true` cannot be accepted as a complete identity check because namespace values are blank; `PID_NETNS_DRIFT` is a misleading category in this old source when the reference netns was empty; `DOCKER_DECLARATION_MISMATCH` cannot be diagnosed as real host configuration drift without the raw Docker bindings.

**What later source changes address:** the newer (unverified-on-DGX) P5-D collector closes the `os.scandir` iterator, explicitly classifies unavailable/empty namespaces, rejects blank namespace IDs for identity continuity, records per-PID `SMAPS_ACCESS_DENIED`/not-found classification when the errno is available, and distinguishes compatible Docker dual-stack wildcard declarations. **These changes do not retroactively establish PLE RSS/PSS, pinned inode ownership, or kernel NAT port owner.**

### Acceptance after full-file inspection

`P5D_FULL_PRIVATE_RECEIPT_REVIEWED / SOURCE_SHA_BOUND_OPERATOR_EVIDENCE / DOCKER_PID_CGROUP_API_CORRELATED / PID_NAMESPACE_IDENTITY_UNVERIFIED / SMAPS_READ_ZERO_BYTES_ALL_3 / PLE_RSS_PSS_INODE_NOT_OBSERVED / NAT_OWNER_NOT_OBSERVED / PRODUCTION_BLOCKED`

**No additional GPU workload is needed.** The next possible *strictly read-only* diagnostic would require a new operator-provided output from the updated collector / accessible PID procfs, or independent privilege-aware evidence acquisition. Do not automatically rerun or invoke sudo, Docker exec, firewall changes or operation. The existing uploaded JSON has no more raw evidence for determining the exact `smaps` errno, actual Docker HostConfig/NetworkSettings entries, or owner of a socket inode. PR #1 remains Draft/Open/Unmerged; CI is not independently verified.

---

## Live operator observation (historical run, source 4366f3b)

At operator checkout `4366f3b1476105c6f556e0e93c4f5e1da64f68fa`, read-only wrapper `scripts/temporary/p5d-readonly-once.sh` printed:

- `test_p5d_live_audit_cpu.py`: **14/14 PASS**, `P5D_LIVE_AUDIT_CPU_RC=0`; one Python `ResourceWarning` from unclosed `os.scandir` during a passing test.
- `test_p5_readonly_attribution_cpu.py`: **7/7 PASS**, `P5D_ATTRIBUTION_CPU_RC=0`.
- `test_p5d_p6e_cpu.py`: **19/19 PASS**, `P5D_P6E_CPU_RC=0`.
- Total **40/40 selected CPU tests PASS**, not full workflow or latest source SHA CI. `P5D_SERVICE_PREFLIGHT_PASS`: active Orcarouter MTP0 developer trial with API.
- Actual audit `status=BLOCKED_PARTIAL_PROVENANCE`, `P5D_READONLY_AUDIT_RC=3`; `service_api_model_id_confirmed=true`, `container_id_continuous=true`, `pid_identity_continuous=true`, `executed_inference=false`, `service_mutated=false`, `production_released=false`.
- Container `qwen38-orcarouter-qsa62318-lmhead-v3`, exact Docker ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`; 3 host PIDs examined, init PID 4016083 at capture time (PIDs are transient).
- Private full receipt path **reported by operator**, not yet uploaded or independently inspected: `/home/inlc/.local/state/blazux-wizard/model-measurements/orcarouter--20261119T004619880648Z--bd848453cb4f.json`. Screenshot/stdout alone does not contain the per-PID smaps/read failure reasons or raw Docker inspect PortBindings.

### Exact operational findings and limitations

| Evidence | Actual observed | Grounded interpretation |
| --- | --- | --- |
| API `/v1/models` | exact expected served ID confirmed | Service/model served at observation time; does not attest host port kernel owner |
| Docker identity | same exact ID, initial/final host PID set, `pid_identity_continuous=true` | Bounded continuity observation; namespace identifiers were not independently validated as nonempty by old code |
| Docker :8000 publishing | declared=true, effective=true, `DOCKER_DECLARATION_MISMATCH` | **Not proof of real bad network config**. Current generic comparer treats an extra Docker IPv6 `::` wildcard as a mismatch with IPv4-only HostConfig; actual raw bindings have not been inspected, so root cause remains uncertain |
| Container network namespace | `container_netns=""`, TCP LISTEN socket inode count 1 | Old code issued `PID_NETNS_DRIFT` for any empty namespace string, which is not independent proof of namespace change. No matching FD-owner PID reported |
| Host port NAT | host listener PID absent, `iptables-save` unavailable | Compatible with Docker bridge/NAT or inspection permissions; no trusted DNAT path, port process or kernel owner proof |
| PLE candidate mappings | 0, `SMAPS_UNREADABLE` and `PINNED_SNAPSHOT_DIRECTORY_UNREADABLE` | No per-file RSS/PSS, no mapped inode, no pinned snapshot alias; could be permissions, path/mount assumptions or other read failure, not demonstration of PLE eviction |
| PLE unique physical residency | `null`, `ple_residency_authenticated=false` | Correctly not measured; do not confuse mapped RSS/PSS with unique physical bytes or other checkpoint tensors |
| GPU exclusivity | false | No independently authenticated GPU exclusivity or production release |

**Status**: `P5D_REAL_READONLY_EXECUTED_SOURCE_SHA_BOUND / CPU_40_PASS_OPERATOR_REPORTED / ACTUAL_PROVENANCE_BLOCKED_PARTIAL / API_DOCKER_CONTINUITY_OBSERVED / PLE_RSS_NAT_OWNER_UNOBSERVED / PRODUCTION_BLOCKED`.

## Source-only follow-up after the actual run — not DGX tested

The source/test revision after the above live run makes the following targeted, conservative changes:

1. `scripts/manager/p5d_live_audit.py` closes the `os.scandir` iterator even on early socket match; treats empty netns as an *unqualified observation* instead of `PID_NETNS_DRIFT`; disallows blank ns IDs from counting as valid PID identity continuity; adds `SMAPS_ACCESS_DENIED` vs missing PID/file classification; recognizes an HF read-only bind mount that already ends in `/hub`; and reports bounded per-PID candidate mapping and access outcomes in stdout summary.
2. `scripts/manager/p5_readonly_attribution.py` allows **only** a specific Docker port declaration normalization: HostConfig IPv4 wildcard :8000 with effective IPv4 wildcard *plus* IPv6 wildcard `::` :8000. Any different IP/port or unexpected extra binding still fails closed. This is **not** kernel NAT verification.
3. Adds CPU tests for empty/unqualified namespace values, smaps permission error, already-hub cached revision, Docker compatible IPv6 wildcard and mismatched extra host binding. The older audit's verdict is **never retroactively promoted**.

The **revised source CPU tests, new exact SHA, GitHub Actions and any new DGX read-only observation are not verified by this historical operator log**. Do not claim source fix alone resolves the missing PLE RSS, actual NAT owner or service qualification. No new GPU inference, model stop/restart, Docker settings, privilege escalation, operating Journal changes, auto-recovery, PR merge, asset deletion or production promotion authorized.

## Next low-risk evidence action (no new GPU or DGX probe required)

Review the **already-created private full receipt** `orcarouter--20261119T004619880648Z--bd848453cb4f.json` by operator upload in ChatGPT. It contains `file_mappings`, `pid_identity_before/after`, `pinned_snapshot`, and the P5-D before/after ownership evidence omitted from compact stdout. This can distinguish per-PID access denial from missing mappings, and show the actual namespace observation, without rerunning the P5-D audit or changing the live system.

If the full receipt is insufficient, any further read-only *host* probe or role-based permission/elevated audit is a separate bounded decision; **no automatic sudo, root, Docker exec or service mutation**. PR remains Draft/Open/Unmerged, CI new HEAD unverified. P6-E/P7/P8 release unaffected.
