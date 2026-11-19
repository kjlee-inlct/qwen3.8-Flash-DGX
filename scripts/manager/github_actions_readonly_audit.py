"""Read-only, source-only GitHub Actions trigger receipt (stdlib; no writes).

Calls a fixed set of GitHub REST GET endpoints. No service/GPU/Docker actions.
Optional GH_TOKEN is used ONLY when explicitly requested; never printed.
Exit 3 means partial evidence, not a service or CI failure.
Exit 0 means complete diagnostic fields, not that CI ran or passed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

_REPO = "kjlee-inlct/qwen3.8-Flash-DGX"
_BRANCH = "feature/recipe-wizard-handoff"
_WORKFLOW = 406361282
_MAX_BYTES = 512 * 1024
_SHA = re.compile(r"[0-9a-f]{40}\Z")
_REPO_NAME = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_BRANCH_NAME = re.compile(r"[A-Za-z0-9_.\-/]+\Z")


def _get_json(path, *, token=None, opener=urlopen):
    """Return only status and bounded parsed JSON; never log URL credentials."""
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "blazux-source-only-actions-audit",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request("https://api.github.com" + path, headers=headers,
                      method="GET")
    try:
        with opener(request, timeout=8) as response:
            raw = response.read(_MAX_BYTES + 1)
            status = response.status
        if len(raw) > _MAX_BYTES:
            return {"http_status": status, "data": None, "issue": "RESPONSE_SIZE_LIMIT"}
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            return {"http_status": status, "data": None, "issue": "JSON_OBJECT_REQUIRED"}
        return {"http_status": status, "data": data}
    except HTTPError as exc:
        return {"http_status": exc.code, "data": None, "issue": "HTTP_UNAVAILABLE"}
    except (URLError, TimeoutError, OSError, ValueError, UnicodeError):
        return {"http_status": None, "data": None, "issue": "REQUEST_UNAVAILABLE"}


def _evidence_complete(receipt):
    """HTTP 404 for an absent default-branch file is a conclusive observation.

    Complete diagnostics do not constitute CI success or production approval.
    """
    http = receipt.get("endpoint_http_status")
    if not isinstance(http, dict):
        return False
    required = ("workflow", "permissions", "branch_file", "runs", "check_runs")
    return (
        all(http.get(key) == 200 for key in required)
        and http.get("default_file") in (200, 404)
        and isinstance(receipt.get("workflow_state"), str)
        and bool(receipt["workflow_state"])
        and type(receipt.get("repository_actions_enabled")) is bool
        and receipt.get("feature_branch_workflow_present") is True
        and type(receipt.get("default_branch_workflow_present")) is bool
        and type(receipt.get("exact_sha_runs_in_latest_page")) is int
        and receipt["exact_sha_runs_in_latest_page"] >= 0
        and type(receipt.get("exact_sha_check_runs")) is int
        and receipt["exact_sha_check_runs"] >= 0
    )


def collect(*, repo=_REPO, branch=_BRANCH, sha, workflow_id=_WORKFLOW,
            token=None, fetch=_get_json):
    """Never infer a passing CI result from absent runs or a workflow declaration."""
    if not _REPO_NAME.fullmatch(repo):
        raise ValueError("invalid repository name")
    if not _BRANCH_NAME.fullmatch(branch) or ".." in branch or branch.startswith("/"):
        raise ValueError("invalid branch name")
    if not _SHA.fullmatch(sha):
        raise ValueError("expected a full 40-character lowercase commit SHA")
    if type(workflow_id) is not int or workflow_id < 1:
        raise ValueError("invalid workflow id")

    root = "/repos/" + repo
    encoded_branch = quote(branch, safe="")
    paths = {
        "workflow": f"{root}/actions/workflows/{workflow_id}",
        "permissions": f"{root}/actions/permissions",
        "default_file": f"{root}/contents/.github/workflows/recipe-manifest-cpu.yml?ref=main",
        "branch_file": f"{root}/contents/.github/workflows/recipe-manifest-cpu.yml?ref={encoded_branch}",
        "runs": f"{root}/actions/runs?branch={encoded_branch}&per_page=10",
        "check_runs": f"{root}/commits/{sha}/check-runs?per_page=10",
    }
    evidence = {key: fetch(path, token=token) for key, path in paths.items()}
    workflow = evidence["workflow"].get("data") or {}
    permissions = evidence["permissions"].get("data") or {}
    runs = evidence["runs"].get("data") or {}
    checks = evidence["check_runs"].get("data") or {}
    raw_runs = runs.get("workflow_runs", [])
    run_rows = raw_runs if isinstance(raw_runs, list) else []
    exact = [item for item in run_rows if
             isinstance(item, dict) and item.get("head_sha") == sha]
    recent = next((item for item in run_rows if isinstance(item, dict)), {})

    state = workflow.get("state") if isinstance(workflow.get("state"), str) else None
    enabled = permissions.get("enabled") if type(permissions.get("enabled")) is bool else None
    if state and state.startswith("disabled"):
        finding = "WORKFLOW_DISABLED_OBSERVED"
    elif enabled is False:
        finding = "REPOSITORY_ACTIONS_DISABLED_OBSERVED"
    elif exact:
        finding = "WORKFLOW_RUN_OBSERVED_NOT_CI_ATTESTED"
    elif evidence["runs"].get("data") is not None:
        finding = "NO_MATCHING_RUN_IN_LATEST_BRANCH_PAGE"
    else:
        finding = "INCOMPLETE_API_EVIDENCE"

    def present(key):
        code = evidence[key].get("http_status")
        if code == 200:
            return True
        if code == 404:
            return False
        return None

    receipt = {
        "action": "github-actions-readonly-diagnosis",
        "repo": repo, "branch": branch, "tested_sha": sha,
        "workflow_id": workflow_id,
        "finding": finding,
        "workflow_state": state,
        "repository_actions_enabled": enabled,
        "default_branch_workflow_present": present("default_file"),
        "feature_branch_workflow_present": present("branch_file"),
        "exact_sha_runs_in_latest_page": len(exact) if evidence["runs"].get("data") is not None else None,
        "exact_sha_check_runs": checks.get("total_count") if type(checks.get("total_count")) is int else None,
        "last_branch_run": {k: recent.get(k) for k in
                            ("head_sha", "created_at", "event", "status", "conclusion")} if recent else None,
        "endpoint_http_status": {key: evidence[key].get("http_status") for key in paths},
        "read_only": True, "mutated_github_or_dgx": False,
        "ci_verified": False, "production_released": False,
        "note": ("Latest-page run count is not exhaustive history. HTTP 401/403/404 on "
                 "Actions permissions is not proof that Actions are disabled. "
                 "The result never authorizes service or repository settings changes.")
    }
    receipt["audit_evidence_complete"] = _evidence_complete(receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--repo", default=_REPO)
    parser.add_argument("--branch", default=_BRANCH)
    parser.add_argument("--workflow-id", type=int, default=_WORKFLOW)
    parser.add_argument("--use-gh-token", action="store_true",
                        help="Explicitly use GH_TOKEN (read-only requests; value never printed)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    token = os.environ.get("GH_TOKEN") if args.use_gh_token else None
    if args.use_gh_token and not token:
        print(json.dumps({"status": "BLOCKED", "issue": "GH_TOKEN_NOT_SET"}))
        return 3
    try:
        result = collect(repo=args.repo, branch=args.branch, sha=args.sha,
                         workflow_id=args.workflow_id, token=token)
    except ValueError:
        print(json.dumps({"status": "BLOCKED", "issue": "INVALID_AUDIT_SCOPE"}))
        return 3
    print(json.dumps(result, indent=2, sort_keys=True))
    # RC0 means complete read-only observation, NEVER CI PASS.
    return 0 if result.get("audit_evidence_complete") is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
