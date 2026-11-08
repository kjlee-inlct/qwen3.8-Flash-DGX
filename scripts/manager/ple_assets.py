"""Read-only manifest-led PLE asset lifecycle and checkpoint metadata state.

PLE source assets are independently managed from Docker/service lifecycle.
No Docker/GPU calls, no HF asset writes, no whole-checkpoint hash or memmap
activation. PASS means pinned checkpoint *metadata* audit, NOT runtime PASS.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

from scripts.manager import manifest_registry
from scripts.p5_vendor.audit import AuditError, audit_checkpoint
from scripts.p5_vendor.manifest import load_manifest
from scripts.p5_vendor.safetensors import strict_json_loads

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "runtimes" / "ple-assets.json"
REF_PATH = ROOT / "scripts" / "p5_vendor" / "compatibility.json"
ASSET_ID = "orcarouter-bf16-ple"
_REPO = "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4"
_REVISION = "3a3b63161c0745390e5270179af42e46efc70799"
_REV = re.compile(r"[0-9a-f]{40}\Z")
_SIZE_LIMIT = 32768


def asset_spec(asset_id: str = ASSET_ID, *, path: Path | None = None) -> dict[str, Any]:
    """Strict manifest loader: never trust a runtime writable/overridden path."""
    file = MANIFEST_PATH if path is None else path
    if file.is_symlink() or not file.is_file() or file.stat().st_size > _SIZE_LIMIT:
        raise ValueError("PLE_MANIFEST_MISSING_OR_UNTRUSTED")
    try:
        doc = manifest_registry.read_json(file, max_bytes=_SIZE_LIMIT)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("PLE_MANIFEST_INVALID") from exc
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise ValueError("PLE_MANIFEST_SCHEMA_MISMATCH")
    assets = doc.get("assets")
    if not isinstance(assets, dict) or set(assets) != {ASSET_ID}:
        raise ValueError("PLE_ASSET_REGISTRY_MISMATCH")
    if asset_id != ASSET_ID:
        raise ValueError("UNKNOWN_PLE_ASSET")
    spec = assets[asset_id]
    if not isinstance(spec, dict):
        raise ValueError("PLE_ASSET_NOT_AN_OBJECT")
    src = spec.get("source")
    ref = spec.get("reference")
    layout = spec.get("layout")
    life = spec.get("lifecycle")
    verify = spec.get("verification")
    if not all(isinstance(d, dict) for d in (src, ref, layout, life, verify)):
        raise ValueError("PLE_ASSET_FIELDS_INVALID")
    baseline = load_manifest(REF_PATH).target("orca-uncensored")
    expected = {
        "dtype": baseline.expected_ple.dtype,
        "tensor_count": baseline.expected_ple.tensor_count,
        "total_rows": baseline.expected_ple.total_rows,
        "width": baseline.expected_ple.width,
        "split_parts": baseline.expected_ple.split_parts,
        "layer_id": baseline.expected_ple.layer_id,
        "weight_scale_present": False,
        "mmap_bytes": 320001536 * 160 * 2,
    }
    if (spec.get("owner_model") != "orcarouter"
        or spec.get("role") != "PLE_NGRAM_EMBEDDING"
        or src != {"kind": "PINNED_HF_SNAPSHOT", "repo_id": _REPO,
                   "revision": _REVISION}
        or ref != {"manifest": "scripts/p5_vendor/compatibility.json",
                   "target": "orca-uncensored", "mode": "direct_bf16"}
        or layout != expected
        or baseline.repo_id != _REPO or baseline.revision != _REVISION
        or spec.get("profiles") != ["mtp0", "mtp2"]
        or life != {"managed": True, "source_checkpoint_immutable": True,
                    "cache_preserve": True, "derived_view_separate": True,
                    "delete_requires_separate_approval": True,
                    "runtime_qualified": False, "activation": "NOT_RUN"}
        or verify != {"method": "PINNED_INDEX_AND_SAFETENSORS_HEADER_METADATA",
                      "sha256_whole_checkpoint": False, "gpu_runtime_verified": False}
        or not _REV.fullmatch(src["revision"])):
        raise ValueError("PLE_ASSET_PIN_OR_POLICY_MISMATCH")
    return spec


def configured_roots(*, home: Path | None = None,
                     environment: dict[str, str] | None = None) -> list[Path]:
    """Use the same configured roots as model discovery without importing it."""
    home = Path.home() if home is None else Path(home)
    env = os.environ if environment is None else environment
    document = manifest_registry.load("model_discovery")
    roots = []
    if document.get("include_hf_cache_environment"):
        roots = [env[k] for k in ("HF_CACHE", "HF_HOME") if env.get(k)]
    roots += document.get("cache_roots", [])
    result: list[Path] = []
    for item in roots:
        if not isinstance(item, str) or not item:
            continue
        path = home / item[2:] if item.startswith("~/") else Path(item)
        if path.is_absolute() and path not in result:
            result.append(path)
    return result


def inspect_ple_asset(*, asset_id: str = ASSET_ID,
                      roots: list[Path] | None = None,
                      manifest_path: Path | None = None) -> dict[str, Any]:
    """Fresh, bounded header/index audit; never claim GPU or full SHA verification."""
    try:
        spec = asset_spec(asset_id, path=manifest_path)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {
            "asset_id": asset_id, "gate": "bf16_direct_ple", "status": "BLOCKED",
            "registration": "MANIFEST_INVALID", "issues": [str(exc)],
            "metadata_verified": False, "checkpoint_sha_verified": False,
            "gpu_verified": False, "runtime_qualified": False, "executed": False,
        }
    layout = spec["layout"]
    src = spec["source"]
    base = {
        "asset_id": asset_id, "gate": "bf16_direct_ple",
        "managed": True, "manifest": "runtimes/ple-assets.json",
        "registration": "REGISTERED", "source_repo": src["repo_id"],
        "revision": src["revision"],
        "expected": dict(layout), "profiles": list(spec["profiles"]),
        "verification_method": spec["verification"]["method"],
        "checkpoint_sha_verified": False, "gpu_verified": False,
        "runtime_qualified": False, "runtime_mmap_status": "NOT_RUN",
        "executed": False,
    }
    roots = configured_roots() if roots is None else roots
    for root in roots:
        if not isinstance(root, Path):
            root = Path(root)
        snapshot = (root / "hub" /
                    ("models--" + src["repo_id"].replace("/", "--", 1)) /
                    "snapshots" / src["revision"])
        if snapshot.is_symlink() or not snapshot.is_dir():
            continue
        try:
            resolved_root = (root / "hub").resolve(strict=True)
            resolved_snapshot = snapshot.resolve(strict=True)
            if not resolved_snapshot.is_relative_to(resolved_root):
                raise ValueError("PLE_CHECKPOINT_OUTSIDE_CONFIGURED_CACHE")
            target = load_manifest(REF_PATH).target(spec["reference"]["target"])
            outcome = audit_checkpoint(snapshot, target, (resolved_root,))
            observed = {"dtype": outcome.ple_dtype, "tensor_count": outcome.ple_tensor_count,
                        "total_rows": outcome.ple_rows, "width": layout["width"]}
            if any(observed[key] != layout[key] for key in observed):
                raise ValueError("PLE_METADATA_LAYOUT_MISMATCH")
            return {**base, "status": "PASS",
                    "source_state": "PINNED_SNAPSHOT_METADATA_VERIFIED",
                    "metadata_verified": True, "tensor_count": observed["tensor_count"],
                    "rows": observed["total_rows"], "width": observed["width"],
                    "dtype": observed["dtype"], "issues": []}
        except (OSError, ValueError, AuditError, TypeError, KeyError,
                RecursionError):
            return {**base, "status": "BLOCKED", "metadata_verified": False,
                    "source_state": "PINNED_SNAPSHOT_AUDIT_FAILED",
                    "issues": ["PLE_METADATA_AUDIT_FAILED"]}
    return {**base, "status": "BLOCKED",
            "source_state": "PINNED_SNAPSHOT_NOT_FOUND",
            "metadata_verified": False, "tensor_count": None, "rows": None,
            "issues": ["PINNED_ORCAROUTER_SNAPSHOT_NOT_PRESENT"]}


def catalog() -> dict[str, Any]:
    """Manifest registration view; no cache scan, API or GPU proof."""
    spec = asset_spec()
    return {"schema_version": 1, "manifest": "runtimes/ple-assets.json",
            "assets": [{
                "asset_id": ASSET_ID, "owner_model": spec["owner_model"],
                "registered": True, "expected": dict(spec["layout"]),
                "profiles": list(spec["profiles"]), "runtime_qualified": False,
                "source_repo": spec["source"]["repo_id"],
                "revision": spec["source"]["revision"],
            }]}
