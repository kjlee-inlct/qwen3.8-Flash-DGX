"""P3 experimental two-cycle Flash-Next->27B->Flash-Next acceptance trial.

NOT a persistent model switch. Uses P2's exact-approved one-shot executor
for each cycle; every cycle must restore the original before the next.
No executable plan until a successful actual P2 benchmark receipt exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import time
from typing import Any

from scripts.manager import p2_27b_gpu_trial as trial
from scripts.manager.service_status import inspect_live_status

CYCLES = 2
VERSION = "p3-two-roundtrips-v1"
EVIDENCE_ROOT = Path.home() / ".local/state/blazux-wizard/p2"


def latest_p2_benchmark(root: Path = EVIDENCE_ROOT):
    try:
        candidates = sorted(root.glob("*.benchmark.json"), reverse=True)
        if not candidates:
            return None, "P2_BENCHMARK_RECEIPT_NOT_FOUND"
        # The newest receipt is authoritative: do not skip a newer failure
        # to silently reuse a successful stale record.
        path = candidates[0]
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
            return None, "P2_BENCHMARK_RECEIPT_UNTRUSTED"
        if not path.resolve().is_relative_to(root.resolve()):
            return None, "P2_BENCHMARK_RECEIPT_OUTSIDE_STATE"
        raw = path.read_bytes()
        data = json.loads(raw)
        if not isinstance(data, dict):
            return None, "P2_BENCHMARK_RECEIPT_INVALID"
        benchmark = data.get("benchmark") or {}
        restored = data.get("restoration") or {}
        post = data.get("post_restore_wizard_status") or {}
        if not (data.get("status") == "BENCH_PASS_RESTORED_VERIFIED"
                and benchmark.get("status") == "PASS"
                and benchmark.get("benchmark_version") == "p2-27b-api-benchmark-v1"
                and restored.get("status") == "RESTORED"
                and post.get("status") == "LIVE_SERVICE_VERIFIED"
                and post.get("observed_model") == "flash-next"
                and post.get("expected_served_id") == trial.ORIGINAL_ID
                and not post.get("issues")):
            return None, "P2_BENCHMARK_NOT_QUALIFIED"
        return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}, None
    except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        return None, "P2_BENCHMARK_RECEIPT_UNREADABLE"


def make_plan(*, base_planner=trial.make_plan, receipt_reader=latest_p2_benchmark):
    base = base_planner()
    receipt, issue = receipt_reader()
    problems = list(base.get("issues") or [])
    if issue:
        problems.append(issue)
    result = dict(base)
    result["action"] = "P3-two-temporary-roundtrips-with-original-restore"
    result["plan_id"] = None
    result["cycles"] = CYCLES
    result["version"] = VERSION
    result["benchmark_receipt"] = receipt
    if base.get("status") == "READY_TO_REQUEST_TRIAL_APPROVAL" and receipt:
        fingerprint = json.dumps({
            "operation": VERSION, "p2_trial_plan": base["plan_id"],
            "p2_benchmark_receipt_sha256": receipt["sha256"],
            "cycles": CYCLES,
        }, sort_keys=True, separators=(",", ":"))
        result["status"] = "READY_TO_REQUEST_TRIAL_APPROVAL"
        result["plan_id"] = hashlib.sha256(fingerprint.encode()).hexdigest()
    else:
        result["status"] = "BLOCKED"
    result["issues"] = sorted(set(problems))
    result["notice"] = ("Requires separate exact P3 approval + Flash-Next downtime ack; "
                        "performs TWO temporary trials, each Flash->27B->original Flash. "
                        "Never leaves 27B serving and does not establish a persistent "
                        "production switch. Power/Docker failure may defeat recovery.")
    return result


def verify_original_after_cycle(source_id, *, inspector=inspect_live_status,
                                docker_inspector=trial.docker_info) -> dict[str, Any]:
    try:
        live = inspector()
        original = docker_inspector(trial.ORIGINAL_CONTAINER)
        ok = (live.get("status") == "LIVE_SERVICE_VERIFIED"
              and live.get("observed_model") == "flash-next"
              and live.get("expected_served_id") == trial.ORIGINAL_ID
              and live.get("host_port") == 8000
              and live.get("issues") == []
              and original.get("Id") == source_id
              and (original.get("State") or {}).get("Running") is True)
        return {"status": "PASS" if ok else "BLOCKED",
                "live_status": live.get("status"),
                "model": live.get("observed_model"),
                "source_container_id_preserved": original.get("Id") == source_id}
    except (OSError, ValueError, RuntimeError):
        return {"status": "BLOCKED",
                "issues": ["POST_CYCLE_LIVE_STATE_UNAVAILABLE"]}


def execute(approved, ack, *, planner=make_plan, core=trial.execute,
            verifier=verify_original_after_cycle, state_root: Path = EVIDENCE_ROOT):
    if not isinstance(approved, str) or not re.fullmatch(r"[a-f0-9]{64}", approved) or ack != trial.ACK:
        return 3, {"status": "BLOCKED", "executed": False,
                   "issues": ["NEW_P3_PLAN_AND_DOWNTIME_ACK_REQUIRED"]}
    before = planner()
    if before.get("status") != "READY_TO_REQUEST_TRIAL_APPROVAL" or before.get("plan_id") != approved:
        return 3, {"status": "BLOCKED", "executed": False,
                   "issues": ["P3_APPROVAL_STALE_OR_PREFLIGHT_CHANGED"]+before.get("issues", [])}
    source_id = before.get("source_container_id")
    cycles = []
    for index in range(CYCLES):
        # Trial uses its own lock, immutable source/container ID, target label
        # and mandatory same-original recovery. Replans before EVERY cycle.
        rc, result = core(approved, ack, planner=planner, inference=trial.one_inference,
                          state_dir=state_root)
        item = {"index": index+1, "trial_status": result.get("status"),
                "target_api_ready": result.get("target_api_ready", False),
                "inference_ok": result.get("inference_ok", False),
                "restoration": result.get("restoration"),
                "trial_evidence": result.get("evidence"), "return_code": rc}
        if rc == 0 and result.get("status") == "PASS_RESTORED":
            item["post_restore"] = verifier(source_id)
        cycles.append(item)
        if rc != 0 or result.get("status") != "PASS_RESTORED" or (
            item.get("post_restore") or {}).get("status") != "PASS":
            break
    all_pass = len(cycles) == CYCLES and all(
        c["trial_status"] == "PASS_RESTORED"
        and c["post_restore"]["status"] == "PASS" for c in cycles)
    status = "P3_TEMPORARY_ROUNDTRIP_PASS" if all_pass else "P3_INCOMPLETE_OR_BLOCKED"
    report = {"schema_version": 1, "status": status,
              "operation": VERSION, "approved_plan_id": approved,
              "completed_cycles": len(cycles), "requested_cycles": CYCLES,
              "cycle_results": cycles, "executed": any(
                  c["trial_status"] != "BLOCKED" for c in cycles),
              "permanent_switch_qualified": False,
              "gpu_exclusivity_outside_docker_verified": False,
              "notice": ("Repeating temporary stop/restore is not evidence of "
                         "persistent production model switching.")}
    try:
        state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        output = state_root / ("p3-roundtrips-" + time.strftime(
            "%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + approved[:12] + ".json")
        fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(report, sort_keys=True, indent=2) + "\n")
        report["evidence"] = str(output)
    except OSError:
        report["evidence_error"] = "UNAVAILABLE"
        report["status"] = "P3_EVIDENCE_WRITE_FAILED" if all_pass else report["status"]
        all_pass = False
    return (0 if all_pass else 4), report


def main(argv=None):
    parser = argparse.ArgumentParser(description="P3 two-cycle roundtrip trial")
    parser.add_argument("mode", choices=("plan", "execute"))
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    opts = parser.parse_args(argv)
    if opts.mode == "plan":
        if opts.approve_plan or opts.ack_downtime:
            parser.error("no approval on read-only plan")
        result = make_plan()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "READY_TO_REQUEST_TRIAL_APPROVAL" else 3
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    rc, result = execute(opts.approve_plan, opts.ack_downtime)
    print(json.dumps(result, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
