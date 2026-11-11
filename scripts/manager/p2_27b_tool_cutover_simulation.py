"""P2-FINAL Native Tools V1: CPU/Fake-DGX transaction contract simulation ONLY.

There is intentionally NO Docker adapter, CLI execute route, disk journal,
live service mutator, or production release toggle. This module exercises the
desired stop-before-start, identity and restore decisions on injected fake
backends. It is NOT a deployment executor or operator consent.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from scripts.manager.p2_27b_tool_variant import (
    VARIANT_CONTAINER, SOURCE_CONTAINER, FALLBACK_CONTAINER, VARIANT_ID,
)
from scripts.manager.p2_27b_launch_preview import SERVED, REVISION

SHA = re.compile(r"^[0-9a-f]{64}$")
IMAGE = re.compile(r"^sha256:[0-9a-f]{64}$")
ACK = "I_ACCEPT_P2_FINAL_NATIVE_TOOLS_DOWNTIME"
ACK_TARGET = "I_APPROVE_DISTINCT_27B_NATIVE_TOOLS_V1"


def simulated_approval_digest(facts: dict) -> str | None:
    """Different namespace from historical P2/P3 and operating-switch SHA."""
    if not isinstance(facts, dict):
        return None
    if (
        facts.get("kind") != "P2_FINAL_NATIVE_TOOLS_V1_SIMULATION"
        or facts.get("variant_id") != VARIANT_ID
        or facts.get("original") != SOURCE_CONTAINER
        or facts.get("target") != VARIANT_CONTAINER
        or facts.get("fallback") != FALLBACK_CONTAINER
        or facts.get("served_id") != SERVED
        or facts.get("pinned_revision") != REVISION
        or facts.get("port") != 8000
        or not SHA.fullmatch(str(facts.get("source_container_id") or ""))
        or not SHA.fullmatch(str(facts.get("fallback_container_id") or ""))
        or not IMAGE.fullmatch(str(facts.get("source_image") or ""))
        or not IMAGE.fullmatch(str(facts.get("fallback_image") or ""))
        or facts.get("parser_audited") is not True
        or facts.get("tokenizer_audited") is not True
        or facts.get("one_active_gpu_model") is not True
        or type(facts.get("expires_at")) is not int
    ):
        return None
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def simulate_transaction(
    facts: dict, approval: str | None, downtime_ack: str | None,
    target_ack: str | None, *,
    adapter: Any, now: int,
) -> dict:
    """Pure Fake-DGX contract exercise; never called from a live CLI.

    Fake adapter API: locked, journal_clean, source, fallback, variant_absent,
    gpu_running, stop_original, port_free, start_variant, verify_variant,
    confirm_original_stopped, confirm_original_preserved, stop_variant,
    restore_original, confirm_original_restored, release.
    Identity values returned by source/fallback are (64hex ID, sha256:image).
    """
    result = {
        "schema_version": 1, "mode": "FAKE_DGX_ONLY",
        "status": "SIMULATED_BLOCKED", "executed_on_real_dgx": False,
        "production_executor_available": False, "issues": [], "phases": [],
    }
    digest = simulated_approval_digest(facts)
    if (
        digest is None or approval != digest
        or downtime_ack != ACK or target_ack != ACK_TARGET
        or type(now) is not int
        or not (now + 120 <= facts["expires_at"] <= now + 600)
    ):
        result["issues"].append("SIMULATED_PLAN_APPROVAL_OR_EXPIRY_INVALID")
        return result
    if not adapter.locked():
        result["issues"].append("SIMULATED_LOCK_NOT_ACQUIRED")
        return result
    source_stop_attempted = False
    variant_started = False
    phase = "PREFLIGHT"
    try:
        if not adapter.journal_clean():
            raise RuntimeError("UNCERTAIN_PREVIOUS_JOURNAL")
        if adapter.source() != (
            facts["source_container_id"], facts["source_image"], True,
        ):
            raise RuntimeError("SOURCE_IDENTITY_CHANGED")
        if adapter.fallback() != (
            facts["fallback_container_id"], facts["fallback_image"], False,
        ):
            raise RuntimeError("FALLBACK_IDENTITY_CHANGED")
        if not adapter.variant_absent():
            raise RuntimeError("VARIANT_NAME_COLLISION")
        if adapter.gpu_running() != [SOURCE_CONTAINER]:
            raise RuntimeError("FOREIGN_OR_PARALLEL_GPU_MODEL")
        result["phases"].append("PREFLIGHT")
        # Read the exact source identity once more immediately before stop.
        if adapter.source() != (
            facts["source_container_id"], facts["source_image"], True,
        ):
            raise RuntimeError("SOURCE_DRIFT_BEFORE_STOP")
        result["phases"].append("OLD_STOPPING")
        phase = "OLD_STOPPING"
        source_stop_attempted = True
        adapter.stop_original()
        if not adapter.confirm_original_stopped():
            raise RuntimeError("ORIGINAL_NOT_STOPPED")
        result["phases"].append("OLD_STOPPED")
        phase = "OLD_STOPPED"
        if not adapter.port_free():
            raise RuntimeError("PORT_8000_NOT_RELEASED")
        if adapter.gpu_running():
            raise RuntimeError("FOREIGN_GPU_AFTER_ORIGINAL_STOP")
        result["phases"].append("NEW_STARTING")
        phase = "NEW_STARTING"
        adapter.start_variant()
        variant_started = True
        result["phases"].append("NEW_VERIFYING")
        phase = "NEW_VERIFYING"
        if not adapter.verify_variant(SERVED):
            raise RuntimeError("VARIANT_API_CHAT_OR_TOOLS_NOT_VERIFIED")
        if adapter.gpu_running() != [VARIANT_CONTAINER]:
            raise RuntimeError("PARALLEL_GPU_AFTER_VARIANT_START")
        if not adapter.confirm_original_preserved(
            facts["source_container_id"], facts["source_image"]
        ):
            raise RuntimeError("ORIGINAL_LINEAGE_CHANGED")
        result["phases"].append("SIMULATED_COMMITTED")
        result["status"] = "SIMULATED_PASS"
        return result
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        reason = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        result["issues"].append(reason)
        result["failed_phase"] = phase
        if not source_stop_attempted:
            result["phases"].append("SIMULATED_CANCELLED")
            return result
        try:
            result["phases"].append("SIMULATED_RESTORING")
            # The adapter owns only the *variant* container; never remove original.
            # If an attempted start failed partially, always inspect/stop variant.
            if variant_started or phase in ("NEW_STARTING", "NEW_VERIFYING"):
                adapter.stop_variant()
            adapter.restore_original()
            if not adapter.confirm_original_restored(
                facts["source_container_id"], facts["source_image"], SERVED
            ):
                raise RuntimeError("ORIGINAL_ROLLBACK_NOT_VERIFIED")
            result["status"] = "SIMULATED_FAIL_RESTORED"
            result["phases"].append("SIMULATED_RESTORED")
        except (OSError, RuntimeError, TypeError, ValueError) as restore_err:
            result["status"] = "SIMULATED_RECOVERY_FAILED"
            result["issues"].append("RESTORE_UNCERTAIN:" + type(restore_err).__name__)
            result["phases"].append("SIMULATED_RECOVERY_FAILED")
        return result
    finally:
        adapter.release()


def main() -> int:
    print(json.dumps({
        "status": "BLOCKED_NOT_A_LIVE_EXECUTOR",
        "mode": "FAKE_DGX_ONLY",
        "execution_supported": False,
        "notice": "No Docker adapter, live execute route or approval collector exists.",
    }, sort_keys=True))
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
