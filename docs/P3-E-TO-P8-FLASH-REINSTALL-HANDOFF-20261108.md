# P3-E → P8 — Flash-Next canonical reinstall acceptance handoff (2026-11-08)

## Decision and current truth

**Move the real Flash-Next canonical reinstall acceptance and final production release check to P8.** This is a scope transfer, NOT an acceptance claim. P3-E remains source-preparation/draft, with no registered or executable canonical Flash runtime recipe, and no approved live reinstall. Historical actual P3-G bidirectional 27B↔Flash switch remains PASS/CLOSED. P8 failure injection, auto-recovery and final operations acceptance remain NOT_RUN/NOT_RELEASED.

Actual operator DGX read-only Flash FP8-hybrid evidence:
- Pinned NVIDIA `fc694b54fb0174e0913e6adf86691ef85a4ead47` derived view and exact legacy command normalized using Flash-specific parser. Documented fields match, source/host full reinstall does not.
- `model.safetensors.index.json`: **31,907,813 bytes** and **299,845 `weight_map` keys**, JSON `OBJECT`. The old CPU-only cap 100,000 produced an expected safety block; no shard integrity assertion was reached.
- Explicit source-only 400,000-key bound with 128 MiB independent byte cap, 256 maximum shard files, per-path containment, 8 MiB small metadata and 256 KiB template limits. Next real host read-only recheck remains required.
- Last observed live service is `qwen38-27b` serving `qwen3.8-27b` on :8000, single active model; do not recreate, stop or switch as part of this handoff.

## P3-E closeout scope (source artifacts only)

1. Preserve the pinned, **unregistered** `recipes/qwen38-flash-next.runtime.draft.json` (`launch_allowed=false`, `register_as_runtime_recipe=false`) and all historical source/recipe evidence.
2. Run CPU/Fake-DGX command normalization, asset presence/index/size/metadata tests; source commits and Actions CI must be tied to a specific HEAD.
3. Request a fresh bounded read-only DGX `python3 -m scripts.manager.flash_host_assets --json` following pull, to verify index referenced shard presence, template hash and host metadata. Any failure remains a pending prerequisite for P8, not an auto-fix command.
4. Record unresolved host gaps: inherited vs Docker runtime Env, template bytes/digest provenance, cache ownership/permissions and legacy writable /hf bind, image tag vs immutable registry digest, full HostConfig/Config/network/security/restart/IPCs, reproducible creation options.
5. Mark handoff `P3_E_SOURCE_PREPARATION_HANDOFF_PENDING`; **never** label `P3_E_REAL_REINSTALL_PASS` without a separate P8 real acceptance record.

## P8 canonical reinstall acceptance — new prerequisites and gates

**P8-R0 — source preflight / no mutation:** versioned **desired runtime contract** covering Flash-specific command with 500k context, MTP=2, Yarn, tool/reasoning parser, prepared cache view, HF mounts and template, env classification, container image provenance, security/network/restart policy and port 8000. Build strict Fake-DGX desired-vs-observed diff and plan/approval tests. No canonical production recipe is enabled by this stage.

**P8-R1 — exact-plan approved real fresh Flash reinstall:** a new target container with fresh immutable plan SHA and separately expressed downtime, explicit TTY operator approval and preflight proving 27B current identity, model cache and template, image, port/GPU exclusive ownership, preserved original service and journal. Verify that the existing/alternate service can be restored and that no unapproved image or HF cache deletion occurs. Only then allow a bounded real create/start/verify trial.

**P8-R2 — functional and repeatable acceptance:** verify ready health, exact `qwen3.8-flash-next` API identity, chat/completions/tool/vision as applicable, configuration consistency against recorded contract, saved journal + immutable receipts, restart/reinstall idempotence, transition back to 27B :8000 under separate authorization. Distinguish manual restoration from **automatic** rollback; no undocumented silent retries. Fail closed for uncertain state.

**P8-R3 — deliberate fault/automatic recovery and final signoff:** only an **independently** approved bounded fault-injection trial can validate automatic recovery; no P3-G authorization can be reused. Combine P5/P6/P7 prerequisites, Wizard UI/operator controls, security, routing, audit, backups/storage and final release checklist. Release remains `false` unless separate explicit operator signoff.

### Explicit no-go conditions

- `ONE_ACTIVE_MODEL_ONLY`; vLLM 0.32; no SGLang; fixed host API port 8000.
- No destructive container/asset action without separate exact operator approval; no P3-A/B/C/G replay.
- No automatic deletion/recreation on drift, no proxy/gateway changes, no outage in source work.
- 27B canonical recipe/hash and P3 receipts remain unchanged.
- P8-R0/R1/R2/R3 are **planning labels only**. No P8 live run or production release is authorized by this document.

## Next read-only operator commands

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
python3 -m scripts.manager.flash_host_assets --json
./wizard.sh service manager status --json
```

The host asset report is diagnostic. Even success has status `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`. **Do not treat that as a live reinstall approval.**
