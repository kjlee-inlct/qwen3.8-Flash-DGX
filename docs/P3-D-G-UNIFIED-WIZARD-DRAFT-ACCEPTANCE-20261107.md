# P3-D / P3-E / P3-F / P3-G — Unified Wizard Acceptance Draft

**Status:** SOURCE DRAFT IMPLEMENTED, CPU tests pending/qualifying, real DGX D-G acceptance NOT COMPLETE.  
**Branch:** `feature/recipe-wizard-handoff`; existing PR #1 remains Draft, unmerged.  
**Policy:** vLLM 0.32, one GPU model active at a time, fixed API port 8000. SGLang not permitted. Canonical 27B Native Tools recipe SHA and historic P3 A/B/C receipts must not be changed.

## 1. Stage contract

Historical P3-A/B/C are **already REAL PASS and CLOSED** and do not need to rerun. New D–G are **additional stages**. Recurrent switching and general recipe lifecycle apply to all future models, while P4 remains an optional Flash removal/recovery decision, P5 Orcarouter serving/benchmark, P6 Orcarouter/27B transfer, P7 final integrated system release.

| Stage | Objective | Automatic read-only/CPU checks | REAL acceptance gate | Current classification |
| --- | --- | --- | --- | --- |
| **P3-D** | Independent GPU process exclusivity and port 8000 process ownership | Docker complete inventory + `ss -ltnp` port listener + `nvidia-smi` compute-app PIDs + `/proc/<pid>/cgroup` attribution, local active API check | Both GPU and port PID attribution must pass; unavailable tools or docker-proxy outside cgroup are **UNVERIFIED**, not PASS | Source draft only, real DGX pending |
| **P3-E** | Flash-Next canonical runtime/reinstall recipe | Inspect the preserved `qwen38-flash` (current Docker ID + image, command, env, read-only `/hf` mount, GPU/port, P3 provenance); emit **candidate observation**, no recipe promotion | Qualified, versioned Flash runtime recipe and safe reinstall/rollback tested independently on DGX; never auto copy 27B Native Tools flags | Source draft candidate; qualified recipe missing |
| **P3-F** | Repeatable model lifecycle and safe operating executor | Five Python CPU/Fake-DGX suites; existing exact SHA, locks, journal, stop-before-start and rollback code remains release-gated | Production integration, crash/recovery and benchmark pointer/backup cleanup semantics independently accepted; no blind retry | CPU source gate only, not released |
| **P3-G** | General Wizard end-to-end real DGX acceptance | Read-only current-ID operating switch preview, private journal integrity, API identity; no mutation | **Separate authorized** real 27B→Flash→27B, deliberate safe fault test, rollback, postcheck, Wizard UX and persistent evidence, with fresh approval per disruptive action | Preview real DGX PASS in previous observation; actual renewed post-change execution pending |

The automatic single-script D–G runner cannot silently grant downtime/approval. **P3-G cannot become REAL PASS from read-only checks, source-only CI, or a plan SHA.**

## 2. Single command on DGX after fast-forward

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff

# 1. Does not access Docker/GPU/API; prints D-G test and risk contract
bash scripts/temporary/p3-d-g-acceptance.sh --plan

# 2. One command runs CPU/Fake-DGX suites + actual DGX READ-ONLY inspections
bash scripts/temporary/p3-d-g-acceptance.sh --run \
  --report /tmp/blazux-p3-d-g-draft-$(date +%Y%m%dT%H%M%S).json

# Optional CPU-only developer workstation/CI
bash scripts/temporary/p3-d-g-acceptance.sh --cpu-only

