# Evidence ledger — observed facts and test reports

Use an append-only entry for every meaningful result. Never substitute README claims or previous chats for locally reproduced tests.

## Entry template

| Field | Value |
|---|---|
| ID / KST | `E-YYYYMMDD-NN` / timestamp |
| Model / recipe / revision | full id + immutable revision |
| Git HEAD / branch | exact actual SHA and branch |
| Runtime image / host | immutable digest, vLLM version, GPU/driver/OS |
| Scope | SOURCE / CPU / CI / GPU / API / SWITCH / RELEASE |
| Exact invocation | command/environment; redact secrets |
| Inputs | test names, prompt/seed hashes, dataset scope |
| Result | PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE |
| Artifacts | paths/URLs/digests |
| Limits | scope, caveats, unresolved mismatches |

## E-20261104-01 — source-only planning baseline

- **Scope:** SOURCE / GitHub metadata and public source inspection, **not** GPU.
- **Repo:** `kjlee-inlct/qwen3.8-Flash-DGX`.
- **Source commit:** `blazux/qwen3.8-Flash-DGX@b0aa8b77604139557169387b2fa8386355d8b651`; user fork main same at branch creation.
- **Source observations:** `flash` and `profiles` cover NVIDIA and RadixArk Flash-Next; `scripts/serve.sh` removes container matching `NAME`; `feature/orcarouter-bf16-adapter` already holds a design doc; aphex3k 27B recipe uses SGLang, **not** local vLLM 0.32 proof.
- **Result:** `PASS_SOURCE_INSPECTION` for cited facts; `NOT_RUN` for CPU tests, CI, DGX runtime/benchmark.
- **Artifacts:** [Blazux source](https://github.com/blazux/qwen3.8-Flash-DGX/tree/b0aa8b77604139557169387b2fa8386355d8b651), [Orcarouter parallel branch design](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/blob/feature/orcarouter-bf16-adapter/docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md), [27B external reference](https://github.com/aphex3k/Qwen3.8-27B-on-DGX-Spark).
- **Limits:** No current disk, container, memory or actual 27B vLLM evidence.

## E-20261104-02 — new planning branch and documentation

- **Scope:** GitHub SOURCE / documentation-only.
- **Branch base:** `feature/recipe-wizard-handoff` created from `b0aa8b77604139557169387b2fa8386355d8b651`.
- **Result:** `PASS_SOURCE/GITHUB`: 10-file commit `76cd8dae16b0f34e47c353b56b6e9dbcc5fcde25` confirmed by branch readback and compare with `main`; draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) opened against `main`, unmerged. `NO_CHECKS_REPORTED` for that original commit (0 check-runs, 0 PR workflow runs). **No CPU, CI, GPU or service tests run.** This entry does not qualify any runtime.
- **Artifacts:** `docs/MODEL-RECIPE-WIZARD-PLAN.md`, `docs/MANIFEST-CONTRACTS.md`, `handoff/*`.
- **Limits:** Manifest examples, wizard commands and state machines are designs, not implemented software.

## E-20261104-03 — N1 isolated CPU source contract check

- **Scope:** SOURCE/CPU (2026-11-04 KST). Executed in a separate CPU container, **not DGX**. Previous fork HEAD read: feature/recipe-wizard-handoff@07b0e3d49b387ecc29c00e3f5338e4e7065bcc27; new commit must be verified independently.
- **Tools:** Python 3, PyYAML 6.0.3, jsonschema 4.26.0; no vLLM/CUDA/Docker.
- **Exact commands:** python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -q => **15 PASS**; python3 -m scripts.manager.manifest validate recipes/qwen38-27b.candidate.yaml => expected **FAIL**, exit 2, 6 invalid/unverified fields; same command with tests/fixtures/recipe-valid.synthetic.yaml => schema **PASS**, exit 0, launch_authorized=false.
- **Artifacts:** schemas/recipe.schema.json; scripts/manager/manifest.py; recipes/qwen38-27b.candidate.yaml; tests/test_manager_manifest_cpu.py; tests/fixtures/recipe-valid.synthetic.yaml.
- **Limits:** synthetic a/b/c-character SHA values are fake fixture data; schema PASS is not repository existence/image runtime compatibility evidence. CI awaits new PR SHA observation. GPU/API/SWITCH/RELEASE NOT_RUN. No current DGX state observed.

## E-20261105-01 — Flash-Next 8000 default/N2 inventory source implementation

