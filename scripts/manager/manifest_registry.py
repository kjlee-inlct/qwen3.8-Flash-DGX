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
    "ple_loader_profiles": "runtimes/ple-loader-profiles.json",
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


def read_json(path: Path, *, max_bytes: int = MAX_BYTES,
              schema_versions: tuple[int, ...] = (1,)) -> dict[str, Any]:
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
    if (not isinstance(result, dict)
        or type(result.get("schema_version")) is not int
        or result["schema_version"] not in schema_versions):
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
    return read_json(root / rel,
                     schema_versions=(2,) if kind == "ple_assets" else (1,))


def _required(condition: bool, code: str) -> None:
    if not condition:
        raise ManifestContractError(code)


def _validate_bundle(parts: dict[str, dict[str, Any]], *, root: Path = ROOT) -> None:
    svc = parts["service_policy"]
    discovery = parts["model_discovery"]
    ple = parts["ple_assets"]
    loaders = parts["ple_loader_profiles"]
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
              and {"flash-next", "27b", "orcarouter"}.issubset(set(models))
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
    dev_trial = svc.get("transitions", {}).get("trial_overrides", {}).get(
        "p5_orcarouter_mtp0")
    _required(dev_trial == {
        "purpose": "DEVELOPMENT_GPU_TRIAL",
        "source_model": "27b", "target_model": "orcarouter",
        "one_active_model_only": True, "host_api_port": 8000,
        "stop_source_before_target": True,
        "automatic_restore_on_failure": False,
        "retain_stopped_source_container": True,
        "preserve_all_images_and_cached_snapshots": True,
        "requires_exact_plan_and_downtime_ack": True,
        "trial_result_does_not_produce_production_release": True,
    } and svc["transitions"]["failed_new_model_rollback_to_old"] is True,
    "P5_NON_PRODUCTION_NO_ROLLBACK_TRIAL_POLICY_DRIFT")
    _required(orca.get("trial") == {
        "profile": "mtp0",
        "mode": "ONE_SHOT_DEVELOPMENT_GPU_NO_ROLLBACK",
        "start_interface": "./wizard.sh p5 trial",
        "requires_exact_plan": True,
        "automatic_restore_on_failure": False,
        "preserve_source_container_and_image": True,
        "derived_overlay_required": False,
        "production_launch_allowed": False,
        "source_immutable": True,
        "runtime_strategy": "RECIPE_PINNED_QSA62318_LMHEAD_V3_DERIVED_IMAGE_FROM_EXISTING_VLLM032",
        "require_image_build": True,
        "allow_source_patch": False,
        "read_only_image_capability_probe": True,
        "image_source": "VERIFIED_STOPPED_OR_RUNNING_27B_IMAGE_ID",
        "on_incompatible_loader": "FAIL_NO_ROLLBACK_PRESERVE_LOG_AND_CHECKPOINT",
        "p5_env": {
            "HF_HOME": "/hf", "HF_HUB_OFFLINE": "1",
            "VLLM_PLE_MMAP": "1", "VLLM_PLE_MMAP_WORKERS": "16",
            "VLLM_PLE_MMAP_PREWARM": "0",
        },
        "container_name": "qwen38-orcarouter-qsa62318-lmhead-v3",
        "adapter": "qwen4exp-qsa62318-lmhead-v032-v3",
        "image_tag": "blazux-p5-orcarouter:qsa62318-lmhead-v3-v032",
        "allow_isolated_derived_image_source_backport": True,
        "preserve_previous_failed_trial_container": True,
        "allow_idle_source_after_failed_p5": True,
    } and orca.get("compatibility_adapter") == {
        "id": "qwen4exp-qsa62318-lmhead-v032-v3",
        "scope": "P5_ORCAROUTER_MTP0_ONLY",
        "upstream_issue": "https://github.com/vllm-project/vllm/issues/62308",
        "upstream_pr": "https://github.com/vllm-project/vllm/pull/62318",
        "upstream_commit": "fe833b1",
        "dockerfile": "Dockerfile.p5.qsa62318-lmhead-v3",
        "patch_script": "src/p5_qsa_quant_backport_v032.py",
        "lm_head_patch_script": "src/p5_lm_head_quant_backport_v032_v3.py",
        "allowed_vllm_version": "0.32.0",
        "apply_only_in_derived_image": True,
        "preserve_original_27b_image": True,
        "launch_profile": "mtp0",
        "gpu_qualified": False,
        "adapter_qualified": False,
    } and orca.get("runtime", {}).get("source_patch_required") ==
          "SCOPED_QSA62318_AND_LM_HEAD_QUANT_BACKPORT_ISOLATED_IMAGE"
      and orca["runtime"].get("dtype") == "bfloat16"
      and orca["runtime"].get("load_format") == "safetensors"
      and orca.get("profiles", {}).get("mtp0", {}).get("num_speculative_tokens") == 0
      and orca["profiles"]["mtp0"].get("enforce_eager") is True
      and orca["profiles"]["mtp0"].get("enable_native_tools") is True
      and orca["profiles"]["mtp0"].get("tool_call_parser") == "qwen3_coder"
      and orca["profiles"]["mtp0"].get("reasoning_parser") == "qwen3",
      "P5_SCOPED_QSA62318_RECIPE_ADAPTER_DRIFT")
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
    from scripts.manager.ple_format import validate_asset
    assets = ple.get("assets", {})
    _required(ple.get("schema_version") == 2
              and isinstance(assets, dict) and ASSET_ID in assets,
              "PLE_REGISTRY_INVALID")
    _required(ple.get("transition_policy") == {
        "release_source_mmap_before_target": True,
        "verify_gpu_allocation_release": True,
        "stop_old_before_new": True,
        "host_port": 8000,
        "preserve_source_and_rollback_assets": True,
    } and ple.get("compatibility", {}).get("auto_convert_on_switch") is False
      and ple.get("compatibility", {}).get("auto_reuse_mmap_between_models") is False
      and ple.get("compatibility", {}).get(
          "format_change_requires_explicit_runtime_requalification") is True
      and ple.get("compatibility", {}).get(
          "model_ple_dtype_independent_from_inference_dtype") is True
      and ple.get("compatibility", {}).get(
          "independent_inference_dtype_and_kv_cache_dtype") is True,
      "PLE_TRANSITION_POLICY_INVALID")
    for asset_id, spec in assets.items():
        try:
            validate_asset(asset_id, spec, registered_models=set(models))
        except (TypeError, ValueError, KeyError) as exc:
            raise ManifestContractError("PLE_ASSET_FORMAT_INVALID") from exc
    # Any model may reference an explicitly registered format; the PLE on-disk
    # dtype and inference/KV dtype are separate. Never infer a PLE from a model.
    for key, desc in models.items():
        asset_id = desc.get("ple_asset_id")
        discovered_id = found[key].get("ple_asset_id")
        _required(asset_id == discovered_id, "PLE_MODEL_DISCOVERY_BINDING_DRIFT")
        if asset_id is not None:
            _required(asset_id in assets, "PLE_MODEL_ASSET_NOT_REGISTERED")
            owned = assets[asset_id]
            _required(owned["owner_model"] == key
                      and owned["source"]["repo_id"] == found[key]["repo_id"]
                      and owned["source"]["revision"] == found[key]["pinned_revision"],
                      "PLE_MODEL_SOURCE_PIN_DRIFT")
    entry = assets[ASSET_ID]
    _required(entry.get("owner_model") == "orcarouter"
              and entry.get("source", {}).get("repo_id") == ORCA
              and entry.get("source", {}).get("revision") == ORCA_REV
              and entry.get("reference", {}).get("manifest") == FILES["yslab_compatibility"]
              and entry.get("reference", {}).get("target") == "orca-uncensored"
              and entry.get("reference", {}).get("mode") == "direct_bf16"
              and entry.get("layout") == orca["model"].get("expected_ple")
              and entry.get("format") == {
                  "storage_dtype": "BF16", "scale_mode": "NONE",
                  "scale_dtype": None, "scale_block_shape": None,
                  "packing": "ELEMENT_ALIGNED", "loader_qualified": False,
              }
              and entry.get("profiles") == ["mtp0", "mtp2"],
              "PLE_ORCAROUTER_PINNED_CONTRACT_DRIFT")
    _required(entry.get("placement") == {
        "table_memory": "DISK_MMAP",
        "offload_backend": "MODEL_SPECIFIC_SOURCE",
        "prewarm": False,
        "tp1_executor_requirement": "VERIFY_ON_TARGET_ENGINE",
        "validated_on_gpu": False,
    }, "PLE_ORCAROUTER_PLACEMENT_DRIFT")
    layout = entry["layout"]
    _required(layout.get("dtype") == "BF16"
              and layout.get("tensor_count") == layout.get("split_parts") == 128
              and layout.get("total_rows") == 320001536
              and layout.get("width") == 160
              and layout.get("mmap_bytes") == 102400491520
              and layout.get("weight_scale_present") is False,
              "PLE_ORCAROUTER_LAYOUT_DRIFT")
    # Source asset and loader capability are different types of declarations.
    # A separate engine/FP8 reference must never automatically become runnable.
    profile_id = "blazux-vllm032-orcarouter-bf16"
    matrix = loaders.get("profiles", {})
    _required(loaders.get("registry_kind") == "PLE_LOADER_CAPABILITIES"
              and isinstance(matrix, dict)
              and profile_id in matrix
              and orca.get("runtime", {}).get("ple_loader_profile") == profile_id,
              "PLE_LOADER_PROFILE_REFERENCE_DRIFT")
    adapter = matrix[profile_id]
    _required(adapter.get("owner_model") == "orcarouter"
              and adapter.get("ple_asset_id") == ASSET_ID
              and adapter.get("engine") == "vllm"
              and adapter.get("runtime_version") == "0.32.0"
              and adapter.get("hardware") == "NVIDIA_GB10_SM121A"
              and adapter.get("architecture") == "linux/arm64"
              and adapter.get("storage_dtype") == entry["format"]["storage_dtype"]
              and adapter.get("scale_mode") == entry["format"]["scale_mode"]
              and adapter.get("table_memory") == entry["placement"]["table_memory"]
              and adapter.get("mtp_profile_candidates") == ["mtp0", "mtp2"]
              and adapter.get("container_image_digest") is None
              and adapter.get("source_adapter_state") ==
                  "SCOPED_QSA62318_LMHEAD_V3_IMAGE_CANDIDATE_UNQUALIFIED"
              and adapter.get("runtime_strategy") ==
                  "RECIPE_PINNED_QSA62318_LMHEAD_V3_DERIVED_IMAGE_FROM_EXISTING_VLLM032"
              and adapter.get("compatibility_adapter_id") ==
                  orca["compatibility_adapter"]["id"]
              and adapter.get("original_engine_image_patched") is False
              and adapter.get("qsa_upstream_fix") == "vllm-project/vllm#62318"
              and adapter.get("cpu_image_abi_audit_required") is True
              and all(adapter.get(name) is False for name in (
                  "cuda_loader_verified", "tp1_offload_worker_verified",
                  "mmap_gpu_verified", "api_model_identity_verified",
                  "tool_calls_verified", "benchmark_verified",
                  "rollback_verified", "autostart_released"))
              and adapter.get("explicit_gpu_trial_requires_new_guarded_plan") is True,
              "PLE_LOADER_UNQUALIFIED_POLICY_DRIFT")
    refs = loaders.get("external_references", [])
    _required(isinstance(refs, list) and len(refs) >= 2
              and all(ref.get("verified_in_blazux_032") is False
                      and ref.get("import_as_runtime") is False for ref in refs),
              "PLE_EXTERNAL_REFERENCE_MUST_REMAIN_NON_EXECUTABLE")
    rules = loaders.get("policy", {})
    _required(rules.get("port") == 8000
              and rules.get("max_active_gpu_models") == 1
              and rules.get("model_body_quantization_does_not_define_ple_dtype") is True
              and rules.get("mtp_donor_dtype_is_separate") is True
              and rules.get("never_reuse_ple_mmap_across_model_transitions") is True
              and rules.get("require_fresh_runtime_qualified_image_and_rollback") is True
              and rules.get("do_not_copy_external_runtime_flags_without_abi_audit") is True,
              "PLE_LOADER_POLICY_INVALID")
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
        "registered_ple_loader_profiles": sorted(
            documents.get("ple_loader_profiles", {}).get("profiles", {})),
        "external_ple_references_count": len(
            documents.get("ple_loader_profiles", {}).get("external_references", [])),
        "registered_ple_formats": {
            name: spec.get("format", {}).get("storage_dtype")
            for name, spec in documents.get("ple_assets", {}).get("assets", {}).items()
        },
        "ple_manifest_schema": documents.get("ple_assets", {}).get("schema_version"),
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
