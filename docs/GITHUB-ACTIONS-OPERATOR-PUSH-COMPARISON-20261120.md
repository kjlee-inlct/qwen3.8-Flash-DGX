# GitHub Actions operator-push comparison — 2026-11-20 KST

## Decision: document and park; do not block P5-D source development

- Repository: `kjlee-inlct/qwen3.8-Flash-DGX`
- Feature branch: `feature/recipe-wizard-handoff`
- Draft PR: [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1), Open / Unmerged
- Approved experimental base: `c5b05b0a7bb453fa21757f101061d7c280afb919`
- Operator-created and pushed probe: `2b97762a9da9287d4e111a8e86fd8cc5089ab496`
- Single changed path: `handoff/CI-TRIGGER-COMPARISON-20261119.md` (12 insertions; matches both `on.push.paths` and `on.pull_request.paths`)
- Operator-reported transport: HTTPS; operator-declared credential type: `gh-oauth`. **Credential type was not independently attested.**
- Operator terminal receipt: `PUSH_RC=0`; original `c5b05b0` -> new `2b97762`; bounded post-push observation returned `push_run_id=null`, `pr_run_id=null`, `runs=[]`, `ci_verified=false`.

## Independent GitHub connector cross-check (2026-11-20 KST)

1. PR #1 HEAD is exactly `2b97762a9da9287d4e111a8e86fd8cc5089ab496`, still Draft/Open/Unmerged. The remote commit changes only `handoff/CI-TRIGGER-COMPARISON-20261119.md`.
2. `GET /actions/runs?head_sha=2b97762a9da9287d4e111a8e86fd8cc5089ab496` returned `total_count=0`. `GET /commits/<sha>/check-runs` returned `total_count=0`; connector commit-to-workflow lookup returned no PR workflow runs.
3. Branch/global Actions history still lists 1,640 runs and the newest visible successful pair as [Push 43107837772](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/43107837772) and [PR 43108072440](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/43108072440), at old SHA `8b118c8b1ef7079fabe0b4edbc6d8a2860fd98d8`, 2026-11-11 21:59/22:00 UTC.
4. Workflow `.github/workflows/recipe-manifest-cpu.yml` is present on the feature branch, with both `push` and `pull_request` filters including `handoff/**`. The workflow directory is absent from `main` (HTTP 404). Historical feature-branch Push/PR runs occurred with that same default-branch absence, so it is not an established explanation for missing new Push/PR runs.
5. A previous operator HTTPS Git Push probe `93473eda06769614ef259a1ab6acdc6e9db13b4b` on 2026-11-18 also showed no new runs. See [earlier zero-run incident analysis](GITHUB-ACTIONS-NO-RUN-INVESTIGATION-20261118.md). Four older orphaned queued/zero-job run IDs (43096807109, 43096812698, 43097090510, 43097097266) were recorded separately; their possible platform-incident relationship is **unconfirmed**.
6. Prior authenticated **read-only operator receipt** recorded `workflow_state=active`, `repository_actions_enabled=true`, HTTP 200 for workflow/permissions/feature-file/runs/checks and 404 for the default-branch file. This is historical operator evidence, **not a new permissions query made in this cross-check**. The connector disallows the workflow state and repository Actions permissions endpoints.

## Interpretation and gates

**Reproduced**: a normal local `git push` can succeed while no new Actions Run or Check Run is observed. This excludes a *connector-only Git-data write path* as a sufficient diagnosis. It does **not** independently prove the push credential, GitHub event delivery, platform policy, or a single root cause. Absence of a run is not a test failure; conversely no CPU or CI PASS can be inferred for `2b97762` or a later SHA.

- `OPERATOR_PUSH_PASS / ACTIONS_PUSH_RUN_NOT_OBSERVED / ACTIONS_PR_RUN_NOT_OBSERVED`
- `ROOT_CAUSE_UNVERIFIED / GITHUB_CI_UNVERIFIED`
- `P5D_SOURCE_DEVELOPMENT_APPROVED / CPU_FAKE_DGX_REGRESSION_REQUIRED`
- `WIZARD_MANIFEST_CONTRACTS_REQUIRED / DGX_RUNTIME_NOT_AUTHORIZED`
- `OPERATING_JOURNAL_MUTATION_BLOCKED / PR_MERGE_BLOCKED / PRODUCTION_RELEASE_BLOCKED`

**Execution decision:** stop repeated trigger-probe commits and move Actions triage to an independent tracked follow-up. Preserve existing evidence and inspect repository Actions UI/account restrictions, GitHub Support/event delivery, and the orphaned jobs **read-only** when practical. Do not change `main`, workflow settings or policies, dispatch/rerun jobs, or merge the PR without fresh authorization. This issue **does not gate source-only P5-D development** but does gate claims of exact-HEAD CI acceptance and Production Release.

P5-D priority: read-only PLE file RSS/PSS + inode/PID mapping and Docker NAT port-owner evidence with explicit absence/permission/staleness classifications. Preserve the shared Wizard routes, registry/manifest validation, negative fail-closed CPU/Fake-DGX fixtures, and SHA-bound test results. Never promote source-only matching evidence to live production qualification.
