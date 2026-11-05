# Handoff changelog (append-only)

## 2026-11-05 — H-008 — P1 Wizard code batch and operator build/download evidence

- Operator-provided DGX log: Docker image `qwen38-flash-dgx:v0.32` built (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`), port :8000 free at earlier read-only scan, model download 9/25 = 36% in last visible line. OpenWebUI/Portainer kept running. Shell has queued `serve/wait/test` after `./flash setup default`.
- Added `scripts/manager/p1_assets.py` (read-only shard/index/cache/image integrity), `p1_wizard.py` (guarded actions, approval plan hashes, API smoke, immutable JSON evidence), `p1_bench.py` (bounded streaming TTFT/latency/tokens), `wizard/p1.sh` (guided and noninteractive), isolated mock CPU tests and GitHub Actions coverage.
- First source commit `c625a49276272e90d19ab6367f580a0230754890` applied; two GitHub Actions runs SUCCESS with 80/80 CPU tests each (41 new P1 + 39 baseline). No assistant-executed Docker, HF cache, GPU or API action. P1 runtime remains `NOT_RUN`. Do not start a duplicate download or interfere with existing operator setup.


## 2026-11-05 — H-007 — User reports NVIDIA Flash-Next checkpoint download in progress

- At 11:46 KST user reports `nvidia/Qwen3.8-Flash-Next-NVFP4` download is **still running**. This is USER_REPORTED, not independently inspected on DGX. Completion percentage, cache path, revision and storage remaining unknown.
- Recorded `DOWNLOAD_IN_PROGRESS` in CURRENT-STATE, priority guard in NEXT-ACTIONS and E-20261105-04 in evidence ledger. `DOWNLOAD_COMPLETE`, `HYBRID_READY`, GPU, API and benchmarks remain **NOT_VERIFIED / NOT_RUN**.
- Do not launch a competing download, `./flash setup default` or hybrid preparation while it may modify active weights/cache. P1 Wizard code and synthetic CPU tests can proceed while assets download.
- GitHub documentation change only: no Docker, image, download, cache or GPU operations performed by this session.

## 2026-11-05 — H-006 — Confirm all P1–P7 stages must be Wizard-driven

- User explicitly confirmed exact sequential target: Wizard Flash-Next install/run/bench → Wizard 27B install/run/bench → Wizard Flash-Next ↔ 27B switching → optional approved Flash-Next cleanup if storage insufficient → Wizard Orcarouter-Flash-Next install/run/bench → Wizard Orcarouter ↔ 27B switching → integrated Wizard operations release.
- Clarified `P4=SKIPPED_NOT_NEEDED` when disk allows; no automatic deletion. External port :8000 is the desired stable API entrypoint; actual DGX occupancy and activation remain NOT_OBSERVED.
- Promoted the sequence into `handoff/README.md`, `OPERATING-RULES.md`, `NEXT-ACTIONS.md`, `CURRENT-STATE.md`, `DECISIONS.md`, `SESSION-START-PROMPT.md` and master plan. First unfinished implementation remains **P1 Wizard end-to-end**, not merely manual `flash serve`.
- Documentation-only GitHub commit; no DGX, GPU, Docker operations, benchmark, deletion or model switch. Previously verified code HEAD `017319a`: 39/39 CPU tests in each of two successful GitHub Actions runs; recheck new commit checks separately.

## 2026-11-05 — H-005 — Restore executable bits and record CI failure

- Commit `7e8f4a109a04c130a5dba0d73e3ece0881d85478` had a real **CI FAIL**: manifest 15/15 PASS; inventory 10/10 PASS; shell launcher 9/13 PASS and 4/13 FAIL, exit 126 because `flash`/`scripts/serve.sh` lost executable permissions in GitHub tree update.
- Restored executable mode `100755` for both scripts; added a CPU regression test asserting launch scripts are executable and `bash -n` workflow checks. Rerun CI on new HEAD; preserve failed evidence instead of rewriting.
- No DGX, Docker runtime, GPU, API port or model state changed.

## 2026-11-05 — H-004 — Flash-Next on legacy :8000 and source-safe inventory

- User reports previous operating services deleted; current Docker/ports/images/weights on DGX **NOT OBSERVED**. Do not treat past Orcarouter container or model ID as current deployment state.
- Updated `flash`, `profiles/default.env`, `scripts/serve.sh` so NVIDIA Flash-Next default profile exposes host port 8000 and served name `qwen3.8-flash-next`. The upstream profile continues Hybrid+YaRN+MTP2; no SGLang.
- Replaced implicit `docker rm -f "$NAME"` with refusal to replace any existing exact Docker container name. No automatic removal on failed launch.
- Removed historical hard-coded 8000/name manifest bans. Added `scripts/manager/inventory.py` (read-only Docker/ss/disk/cache/mount reconciliation), Wizard `00-doctor.sh`/`10-plan.sh` wrappers, deterministic synthetic CPU tests, CI workflow coverage.
- This commit is SOURCE-only; tests CI verification to follow actual commit. No DGX GPU, cache mutations, download, Docker actions or API benchmark. Updated rules, decisions, contracts and runbook.

## 2026-11-04 — H-003 — N1 source-only manifest validation

- Added YAML recipe JSON Schema Draft 2020-12, CPU-only validator, pinned SHA/digest constraints, historical protected name/port denial, no approval bypass.
- Added deliberately invalid 27B candidate, synthetic fixture, 15 isolated CPU tests and new GitHub Actions CPU workflow. No Docker, GPU, actual DGX or model/cache/port changes.
- Ran: python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -q -> **15/15 PASS**; 27B candidate -> expected FAIL (exit 2); synthetic fixture -> schema PASS (exit 0) with launch_authorized=false.
- Updated CURRENT-STATE, NEXT-ACTIONS, EVIDENCE-LEDGER, DECISIONS and planning contracts. Draft PR #1 still requires CI readback and review; N2 and all operational testing remain outstanding.

## 2026-11-04 — H-002 — Documentation committed and draft PR opened

- Verified the new planning branch was 1 commit ahead of `main`, 10 tracked doc files, all under `docs/` and `handoff/`.
- Commit `76cd8dae16b0f34e47c353b56b6e9dbcc5fcde25` created the initial document set.
- Opened [Draft PR #1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1); no merge. At original commit check, GitHub showed 0 check-runs/0 PR workflow runs; **not CI PASS**.
- Corrected illustrative 27B recipe to keep PLE semantics `UNVERIFIED_FOR_27B` rather than assuming no PLE; still no runtime/CPU tests.
- Updated live handoff state, next actions and evidence. All work was GitHub-only.

## 2026-11-04 — H-001 — Recipe/Wizard migration planning initialized

- Confirmed user preference: **vLLM 0.32 only**, no SGLang, one large target at a time by default.
- Created planning branch `feature/recipe-wizard-handoff` from fork `main@b0aa8b77604139557169387b2fa8386355d8b651`.
- Preserved parallel `feature/orcarouter-bf16-adapter` design branch.
- Defined P0→P7 roadmap, manifest separation, wizard steps, protected runtime boundaries, gated checkpoint deletion and switch/rollback semantics.
- Added a standard entrypoint, living current state, evidence ledger, decisions, next tasks and new-conversation prompt under `handoff/`.
- **Tests:** documentation/source review only. No new CPU/CI/GPU/benchmark runs; no Docker, HF weights, model or service changes.
- PR/CI state should be read from GitHub; do not infer a merge.

## Future entry template

`YYYY-MM-DD — H-NNN — Subject`: exact changes, files, branch/commit, PR, test outcomes, external effects, remaining blockers. Newer entries should be placed **above** older entries while preserving them.
