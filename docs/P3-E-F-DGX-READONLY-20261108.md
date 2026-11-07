# P3-E/F real DGX read-only diagnostic — operator supplied, 2026-11-08

This record summarizes operator-pasted output from `./wizard.sh service manager status --json` and the existing `p3-d-g-acceptance.sh --run --report ...` on DGX Spark. **No new GPU run, Docker mutation, start/stop, reinstall, or fault injection was executed by GitHub source work.** This is a new observation of a 27B service, not a new P3-G successful transfer.

## Current observed service

- `LIVE_SERVICE_VERIFIED`, API `qwen3.8-27b` on host port 8000, running `qwen38-27b`, 8/8 manifest/API scope checks true, `issues=[]`.
- The status query reports `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` because these were outside that command's independent probe.
- Service state is time-bound; container name/uptime are not proof that all later executions share the same Docker ID.

## P3-D — current block is PID visibility, not a demonstrated collision

- Read-only `ss` saw both 0.0.0.0:8000 and [::]:8000; independent GPU process exclusivity true; GPU compute PID 2560905 attributed.
- Docker :8000 owner: `qwen38-27b`. `ss_returncode=0` but `observed_port_pids=[]` and `sudo_ss_requested=false`.
- `HOST_PORT_PROCESS_PID_UNAVAILABLE`: process ownership remains **NOT VERIFIED in this run**. Previous independently authorized `--sudo-ss` D read-only PASS is historical and does not automatically qualify current PIDs.
- Follow-up only if operator intentionally permits read-only privileged `ss`: `sudo -v`, then `bash scripts/temporary/p3-d-g-acceptance.sh --run --sudo-ss --report /tmp/p3-d-g-readonly-pids-new.json` (choose a fresh report path). No runtime mutation.

## P3-E — documented-field match, unqualified host/runtime

- `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED`, `issues=[]`, `DRAFT_REVIEW_REQUIRED`, `canonical_recipe_registered=false`, `launch_allowed=false`.
- Confirmed local prepared `-fp8hybrid` checkpoint view, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, 500000 max context, MTP=2, Yarn override, native tools/reasoning parser, GPU all, shm 16GiB, IPC host and host port 8000.
- `additional_environment_key_count=37`; **counts are not errors**, and inherited image variables must be distinguished from operator-added runtime variables. `additional_mount_count=0`.
- Still unqualified: exact host cache/template contents and digest, full environment and Docker security/network settings, image registry digest and fresh canonical reinstall result.
- Original `cmd_normalization_error=UNEXPECTED_MODEL_CHECKPOINT_POSITIONAL` was caused by applying 27B-only syntax to Flash-specific `-cc.*` command tokens. Separate Flash documented-field comparison passed. Follow-on source-only Flash-specific parser prevents treating these tokens as positional without registering any production recipe.

## P3-F and P3-G scope

- Local DGX **150/150 CPU tests PASS** across the six existing P3-F suites, **not GPU/fault-recovery acceptance**. This confirms the previous source CI additions run on the operator machine.
- G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN` means **this D–G draft runner did not transfer**. Previous independent DGX operator-approved 27B↔Flash-NEXT actual bidirectional PASS/CLOSED remains valid. P8 continues to own deliberate failure injection/automatic original recovery and final production signoff.
- Total draft `acceptance_complete=false`, `blocked_stages=["P3-D"]` is correct given current PID probe.

## Next source/deployment boundary

1. Read-only privileged P3-D PID attribution if separately approved by the operator; do not relax validation to force PASS.
2. Normalize model-specific full Flash command but leave `launch_allowed=false`, `canonical_recipe_registered=false` and production lifecycle locked. Failing to parse unknown flags must not auto-qualify new options.
3. Gather and redact full Docker Config/HostConfig/mount and image-template provenance **without printing secrets in public CI/PR**. Compare against new versioned Flash target contract before requesting a bounded real reinstall.
4. No P3-A/B/C/G repeat, no P8 fault injection, no unauthorized state changes.
