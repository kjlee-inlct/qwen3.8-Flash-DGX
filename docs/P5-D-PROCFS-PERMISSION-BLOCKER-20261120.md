# P5-D host procfs permissions blocker — 2026-11-20 KST

## Follow-up 2026-11-20 KST — permission boundary now localized

An exact-SHA (`045947fccd33952ef4911c908ffb480d62b3d82b`) operator one-turn preflight confirmed audit EUID 1001 vs three root-owned model PIDs (UID 0), smaps EACCES 3/3, FD EACCES 3/3, container root link EACCES, pinned snapshot dir access denied 2/2, stable start ticks, no explicit procfs hidepid/subset and Yama ptrace_scope=1 policy hint. No full P5-D audit was repeated. See [P5-D one-turn permission diagnosis](P5-D-ONE-TURN-PERMISSION-DIAGNOSIS-20261120.md) for complete SHA-bound transcript classification. Namespace links were UNQUALIFIED but lacked errno. No new live PLE/NAT acceptance.

## 1. Fresh operator-run DGX evidence (exact-source bound)

Source: operator-provided terminal transcript from `~/Workspace/llm/blazux-orcarouter`, following an exact clean-tree `git pull --ff-only` on `feature/recipe-wizard-handoff`.

- **Audited and reported SHA:** `fd338efa549a8c3bb54e65e5e033d2334d9e96e1` (documentation-only child of CPU-tested `7c11d0d1a0921ef7b0f4134bd3d3c0d8ac4e5795`).
- **Source Manifest:** `wizard manifest validate --json` reported `status=PASS`, `issues=[]`, seven manifest files and registry/cross-reference PASS, no runtime release.
- **Wizard P5-D binding:** `operations generic p5d-source-binding-review --model orcarouter --json` reported `DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED`, `asset_id=orcarouter-bf16-ple`, source pin `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799`, `format=BF16`, `placement=DISK_MMAP`, `served_id_provisional=true`. This is configuration/source validation only.
- **P5-D bounded live read-only audit:** status `BLOCKED_PARTIAL_PROVENANCE`, `P5D_READONLY_RC=3`, run timestamp `2026-11-19T23:19:44.346912+00:00` (Nov 20 KST), `executed_inference=false`, `service_mutated=false`, `production_released=false`. Its original local private receipt basename is `orcarouter--20261119T231947672182Z--ea15d0ce12cc.json`. **Only compact terminal JSON was uploaded** here, not the complete private receipt.

## 2. New negative evidence: permission denial is known, not inferred

| Scope | Operator-reported value | Correct interpretation |
| --- | --- | --- |
| Docker container identity | `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`; name `qwen38-orcarouter-qsa62318-lmhead-v3`; `container_id_continuous=true` | Short read-only correlation of same Docker object |
| API | `service_api_model_id_confirmed=true` | API model ID matched, not independent host port/PID ownership |
| Docker bridge port declarations | `docker_ipv6_wildcard_extension_observed=true`, `docker_port_declarations_consistent=true`, `status=DOCKER_DECLARATION_CONSISTENT_NOT_HOST_VERIFIED`; bridge IP `172.17.0.3` | The former mismatch is now resolved **at Docker declaration-comparison level**, not by a network configuration change; kernel DNAT still unverified |
| `/proc/4016083/smaps` | `smaps_errno=13`, `SMAPS_ACCESS_DENIED`, `NOT_OBSERVED` | EACCES: process file mappings are unreadable by current audit credential |
| `/proc/4016529/smaps` | `smaps_errno=13`, `SMAPS_ACCESS_DENIED`, `NOT_OBSERVED` | Same; no RSS/PSS measurement |
| `/proc/4016530/smaps` | `smaps_errno=13`, `SMAPS_ACCESS_DENIED`, `NOT_OBSERVED` | Same; 3/3 PID reads denied |
| PID identity before/after | `pid_identity_continuous=false`; `PID_STARTTIME_OR_NAMESPACE_DRIFT_OR_UNAVAILABLE` | Namespace/start-time chain unqualified; **not proof of actual PID reuse or drift**. Namespace readlink errno was not retained, so EACCES for namespace links is **not established** |
| Container :8000 socket | LISTEN inode count 1; `container_netns=""`; matched FD/PID owners=[] | Listener candidate exists, but namespace and FD ownership chain unqualified |
| Host NAT | `iptables_nat.status=UNAVAILABLE`; `host_nat_path_authenticated=false` | Unknown NAT owner/path; not proof of missing NAT rule |
| Pinned snapshot / files | `PINNED_SNAPSHOT_DIRECTORY_UNREADABLE`, no file aliases or mapping rows; `ple_specific_unique_resident_bytes=null` | PLE file access/path state and resident-byte values **unobserved**, not zero |

This run resolves one important uncertainty in the historical 2026-11-19 private receipt: the current `smaps` failures are demonstrably `errno=13/EACCES` for **all three** PIDs. It also confirms that strict Docker IPv4+IPv6 wildcard declaration normalization prevents falsely calling the present port publishing config a mismatch. It does **not** establish an independently verified actual NAT mapping, kernel socket owner, PLE tensor identity, memory amount, namespace continuity, or GPU exclusivity. The previous `138/138` operator CPU tests were run on `7c11d0d`, not on this evidence-only SHA.

## 3. Immediate operational decision

**Do not rerun the expensive P5-D host audit in a loop without a change in read permissions or a new evidence method.** Reproducing the same `EACCES` on three PIDs will not yield RSS/PSS. Next step is a separately approved **non-elevated, read-only permission preflight** inspecting audit UID vs process UID and procfs access controls; record its exact SHA and stdout. Without positive permission/readability evidence, classify `P5D_PROCFS_ACCESS_BLOCKED` and leave PLE RSS/PSS, inode, NAT, and live acceptance `BLOCKED`. Do not automatically use sudo, Docker exec, host firewall mutation, containers or privileged file access. Unattested `namespace=""` must remain `UNQUALIFIED`, not `DRIFT`.

A proposed bounded non-elevated diagnostic (for operator review/authorization; no automatic execution):

```bash
id
findmnt -no TARGET,OPTIONS -T /proc || true
for pid in 4016083 4016529 4016530; do
  ps -o pid=,uid=,user=,comm= -p "$pid" || true
  stat -Lc '%n uid=%u gid=%g mode=%a' "/proc/$pid/smaps" || true
  for ns in net mnt pid; do
    readlink "/proc/$pid/ns/$ns" || true
  done
done
```

The above PIDs are **historical**, not permanent identities. Before an operator uses the diagnostic, they must establish fresh Docker/PID ownership and avoid treating recycled PIDs as the same processes. Access metadata alone cannot override kernel ptrace/LSM permissions.

**Independent gates:** `MANIFEST_PASS / WIZARD_P5D_SOURCE_BINDING_PASS / P5D_REAL_READONLY_RC3_EACCES_3_OF_3 / PORT_DECLARATIONS_CONSISTENT_NOT_KERNEL_VERIFIED / PID_NAMESPACE_UNQUALIFIED / PLE_RSS_PSS_UNOBSERVED / NAT_OWNER_UNVERIFIED / CI_UNVERIFIED / PR_DRAFT_OPEN_UNMERGED / PRODUCTION_BLOCKED`.
