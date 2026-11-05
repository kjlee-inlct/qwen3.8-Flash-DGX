# Handoff changelog (append-only)

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
