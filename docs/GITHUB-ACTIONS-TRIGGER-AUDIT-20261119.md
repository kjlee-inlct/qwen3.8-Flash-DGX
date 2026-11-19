# GitHub Actions missing-run audit — 2026-11-19 (source-only)

## 2026-11-19 KST — operator authenticated Actions audit COMPLETE, 9/9 CPU PASS at 178a328

**Evidence origin: operator-provided authenticated terminal stdout from source SHA `178a328c25b1fd8b408f655588229258066cb4df` (not GitHub Actions execution).** The selected test module `tests/test_github_actions_readonly_audit_cpu.py` reported **9/9 tests OK (0.001s), `ACTIONS_CPU_RC=0`**. The CLI receipt reported `audit_evidence_complete=true`, **`AUTH_AUDIT_RC=0`**, workflow ID `406361282`, `workflow_state=active`, `repository_actions_enabled=true`, and endpoint HTTP statuses `workflow=200`, `permissions=200`, `branch_file=200`, `default_file=404`, `runs=200`, `check_runs=200`. `feature_branch_workflow_present=true`; `default_branch_workflow_present=false`. Exact tested SHA `178a328c25b1fd8b408f655588229258066cb4df` had **0 check-runs** and **0 runs in the latest branch-page**, with last listed successful run at old SHA `8b118c8b1ef7079fabe0b4edbc6d8a2860fd98d8` on 2026-11-11 22:00:50 UTC (pull_request). Receipt explicitly says `ci_verified=false`, `mutated_github_or_dgx=false`, `production_released=false`. No new CI run and no production authorization can be inferred from RC0.

**Corrected interpretation:** the source-level exit-code classification fix at `178a328c25b1fd8b408f655588229258066cb4df` is validated by this operator CPU-only execution and authenticated read-only API receipt: an absent `main` workflow file (HTTP 404) is completed negative evidence, not an incomplete lookup. GitHub's workflow is independently observed **ACTIVE**, repository Actions **ENABLED**; missing new CI triggers remain **ROOT_CAUSE_UNVERIFIED**. Current feature path filters cover changed Python and handoff files. Historical feature push + PR runs succeeded on Nov 12 while `main` was unchanged since Nov 2, so lack of a `main` workflow file alone is not an established explanation. The GitHub identity/credential type for later connector-authored commits has not been demonstrated; GitHub `GITHUB_TOKEN` event suppression is a **hypothesis**, not a proven diagnosis.

**Current gates:** `ACTIONS_AUDIT_CPU_OPERATOR_9_OF_9_PASS_AT_178A328 / ACTIONS_AUTH_READONLY_COMPLETE_RC0_AT_178A328 / WORKFLOW_ACTIVE / REPO_ACTIONS_ENABLED / CI_MISSING_ROOT_CAUSE_UNKNOWN / GITHUB_CI_UNVERIFIED / P5D_SELECTED_CPU_OPERATOR_50_OF_50_PASS_AT_08D03B1 / LIVE_PLE_NAT_PROVENANCE_UNQUALIFIED / PRODUCTION_BLOCKED`. Future documentation-only commits do not change which SHA was operator tested.

**Next scoped option (requires separately stated approval):** normal operator-authenticated `git push` to feature branch, with a deliberately safe source-free/no-op commit, to test push-trigger behavior versus previous connector ref updates. This may initiate GitHub Actions and is **not approved or performed by this record**. Keep `main`, PR #1 merge, GitHub Actions settings, DGX model/service, GPU inference, sudo and live Journal unchanged. Alternatively inspect the existing GitHub workflow event/audit trail read-only if available.

---


## 2026-11-19 KST — authenticated operator receipt: active/enabled, default-file absent

The operator ran the opt-in existing-GH-CLI-authenticated **read-only** diagnostic at exact code SHA `863e5b453ee58da39180ea7efefc0901eecfaf44`. The JSON showed `workflow_state="active"`, `repository_actions_enabled=true`, `workflow=200`, `permissions=200`, `branch_file=200`, `default_file=404`, `runs=200`, `check_runs=200`, `exact_sha_check_runs=0`, `exact_sha_runs_in_latest_page=0`; latest listed run remained old `8b118c8` (PR, success, 2026-11-11 22:00:50 UTC). `mutated_github_or_dgx=false`, `ci_verified=false`, `production_released=false`. The submitted `AUTH_AUDIT_RC=3` is caused by a **collector status-code bug**: it required HTTP 200 for `default_file`, although 404 is a conclusive observation that the workflow is absent from `main`. No permission-read failure remains.

This evidence **rules out** a manually disabled workflow and disabled repository-wide Actions as the present causes. It does **not** prove why the more recent branch commits did not create push/PR workflow runs. In particular, the workflow's default-branch absence does not independently explain the previously successful feature push/PR runs (the `main` SHA is unchanged since Nov 2). GitHub documents that workflow-generated `GITHUB_TOKEN` events can suppress new runs, but we have **not** attested the credentials or webhook event associated with these particular GitHub connector branch updates. Do not label the GitHub REST Git-data update path or `GITHUB_TOKEN` as a confirmed root cause. `workflow_dispatch` has a separate default-branch requirement; no dispatch was attempted.

