"""RETIRED P3 two-roundtrip interface (2026-11-06).

The operator replaced the temporary Flash->27B->Flash x2 trial with
an explicitly entered staged flow: 27B->Flash-Next, P1 gap closure +
benchmark, then final Flash-Next->27B. This legacy P3 executor MUST
remain fail-closed even if a previous P2 benchmark receipt is available.

The older implementation is preserved in Git history, not executable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EVIDENCE_ROOT = Path.home() / ".local/state/blazux-wizard/p2"


def latest_p2_benchmark(root: Path = EVIDENCE_ROOT):
    """Read the newest bounded private P2 bench receipt without modifying it."""
    try:
        candidates = sorted(root.glob("*.benchmark.json"), reverse=True)
        if not candidates:
            return None, "P2_BENCHMARK_RECEIPT_NOT_FOUND"
        path = candidates[0]
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
            return None, "P2_BENCHMARK_RECEIPT_UNTRUSTED"
        if not path.resolve().is_relative_to(root.resolve()):
            return None, "P2_BENCHMARK_RECEIPT_OUTSIDE_STATE"
        content = path.read_bytes()
        doc = json.loads(content)
        if not isinstance(doc, dict):
            return None, "P2_BENCHMARK_RECEIPT_INVALID"
        benchmark = doc.get("benchmark") or {}
        restore = doc.get("restoration") or {}
        live = doc.get("post_restore_wizard_status") or {}
        if not (doc.get("status") == "BENCH_PASS_RESTORED_VERIFIED"
                and benchmark.get("status") == "PASS"
                and benchmark.get("benchmark_version") == "p2-27b-api-benchmark-v1"
                and restore.get("status") == "RESTORED"
                and live.get("status") == "LIVE_SERVICE_VERIFIED"
                and live.get("observed_model") == "flash-next"
                and live.get("expected_served_id") == "qwen3.8-flash-next"
                and not live.get("issues")):
            return None, "P2_BENCHMARK_NOT_QUALIFIED"
        return {"path": str(path), "sha256": hashlib.sha256(content).hexdigest()}, None
    except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        return None, "P2_BENCHMARK_RECEIPT_UNREADABLE"


def make_plan(*args, **kwargs):
    return {
        "stage": "p3", "action": "retired-two-roundtrips",
        "status": "BLOCKED", "executed": False, "plan_id": None,
        "operations_enabled": False,
        "issues": ["P3_LEGACY_ROUNDTRIP_RETIRED", "P3_NEW_MANUAL_SEQUENCE_REQUIRED"],
        "notice": "See ./wizard.sh switch flash-next-27b sequence --plan --json.",
    }


def execute(*args, **kwargs):
    return 3, make_plan()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Retired P3 roundtrip; all modes blocked")
    parser.add_argument("mode", nargs="?", choices=("plan", "execute"), default="plan")
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    parser.parse_args(argv)
    print(json.dumps(make_plan(), indent=2, sort_keys=True))
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
