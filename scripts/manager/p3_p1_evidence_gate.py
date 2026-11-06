"""P3 final-27B prerequisite: verify *actual* post-return P1 evidence.

This module is read-only. Old P1 PASS labels are not new benchmark evidence.
The diagnostic receipt is an operator-created, audited local file; no guess
about historical rc=3 is permitted.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

P1_ROOT = Path.home() / ".local/state/blazux-wizard/p1"
P3_ROOT = Path.home() / ".local/state/blazux-wizard/p3"
FLASH_REPO = "nvidia/Qwen3.8-Flash-Next-NVFP4"
FLASH_ID = "qwen3.8-flash-next"


def _time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("MISSING_EVIDENCE_TIMESTAMP")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("NAIVE_EVIDENCE_TIMESTAMP")
    return result.astimezone(timezone.utc)


def _read_private(path: Path, root: Path) -> tuple[dict[str, Any], str]:
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("EVIDENCE_OUTSIDE_EXPECTED_ROOT")
    if path.is_symlink() or not path.is_file():
        raise ValueError("EVIDENCE_FILE_NOT_REGULAR")
    stat = path.stat()
    if stat.st_size > 131072 or stat.st_size <= 0 or stat.st_mode & 0o077:
        raise ValueError("EVIDENCE_MODE_OR_SIZE_INVALID")
    raw = path.read_bytes()
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("EVIDENCE_NOT_OBJECT")
    return parsed, hashlib.sha256(raw).hexdigest()



def _expected_active_flash_collision(output: Any, flash_image: str) -> bool:
    """A launch preflight exits 3 when Flash-Next already occupies :8000.

    Do not accept rc=3 without parsed doctor/plan observation. Inventory
    errors and foreign Docker/port owners are never benign collisions.
    """
    if not isinstance(output, dict):
        return False
    if (output.get("status") != "PASS" or output.get("errors") != []
            or output.get("name_conflict") is not True
            or output.get("port_conflict") is not True
            or output.get("collision_free") is not False
            or output.get("scope") != "SOURCE"
            or output.get("dry_run") is not True):
        return False
    proposed = output.get("proposed")
    if (not isinstance(proposed, dict)
            or proposed.get("container_name") != "qwen38-flash"
            or proposed.get("port") != 8000
            or proposed.get("served_model_name") != FLASH_ID):
        return False
    containers = output.get("containers")
    if not isinstance(containers, list):
        return False
    originals = [item for item in containers
                 if isinstance(item, dict) and item.get("name") == "qwen38-flash"]
    if len(originals) != 1:
        return False
    observed = originals[0]
    return (observed.get("image_id") == flash_image
            and isinstance(observed.get("status"), str)
            and observed["status"].startswith("Up")
            and isinstance(observed.get("ports"), str)
            and "8000->8000/tcp" in observed["ports"])


def _diagnostic_checks_qualify(doc: dict[str, Any], flash_image: str) -> bool:
    """An active Flash service correctly makes both launch probes return 3."""
    return (doc.get("doctor_exit_code") == 3
            and doc.get("inventory_plan_exit_code") == 3
            and _expected_active_flash_collision(doc.get("doctor_output"), flash_image)
            and _expected_active_flash_collision(doc.get("inventory_plan_output"),
                                                 flash_image))


def assess_p1(*, stage_b: dict[str, Any], flash_image: str,
              p1_root: Path = P1_ROOT, p3_root: Path = P3_ROOT) -> dict[str, Any]:
    """Fail closed until both real P1 actions and rc=3 disposition exist.

    P1 verify/benchmark evidence must be newer than successful P3 stage B,
    from the unchanged source image and using explicit Wizard approvals.
    """
    issues = []
    hashes: dict[str, str] = {}
    try:
        cutoff = _time(stage_b["finished_at_utc"])
    except (KeyError, ValueError, TypeError):
        return {"status": "BLOCKED", "issues": ["P3_B_TIMESTAMP_UNVERIFIED"],
                "evidence_hashes": hashes}
    for action in ("verify", "benchmark"):
        try:
            files = sorted(p1_root.glob("*.json"), reverse=True)
            records = []
            for path in files[:256]:
                doc, digest = _read_private(path, p1_root)
                if doc.get("action") == action:
                    records.append((doc, digest))
            if not records:
                issues.append("P1_" + action.upper() + "_RECEIPT_NOT_FOUND")
                continue
            doc, digest = records[0]
            if (doc.get("status") != "PASS" or doc.get("executed") is not True
                    or doc.get("approval") != "explicit_plan_id"
                    or doc.get("model_repo") != FLASH_REPO
                    or doc.get("served_model") != FLASH_ID
                    or doc.get("image_id") != flash_image
                    or _time(doc.get("finished_at_utc")) <= cutoff):
                issues.append("P1_" + action.upper() + "_RECEIPT_UNQUALIFIED")
                continue
            result = doc.get("result") or {}
            if not isinstance(result, dict) or result.get("status") != "PASS":
                issues.append("P1_" + action.upper() + "_RESULT_UNQUALIFIED")
                continue
            if action == "verify":
                probes = result.get("probes") or {}
                if (result.get("baseline_status") != "PASS"
                        or result.get("extended_status") != "PASS"
                        or not isinstance(probes, dict)
                        or not all((probes.get(key) or {}).get("status") == "PASS"
                                   for key in ("identity", "default_completion", "chat", "tools", "vision"))):
                    # Older P1 verify records place identity outside probes.
                    identity = result.get("identity") or {}
                    if (not isinstance(probes, dict)
                            or result.get("baseline_status") != "PASS"
                            or result.get("extended_status") != "PASS"
                            or not isinstance(identity, dict)
                            or identity.get("health") != "PASS"
                            or not isinstance(identity.get("models"), list)
                            or FLASH_ID not in identity["models"]
                            or not all((probes.get(key) or {}).get("status") == "PASS"
                                       for key in ("default_completion", "chat", "tools", "vision"))):
                        issues.append("P1_FUNCTIONAL_PROBES_INCOMPLETE")
                        continue
            else:
                bench = result.get("benchmark") or {}
                metrics = bench.get("metrics") or {}
                samples = bench.get("samples") or []
                if (bench.get("status") != "PASS" or len(samples) < 3
                        or not isinstance(metrics, dict)
                        or any(not isinstance(metrics.get(key), (int, float))
                               or metrics[key] <= 0 for key in
                               ("latency_p50_sec", "ttft_p50_sec", "mean_tokens_per_sec"))
                        or not all((isinstance(s.get("completion_tokens"), int)
                                    and s["completion_tokens"] > 0
                                    and isinstance(s.get("ttft_sec"), (float, int))
                                    and s["ttft_sec"] >= 0) for s in samples)):
                    issues.append("P1_ACTUAL_BENCHMARK_METRICS_INCOMPLETE")
                    continue
            hashes[action] = digest
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            issues.append("P1_" + action.upper() + "_EVIDENCE_UNTRUSTED")

    diagnostic = p3_root / "p1-diagnostics.json"
    try:
        doc, digest = _read_private(diagnostic, p3_root)
        disposition = doc.get("historical_rc3_disposition")
        if (doc.get("status") != "PASS"
                or not _diagnostic_checks_qualify(doc, flash_image)
                or not isinstance(disposition, str) or len(disposition.strip()) < 20
                or _time(doc.get("finished_at_utc")) <= cutoff):
            issues.append("P1_HISTORIC_RC3_DISPOSITION_NOT_VERIFIED")
        else:
            hashes["diagnostics"] = digest
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        issues.append("P1_HISTORIC_RC3_DIAGNOSTIC_EVIDENCE_MISSING")

    return {"status": "PASS" if not issues else "BLOCKED",
            "issues": sorted(set(issues)), "evidence_hashes": hashes,
            "stage_b_finished_at_utc": stage_b.get("finished_at_utc"),
            "notice": "Actual post-B P1 evidence is mandatory; no benchmark is executed by this checker."}
