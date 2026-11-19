# GitHub Actions missing-run audit — 2026-11-19 (source-only)

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
