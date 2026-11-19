# P5-D one-shot permissions preflight / Wizard / Manifest (2026-11-20 KST)

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
