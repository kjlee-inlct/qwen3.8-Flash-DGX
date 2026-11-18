"""P3-P5 one-command SOURCE/CPU and DGX read-only closure evidence collector.

This is NOT a lifecycle executor, benchmark runner or production acceptance gate.
It reuses existing project validators; never loads/switches/stops/deletes a model,
writes operating Journal state, performs inference, or grants approval.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MAX_OUTPUT = 1_000_000
SHA40 = re.compile(r"^[0-9a-f]{40}$")
_COUNT = re.compile(r"\bRan ([0-9]+) tests? in ")
PYTHON = sys.executable


def tasks_for(mode: str, *, with_p5_asset_hashes: bool = False) -> list[dict]:
    """Explicit, fixed command list; inputs cannot supply command fragments."""
    if mode not in ("cpu-only", "read-only", "plan"):
        raise ValueError("INVALID_MODE")
    if with_p5_asset_hashes and mode != "read-only":
        raise ValueError("P5_ASSET_HASHES_REQUIRES_READ_ONLY")
    if mode == "plan":
        return []
    if mode == "cpu-only":
        return [
            {"name": "p3_dg_cpu", "json": True, "timeout": 1000,
             "cmd": [PYTHON, "-B", "-m", "scripts.manager.p3_dg_acceptance", "--cpu-only"]},
            {"name": "p4_a_cpu", "json": False, "timeout": 180,
             "cmd": [PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests",
                     "-p", "test_p4_a_inventory_cpu.py", "-v"]},
            {"name": "p4_bc_cpu", "json": False, "timeout": 180,
             "cmd": [PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests",
                     "-p", "test_p4_bc_dry_run_cpu.py", "-v"]},
            {"name": "p5_source_cpu", "json": True, "timeout": 400,
             "cmd": [PYTHON, "-B", "-m", "scripts.manager.p5_orcarouter", "--cpu-only", "--json"]},
            {"name": "p5_measurement_cpu", "json": False, "timeout": 180,
             "cmd": [PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests",
                     "-p", "test_model_measurements_cpu.py", "-v"]},
            {"name": "p5_session_cpu", "json": False, "timeout": 180,
             "cmd": [PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests",
                     "-p", "test_benchmark_session_cpu.py", "-v"]},
        ]
    tasks = [
        {"name": "p3_dg_read_only", "json": True, "timeout": 1000,
         "cmd": [PYTHON, "-B", "-m", "scripts.manager.p3_dg_acceptance", "--run"]},
        {"name": "p4_a_bc_read_only", "json": True, "timeout": 240,
         "cmd": [PYTHON, "-B", "-m", "scripts.manager.p4_bc_dry_run", "--json"]},
        {"name": "p5_source_plan", "json": True, "timeout": 60,
         "cmd": [PYTHON, "-B", "-m", "scripts.manager.p5_orcarouter", "--plan", "--json"]},
        {"name": "p5_model_inventory", "json": True, "timeout": 150,
         "cmd": [PYTHON, "-B", "-m", "scripts.manager.model_measurements",
                 "inventory", "--model", "orcarouter", "--summary-only", "--json"]},
        {"name": "p5_benchmark_plan", "json": True, "timeout": 60,
         "cmd": [PYTHON, "-B", "-m", "scripts.manager.model_measurements",
                 "benchmark-plan", "--model", "orcarouter",
                 "--contexts-k", "1,4,8", "--max-output-tokens", "128", "--json"]},
    ]
    if with_p5_asset_hashes:
        tasks.append({"name": "p5_asset_hash_read_only", "json": True, "timeout": 900,
                      "cmd": [PYTHON, "-B", "-m", "scripts.manager.p5_orcarouter",
                              "--read-only", "--json"]})
    return tasks


def _safe_doc(raw: str) -> dict | None:
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_OUTPUT:
        return None
    try:
        doc = json.loads(raw, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, TypeError):
        return None
    return doc if isinstance(doc, dict) else None


def _issues(value) -> list[str]:
    """Report only bounded failure reason codes, never raw host paths or logs."""
    if not isinstance(value, list):
        return []
    codes = []
    for item in value[:20]:
        if not isinstance(item, str) or not re.fullmatch(r"[A-Z0-9_:-]{1,120}", item):
            codes.append("NON_CODE_ISSUE_REDACTED")
        else:
            codes.append(item)
    return codes


def _stage_summary(doc: dict, task_name: str) -> dict:
    summary_keys = ("status", "scope", "stage", "mode", "action",
                    "model", "blocked_stages", "executed",
                    "production_released", "acceptance_complete",
                    "inventory_status")
    summary = {key: doc[key] for key in summary_keys if key in doc}
    summary["issues"] = _issues(doc.get("issues"))
    if task_name == "p3_dg_read_only":
        sections = doc.get("stages")
        if isinstance(sections, dict):
            summary["stages"] = {
                stage: {"status": part.get("status"), "issues": _issues(part.get("issues"))}
                for stage, part in sections.items()
                if stage in ("P3-D", "P3-E", "P3-F", "P3-G") and isinstance(part, dict)
            }
    elif task_name == "p4_a_bc_read_only":
        for key in ("candidate_review", "cleanup_rehearsal"):
            section = doc.get(key)
            if isinstance(section, dict):
                summary[key] = {"status": section.get("status"),
                                "issues": _issues(section.get("issues"))}
    elif task_name == "p5_source_cpu":
        stages = doc.get("stages")
        if isinstance(stages, list):
            for section in stages:
                if isinstance(section, dict) and section.get("gate") == "cpu_fake_dgx":
                    cases = section.get("test_cases")
                    summary["cpu_suite"] = {
                        "status": section.get("status"),
                        "exit_code": section.get("exit_code"),
                        "test_summary": section.get("test_summary"),
                        "parsed_case_count": len(cases) if isinstance(cases, list) else None,
                        "failed_cases": [
                            case.get("case") for case in (cases or [])[:25]
                            if isinstance(case, dict) and case.get("status") != "PASS"
                            and isinstance(case.get("case"), str)
                            and re.fullmatch(r"test_[A-Za-z0-9_]{1,110}", case["case"])
                        ] if isinstance(cases, list) else [],
                        "issues": _issues(section.get("issues")),
                        "failure_detail_available_in_direct_p5_output":
                            section.get("failure_details") is not None,
                    }
                    break
    return summary


def _execute(task: dict, *, runner=subprocess.run) -> dict:
    try:
        result = runner(task["cmd"], cwd=ROOT, capture_output=True, text=True,
                        timeout=task["timeout"], check=False,
                        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return {"task": task["name"], "result": "UNAVAILABLE",
                "reason": type(exc).__name__, "collected": False, "accepted": False}
    out = {"task": task["name"], "returncode": result.returncode,
           "collected": False, "accepted": False}
    if task["json"]:
        doc = _safe_doc(result.stdout)
        if doc is None or not isinstance(doc.get("status"), str):
            return {**out, "result": "INVALID_JSON_RECEIPT"}
        state = doc["status"]
        # Exit=3 can be a legitimate fail-closed observation, not an invalid
        # receipt and never a PASS. Ensure the status/exit combination agrees.
        good = result.returncode == 0 and state in (
            "CPU_ONLY_SOURCE_PASS_NOT_DGX", "PASS",
            "DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED", "READ_ONLY_DRY_RUN_PASS",
            "READ_ONLY_PARTIAL", "READ_ONLY_COMPLETE", "COLLECTED_UNQUALIFIED",
            "PLAN_ONLY_ACK_REQUIRED", "SOURCE_CATALOG_ONLY")
        blocked = result.returncode == 3 and state in (
            "BLOCKED", "FAIL", "INCOMPLETE_MEASUREMENT",
            "READ_ONLY_DRY_RUN_BLOCKED")
        if not (good or blocked):
            return {**out, "result": "INVALID_EXIT_OR_STATUS",
                    "summary": _stage_summary(doc, task["name"])}
        qualified = (good and
                     ((task["name"] == "p3_dg_cpu" and state == "CPU_ONLY_SOURCE_PASS_NOT_DGX")
                      or (task["name"] == "p5_source_cpu" and state == "PASS")
                      or (task["name"] == "p3_dg_read_only"
                          and state == "DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED"
                          and not doc.get("blocked_stages"))
                      or (task["name"] == "p4_a_bc_read_only"
                          and state == "READ_ONLY_DRY_RUN_PASS")
                      or (task["name"] == "p5_model_inventory"
                          and state == "READ_ONLY_COMPLETE")
                      or (task["name"] == "p5_benchmark_plan"
                          and state == "PLAN_ONLY_ACK_REQUIRED")))
        return {**out, "collected": True, "accepted": bool(qualified),
                "result": ("CPU_PASS" if qualified and task["name"].endswith("_cpu") else
                           "OBSERVATION_PASS_NOT_RELEASED" if qualified else
                           "BLOCKED_RECEIPT" if blocked else "PARTIAL_RECEIPT"),
                "expected_non_authorizing_plan":
                    task["name"] == "p5_source_plan" and state == "BLOCKED",
                "summary": _stage_summary(doc, task["name"])}
    log = (result.stdout or "") + "\n" + (result.stderr or "")
    count = _COUNT.findall(log)
    passed = (result.returncode == 0 and len(count) == 1 and
              int(count[0]) > 0 and re.search(r"(?m)^OK\s*$", log) is not None)
    return {**out, "collected": True,
            "result": "CPU_PASS" if passed else "CPU_FAILED_OR_INCOMPLETE",
            "tests": int(count[0]) if len(count) == 1 else 0,
            "accepted": bool(passed)}


def collect(mode: str, *, with_p5_asset_hashes: bool = False,
            runner=subprocess.run) -> dict:
    tasks = tasks_for(mode, with_p5_asset_hashes=with_p5_asset_hashes)
    if mode == "plan":
        return {"schema_version": 1, "action": "p3-p5-closeout", "mode": mode,
                "status": "PLAN_ONLY", "commands_executed": False,
                "operations_enabled": False, "production_released": False,
                "note": "Use --cpu-only or --read-only; neither grants live acceptance."}
    try:
        sha = runner(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                     capture_output=True, timeout=10, check=False)
        status = runner(["git", "status", "--porcelain"], cwd=ROOT, text=True,
                        capture_output=True, timeout=10, check=False)
        head = sha.stdout.strip() if sha.returncode == 0 else None
        head = head if head is not None and SHA40.fullmatch(head) else None
        clean = status.returncode == 0 and not status.stdout.strip()
    except (OSError, ValueError, subprocess.TimeoutExpired):
        head, clean = None, False
    outcomes = [_execute(t, runner=runner) for t in tasks]
    valid_provenance = bool(head and clean)
    cpu_pass = (mode == "cpu-only" and all(r["accepted"] for r in outcomes)
                and valid_provenance)
    observed = (mode == "read-only" and all(r["collected"] for r in outcomes)
                and valid_provenance)
    # A valid blocked P5 source plan is expected but not an acceptance PASS.
    # P3 and P4 actual blocked stages and partial model inventory remain gaps.
    read_only_complete = (observed and all(
        r["accepted"] or r.get("expected_non_authorizing_plan")
        for r in outcomes))
    return {
        "schema_version": 1, "action": "p3-p5-closeout", "mode": mode,
        "status": ("CPU_SELECTED_PASS_NOT_CI" if cpu_pass else
                   "READ_ONLY_COLLECTED_NOT_RELEASED" if read_only_complete else
                   "READ_ONLY_COLLECTED_WITH_GAPS" if observed else
                   "INCOMPLETE_OR_BLOCKED"),
        "source_head": head, "clean_before_run": clean,
        "tasks": outcomes, "commands_executed": True,
        "receipts_collected": sum(bool(r["collected"]) for r in outcomes),
        "task_count": len(outcomes),
        "source_cpu_selected_pass": cpu_pass,
        "read_only_all_receipts_collected": observed,
        "real_model_switch_executed": False, "live_deletion_executed": False,
        "inference_executed": False, "operating_journal_written": False,
        "operations_enabled": False, "production_released": False,
        "actual_p3_p4_p5_complete": False,
        "ci_verified": False,
        "note": "Results are operator-local source/observation receipts, never independent live or CI acceptance.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="P3-P5 source-safe closure collection",
                                     allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--cpu-only", action="store_true")
    modes.add_argument("--read-only", action="store_true")
    parser.add_argument("--with-p5-asset-hashes", action="store_true",
                        help="Explicitly opt in to heavy read-only P5 asset hashing")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    mode = "plan" if args.plan else "cpu-only" if args.cpu_only else "read-only"
    if args.with_p5_asset_hashes and mode != "read-only":
        parser.error("--with-p5-asset-hashes requires --read-only")
    result = collect(mode, with_p5_asset_hashes=args.with_p5_asset_hashes)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.json else None,
                     sort_keys=True))
    return 0 if result["status"] in ("PLAN_ONLY", "CPU_SELECTED_PASS_NOT_CI",
                                      "READ_ONLY_COLLECTED_NOT_RELEASED") else 3


if __name__ == "__main__":
    raise SystemExit(main())