- **Scope:** SOURCE/CPU TEST CODE. Old fork HEAD was `bf453aea425c0d9136d67ac003a4f296a0a96885`; GitHub commit/CI outcome must be re-read after updating branch.
- **Change:** default Blazux NVIDIA Flash-Next, hybrid/YaRN/MTP2, exposed :8000/v1, served `qwen3.8-flash-next`; refactored unsafe implicit Docker container replacement into fail-on-name-exists. Removed outdated schema hard-coding of port 8000 and historic Orcarouter name.
- **Added read-only inspections:** `python3 -m scripts.manager.inventory doctor --dry-run` and `plan --dry-run` via Wizard. Commands collect local Docker/ss/disk/HF cache metadata; never execute model/Docker mutation.
- **New tests:** `tests/test_manager_inventory_cpu.py` (10 synthetic scenarios), `tests/test_flash_launch.py` (+4 cases), `tests/test_manager_manifest_cpu.py` updated old port expectations. GitHub CPU workflow expanded; **CI_NOT_YET_OBSERVED** in this source entry.
- **DGX:** user reports old services removed, **NOT_INDEPENDENTLY_VERIFIED**. No model/download/GPU/API/bench, no new runtime measured; required source/model image revisions still to be pinned for release.

## E-20261105-02 — CI failure and corrective script mode

- **Scope:** CI, commit `7e8f4a109a04c130a5dba0d73e3ece0881d85478`.
- **Observed:** GitHub Actions jobs [push failure](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41947918546/job/126984612955) and [PR run](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41947924748/job/126984632242) reported manifest **15/15 PASS**, N2 Inventory **10/10 PASS** and launch **4 FAIL/13**. Exact failures: `test_capable_dflash_launch`, `test_default_options_remain_empty`, `test_default_port_8000_and_next_flash_model_id`, `test_docker_options_reach_docker_not_vllm`; shell exit 126.
- **Root cause:** GitHub tree update accidentally wrote executable shell paths `flash` and `scripts/serve.sh` as `100644`. Root Git tree confirmed incorrect modes; not a demonstrated model/runtime bug. Correction restores `100755`; actual CI rerun must be independently checked. No failure history removed.
- **DGX:** NOT_RUN, no status observed.

## E-20261105-03 — Confirmed Wizard-first P1–P7 roadmap (decision, not test)

- **Scope:** USER_DECISION / DOCUMENTATION. The user reconfirmed sequential Wizard execution for all milestones. Evidence is the user request; not runtime testing.
- **Last independently verified source CI:** `feature/recipe-wizard-handoff@017319a5394155797bcb7e5c933ccef35080d669`; [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41948116286/job/126985272415) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41948122438/job/126985292140) **SUCCESS** (15 manifest + 10 inventory + 13 launch + 1 script modes = 39/39 tests each). Historical `7e8f4a1` four test failures remain recorded in E-20261105-02.
- **Current deliverable:** documentation-only alignment, no new source-test execution; CI for resulting documentation HEAD to be read back. **GPU/API/BENCH/SWITCH/RELEASE = NOT_RUN**; live DGX and :8000 occupancy **NOT_OBSERVED**.
- **Boundary:** Roadmap confirmation does not itself approve GPU loading or model/cache deletion. P4 is conditional with exact approval; `SKIPPED_NOT_NEEDED` permitted.

## Historic evidence not transferred

## E-20261105-04 — User-reported Flash-Next download still in progress

- **Time/subject:** 2026-11-05 11:46 KST, `nvidia/Qwen3.8-Flash-Next-NVFP4`.
- **Evidence:** user said checkpoint was **still downloading**. Classification: `USER_REPORTED / DOWNLOAD_IN_PROGRESS`, not a DGX/filesystem observation and **not** a checksum or completion proof.
- **Unknown:** actual download process, command, bytes, completion percentage, snapshot revision, local cache path and storage headroom.
- **Verification:** `DOWNLOAD_COMPLETE=NOT_VERIFIED`; `HYBRID_PREPARED=NOT_VERIFIED`; `GPU/API/BENCH=NOT_RUN`. No upload/download/cache/operational operation by the assistant.
- **Next safe action:** build P1 Wizard flows and download-in-progress fail-closed tests from synthetic data; after reported completion, verify snapshot and all weight shards read-only before preparation/serve, avoiding concurrent writes.


Old Preview/YSLAB projects reported Orcarouter BF16 PLE/MTP results; those are **reference evidence only**, not proof of the new vLLM 0.32 fork. Historical Preview strict same-token logprob `1e-4` release blocker remains unresolved. DGX status is unobserved this session.

## Update policy

Append new measured entries, never replace failures. When rerunning a test, give it a new ID and reference prior entry. If an entry proves wrong, add an explicit correction with link; do not rewrite history. Publish non-sensitive artifact locations and keep credentials/private data out.
