"""Wizard shared manifest reader, registry and cross-reference validation.

One declarative contract for model discovery, service, recipes, PLE assets and
pinned YSLAB compatibility. All routines are read-only, side-effect-free and
never authorize a Docker/GPU/storage action. Observations are separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_FILE = "runtimes/manifest-registry.json"
FILES = {
    "service_policy": "runtimes/service-policy.json",
    "model_discovery": "runtimes/model-discovery.json",
    "ple_assets": "runtimes/ple-assets.json",
    "orcarouter_recipe": "recipes/qwen38-orcarouter.runtime.json",
    "27b_recipe": "recipes/qwen38-27b.runtime.json",
    "yslab_compatibility": "scripts/p5_vendor/compatibility.json",
}
MAX_BYTES = 128 * 1024
REV = re.compile(r"[0-9a-f]{40}\Z")
REPO = re.compile(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+\Z")
ASSET_ID = "orcarouter-bf16-ple"
ORCA = "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4"
ORCA_REV = "3a3b63161c0745390e5270179af42e46efc70799"
DONOR = "RadixArk/Qwen3.8-Flash-Next-NVFP4"
DONOR_REV = "7b719225242aacd3dbd3f9407468c2ee9a9d2594"


class ManifestContractError(ValueError):
    pass


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise ManifestContractError("MANIFEST_DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ManifestContractError("MANIFEST_NONFINITE_NUMBER")


def read_json(path: Path, *, max_bytes: int = MAX_BYTES) -> dict[str, Any]:
    """Bounded strict JSON; reject symlinks, duplicates, NaN, BOM, large input."""
    path = Path(path)
    try:
        if path.is_symlink() or not path.is_file():
            raise ManifestContractError("MANIFEST_PATH_NOT_REGULAR")
        size = path.stat().st_size
        if size > max_bytes or size <= 0:
            raise ManifestContractError("MANIFEST_INVALID_SIZE")
        data = path.read_bytes()
        result = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                            parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestContractError("MANIFEST_JSON_INVALID") from exc
    if not isinstance(result, dict) or result.get("schema_version") != 1:
        raise ManifestContractError("MANIFEST_SCHEMA_VERSION")
    return result


def registry(*, root: Path = ROOT) -> dict[str, Any]:
    doc = read_json(root / REGISTRY_FILE)
    if (doc.get("registry_id") != "blazux-wizard-v1"
            or doc.get("engine") != "vllm-0.32"
            or doc.get("api_port") != 8000
            or doc.get("entries") != FILES):
        raise ManifestContractError("MANIFEST_REGISTRY_CONTRACT")
    return doc


def load(kind: str, *, root: Path = ROOT) -> dict[str, Any]:
    if kind not in FILES:
        raise ManifestContractError("UNKNOWN_MANIFEST_KIND")
    registered = registry(root=root)
    rel = registered["entries"][kind]
    return read_json(root / rel)


def _required(condition: bool, code: str) -> None:
    if not condition:
        raise ManifestContractError(code)


def _validate_bundle(parts: dict[str, dict[str, Any]], *, root: Path = ROOT) -> None:
    svc = parts["service_policy"]
    discovery = parts["model_discovery"]
    ple = parts["ple_assets"]
    orca = parts["orcarouter_recipe"]
    nvidia = parts["27b_recipe"]
    compat = parts["yslab_compatibility"]

    _required(svc.get("engine") == "vllm-0.32"
              and svc.get("max_active_gpu_models") == 1
              and svc.get("api", {}).get("host_port") == 8000
              and svc.get("transitions", {}).get("stop_old_before_start_new") is True,
              "SERVICE_POLICY_INVARIANTS")
    models = svc.get("models", {})
    found = discovery.get("models", {})
    _required(isinstance(models, dict) and isinstance(found, dict)
              and set(models) == {"flash-next", "27b", "orcarouter"}
              and set(found) == set(models), "MODEL_REGISTRATION_DRIFT")
    _required(discovery.get("ple_asset_manifest") == FILES["ple_assets"]
              and isinstance(discovery.get("cache_roots"), list)
              and discovery.get("include_hf_cache_environment") is True,
              "DISCOVERY_MANIFEST_CONTRACT")
    for key in models:
        descriptor = models[key]
        discovered = found[key]
        _required(isinstance(descriptor, dict) and isinstance(discovered, dict),
                  "MODEL_MANIFEST_INVALID")
        repo = discovered.get("repo_id")
        _required(isinstance(repo, str) and REPO.fullmatch(repo) is not None
                  and descriptor.get("checkpoint") == repo,
                  "MODEL_REPO_REFERENCE_DRIFT")
        pin = discovered.get("pinned_revision")
        _required(pin is None or (isinstance(pin, str) and REV.fullmatch(pin) is not None),
                  "MODEL_REVISION_INVALID")
    _required(models["orcarouter"].get("source_recipe") == FILES["orcarouter_recipe"]
              and models["orcarouter"].get("ple_asset_manifest") == FILES["ple_assets"]
              and models["orcarouter"].get("ple_asset_id") == ASSET_ID
              and found["orcarouter"].get("ple_asset_id") == ASSET_ID
              and orca.get("model", {}).get("ple_asset_id") == ASSET_ID,
              "PLE_MANIFEST_REFERENCE_DRIFT")
    _required(models["orcarouter"].get("pinned_revision") == ORCA_REV
              and found["orcarouter"].get("repo_id") == ORCA
              and found["orcarouter"].get("pinned_revision") == ORCA_REV
              and orca["model"].get("repo_id") == ORCA
              and orca["model"].get("revision") == ORCA_REV,
              "ORCAROUTER_MODEL_PIN_DRIFT")
    _required(models["orcarouter"].get("served_id") is None
              and orca.get("launch_allowed") is False
              and orca.get("register_as_runtime_recipe") is False
              and orca.get("vllm_version") == "0.32.0"
              and orca.get("runtime", {}).get("image_id") is None
              and orca.get("runtime", {}).get("host_port") == 8000
              and orca.get("runtime", {}).get("one_active_model_only") is True,
              "ORCAROUTER_UNRELEASED_RUNTIME_POLICY_DRIFT")
    _required(models["27b"].get("runtime_recipe") == FILES["27b_recipe"]
              and models["27b"].get("served_id") == nvidia.get("model", {}).get("served_id")
              and found["27b"].get("repo_id") == nvidia.get("model", {}).get("repo_id")
              and found["27b"].get("pinned_revision") == nvidia.get("model", {}).get("revision")
              and nvidia.get("runtime", {}).get("port") == 8000,
              "CANONICAL_27B_REFERENCE_DRIFT")
    assets = ple.get("assets", {})
    _required(isinstance(assets, dict) and set(assets) == {ASSET_ID},
              "PLE_REGISTRY_INVALID")
    entry = assets[ASSET_ID]
    _required(entry.get("owner_model") == "orcarouter"
              and entry.get("source", {}).get("repo_id") == ORCA
              and entry.get("source", {}).get("revision") == ORCA_REV
              and entry.get("reference", {}).get("manifest") == FILES["yslab_compatibility"]
              and entry.get("reference", {}).get("target") == "orca-uncensored"
              and entry.get("reference", {}).get("mode") == "direct_bf16"
              and entry.get("layout") == orca["model"].get("expected_ple")
              and entry.get("profiles") == ["mtp0", "mtp2"]
              and entry.get("lifecycle", {}).get("runtime_qualified") is False
              and entry.get("lifecycle", {}).get("source_checkpoint_immutable") is True
              and entry.get("lifecycle", {}).get("delete_requires_separate_approval") is True,
              "PLE_ASSET_CONTRACT_DRIFT")
    layout = entry["layout"]
    _required(layout.get("dtype") == "BF16"
              and layout.get("tensor_count") == layout.get("split_parts") == 128
              and layout.get("total_rows") == 320001536
              and layout.get("width") == 160
              and layout.get("mmap_bytes") == 102400491520
              and layout.get("weight_scale_present") is False,
              "PLE_LAYOUT_DRIFT")
    _required(orca.get("mtp_donor", {}).get("repo_id") == DONOR
              and orca.get("mtp_donor", {}).get("revision") == DONOR_REV
              and orca.get("mtp_donor", {}).get("tensor_count") == 31
              and len(orca.get("mtp_donor", {}).get("shards", [])) == 3,
              "MTP_DONOR_PIN_DRIFT")
    from scripts.p5_vendor.manifest import load_manifest
    from scripts.p5_vendor.mtp import MTP_TENSOR_NAMES
    try:
        upstream = load_manifest(root / FILES["yslab_compatibility"])
    except (OSError, ValueError) as exc:
        raise ManifestContractError("YSLAB_PINNED_MANIFEST_INVALID") from exc
    direct = upstream.target("orca-uncensored")
    overlay = upstream.target("orca-uncensored-bf16-mtp")
    _required(direct.repo_id == ORCA and direct.revision == ORCA_REV
              and direct.mode == "direct_bf16"
              and direct.expected_ple.dtype == layout["dtype"]
              and direct.expected_ple.tensor_count == layout["tensor_count"]
              and direct.expected_ple.total_rows == layout["total_rows"]
              and direct.expected_ple.width == layout["width"]
              and direct.expected_ple.split_parts == layout["split_parts"]
              and direct.expected_ple.layer_id == layout["layer_id"],
              "YSLAB_PLE_REFERENCE_DRIFT")
    donor = overlay.mtp_source
    _required(donor is not None
              and donor.repo_id == DONOR and donor.revision == DONOR_REV
              and donor.tensor_count == len(MTP_TENSOR_NAMES) == 31
              and [(x.filename, x.size, x.sha256) for x in donor.shards] ==
                  [(s["filename"], s["size"], s["sha256"])
                   for s in orca["mtp_donor"]["shards"]],
              "YSLAB_MTP_DONOR_REFERENCE_DRIFT")


def validate(*, root: Path = ROOT) -> dict[str, Any]:
    """Manifest graph validation; no Docker, network, HF/cache, GPU or writes."""
    checks: list[dict[str, Any]] = []
    documents: dict[str, dict[str, Any]] = {}
    errors: set[str] = set()
    try:
        registry(root=root)
        checks.append({"manifest": REGISTRY_FILE, "status": "PASS"})
    except (ManifestContractError, OSError, ValueError, TypeError):
        errors.add("MANIFEST_REGISTRY_INVALID")
        checks.append({"manifest": REGISTRY_FILE, "status": "FAIL"})
    if not errors:
        for kind, rel in FILES.items():
            try:
                document = load(kind, root=root)
                documents[kind] = document
                checks.append({"manifest": rel, "status": "PASS"})
            except (ManifestContractError, OSError, ValueError, TypeError):
                errors.add("MANIFEST_" + kind.upper() + "_INVALID")
                checks.append({"manifest": rel, "status": "FAIL"})
    if not errors:
        try:
            _validate_bundle(documents, root=root)
            checks.append({"manifest": "cross_reference", "status": "PASS"})
        except (ManifestContractError, OSError, ValueError, TypeError, KeyError):
            errors.add("MANIFEST_CROSS_REFERENCE_INVALID")
            checks.append({"manifest": "cross_reference", "status": "FAIL"})
    return {
        "schema_version": 1, "stage": "manifest", "action": "validate",
        "scope": "DECLARATIVE_MANIFEST_ONLY",
        "status": "PASS" if not errors else "FAIL",
        "checks": checks, "issues": sorted(errors),
        "manifest_files_verified": len(documents),
        "registered_models": sorted(documents.get("service_policy", {}).get("models", {})),
        "registered_ple_assets": sorted(documents.get("ple_assets", {}).get("assets", {})),
        "runtime_manifest_gaps": ["FLASH_NEXT_CANONICAL_RECIPE_NOT_REGISTERED",
                                  "ORCAROUTER_RUNTIME_IMAGE_UNQUALIFIED"],
        "execution_release": False,
        "gpu_verified": False, "runtime_qualified": False,
        "source_snapshot_verified": False,
        "executed": False, "operations_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wizard manifest")
    parser.add_argument("action", choices=("status", "validate"), nargs="?", default="status")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    args = parser.parse_args(argv)
    if args.execute or args.approve_plan:
        doc = {"schema_version": 1, "stage": "manifest", "status": "BLOCKED",
               "issues": ["MANIFEST_READ_ONLY"], "executed": False,
               "operations_enabled": False}
    else:
        doc = validate()
        doc["action"] = args.action
    if args.dry_run:
        doc["dry_run"] = True
    if args.json:
        print(json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print("Manifest integrity: " + doc["status"])
        for row in doc.get("checks", []):
            print(f"  {row['manifest']}: {row['status']}")
        for issue in doc["issues"]:
            print("  - " + issue)
    return 0 if doc["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
