"""Opt-in DGX P1 post-download inspection, approved GPU checks and evidence pack.

Never performs git pull/setup/download/serve/stop/cleanup or background work.
Run ONLY after the operator's original setup/serve/wait/test chain ends.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
BRANCH = "feature/recipe-wizard-handoff"
WIZARD = ("./wizard.sh", "model", "flash-next")
CHECKS = (
    ("branch", ("git", "branch", "--show-current")),
    ("head", ("git", "rev-parse", "HEAD")),
    ("tracked_changes", ("git", "status", "--porcelain", "--untracked-files=no")),
    ("catalog", ("./wizard.sh", "list", "--json")),
    ("doctor", ("bash", "wizard/00-doctor.sh")),
    ("inventory_plan", ("bash", "wizard/10-plan.sh")),
    ("containers", ("docker", "ps", "-a", "--format",
                    "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}")),
    ("gpu", ("nvidia-smi",)),
    ("disk", ("df", "-h", ".")),
    ("health", ("curl", "-fsS", "--max-time", "8", "http://127.0.0.1:8000/health")),
    ("models", ("curl", "-fsS", "--max-time", "8", "http://127.0.0.1:8000/v1/models")),
    ("status", (*WIZARD, "status", "--json")),
    ("cache_diagnosis", ("python3", "-m",
                         "scripts.temporary.p1_cache_diagnosis")),
)
ACTIVE_MARKERS = (
    "./flash setup ", "bash flash setup ", "scripts/download-weights.sh",
    "scripts/prepare-hybrid.sh", "./flash serve ", "./flash wait",
    "./flash test ", "scripts/serve.sh",
)


def call(args, *, runner=subprocess.run, timeout=90):
    """Bounded argv-only subprocess; return code and output are preserved."""
    try:
        r = runner(list(args), cwd=ROOT, capture_output=True, text=True,
                   check=False, timeout=timeout)
        out, err = r.stdout or "", r.stderr or ""
        return {"argv": list(args), "returncode": r.returncode,
                "stdout": out[:65536], "stderr": err[:65536],
                "truncated": len(out) > 65536 or len(err) > 65536}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"argv": list(args), "returncode": None, "stdout": "", "stderr": "",
                "error_type": type(exc).__name__}


def busy(*, runner=subprocess.run):
    info = call(("ps", "-eo", "pid=,args="), runner=runner, timeout=10)
    if info["returncode"] != 0 or info.get("truncated"):
        return {"blocked": True, "reason": "process_inspection_unavailable"}
    pids = []
    for line in info["stdout"].splitlines():
        part = line.strip().split(maxsplit=1)
        if len(part) != 2 or not part[0].isdigit():
            continue
        pid = int(part[0])
        if pid not in (os.getpid(), os.getppid()) and any(
                marker in part[1] for marker in ACTIVE_MARKERS):
            pids.append(pid)
    return {"blocked": bool(pids), "reason": "operator_setup_or_test_active" if pids else None,
            "matching_process_count": len(pids)}


def plan(action, *, runner=subprocess.run, requests=3, max_tokens=64, seed=1234):
    argv = [*WIZARD, "plan", "--for-action", action, "--json"]
    if action == "benchmark":
        argv += ["--requests", str(requests), "--max-tokens", str(max_tokens),
                 "--seed", str(seed)]
    result = call(argv, runner=runner, timeout=50)
    try:
        data = json.loads(result["stdout"])
        if not isinstance(data, dict):
            raise ValueError("invalid plan")
    except (ValueError, TypeError):
        data = {"status": "BLOCKED", "issues": ["plan_json_unavailable"]}
    good = (result["returncode"] == 0 and data.get("action") == action and
            data.get("status") == "READY_TO_REQUEST_APPROVAL" and
            isinstance(data.get("plan_id"), str) and
            bool(re.fullmatch("[0-9a-f]{64}", data["plan_id"])))
    return {"command": result, "plan": data, "ready": bool(good)}


def consent(action, plan_id, *, value=None, interactive=False, input_fn=input):
    if value is not None:
        return value == plan_id
    if not interactive:
        return False
    print(f"APPROVAL REQUIRED — {action}: {plan_id}", flush=True)
    try:
        return input_fn("Full plan_id (Enter cancels): ").strip() == plan_id
    except (EOFError, KeyboardInterrupt):
        return False


def perform(action, plan_id, *, runner=subprocess.run,
            requests=3, max_tokens=64, seed=1234):
    args = [*WIZARD, action, "--execute", "--approve-plan", plan_id, "--json"]
    if action == "benchmark":
        args += ["--requests", str(requests), "--max-tokens", str(max_tokens),
                 "--seed", str(seed)]
    # Wizard validates current host state AGAIN before every real invocation.
    return call(args, runner=runner,
                timeout=500 if action == "verify" else 1800)


def session(*, runner=subprocess.run, input_fn=input, interactive=False,
            inspect_only=False, approve_verify=None, approve_benchmark=None,
            requests=3, max_tokens=64, seed=1234):
    """Phases: inspect -> individually approved verify/benchmark -> evidence."""
    checks = {key: call(argv, runner=runner, timeout=65)
              for key, argv in CHECKS}
    activity = busy(runner=runner)
    clean = checks["tracked_changes"]["returncode"] == 0 and not checks["tracked_changes"]["stdout"].strip()
    branch = checks["branch"]["returncode"] == 0 and checks["branch"]["stdout"].strip() == BRANCH
    allowed = bool(clean and branch and not activity["blocked"])
    plans, actions = {}, {}
    for action in ("verify", "benchmark"):
        info = plan(action, runner=runner, requests=requests,
                    max_tokens=max_tokens, seed=seed)
        plans[action] = info
        actions[action] = {"status": "BLOCKED", "executed": False}
        if inspect_only or not allowed or not info["ready"]:
            actions[action]["reason"] = (
                "inspection_only" if inspect_only
                else "branch_worktree_or_operator_process_blocked" if not allowed
                else "wizard_plan_not_ready"
            )
            continue
        selected = approve_verify if action == "verify" else approve_benchmark
        if not consent(action, info["plan"]["plan_id"], value=selected,
                       interactive=interactive, input_fn=input_fn):
            actions[action]["reason"] = "independent_operator_approval_missing"
            continue
        if action == "benchmark" and actions["verify"]["status"] != "PASS":
            actions[action]["reason"] = "verification_not_passed"
            continue
        if busy(runner=runner)["blocked"]:
            actions[action]["reason"] = "operator_work_started_after_preflight"
            continue
        result = perform(action, info["plan"]["plan_id"], runner=runner,
                         requests=requests, max_tokens=max_tokens, seed=seed)
        actions[action] = {"status": "FAIL", "executed": True, "command": result}
        if result["returncode"] == 0:
            try:
                parsed = json.loads(result["stdout"])
                if isinstance(parsed, dict):
                    actions[action]["wizard_result"] = parsed
                    actions[action]["status"] = parsed.get("status", "FAIL")
            except (ValueError, TypeError):
                pass
    return {"schema_version": 1, "stage": "P1",
            "preflight": {"expected_branch": BRANCH, "branch_ok": branch,
                          "tracked_tree_clean": clean,
                          "operator_process": activity, "runtime_allowed": allowed},
            "checks": checks, "plans": plans, "actions": actions,
            "scope": "DGX_INSPECTION_AND_EXPLICITLY_APPROVED_API"}



def cache_diagnosis_summary(checks):
    """A missing, failed or truncated optional diagnostic must never break a report."""
    check = checks.get("cache_diagnosis", {})
    if check.get("returncode") != 0 or check.get("truncated"):
        return {"status": "UNAVAILABLE"}
    try:
        value = json.loads(check["stdout"])
        if isinstance(value, dict) and value.get("type") == "P1_READ_ONLY_CACHE_DIAGNOSIS":
            return value
    except (KeyError, TypeError, ValueError):
        pass
    return {"status": "UNAVAILABLE"}


def api_model_ids(checks):
    """Extract only public model IDs, never raw API response or credentials."""
    check = checks.get("models", {})
    if check.get("returncode") != 0 or check.get("truncated"):
        return []
    try:
        payload = json.loads(check["stdout"])
        entries = payload.get("data", [])
        if not isinstance(entries, list):
            return []
        return [item["id"] for item in entries[:8]
                if isinstance(item, dict) and isinstance(item.get("id"), str)
                and len(item["id"]) <= 256]
    except (TypeError, KeyError, ValueError):
        return []


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inspect-only", action="store_true")
    ap.add_argument("--approve-verify", help="fresh complete SHA-256 verify plan_id")
    ap.add_argument("--approve-benchmark", help="fresh complete SHA-256 bench plan_id")
    ap.add_argument("--requests", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=64)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--report-root", type=Path, default=Path.home() / "blazux-p1-reports")
    ns = ap.parse_args(argv)
    if not (1 <= ns.requests <= 20 and 1 <= ns.max_tokens <= 256 and 0 <= ns.seed <= 2**31 - 1):
        ap.error("unsafe benchmark settings")
    if ns.inspect_only and (ns.approve_verify or ns.approve_benchmark):
        ap.error("inspect-only cannot include action approvals")
    root = ns.report_root.expanduser().resolve()
    cache = Path(os.environ.get("HF_CACHE", str(Path.home() / ".cache/huggingface"))).expanduser().resolve()
    if root.is_relative_to(ROOT.resolve()) or root.is_relative_to(cache):
        ap.error("report root must be outside Git and HF model cache")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    report = root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
    report.mkdir(mode=0o700)
    print("REPORT_DIR=" + str(report), flush=True)
    result = session(interactive=sys.stdin.isatty() and not ns.inspect_only,
                     inspect_only=ns.inspect_only,
                     approve_verify=ns.approve_verify,
                     approve_benchmark=ns.approve_benchmark,
                     requests=ns.requests, max_tokens=ns.max_tokens, seed=ns.seed)
    result["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    path = report / "result.json"
    with path.open("x", encoding="utf-8") as file:
        json.dump(result, file, indent=2, sort_keys=True, ensure_ascii=False)
        file.write("\n")
    path.chmod(0o600)
    print(json.dumps({
        "result_file": str(path), "preflight": result["preflight"],
        "checks": {k: v["returncode"] for k, v in result["checks"].items()},
        "plans": {k: {"ready": v["ready"],
                       "issues": v["plan"].get("issues", [])}
                  for k, v in result["plans"].items()},
        "cache_diagnosis": cache_diagnosis_summary(result.get("checks", {})),
        "api_model_ids": api_model_ids(result.get("checks", {})),
        "actions": {k: {"status": v["status"], "reason": v.get("reason"),
                        "evidence": (v.get("wizard_result") or {}).get("evidence")}
                    for k, v in result["actions"].items()},
    }, indent=2, sort_keys=True))
    if ns.inspect_only:
        return 0
    return 0 if all(x["status"] == "PASS" for x in result["actions"].values()) else 3


if __name__ == "__main__":
    raise SystemExit(main())
