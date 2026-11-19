# P5-D — One-turn DGX read-only result and evidence-bound diagnosis (2026-11-19 KST)

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