# Optional: explicit nonzero exit unless ALL stages have real acceptance.
# Source-only draft always exits nonzero here even if all read-only probes pass.
bash scripts/temporary/p3-d-g-acceptance.sh --run --strict
```

The shell script is a thin wrapper for `python3 -m scripts.manager.p3_dg_acceptance`. It does NOT include `--execute` or an approval flag. No Docker stop/start/run/rm, model download, benchmark, delete, cache writes, journal mutations, or live model changes. `--report` is the only optional local file output; it uses exclusive creation (existing report will not be overwritten). Written reports may include Docker IDs, process PIDs and local host cache paths; inspect before sharing.

The script runs CPU-only suites:
`test_recipe_drift_cpu.py`,
`test_model_lifecycle_cpu.py`,
`test_operational_switch_cpu.py`,
`test_operational_executor_cpu.py`,
`test_p3_dg_acceptance_cpu.py`.
Each yields a PASS/BLOCKED verdict and test count. It **does not** run existing destructive operator trials or P3 A/B/C stages.

## 3. Verdict and exit semantics

| Status | Meaning |
| --- | --- |
| `P3-D.READ_ONLY_PASS` | Docker GPU-exclusive AND host port PID and NVIDIA compute PID provenance actually verified |
| `P3-D.BLOCKED` | Unverified/inconsistent processes, no privileges, unsupported GB10 NVML reporting, unknown Docker ownership, or anomaly |
| `P3-E.DRAFT_REVIEW_REQUIRED` | Preserved Flash runtime was observed and historically qualified, but no canonical reinstall-ready Flash recipe exists |
| `P3-E.READ_ONLY_PASS` | A registered qualified Flash recipe was found and observation checks passed; **not itself proof of reinstall** |
| `P3-F.SOURCE_CPU_PASS_NOT_RELEASED` | All 5 CPU/Fake-DGX regressions passed; no real operating release |
| `P3-G.PREVIEW_PASS_REAL_SWITCH_NOT_RUN` | Current-ID ordinary switch preflight and journal check passed; no transfer/rollback test |
| `overall.DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` | Runner executed, no hard blocker, but real acceptance incomplete |
| `overall.BLOCKED` | At least one read-only or CPU check has a concrete blocker |
| `overall.CPU_ONLY_SOURCE_PASS_NOT_DGX` | CPU-only development run; no DGX observation |
| `acceptance_complete=false` | **Always false** for this draft runner; independent real G acceptance and production release are separate |

Exit 0 means the chosen **non-mutating draft checks completed without a hard blocker** (not P3-D~G completion). Exit 3 denotes a hard blocker or unsatisfied `--strict` acceptance. The full JSON must be inspected for per-stage statuses. A `--strict` run is intentionally nonzero until an independently documented real-G acceptance process exists.

**Important nuance:** `ss` may show `docker-proxy` instead of the model container PID; `nvidia-smi` may omit compute-app rows on the DGX GB10 or hide cgroup provenance. This requires more accurate read-only attribution, not removal of the test. The conservative `P3-D.BLOCKED` result should be treated as **verification pending**, not automatic evidence of a GPU conflict or a malfunctioning vLLM service.

## 4. Rollback, immutable receipts, and promotion criteria

- Do not replay P3-A/B/C: their stage receipts are historic. Existing canonical 27B remains running and validated, port 8000.
- `P3-E` discovery is an **observed candidate**; do not write it directly into `runtimes/service-policy.json.runtime_recipe` or promote without reviewing Docker argv, model revision, image, NVFP4 loader and cache path against the actual pinned repository.
- `P3-F` generic lifecycle `PRODUCTION_LIFECYCLE_RELEASED=False` stays locked. Model removal is an allowed future approved action but never automatic. Do not add permanent no-delete bans.
- `P3-G` execution requires a new separate scoped operator maintenance approval, independent fresh SHA/TTY, stop-before-start, single-model API identity and bounded smoke/benchmark, failure restore, append-only receipts and independent status + journal postcheck. Existing script intentionally lacks this authority.
- Changes to canonical 27B recipe JSON may invalidate existing benchmark-SHA lineage; keep the current SHA immutable unless a separately accepted versioned migration is executed.
- Only after P3-G real acceptance and reviewed source gates may a separate release decision enable daily Wizard operations. It is not enabled by a successful `--run`.

## 5. Transition to P4 / P5 / P6 / P7

Once P3-D–G are accepted under their separate actual-vs-CPU scopes, decide P4: Flash removal/recovery is optional; storage sufficiently available may justify `NOT_APPLICABLE`, leaving Flash preserved for testing. P5 then qualifies Orcarouter on vLLM 0.32, P6 proves Orcarouter ↔ 27B, P7 unifies model/recipe lifecycle, proxy/gateway/service observability and release. **Do not equate phase numbering with unattended permission to mutate the DGX.**
