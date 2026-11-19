# P5-D — One-turn DGX read-only result and evidence-bound diagnosis (2026-11-19 KST)

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
