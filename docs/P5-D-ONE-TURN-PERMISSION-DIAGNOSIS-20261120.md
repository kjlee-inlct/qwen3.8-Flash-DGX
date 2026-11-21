# P5-D one-shot permissions preflight / Wizard / Manifest (2026-11-20 KST)

## Operator acceptance: one-shot CPU PASS and live permission blocker classified (2026-11-20 KST)

**Evidence origin:** operator-pasted DGX terminal stdout (not GitHub Actions or an assistant-run host probe). Exact source before and after: `045947fccd33952ef4911c908ffb480d62b3d82b`. The new synthetic `test_p5d_permission_preflight_cpu.py` completed **7/7 OK (0.010s)**, `P5D_PERMISSION_CPU_RC=0`. Wizard `manifest validate --json` yielded `PASS`, seven document files and cross-reference PASS, zero issues; `p5d-source-binding-review --model orcarouter --json` returned `DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED`, no operations/release enabled. This establishes the new source CPU unit test pass on this exact SHA; it does **not** repeat the earlier 138/138 test run (which was at 7c11d0d).

**Fresh Docker/PID identity:** the preflight captured a current, internally consistent 3-PID set for container `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, init PID `4016083`. Start ticks before/after each procfs sample were equal for all three: init PID `159946344`, worker PIDs `4016529`/`4016530` `159948383` each. This is a short read-only consistency observation, not a permanent PID identity or GPU-exclusivity proof.

| Evidence dimension | Value at audited SHA | Interpretation |
| --- | --- | --- |
| Audit credential | `audit_effective_uid=1001` | Non-root operator process |
| All three container process credentials | `real_uid=0`, `effective_uid=0` | Root-owned target processes; **credential mismatch observed** |
| All three `/proc/PID/smaps` samples | `ACCESS_DENIED`, `errno=13` | Permission denial verified 3/3, **not** measured RSS/PSS=0 |
| All three `/proc/PID/fd` sample links | `ACCESS_DENIED`, `errno=13` | Cannot attest LISTEN inode→PID FD owner |
| Container init `/proc/PID/root` link | `ACCESS_DENIED`, `errno=13` | Prevents resolving pinned HF path via container root |
| Pinned HF snapshot directories | two candidates, both `ACCESS_DENIED` | PLE file alias / inode mapping unavailable |
| All three `net`, `mnt`, `pid` namespace links | `UNQUALIFIED` | Link targets did not satisfy namespace identity grammar; errno **not reported**, not proven access denied or real drift |
| All three PID start ticks | stable before/after | PID start-time *portion* observed; combined PID + 3 namespace identity gate still unqualified |
| smaps metadata | owner `uid=0`, `gid=0`, visible mode `0o444` | Mode bits alone do not guarantee procfs access; ptrace/LSM checks can apply |
| procfs mount | `hidepid=NOT_DECLARED`, `subset=NOT_DECLARED` | No matching explicit mount option observed; not proof of unrestricted `/proc` access |
| Yama | `ptrace_scope=1` | Kernel security policy hint; cannot independently assign this as the cause of the read-only denial |

**Outcome:** `BLOCKED_PERMISSION_PREFLIGHT / RC3`, `smaps_access_denied_pid_count=3`, `ready_for_full_readonly_audit=false`, `P5D_FULL_AUDIT_SKIPPED=PROCFS_OR_IDENTITY_BLOCKED`, `P5D_LIVE_ACCEPTANCE=BLOCKED_NOT_SERVICE_OUTAGE`, `P5D_NO_PRODUCTION_RELEASE`; there was **no repeat** of the expensive P5-D live audit and no service mutation or inference.

**Technical conclusion:** the privilege/credential mismatch (auditor 1001 vs target 0) explains a major part of the likely permission boundary. Linux procfs access can involve ptrace read mode (`PTRACE_MODE_READ_FSCREDS`), process credentials/dumpability, capability checks, and LSM policy even if the path appears world-readable. An individual mechanism has not been proven solely by the transcript; especially Yama `ptrace_scope=1` should not be labeled the sole cause. Namespace `UNQUALIFIED` is also not equivalent to `errno=13`. These distinctions must remain explicit.

**Decision:** close the **non-elevated one-turn permission diagnostic** as completed and source-CPU-verified at `045947f`. Keep P5-D live memory/inode/socket/NAT attribution and P6-E/P7/P8/production `BLOCKED`; GitHub Actions CI `UNVERIFIED`. Do not perform repeated non-elevated full audits or attempt privilege escalation, ptrace, sudo, container entry, filesystem permission changes, sysctl changes, cache mutation, service restart or operating Journal write on this result. If a later operator explicitly approves a *separate* narrowly scoped privileged, read-only evidence procedure, refresh PID/Docker identities and independently record who authorized the access; until then there is no further live P5-D acceptance evidence to collect with current credentials.

---

## Scope

Previous real audit at fd338efa549a8c3bb54e65e5e033d2334d9e96e1 returned BLOCKED_PARTIAL_PROVENANCE/RC3 and EACCES errno 13 for all 3 PID smaps. PLE RSS/PSS 0 observed rows does not imply zero resident memory. Historical 138/138 operator CPU PASS belongs only to 7c11d0d.

New scripts/manager/p5d_permission_preflight.py checks the source graph before any host probe, refreshes Docker top/inspect PID identity, then reads at most 256 bytes of each live smaps, metadata-only namespace link, UID, numeric smaps mode/owner, procfs mount hidepid/subset hint, FD directory sample, stat start ticks before/after, root link and manifest-pinned source snapshot directory accessibility. The Yama ptrace_scope value is only a policy hint, never a confirmed explanation of EACCES. No private process data returned, and no sudo, Docker exec, new inference, service change or operating Journal writes.

Wizard CLI: python3 -B -m wizard operations generic p5d-permission-preflight --model orcarouter --json; model-first Wizard menu item 15. The status READABLE_PROCFS_PREFLIGHT_NOT_ATTESTED only means read access samples qualify. It never establishes full mapping coverage, PLE residency, inode authenticity or NAT ownership. The status BLOCKED_PERMISSION_PREFLIGHT returns RC3 and never triggers a full audit.

Operator one-shot (run only after approval for non-elevated read-only host probes):

    cd ~/Workspace/llm/blazux-orcarouter
    git pull --ff-only origin feature/recipe-wizard-handoff
    bash scripts/temporary/p5d-permission-diagnose-once.sh

The wrapper runs newly added synthetic CPU tests, seven-document manifest validation and source binding; it emits the fresh PID permission report. Only if all tested permissions are readable does it invoke the existing bounded full live read-only audit once, optionally writing a private 0600 evidence JSON. If blocked, it skips the known-failing full audit. Source and CPU tests are not verified on this new commit until the operator sends an exact-SHA transcript.

No GPU workload, sudo, Docker mutation, host firewall action, cache deletion, service switch, operating Journal update, CI dispatch, main commit, PR merge, or production release. PR #1 remains Draft/Open/Unmerged and GitHub CI is UNVERIFIED.
