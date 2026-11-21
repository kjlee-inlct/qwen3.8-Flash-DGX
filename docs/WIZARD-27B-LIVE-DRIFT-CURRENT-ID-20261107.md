# 2026-11-07 — 27B recipe-diff live DGX observation and current-ID-aware switch source

## Scope and safety

This document records a READ-ONLY operator DGX observation after git fast-forward to 5456eae, and a subsequent GitHub SOURCE-ONLY code update. It is NOT authorization for Docker/GPU/API mutation or production model switch release. P2-FINAL Native Tools, P3-C CLOSE and prior receipts remain immutable.

## Observed DGX (operator-provided output)

- Repository fast-forward: 9ec7420 -> 5456eae on feature/recipe-wizard-handoff; user reported clean git status before pulling.
- Active model: 27b (`qwen3.8-27b`); current Docker name `qwen38-27b`, **current ID** `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`.
- Canonical recipe hash reported by Wizard: `301c9c7980690b97e357db5fb57090fc82c507ab9c1116c8e154739e360bbbbb`. No recipe file modified in this session.
- Pinned image: `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; 27B repo revision `482ca0f3832238542f8f5295dde86b5f22711d80`.
- `./wizard.sh model 27b recipe-diff --json` reports `status=READ_ONLY_STATUS`, `diff=[]`, `issues=[]`, `installed=true`, `running=true`, active_model=27b, `operations_enabled=false`.
- Actual observed `hf_cache_source=/home/inlc/.cache/huggingface`, `/hf` bind read-only. The recipe does not pin the *host* source, causing advisory `HOST_HF_CACHE_SOURCE_NOT_PINNED_IN_RECIPE`. This is **not an actual Docker mount mismatch**.
- Model command includes native tools (`--enable-auto-tool-choice`, `--tool-call-parser qwen3_coder`, `--reasoning-parser qwen3`, pinned template), ModelOpt mixed, dtype bfloat16, GPU all, IPC host, shm 16GiB, bound host port 8000, same as canonical desired config.
- `./wizard.sh model 27b lifecycle restart --plan --json`: `decision=RESTART_EXISTING`, `diff=[]`, `issues=[]`, `executed=false`.
- `./wizard.sh model 27b lifecycle reinstall --plan --json`: `decision=RECREATE` because reinstall explicitly requested, NOT because current configuration drifted; `executed=false`.
- `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, `API_IDENTITY_CONFIRMED`, `expected_served_id=qwen3.8-27b`, all eight checks true, issues=[]. The `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` fields mean those scopes were NOT measured by this command; they are not observed conflicts.

## Subsequent source implementation

- `scripts/manager/operational_switch.py` uses freshly inspected current Docker IDs, keeping historical P3-A/B/C records only for provenance. A new canonical 27B instance is accepted if its `blazux.recipe=qwen38-27b` label, pinned image and normalized command/mount/ports/GPU/env agree with the unchanged qualified 27B recipe. Its current Docker ID and recipe SHA are included in a fresh read-only switch fingerprint.
- Flash-Next is still required to have its historically qualified Docker ID and image until a separately qualified canonical Flash recipe exists. A different, unqualified Flash container remains blocked. An unrecognized 27B container lacking historical lineage or canonical recipe also remains blocked.
- `scripts/manager/operational_executor.py` distinguishes canonical 27B provenance from historical P3 27B labels in its guarded backend; previous P3 receipts are not rewritten.
- `wizard/main.py` supports optional *read-only* `--cache-source /absolute/host/cache` for `recipe-diff` / `lifecycle` plans. This compares the host mount path explicitly without modifying the canonical JSON or granting execution. Use the actual observed path shown above; the new option is not a permanent site policy or installation approval.
- Fake-DGX tests cover both transfer directions after 27B canonical recreation, changed parser blocking, unknown Flash/27B identities, current-ID plan invalidation, explicit host mount comparison and rejection of malformed/execute CLI flags.
- GitHub Actions source-only run [42367665200](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42367665200) completed SUCCESS: **814/814 tests across 36 groups**. This is NOT a real GPU switching test.

## Next safe operator commands (new source branch)

On clean DGX repo worktree, fast-forward feature/recipe-wizard-handoff and run READ-ONLY:

```bash
./wizard.sh model 27b recipe-diff --cache-source /home/inlc/.cache/huggingface --json
./wizard.sh switch flash-next-27b operational --target flash-next --plan --json
./wizard.sh service manager status --json
```

No approval SHA from these previews grants a production switch. Ordinary production Wizard switch remains release-gated. No P3 A/B/C replay, arbitrary Docker removal, model-cache or image deletion, or two concurrent GPU models. The live failure/rollback path still requires independent DGX acceptance. If the preview is BLOCKED, retain the actual issues and fix the source; do not force execution.
