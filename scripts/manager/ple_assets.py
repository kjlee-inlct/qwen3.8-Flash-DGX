"""Read-only shared PLE asset registry and pinned header-based source inspection.

The registry is model- and storage-format-independent. A format's metadata
support is NOT proof of a vLLM 0.32/GB10 GPU loader, mmap, or online hot swap.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from scripts.manager import manifest_registry
from scripts.manager.ple_format import PLEFormat, validate_asset
from scripts.p5_vendor.audit import AuditError, audit_checkpoint
from scripts.p5_vendor.manifest import load_manifest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "runtimes" / "ple-assets.json"
REF_PATH = ROOT / "scripts" / "p5_vendor" / "compatibility.json"
ASSET_ID = "orcarouter-bf16-ple"
_REPO = "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4"
_REVISION = "3a3b63161c0745390e5270179af42e46efc70799"
_SIZE_LIMIT = 32768

_TRANSITION_POLICY = {
    "release_source_mmap_before_target": True,
    "verify_gpu_allocation_release": True,
    "stop_old_before_new": True,
    "host_port": 8000,
    "preserve_source_and_rollback_assets": True,
}


def _read_assets(path: Path | None = None) -> dict[str, Any]:
    path = MANIFEST_PATH if path is None else Path(path)
    try:
        doc = manifest_registry.read_json(path, max_bytes=_SIZE_LIMIT,
                                          schema_versions=(2,))
    except (OSError, ValueError, TypeError) as exc:
        raise ValueError("PLE_MANIFEST_INVALID") from exc
    if (doc.get("transition_policy") != _TRANSITION_POLICY
        or not isinstance(doc.get("compatibility"), dict)
        or doc["compatibility"].get("model_ple_dtype_independent_from_inference_dtype") is not True
        or doc["compatibility"].get("format_change_requires_explicit_runtime_requalification") is not True
        or doc["compatibility"].get("auto_convert_on_switch") is not False
        or doc["compatibility"].get("auto_reuse_mmap_between_models") is not False):
        raise ValueError("PLE_TRANSITION_POLICY_DRIFT")
    if not isinstance(doc.get("assets"), dict) or not doc["assets"]:
        raise ValueError("PLE_ASSET_REGISTRY_EMPTY")
    for ident, spec in doc["assets"].items():
        validate_asset(ident, spec)
    if ASSET_ID not in doc["assets"]:
        raise ValueError("PLE_ORCAROUTER_PINNED_ASSET_MISSING")
    _check_pinned_reference(doc["assets"][ASSET_ID])
    return doc


def _check_pinned_reference(spec: dict[str, Any]) -> None:
    """Current Orcarouter BF16 fixture remains pinned to the YSLAB source."""
    baseline = load_manifest(REF_PATH).target("orca-uncensored")
    expected = {
        "dtype": baseline.expected_ple.dtype,
        "tensor_count": baseline.expected_ple.tensor_count,
        "total_rows": baseline.expected_ple.total_rows,
        "width": baseline.expected_ple.width,
        "split_parts": baseline.expected_ple.split_parts,
        "layer_id": baseline.expected_ple.layer_id,
        "weight_scale_present": False,
        "mmap_bytes": baseline.expected_ple.total_rows *
                      baseline.expected_ple.width * 2,
    }
    if (spec.get("owner_model") != "orcarouter"
        or spec.get("source") != {
            "kind": "PINNED_HF_SNAPSHOT", "repo_id": _REPO,
            "revision": _REVISION,
        }
        or spec.get("reference") != {
            "manifest": "scripts/p5_vendor/compatibility.json",
            "target": "orca-uncensored", "mode": "direct_bf16",
        }
        or spec.get("layout") != expected
        or spec["format"] != {
            "storage_dtype": "BF16", "scale_mode": "NONE",
            "scale_dtype": None, "scale_block_shape": None,
            "packing": "ELEMENT_ALIGNED", "loader_qualified": False,
        }
        or spec.get("profiles") != ["mtp0", "mtp2"]
        or spec.get("placement") != {
            "table_memory": "DISK_MMAP",
            "offload_backend": "MODEL_SPECIFIC_SOURCE",
            "prewarm": False,
            "tp1_executor_requirement": "VERIFY_ON_TARGET_ENGINE",
            "validated_on_gpu": False,
        }
        or spec.get("verification", {}).get("method") != "PINNED_REFERENCE_HEADER_AUDIT"
        or baseline.repo_id != _REPO or baseline.revision != _REVISION):
        raise ValueError("PLE_ORCAROUTER_PINNED_CONTRACT_DRIFT")


def asset_spec(asset_id: str = ASSET_ID, *, path: Path | None = None) -> dict[str, Any]:
    """Return exactly one registered, fully validated PLE asset."""
    assets = _read_assets(path)["assets"]
    if asset_id not in assets:
        raise ValueError("UNKNOWN_PLE_ASSET")
    return assets[asset_id]


def configured_roots(*, home: Path | None = None,
                     environment: dict[str, str] | None = None) -> list[Path]:
    home = Path.home() if home is None else Path(home)
    env = os.environ if environment is None else environment
    document = manifest_registry.load("model_discovery")
    raw = ([env[k] for k in ("HF_CACHE", "HF_HOME") if env.get(k)]
           if document.get("include_hf_cache_environment") else [])
    raw += document.get("cache_roots", [])
    result: list[Path] = []
    for item in raw:
        if not isinstance(item, str) or not item or "\0" in item:
            continue
        path = home / item[2:] if item.startswith("~/") else Path(item)
        if path.is_absolute() and path not in result:
            result.append(path)
    return result


def inspect_ple_asset(*, asset_id: str = ASSET_ID,
                      roots: list[Path] | None = None,
                      manifest_path: Path | None = None) -> dict[str, Any]:
    """Perform a pinned read-only source inspection if an auditor is qualified."""
    try:
        spec = asset_spec(asset_id, path=manifest_path)
        fmt: PLEFormat = validate_asset(asset_id, spec)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {
            "asset_id": asset_id, "gate": "ple_source_metadata",
            "status": "BLOCKED", "registration": "MANIFEST_INVALID",
            "issues": [str(exc)], "metadata_verified": False,
            "checkpoint_sha_verified": False, "gpu_verified": False,
            "runtime_qualified": False, "executed": False,
        }
    layout, src = spec["layout"], spec["source"]
    base = {
        "asset_id": asset_id,
        "gate": "bf16_direct_ple" if asset_id == ASSET_ID else "ple_source_metadata",
        "managed": True, "manifest": "runtimes/ple-assets.json",
        "registration": "REGISTERED", "source_repo": src["repo_id"],
        "revision": src["revision"], "owner_model": spec["owner_model"],
        "expected": dict(layout), "format": fmt.report(),
        "placement": dict(spec["placement"]),
        "profiles": list(spec["profiles"]), "verification_method": spec["verification"]["method"],
        "checkpoint_sha_verified": False, "gpu_verified": False,
        "runtime_qualified": False, "runtime_mmap_status": "NOT_RUN",
        "executed": False,
    }
    roots = configured_roots() if roots is None else roots
    for root in roots:
        root = Path(root)
        snapshot = (root / "hub" /
                    ("models--" + src["repo_id"].replace("/", "--", 1)) /
                    "snapshots" / src["revision"])
        if snapshot.is_symlink() or not snapshot.is_dir():
            continue
        if spec["verification"]["method"] != "PINNED_REFERENCE_HEADER_AUDIT":
            return {**base, "status": "BLOCKED",
                    "source_state": "PINNED_SNAPSHOT_AUDITOR_UNQUALIFIED",
                    "metadata_verified": False,
                    "issues": ["PLE_FORMAT_AUDITOR_NOT_QUALIFIED"]}
        try:
            resolved_root = (root / "hub").resolve(strict=True)
            resolved_snapshot = snapshot.resolve(strict=True)
            if not resolved_snapshot.is_relative_to(resolved_root):
                raise ValueError("PLE_CHECKPOINT_OUTSIDE_CONFIGURED_CACHE")
            ref = spec["reference"]
            if ref["manifest"] != "scripts/p5_vendor/compatibility.json":
                raise ValueError("PLE_AUDITOR_NOT_REGISTERED")
            target = load_manifest(REF_PATH).target(ref["target"])
            if (target.repo_id != src["repo_id"]
                or target.revision != src["revision"]
                or target.mode != ref["mode"]
                or target.expected_ple.dtype != fmt.dtype
                or target.expected_ple.tensor_count != layout["tensor_count"]
                or target.expected_ple.total_rows != layout["total_rows"]
                or target.expected_ple.width != layout["width"]
                or target.expected_ple.split_parts != layout["split_parts"]
                or target.expected_ple.layer_id != layout["layer_id"]):
                raise ValueError("PLE_REFERENCE_LAYOUT_MISMATCH")
            result = audit_checkpoint(snapshot, target, (resolved_root,))
            observed = {
                "dtype": result.ple_dtype, "tensor_count": result.ple_tensor_count,
                "total_rows": result.ple_rows, "width": result.ple_width,
            }
            if any(observed[key] != layout[key] for key in observed):
                raise ValueError("PLE_METADATA_LAYOUT_MISMATCH")
            return {
                **base, "status": "PASS",
                "source_state": "PINNED_SNAPSHOT_METADATA_VERIFIED",
                "metadata_verified": True, "tensor_count": observed["tensor_count"],
                "rows": observed["total_rows"], "width": observed["width"],
                "dtype": observed["dtype"], "issues": [],
            }
        except (OSError, ValueError, AuditError, TypeError, KeyError, RecursionError):
            return {
                **base, "status": "BLOCKED", "metadata_verified": False,
                "source_state": "PINNED_SNAPSHOT_AUDIT_FAILED",
                "issues": ["PLE_METADATA_AUDIT_FAILED"],
            }
    return {
        **base, "status": "BLOCKED",
        "source_state": "PINNED_SNAPSHOT_NOT_FOUND",
        "metadata_verified": False, "tensor_count": None, "rows": None,
        "issues": ["PINNED_PLE_SNAPSHOT_NOT_PRESENT"],
    }


def catalog() -> dict[str, Any]:
    """All PLE asset registrations (no cache/GPU calls), including future formats."""
    assets = _read_assets()["assets"]
    results = []
    for aid, spec in sorted(assets.items()):
        fmt = validate_asset(aid, spec)
        results.append({
            "asset_id": aid, "owner_model": spec["owner_model"],
            "registered": True, "expected": dict(spec["layout"]),
            "format": fmt.report(), "placement": dict(spec["placement"]),
            "profiles": list(spec["profiles"]), "runtime_qualified": False,
            "source_repo": spec["source"]["repo_id"],
            "revision": spec["source"]["revision"],
        })
    return {"schema_version": 2, "manifest": "runtimes/ple-assets.json",
            "assets": results}
