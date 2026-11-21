# 2026-11-07 — REAL DGX Wizard manifest retired-container cleanup COMPLETE

## Source and scope

**Evidence source:** actual DGX Spark operator console output provided in the current conversation in an attached terminal log (`붙여넣은 텍스트(1)(20261107-073924).txt`). Source revision after `git pull --ff-only origin feature/recipe-wizard-handoff`: `9518f25e614367ab0ebbb725d7568e5c6bf177ed`. This is REAL execution evidence, not CI or an inferred removal.

Action: `./wizard.sh service manager cleanup --plan` → operator-approved TTY `./wizard.sh service manager cleanup --execute` → independent `cleanup --status` + `service manager status --json` + whole-host `docker ps -a`.

## Verified before execution

- Plan `status=READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL`, `issues=[]`, `target_count=2`.
- Exact fresh plan SHA: `39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5`. **Consumed; never reuse it.**
- Active canonical `qwen38-27b` identity `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`.
- Target **1** `qwen38-27b-failed-6d9ede0904c2`: stopped, exact container ID `44920f80610c5787f7d72064269be175d18150fe68d5a2fe846499129fc596bc`, prior `FAIL_RESTORED` evidence.
- Target **2** `qwen38-27b-native-tools-v1`: stopped, exact container ID `d42a15e2f7959829eeb616d748522193999441c9f418ec5dcae98931dfe5da56`, prior `PASS_RESTORED` evidence.
- The operator entered the exact fresh SHA and two distinct cleanup/preservation acknowledgements.

## Actual execution result

```json
{
  "action": "MANIFEST_RETIRED_27B_CONTAINER_CLEANUP",
  "status": "MANIFEST_RETIRED_CONTAINERS_CLEANED",
  "executed": true,
  "issues": [],
  "deleted": [
    {
      "name": "qwen38-27b-failed-6d9ede0904c2",
      "container_id": "44920f80610c5787f7d72064269be175d18150fe68d5a2fe846499129fc596bc"
    },
    {
      "name": "qwen38-27b-native-tools-v1",
      "container_id": "d42a15e2f7959829eeb616d748522193999441c9f418ec5dcae98931dfe5da56"
    }
  ],
  "remaining": [],
  "preserved_original_model_service": true,
  "preserved_images_and_caches": true
}
```

These fields are reported by the actual guarded executor; they do NOT independently prove the image/cache files' content hashes. No `docker rmi`, HF cache deletion or model restart was requested in this cleanup action.

## Independent post-execution read-only verification

- `./wizard.sh service manager cleanup --status` returned `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, `missing=[both requested names]`, `remaining=[]`, `active_service_preserved=true`, receipt `result-39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5.json`.
- `./wizard.sh service manager status --json` returned `LIVE_SERVICE_VERIFIED`, `API_IDENTITY_CONFIRMED`, `issues=[]`, `qwen38-27b` active using host port **8000**, observed model ID `qwen3.8-27b`; `manifest_status=OBSERVED_UNQUALIFIED`, `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are separate unverified scopes, NOT evidence of a model conflict.
- `docker ps -a` after cleanup lists **only** these four containers: `qwen38-27b` (running), `qwen38-flash` (stopped), `open-webui` (healthy), `portainer` (running). Neither retired test container remains.

## Manifest and Wizard lifecycle consequences

This exact two-target batch is **COMPLETE**, not future pending work. `runtimes/service-policy.json.retired_containers` retains the historical target IDs, names and receipt pointers for reproducibility, with completed-observation metadata. The live Docker inventory and private immutable result receipt remain authoritative over a Git-tracked completion label. When the operator repeats `cleanup --plan`, the Wizard should return **already cleaned** without issuing a new deletion approval; `cleanup --status` remains the canonical read-only verification.

**No blanket deletion prohibition:** `qwen38-27b` and `qwen38-flash` remain valid future remove/reinstall/recreate managed models, separately subject to user approval and availability of their qualified recipes. Those general Wizard lifecycle executors and recipe-diff-aware restart/switch remain future work; this completed cleanup does not imply they are implemented.

P2-FINAL canonical NVIDIA 27B Native Tools recipe plus benchmark v2 already passed; user independently confirmed Open WebUI Native; historical P3-C remains REAL PASS and closed. P8 conditional migration task stays inactive. Do not re-run obsolete one-shot or previous migration plan IDs. Draft PR #1 remains unmerged.
