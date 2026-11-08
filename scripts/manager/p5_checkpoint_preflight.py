"""One-shot, read-only P5 checkpoint + manifest + CPU regression verdict.

Does not invoke Docker, vLLM, GPU, network, or any Wizard execution route.
Status is SOURCE_ONLY even on success; never implies GPU qualification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from scripts.manager import manifest_registry
from scripts.manager.p5_lm_head_checkpoint_audit import inspect


def evaluate(snapshot: Path, cache: Path, *, with_tests: bool = True) -> dict:
    issues = []
    try:
        manifest = manifest_registry.validate()
        manifest_pass = manifest.get("status") == "PASS"
        if not manifest_pass:
            issues.append("P5_PREFLIGHT_MANIFEST_INVALID")
    except (OSError, ValueError, KeyError, TypeError):
        manifest_pass = False
        issues.append("P5_PREFLIGHT_MANIFEST_EXCEPTION")
    checkpoint = inspect(snapshot, cache)
    if checkpoint.get("status") != "PASS":
        issues.extend(checkpoint.get("issues") or ["P5_PREFLIGHT_CHECKPOINT_BLOCKED"])
    cpu = {"status": "NOT_RUN", "count": None, "executed_on_dgx_gpu": False}
    if with_tests:
        try:
            cmd = [sys.executable, "-B", "-m", "unittest", "discover", "-s",
                   "tests", "-p", "test_p5_*_cpu.py", "-v"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True,
                                    check=False, timeout=900)
            summary = re.findall(r"Ran (\d+) tests?", result.stderr[-5000:])
            cpu = {
                "status": "PASS" if result.returncode == 0 and summary else "BLOCKED",
                "count": int(summary[-1]) if summary else None,
                "exit_code": result.returncode,
                "executed_on_dgx_gpu": False,
            }
            if cpu["status"] != "PASS":
                issues.append("P5_PREFLIGHT_CPU_TESTS_FAILED")
        except (OSError, ValueError, subprocess.TimeoutExpired):
            issues.append("P5_PREFLIGHT_CPU_TESTS_EXECUTION_FAILED")
            cpu["status"] = "BLOCKED"
    return {
        "status": "PASS_SOURCE_ONLY" if not issues else "BLOCKED",
        "issues": sorted(set(issues)),
        "manifest": "PASS" if manifest_pass else "BLOCKED",
        "checkpoint": checkpoint,
        "cpu_tests": cpu,
        "gpu_verified": False,
        "api_verified": False,
        "image_built": False,
        "executed": False,
        "service_mutated": False,
        "hf_cache_mutated": False,
        "approval_generated": False,
        "production_released": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--skip-tests", action="store_true",
                        help="Use for metadata-only diagnostics")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    from scripts.manager.p5_live_trial import CACHE, SNAPSHOT
    result = evaluate(args.snapshot or SNAPSHOT, args.cache_root or CACHE,
                      with_tests=not args.skip_tests)
    print(json.dumps(result, indent=2 if args.json else None, sort_keys=True))
    return 0 if result["status"] == "PASS_SOURCE_ONLY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