**Source-only fix (pending CPU verification):** `github_actions_readonly_audit.py` now treats 404 for the exact default workflow file as a valid **complete diagnostic** response if all other required endpoints returned HTTP 200 and schema fields are populated (including active/disabled workflow state, Boolean Actions-enabled status, branch-file presence, numeric check-run count and branch-run subset). Adds `audit_evidence_complete` and returns 0 for complete **read-only evidence**, **not CI success**; missing permission, missing fields, malformed or incomplete API responses still return 3. Three CPU-only synthetic cases were added; **not executed yet**. The original six tests **6/6 PASS at 2d8be63** remain historical evidence, not the new-source test result.

**Independent gates:** `ACTIONS_ACTIVE_OBSERVED / ACTIONS_ENABLED_OBSERVED / FEATURE_WORKFLOW_PRESENT / DEFAULT_WORKFLOW_ABSENT / EXACT_SHA_RUN_NOT_OBSERVED / ROOT_CAUSE_UNVERIFIED / NEW_DIAGNOSTIC_CPU_PENDING / CI_VERIFIED_FALSE / PRODUCTION_BLOCKED`.

**Next differential experiment (not authorized by this receipt):** A normal, separately approved operator-authenticated `git push` of a safe no-op branch commit could distinguish previous connector-updated refs from conventional push-event behavior, while preserving Draft PR state. This would intentionally trigger a CI run if trigger policy permits and therefore needs its own approval. Do **not** alter `main`, switch service, dispatch jobs, merge, change Actions settings, or run GPU/PLE tests automatically.

---


## 2026-11-19 KST — operator Actions read-only diagnostic evidence: ACTIVE workflow / permissions HTTP 401

**Operator-provided DGX stdout**, source SHA `2d8be63f7c7899e3e048d2544c9b27f817da7f18` (exact `tested_sha` in the JSON): `test_github_actions_readonly_audit_cpu.py` **6/6 PASS**, 0.000s, `ACTIONS_CPU_RC=0`. Read-only audit printed `finding=NO_MATCHING_RUN_IN_LATEST_BRANCH_PAGE`, `workflow_id=406361282`, `workflow_state=active`, `default_branch_workflow_present=false` (HTTP 404), `feature_branch_workflow_present=true` (HTTP 200), `exact_sha_check_runs=0` (HTTP 200), `exact_sha_runs_in_latest_page=0` (HTTP 200), last run old SHA `8b118c8b1ef7079fabe0b4edbc6d8a2860fd98d8` at 2026-11-11 22:00:50 UTC (event pull_request, success). `permissions` endpoint returned **HTTP 401**; `repository_actions_enabled=null`, **NOT OBSERVED, not false**. Final `ACTIONS_AUDIT_RC=3` reflects one incomplete permissions endpoint, **not a CI failure or DGX service failure**. `mutated_github_or_dgx=false`, `ci_verified=false`, `production_released=false` as reported.

**Evidence classification:** workflow **ACTIVE_OBSERVED**, feature workflow file **PRESENT_OBSERVED**, default branch file **ABSENT_OBSERVED**, exact-source CI/checks **NOT_OBSERVED**, repository Actions permissions **UNVERIFIED_UNAUTHENTICATED_401**, trigger root cause **UNDETERMINED**. A missing workflow on `main` does not alone explain why the earlier feature push/PR workflows executed successfully when `main` was unchanged. A disabled workflow is contradicted by the present `active` observation. Path filters for recent `scripts/manager/**`/`handoff/**` commits are present. GitHub documentation notes that some `GITHUB_TOKEN`-generated events do not trigger workflows, but the credential responsible for these feature branch commits is **not known from the commit identity**; do not declare token suppression as proven.

**Next safe evidence:** With an already-authorized GitHub CLI login and no new token disclosure, optionally run `GH_TOKEN="$(gh auth token)" python3 -B -m scripts.manager.github_actions_readonly_audit --sha "$(git rev-parse HEAD)" --use-gh-token --json` in a current checkout, or inspect GitHub repository Settings → Actions → General (read-only). Neither creates jobs or changes settings. Missing login or HTTP 403 is an evidence gap, not proof disabled. **Do not execute a new workflow, submit a synthetic commit, change `main`, enable Actions, merge the Draft PR or modify real DGX resources without separate authorization.**

**Independent gates:** `SOURCE_IMPLEMENTED / ACTIONS_AUDIT_CPU_OPERATOR_6_OF_6_PASS_AT_2D8BE63 / WORKFLOW_ACTIVE / REPO_ACTIONS_PERMISSION_UNKNOWN_401 / CI_UNVERIFIED / P5D_SELECTED_CPU_50_OF_50_PASS_AT_08D03B1 / PLE_NAT_UNQUALIFIED / PRODUCTION_BLOCKED`. The historical 50/50 P5-D tests and 6/6 new diagnostic CPU tests are separate suites at separate SHA scopes.

