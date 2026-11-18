# P5-D — one-turn read-only PLE RSS/PSS + inode/PID + port-8000 NAT attribution (2026-11-19)

## Objective, permission and safety

**Operator requested a single-turn, read-only P5-D diagnostic**, not model switching, inference, Docker mutation, privilege changes or production authorization. A new source-only collector \`scripts/manager/p5d_live_audit.py\`, wrapper \`scripts/temporary/p5d-readonly-once.sh\`, and CPU fixtures \`tests/test_p5d_live_audit_cpu.py\` were created on Draft PR #1.

- **No sudo, docker exec, model inference, restart, container image/cache change, kernel firewall modification, service Journal change, P8 fault injection, or PR merge**. All host operations are reads. Optional \`--save\` creates **one private 0600 JSON evidence file** outside the repository using the existing measurement-history writer; this is the only intentional write.
- First validate source checkout is clean; CPU/Fake-DGX tests must pass before touching live host probes. The wrapper checks the already-active Orcarouter development trial and exact served ID on \`:8000/v1\` before audit.
- The audit is bounded: exact current Docker full ID and init PID, up to 32 Docker host PIDs, maximum 96 MiB streamed \`smaps\` per PID, at most 512 candidate mappings per PID, at most 256 pinned-snapshot entries per cache root; fixed process command arguments and bounded output, sequential before/after Docker ownership receipts.
- **No automatic retries/elevation**. A blocked result is a valid diagnostic outcome, not a reason to change service state.

## A single DGX operator transaction

\`\`\`bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only
bash scripts/temporary/p5d-readonly-once.sh
\`\`\`

The wrapper executes (in order):

1. Print the exact Git SHA and require an empty worktree.
2. Run \`test_p5d_live_audit_cpu.py\` (new scoped tests), \`test_p5_readonly_attribution_cpu.py\` (historical parser), and \`test_p5d_p6e_cpu.py\` (existing ownership/Journaling safety). If *any* suite fails, the host audit is not run.
3. Verify live \`LIVE_P5_TRIAL_API_VERIFIED\`, active \`orcarouter\` v3 MTP0, served ID \`qwen3.8-flash-next-orca-uncensored-bf16\`, \`DEVELOPMENT_TRIAL\` and port 8000, with no service status issues.
4. Read-only \`python3 -B -m scripts.manager.p5d_live_audit --save --json\`:
   - P5-C/P5-D ownership captures before/after: full Docker ID, running/init PID, docker top host PIDs, GPU PID set, host \`ss\` listener.
   - Fresh Docker inspect: read-only bind mounts, \`HostConfig.PortBindings\` versus \`NetworkSettings.Ports\`, bridge container IP.
   - For each bounded Docker host PID: \`/proc/PID/stat\` process start ticks and net/mount/PID namespace symlink, \`/proc/PID/cgroup\` ID relationship, streamed \`/proc/PID/smaps\` model/HF cache-backed mappings, file RSS/PSS/Size, mapping dev major/minor + inode compared to \`/proc/PID/root/<mapped-path>\` stat without opening model contents.
   - Best-effort exact **pinned source snapshot revision alias** \`orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799\`: compare \`snapshots/<revision>/*.safetensors\` inode with mapped dev/inode; do **not** hash huge files or call them PLE-authenticated tensor assets without an independent manifest.
   - Container \`/proc/init-PID/net/tcp* :8000 LISTEN\` socket inode matched with \`/proc/Docker-PID/fd/*\` socket inode and netns equality. This is **container-side listener↔PID**, unlike host \`ss\` listener PID which can be absent under NAT.
   - Unprivileged \`iptables-save -t nat\` if permitted, reduced to Boolean matching exact Docker container IP:8000 DNAT candidate; read-only \`GET http://127.0.0.1:8000/v1/models\` exact served ID. No fabricated NAT owner if kernel rules are inaccessible or contradictory.
5. Print one compact JSON summary, \`P5D_READONLY_AUDIT_RC\`, and exact source HEAD afterward. The full per-file/per-PID mapping evidence is in \`evidence_file\` printed in JSON; attach that file along with terminal stdout for review.

## Classification and important limits

- \`CORRELATED_READ_ONLY_NOT_INDEPENDENTLY_AUTHENTICATED\` / RC=0: source observations agree on model, exact Docker ID, time-continuous PIDs/namespace, one or more file mapping inode matches with pinned cache alias, Docker configured port, API ID and an internal LISTEN socket owning PID; **this is a bounded correlation, not security-grade trusted live provenance, NAT kernel path proof, PLE physical memory uniquely resident, production acceptance or GPU exclusivity**.
- \`BLOCKED_PARTIAL_PROVENANCE\` / RC=3: a missing or inaccessible \`/proc\` field, snapshot path/alias, inode, socket FD or Docker evidence prevents admission. Lack of host \`ss\` PID alone is compatible with Docker NAT and **does not mean the service is down**.
- \`BLOCKED_PREFLIGHT\` / RC=3: exact active Docker/PID identity not qualified. No privileged or destructive fallback.
- Some checkpoint mappings may be unrelated to PLE; \`ple_specific_unique_resident_bytes=null\` and \`ple_residency_authenticated=false\` must remain so unless independent asset/tensor mapping proof exists. Per-PID RSS sums double count shared pages; even PSS is proportional accounting, not authenticated unique system physical memory.
- An iptables DNAT candidate + matching Docker publish + internal socket + healthy API **still does not attest which host kernel NAT path served the request**; Docker nftables, IPv6, rootless routing or inaccessible firewall policy can leave NAT evidence incomplete. No packet capture/flow tracing, no new inference load.
- No known current CPU/CI or real DGX acceptance may be claimed until the operator supplies a fresh exact SHA / test / audit transcript. GitHub Actions on recent feature-branch commits has not produced verified new-head runs. The PR remains Draft/Open/Unmerged, all operation and production flags false.

**Next:** examine operator stdout and the saved private per-PID JSON; classify which files were actually bound, what access was missing, and whether a new strictly read-only capability/privilege grant (not automatic sudo) would be necessary. This plan collects every nonprivileged available evidence source in *one invocation*; it cannot guarantee completeness when the kernel denies inspection.
