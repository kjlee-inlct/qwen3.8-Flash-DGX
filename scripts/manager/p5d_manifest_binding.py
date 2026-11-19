"""Source-only P5-D PLE provenance binding to the Wizard's validated manifest graph.

This is a declarative checkpoint pin, NOT live Docker, PLE mmap, port ownership,
GPU exclusivity, or release attestation. Never performs host/Docker/network reads.
"""
from __future__ import annotations

from pathlib import Path
import re

from scripts.manager.manifest_registry import ROOT, load, validate

_OK = "DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED"
_REV = re.compile(r"[0-9a-f]{40}\Z")
_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def source_binding(model: str, *, root: Path = ROOT) -> dict:
    """Require a fully validated manifest graph before naming an audit target."""
    report = {
        "schema_version": 1, "action": "p5d-source-binding-review",
        "model": model, "status": "BLOCKED_MANIFEST_BINDING",
        "issues": [], "source_only": True, "read_only": True,
        "executed": False, "operations_enabled": False,
        "runtime_qualified": False, "ple_residency_authenticated": False,
        "host_nat_owner_authenticated": False, "production_released": False,
    }
    if not isinstance(model, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", model):
        report["issues"] = ["P5D_MODEL_KEY_INVALID"]
        return report
    try:
        graph = validate(root=root)
        if graph.get("status") != "PASS":
            report["issues"] = ["P5D_MANIFEST_GRAPH_INVALID"] + graph.get("issues", [])
            return report
        service = load("service_policy", root=root)
        discovery = load("model_discovery", root=root)
        assets = load("ple_assets", root=root)
        spec = service.get("models", {}).get(model)
        found = discovery.get("models", {}).get(model)
        if not isinstance(spec, dict) or not isinstance(found, dict):
            report["issues"] = ["P5D_MODEL_NOT_REGISTERED"]
            return report
        asset_id = spec.get("ple_asset_id")
        asset = assets.get("assets", {}).get(asset_id)
        if not isinstance(asset_id, str) or not isinstance(asset, dict):
            report["issues"] = ["P5D_PLE_ASSET_NOT_REGISTERED"]
            return report
        src = asset.get("source")
        proposed = spec.get("proposed_served_ids") or {}
        served = spec.get("served_id") or (
            proposed.get("mtp0") if isinstance(proposed, dict) else None)
        if (not isinstance(src, dict)
                or src.get("kind") != "PINNED_HF_SNAPSHOT"
                or asset.get("owner_model") != model
                or asset.get("role") != "PLE_NGRAM_EMBEDDING"
                or not isinstance(src.get("repo_id"), str)
                or _REPO.fullmatch(src["repo_id"]) is None
                or not isinstance(src.get("revision"), str)
                or _REV.fullmatch(src["revision"]) is None
                or src["repo_id"] != spec.get("checkpoint")
                or src["repo_id"] != found.get("repo_id")
                or src["revision"] != spec.get("pinned_revision")
                or src["revision"] != found.get("pinned_revision")
                or found.get("ple_asset_id") != asset_id
                or not isinstance(served, str) or not served.strip()
                or service.get("max_active_gpu_models") != 1
                or service.get("api", {}).get("host_port") != 8000):
            report["issues"] = ["P5D_SOURCE_MODEL_ASSET_PIN_DRIFT"]
            return report
        report.update({
            "status": _OK, "asset_id": asset_id,
            "source": {"repo_id": src["repo_id"], "revision": src["revision"]},
            "served_id": served,
            "served_id_provisional": spec.get("served_id") is None,
            "format": asset.get("format", {}).get("storage_dtype"),
            "placement": asset.get("placement", {}).get("table_memory"),
            "manifest_files_verified": graph.get("manifest_files_verified"),
            "manifest_graph_validated": True,
            "note": "Manifest pin only; no live PLE file/RSS/PSS, inode, NAT or PID attestation.",
        })
    except (OSError, ValueError, TypeError, KeyError):
        report["issues"] = ["P5D_MANIFEST_READ_OR_SCHEMA_UNAVAILABLE"]
    return report