---


## Scope and evidence (as-of 2026-11-19 KST)

- Repository: `kjlee-inlct/qwen3.8-Flash-DGX`; feature branch `feature/recipe-wizard-handoff`, Draft PR #1 remains Open/Unmerged.
- Audited starting HEAD: `291f76b49c00e9496358457a9b7f0722ec990c27`, with prior operator-selected P5-D CPU result 50/50 PASS at `08d03b182c3a1be78a698312d1abcb5b2cef571e`.
- Last confirmed successful workflow: push run [43107837772](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/43107837772) and PR run [43108072440](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/43108072440), old SHA `8b118c8b1ef7079fabe0b4edbc6d8a2860fd98d8`, UTC 2026-11-11 21:59/22:00 (Nov 12 KST). No subsequent workflow runs observed in branch-level API listings, and queried newer SHA has zero check-runs and no CI status; no new pass is implied.
- `main` remains `b0aa8b77604139557169387b2fa8386355d8b651` from 2026-11-02; `.github/workflows` on that branch returned 404. Feature branch has `.github/workflows/recipe-manifest-cpu.yml`, workflow ID `406361282`; its `push` and `pull_request` path filters include `scripts/manager/**`, `handoff/**`, `docs/P5-*`, `tests/test_p5_*_cpu.py`, and `tests/test_p5d_live_audit_cpu.py`. New commits changed covered files; the path filters do not by themselves explain the observed absence of new runs.
- The workflow was able to run for push and PR on Nov 12 while the current `main` commit had already been present since Nov 2. **Therefore, absence of the workflow file on `main` alone cannot be a demonstrated root cause for the later loss of push/PR runs.** GitHub's `workflow_dispatch` event has distinct default-branch registration rules; do not conflate them with push/PR.
- GitHub connector cannot read `/actions/workflows/{id}` state or repository `/actions/permissions` configuration through its allowed URL set. **Those settings are NOT_OBSERVED**, not known disabled. Other open hypotheses: manually disabled workflow, repo Actions policy, event-producing credential/suppression, disabled event, GitHub platform behavior. Commit author/committer identity does not prove the token used to update the branch. Neither disabled state nor `GITHUB_TOKEN` suppression is confirmed.

References: [GitHub troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows), [workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), [GITHUB_TOKEN trigger suppression](https://docs.github.com/en/actions/concepts/security/github_token), [read-only workflow state endpoint](https://docs.github.com/en/rest/actions/workflows).

## New bounded read-only diagnostic

Run in an up-to-date source checkout (no sudo, Docker actions, inference, or service mutation):

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only
python3 -B -m unittest discover -s tests -p 'test_github_actions_readonly_audit_cpu.py' -v
python3 -B -m scripts.manager.github_actions_readonly_audit \
  --sha "$(git rev-parse HEAD)" --json
echo "ACTIONS_READONLY_AUDIT_RC=$?"
```

The audit uses only six bounded HTTPS `GET` calls to GitHub's `api.github.com` for the workflow state, repo Actions permissions, workflow file presence on `main` and feature branch, latest branch runs, and HEAD check-runs. It prints statuses, never tokens or raw API bodies, and does not persist a file. It does not need GitHub CLI or request operating credentials. **Exit 3 denotes incomplete HTTP/API visibility** (e.g., permissions endpoint may require authorization), **not a failed CI or DGX service**.

If the operator already has a scoped `GH_TOKEN` in the environment and wishes to inspect private repository configuration, `--use-gh-token` explicitly opts in to its use for the same GitHub GET calls. Do not paste credentials or tokens into logs, chat, or repository. The script never prints them. Never create an extra credential solely for this diagnostic unless separately approved.

## Decision / acceptance boundary

The audit is **SOURCE_IMPLEMENTED / CPU_TEST_NEW_DIAGNOSTIC_NOT_EXECUTED / ACTIONS_STATE_NOT_YET_OBSERVED / CI_UNVERIFIED / OPERATION_AUTHORIZED_FALSE / PRODUCTION_BLOCKED** until operator output is received. Do not edit `main`, change Actions settings, dispatch/re-run jobs, merge PR #1, or run a live DGX audit automatically. Existing P5-D 50/50 CPU selected test receipt remains attached to exact code SHA `08d03b1`, not a CI pass. PLE per-file RSS/PSS and NAT kernel provenance remain blocked independently.

Once the read-only receipt identifies `disabled_manually` or repository `enabled=false`, propose a narrowly scoped remediation for explicit confirmation. If active/enabled yet no runs, compare the user-initiated `git push` event path with connector-generated updates (only with separate authorization for any test push). Preserve Draft/Open/Unmerged PR state.
