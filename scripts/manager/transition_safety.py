"""Extended P6/P8 transition safety model with injectable in-memory backend.

There is deliberately NO real Docker, GPU or socket backend in this module.
A future live backend requires a separate approval/authorization contract and
independent runtime acceptance; the Fake-DGX engine grants neither.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json

from scripts.manager.generic_operations import model_catalog

FAULTS = (
    "none", "source-stop", "port-release", "target-start", "target-api",
    "restore-source", "container-drift", "journal-write", "approval-expired",
    "state-drift", "duplicate-execution",
)

EXPECTED = {
    "none": "PASS_FAKE_SWITCH",
    "source-stop": "BLOCKED_FAKE_BEFORE_STOP",
    "port-release": "FAIL_FAKE_PORT_RELEASE",
    "target-start": "PASS_FAKE_RECOVERY",
    "target-api": "PASS_FAKE_RECOVERY",
    "restore-source": "FAIL_FAKE_RECOVERY",
    "container-drift": "BLOCKED_FAKE_BEFORE_STOP",
    "journal-write": "BLOCKED_FAKE_BEFORE_STOP",
    "approval-expired": "BLOCKED_FAKE_BEFORE_STOP",
    "state-drift": "BLOCKED_FAKE_BEFORE_STOP",
    "duplicate-execution": "BLOCKED_FAKE_BEFORE_STOP",
}


@dataclass
class InMemoryBackend:
    """Only approved object type for simulated actions (no I/O methods)."""
    active: str
    port_owner: str
    docker_id: str = "a" * 64  # Synthetic SOURCE ID; legacy fixture field
    target_docker_id: str = "b" * 64  # Synthetic TARGET ID; never reused for source
    source_model: str | None = None
    target_model: str | None = None
    journal: list[dict] = field(default_factory=list)
    mutations: list[str] = field(default_factory=list)
    used_nonces: set[str] = field(default_factory=set)

    def container_id_for(self, model: str | None) -> str | None:
        if model is None:
            return None
        if model == self.source_model:
            return self.docker_id
        if model == self.target_model:
            return self.target_docker_id
        return None

    def record(self, phase: str, action: str) -> None:
        self.journal.append({
            "phase": phase, "action": action,
            "active_models": [self.active] if self.active else [],
            "port_8000_owner": self.port_owner,
            # Retain old key for existing clients, but it ALWAYS means source.
            "docker_id": self.docker_id,
            "source_container_id": self.docker_id,
            "target_container_id": self.target_docker_id,
            "active_container_id": self.container_id_for(self.active),
            "port_owner_container_id": self.container_id_for(self.port_owner),
        })

    def stop(self, model: str, *, release_port: bool = True) -> bool:
        if self.active != model:
            return False
        self.mutations.append("stop:" + model)
        self.active = None
        if release_port:
            self.port_owner = None
        return True

    def start(self, model: str, *, fail: bool = False) -> bool:
        if fail or self.active is not None or self.port_owner is not None:
            return False
        self.mutations.append("start:" + model)
        self.active = model
        self.port_owner = model
        return True


def simulate_transaction(source: str, target: str, *, fault: str = "none",
                         config: dict | None = None,
                         backend: InMemoryBackend | None = None) -> dict:
    catalog = model_catalog(config)
    if source == target or source not in catalog["models"] or target not in catalog["models"]:
        raise ValueError("UNREGISTERED_OR_SAME_MODEL_PAIR")
    if fault not in FAULTS:
        raise ValueError("UNSUPPORTED_EXTENDED_FAULT")
    # Reject arbitrary injected objects, particularly accidental live backends.
    if backend is not None and type(backend) is not InMemoryBackend:
        raise TypeError("ONLY_EXACT_IN_MEMORY_BACKEND_PERMITTED")
    runtime = backend if backend is not None else InMemoryBackend(source, source)
    if runtime.source_model is not None and runtime.source_model != source:
        raise ValueError("IN_MEMORY_BACKEND_SOURCE_BINDING_DRIFT")
    if runtime.target_model is not None and runtime.target_model != target:
        raise ValueError("IN_MEMORY_BACKEND_TARGET_BINDING_DRIFT")
    runtime.source_model, runtime.target_model = source, target
    issues = []
    nonce = hashlib.sha256(
        json.dumps([source, target, fault, "in-memory-only"]).encode()).hexdigest()
    initial_docker = runtime.docker_id
    initial_target_docker = runtime.target_docker_id
    original_owner = runtime.port_owner

    def result(status: str) -> dict:
        active_set = [runtime.active] if runtime.active else []
        violation = (len(active_set) > 1 or
                     runtime.active not in (None, source, target))
        return {
            "schema_version": 1, "stage": "p6" if fault == "none" else "p8",
            "scope": "IN_MEMORY_TRANSACTION_TEST_ONLY", "status": status,
            "expected_status": EXPECTED[fault],
            "source_model": source, "target_model": target,
            "injected_fault": fault, "api_port": 8000,
            "journal": list(runtime.journal),
            "synthetic_mutations": list(runtime.mutations),
            "invariant_issues": ["ONE_GPU_MODEL_INVARIANT"] if violation else [],
            "issues": issues, "final_active_model": runtime.active,
            "final_port_owner": runtime.port_owner,
            "source_container_id": runtime.docker_id,
            "target_container_id": runtime.target_docker_id,
            "final_active_container_id": runtime.container_id_for(runtime.active),
            "final_port_owner_container_id": runtime.container_id_for(runtime.port_owner),
            "fake_executed": True, "executed": False, "real_dgx_verified": False,
            "approval_accepted": False, "operations_enabled": False,
            "production_released": False, "plan_id": None,
        }

    runtime.record("OBSERVED", "inspect-source")
    if (not all(isinstance(x, str) and len(x) == 64
                and all(c in "0123456789abcdef" for c in x)
                for x in (initial_docker, initial_target_docker))
            or initial_docker == initial_target_docker):
        issues.append("SOURCE_TARGET_DOCKER_ID_NOT_DISTINCT_OR_INVALID")
        runtime.record("CANCELLED", "fail-closed-before-stop")
        return result("BLOCKED_FAKE_BEFORE_STOP")
    if runtime.active != source or original_owner != source:
        issues.append("SOURCE_OR_PORT_PRECONDITION_DRIFT")
        return result("BLOCKED_FAKE_BEFORE_STOP")
    runtime.record("PLANNED", "non-authorizing-plan")
    if fault == "approval-expired":
        issues.append("APPROVAL_EXPIRED")
    if fault == "duplicate-execution" or nonce in runtime.used_nonces:
        issues.append("EXECUTION_NONCE_ALREADY_CONSUMED")
    if fault == "state-drift":
        issues.append("SOURCE_STATE_CHANGED_AFTER_PLAN")
    if fault == "journal-write":
        issues.append("JOURNAL_WRITE_UNAVAILABLE")
    if fault == "container-drift":
        runtime.docker_id = "c" * 64
    if runtime.docker_id != initial_docker:
        issues.append("SOURCE_DOCKER_ID_CHANGED_AFTER_PLAN")
    if issues:
        runtime.record("CANCELLED", "fail-closed-before-stop")
        return result("BLOCKED_FAKE_BEFORE_STOP")
    runtime.used_nonces.add(nonce)
    runtime.record("OLD_STOPPING", "stop-first-intent")
    if fault == "source-stop":
        issues.append("SOURCE_STOP_FAILED")
        runtime.record("FAILED", "source-still-active")
        return result("BLOCKED_FAKE_BEFORE_STOP")
    runtime.stop(source, release_port=fault != "port-release")
    runtime.record("OLD_STOPPED", "observe-old-stopped")
    if runtime.port_owner is not None:
        issues.append("PORT_8000_NOT_RELEASED")
        runtime.record("FAILED", "no-target-start-on-port-conflict")
        return result("FAIL_FAKE_PORT_RELEASE")
    runtime.record("NEW_STARTING", "target-start-intent")
    started = runtime.start(target, fail=fault == "target-start")
    if started:
        runtime.record("NEW_VERIFYING", "verify-api-served-id")
    if fault == "target-api" or fault == "restore-source":
        issues.append("TARGET_API_ID_MISMATCH")
    if not started or fault in ("target-api", "restore-source"):
        if not started:
            issues.append("TARGET_START_FAILED")
        if runtime.active == target:
            runtime.stop(target)
        runtime.record("ROLLBACK_STARTING", "restore-source-intent")
        if fault == "restore-source":
            issues.append("SOURCE_RESTORE_FAILED")
            runtime.record("RECOVERY_FAILED", "no-source-running")
            return result("FAIL_FAKE_RECOVERY")
        if not runtime.start(source):
            issues.append("SOURCE_RESTORE_FAILED")
            runtime.record("RECOVERY_FAILED", "restore-blocked")
            return result("FAIL_FAKE_RECOVERY")
        runtime.record("RESTORED", "source-api-id-verified")
        return result("PASS_FAKE_RECOVERY")
    runtime.record("COMMITTED", "target-api-id-verified")
    return result("PASS_FAKE_SWITCH")


def extended_fault_matrix(*, config: dict | None = None) -> dict:
    catalog = model_catalog(config)
    names = sorted(catalog["models"])
    cases = [simulate_transaction(a, b, fault=f, config=config)
             for a in names for b in names if a != b for f in FAULTS]
    complete = bool(cases) and all(
        c["status"] == c["expected_status"] and
        not c["invariant_issues"] and
        not c["executed"] and
        not c["production_released"]
        for c in cases)
    return {
        "schema_version": 1, "stage": "p8",
        "scope": "EXTENDED_MODEL_AGNOSTIC_IN_MEMORY_ONLY",
        "status": "PASS_FAKE_DGX_EXPECTED_OUTCOMES" if complete else "FAIL_FAKE_DGX",
        "models": names, "pair_count": len(names) * (len(names) - 1),
        "fault_count": len(FAULTS), "test_count": len(cases),
        "cases": cases, "executed": False, "fake_executed": True,
        "real_dgx_verified": False, "operations_enabled": False,
        "production_released": False,
        "note": "Contains deliberately blocked/failing synthetic faults; not a live executor.",
    }
