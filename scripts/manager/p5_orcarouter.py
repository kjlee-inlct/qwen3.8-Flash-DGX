"""P5 Orcarouter BF16PLE source adapter and scoped acceptance controller.

The P5 source path is deliberately independent of NVIDIA/27B launchers.
No function in this module starts/stops Docker, loads GPUs, downloads models,
writes HF files, creates an overlay or changes the active :8000 service.
The vetted, pinned YSLAB reference auditors live in scripts.p5_vendor.
GPU launch cannot be approved until the Blazux 0.32 ABI and rollback are proven.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable

from scripts.manager import manifest_registry
from scripts.manager.ple_assets import (ASSET_ID as PLE_ID, asset_spec as ple_asset_spec,
                                        configured_roots as ple_cache_roots,
                                        inspect_ple_asset)
from scripts.p5_vendor.audit import audit_checkpoint
from scripts.p5_vendor.manifest import load_manifest
from scripts.p5_vendor.mtp import MTP_TENSOR_NAMES, MTP_QUANTIZATION_IGNORE, mtp_overlay_fingerprint
from scripts.p5_vendor.safetensors import read_header, strict_json_loads

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "scripts" / "p5_vendor"
RECIPE_PATH = ROOT / "recipes" / "qwen38-orcarouter.runtime.json"
ORCA_REPO = "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4"
ORCA_REV = "3a3b63161c0745390e5270179af42e46efc70799"
DONOR_REPO = "RadixArk/Qwen3.8-Flash-Next-NVFP4"
DONOR_REV = "7b719225242aacd3dbd3f9407468c2ee9a9d2594"
SOURCE_COMMIT = "9492b78c6bc04638587b42f2ffeb0680b0fcb3ef"
PASS = "PASS"
BLOCKED = "BLOCKED"
NOT_RUN = "NOT_RUN"
INCONCLUSIVE = "INCONCLUSIVE"
FAIL = "FAIL"
GPU_EXECUTION_RELEASED = False
_APPROVAL = re.compile(r"[a-f0-9]{64}\Z")


def _gate(name: str, status: str, *issues: str, **extra) -> dict:
    return {"gate": name, "status": status, "issues": list(issues),
            "evidence": None, **extra}


def _recipe() -> dict:
    raw = RECIPE_PATH.read_bytes()
    if len(raw) > 32_768:
        raise ValueError("P5_RECIPE_TOO_LARGE")
    data = manifest_registry.read_json(RECIPE_PATH, max_bytes=32_768)
    if not isinstance(data, dict):
        raise ValueError("P5_RECIPE_INVALID")
    source = data.get("model", {})
    donor = data.get("mtp_donor", {})
    runtime = data.get("runtime", {})
    profiles = data.get("profiles", {})
    if not (
        data.get("schema_version") == 1
        and data.get("recipe_id") == "qwen38-orcarouter-bf16ple-p5"
        and data.get("engine") == "vllm"
        and data.get("vllm_version") == "0.32.0"
        and data.get("launch_allowed") is False
        and data.get("register_as_runtime_recipe") is False
        and source.get("repo_id") == ORCA_REPO
        and source.get("revision") == ORCA_REV
        and source.get("quantization") == "compressed-tensors"
        and source.get("ple_asset_id") == PLE_ID
        and donor.get("repo_id") == DONOR_REPO
        and donor.get("revision") == DONOR_REV
        and donor.get("tensor_count") == 31
        and runtime.get("host_port") == 8000
        and runtime.get("one_active_model_only") is True
        and runtime.get("image_id") is None
        and set(profiles) == {"mtp0", "mtp2"}
        and profiles["mtp0"].get("num_speculative_tokens") == 0
        and profiles["mtp2"].get("num_speculative_tokens") == 2
        and profiles["mtp0"].get("served_id") != profiles["mtp2"].get("served_id")
        and all(p.get("ple_mmap") is True and p.get("ple_prewarm") is False
                and p.get("kv_cache_dtype") == "bfloat16"
                and p.get("cuda_graph") == "PIECEWISE" for p in profiles.values())
    ):
        raise ValueError("P5_RECIPE_POLICY_OR_PIN_MISMATCH")
    manifest = load_manifest(VENDOR / "compatibility.json")
    baseline, overlay = manifest.target("orca-uncensored"), manifest.target("orca-uncensored-bf16-mtp")
    if (baseline.repo_id != ORCA_REPO or overlay.repo_id != ORCA_REPO
            or baseline.revision != ORCA_REV or overlay.revision != ORCA_REV
            or baseline.mode != "direct_bf16" or overlay.mode != "mtp_overlay"
            or overlay.mtp_source is None
            or overlay.mtp_source.repo_id != DONOR_REPO
            or overlay.mtp_source.revision != DONOR_REV
            or len(overlay.mtp_source.shards) != 3
            or overlay.mtp_source.tensor_count != len(MTP_TENSOR_NAMES)
            or len(set(MTP_TENSOR_NAMES)) != 31
            or len(MTP_QUANTIZATION_IGNORE) != len(set(MTP_QUANTIZATION_IGNORE))
            or baseline.expected_ple.dtype != "BF16"
            or baseline.expected_ple.tensor_count != 128
            or baseline.expected_ple.total_rows != 320001536
            or baseline.expected_ple.width != 160
            or baseline.expected_ple.split_parts != 128):
        raise ValueError("P5_REFERENCE_CONTRACT_MISMATCH")
    if [(s.filename, s.size, s.sha256) for s in overlay.mtp_source.shards] != [
            (s["filename"], s["size"], s["sha256"]) for s in donor.get("shards", [])]:
        raise ValueError("P5_DONOR_HASH_MANIFEST_MISMATCH")
    # PLE is an independently registered asset: no divergent inline geometry.
    ple_entry = ple_asset_spec(source["ple_asset_id"])
    if source.get("expected_ple") != ple_entry["layout"]:
        raise ValueError("P5_PLE_RECIPE_MANIFEST_DRIFT")
    return data


def abi_source_audit() -> dict:
    """Prove only static vLLM 0.32 *Blazux source* hooks, not installed GPU ABI."""
    try:
        recipe = _recipe()
        code = (ROOT / "src" / "vllm_ple_mmap.py").read_text(encoding="utf-8")
        ast.parse(code)
        required = ('"BF16": torch.bfloat16', "VLLM_PLE_MMAP_PREWARM",
                    "def parse_safetensors_header(", "def _setup_table(",
                    "def apply(cls: type)", "Qwen4ExpPLEDeviceEmbedding",
                    "ple_mmap_lookup_ids", "torch.bfloat16")
        if not all(marker in code for marker in required):
            raise ValueError("P5_BLAZUX_BF16_PLE_HOOK_MISSING")
        patch_source = (ROOT / "src/p5_patch_qwen4exp_v032.py").read_text(encoding="utf-8")
        ast.parse(patch_source)
        patch_markers = ("VLLM_P5_ORCAROUTER", "compressed-tensors ignore remap",
                         "quant_config=(self.quant_config if ",
                         "native BF16 MTP tensor mismatch",
                         "P5_EXPLICIT_IMAGE_BUILD", 'VLLM = "0.32.0"')
        if not all(marker in patch_source for marker in patch_markers):
            raise ValueError("P5_VLLM032_CANDIDATE_PATCH_INCOMPLETE")
        candidate_dockerfile = (ROOT / "Dockerfile.p5.candidate").read_text(
            encoding="utf-8")
        if ("ARG P5_QUALIFIED_BASE_IMAGE" not in candidate_dockerfile or
                "P5_EXPLICIT_IMAGE_BUILD=1" not in candidate_dockerfile):
            raise ValueError("P5_ISOLATED_DOCKER_CANDIDATE_CONTRACT_FAILED")
        if recipe["runtime"]["image_id"] is not None:
            raise ValueError("P5_RUNTIME_IMAGE_UNQUALIFIED")
        return _gate("blazux_032_source_hooks", PASS,
                     ple_bf16_static_hook=True,
                     quantized_lm_head_source_patch_candidate=True,
                     compressed_tensors_ignore_source_patch_candidate=True,
                     native_mtp_31_bf16_guard_source_patch_candidate=True,
                     gpu_abi_verified=False, mtp_runtime_abi_verified=False)
    except (OSError, ValueError, SyntaxError, TypeError, KeyError):
        return _gate("blazux_032_source_hooks", FAIL, "P5_SOURCE_OR_RECIPE_CONTRACT_FAILED",
                     gpu_abi_verified=False)


def _repo_snapshot(cache_root: Path, repo_id: str, revision: str) -> Path:
    if (repo_id, revision) not in ((ORCA_REPO, ORCA_REV), (DONOR_REPO, DONOR_REV)):
        raise ValueError("UNTRUSTED_HF_IDENTITY")
    return cache_root / "hub" / ("models--" + repo_id.replace("/", "--")) / "snapshots" / revision


def _cache_roots() -> list[Path]:
    return ple_cache_roots()


def _audited_snapshot(repo_id: str, revision: str, roots: list[Path]) -> tuple[Path | None, Path | None]:
    for root in roots:
        path = _repo_snapshot(root, repo_id, revision)
        if path.is_dir() and not path.is_symlink():
            return path, root
    return None, None


def audit_ple(*, roots: list[Path] | None = None) -> dict:
    """Canonical manifest-led pinned PLE metadata audit (not GPU activation)."""
    return inspect_ple_asset(asset_id=PLE_ID, roots=roots)


def audit_donor(*, roots: list[Path] | None = None) -> dict:
    """Read-only 3-shard full SHA256 and 31 BF16 tensor metadata verification."""
    try:
        manifest = load_manifest(VENDOR / "compatibility.json")
        source = manifest.target("orca-uncensored-bf16-mtp").mtp_source
        if source is None:
            raise ValueError("DONOR_NOT_DECLARED")
        roots = _cache_roots() if roots is None else roots
        snapshot, root = _audited_snapshot(DONOR_REPO, DONOR_REV, roots)
        if snapshot is None or root is None:
            return _gate("mtp_donor_31", BLOCKED, "PINNED_MTP_DONOR_SNAPSHOT_NOT_PRESENT")
        weight_path = snapshot / "model.safetensors.index.json"
        if weight_path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError("DONOR_INDEX_TOO_LARGE")
        index = strict_json_loads(weight_path.read_bytes())
        weight_map = index["weight_map"]
        selected = {k: v for k, v in weight_map.items() if k.startswith("mtp.")}
        if set(selected) != set(MTP_TENSOR_NAMES):
            raise ValueError("MTP_31_NAMES_MISMATCH")
        if set(selected.values()) != {s.filename for s in source.shards}:
            raise ValueError("DONOR_SHARD_MAP_MISMATCH")
        observed: dict[str, tuple] = {}
        for shard in source.shards:
            file = snapshot / shard.filename
            resolved = file.resolve(strict=True)
            if not resolved.is_file() or not resolved.is_relative_to(root.resolve(strict=True)):
                raise ValueError("DONOR_SHARD_ESCAPES_CACHE")
            if resolved.stat().st_size != shard.size:
                raise ValueError("DONOR_SHARD_SIZE_MISMATCH")
            digest = hashlib.sha256()
            with resolved.open("rb") as handle:
                for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                    digest.update(block)
            if digest.hexdigest() != shard.sha256:
                raise ValueError("DONOR_SHARD_DIGEST_MISMATCH")
            header = read_header(resolved)
            for name, meta in header.items():
                if name in selected and selected[name] == shard.filename:
                    if (meta.dtype != "BF16" or not meta.shape
                            or any(type(dim) is not int or dim <= 0 for dim in meta.shape)):
                        raise ValueError("MTP_DTYPE_OR_SHAPE_INVALID")
                    size = 2
                    for dim in meta.shape:
                        size *= dim
                    if size != meta.data_end - meta.data_start:
                        raise ValueError("MTP_TENSOR_BYTES_INVALID")
                    if name in observed:
                        raise ValueError("MTP_DUPLICATE_HEADER")
                    observed[name] = meta.shape
        if set(observed) != set(MTP_TENSOR_NAMES):
            raise ValueError("MTP_INDEX_HEADER_DISAGREEMENT")
        return _gate("mtp_donor_31", PASS, tensor_count=31,
                     pinned_shards_verified=3, dtype="BF16",
                     sha256_verified=True, gpu_mtp_load_verified=False)
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
        return _gate("mtp_donor_31", BLOCKED, "MTP_DONOR_INTEGRITY_OR_LAYOUT_FAILED",
                     sha256_verified=False, gpu_mtp_load_verified=False)


def source_plan(profile: str = "mtp0") -> dict:
    if profile not in ("mtp0", "mtp2"):
        raise ValueError("UNKNOWN_P5_PROFILE")
    static = abi_source_audit()
    manifest_integrity = manifest_registry.validate()
    loader_id = _recipe()["runtime"]["ple_loader_profile"]
    loader = manifest_registry.load("ple_loader_profiles")["profiles"][loader_id]
    fingerprint = hashlib.sha256(
        (ORCA_REPO + ORCA_REV + DONOR_REV + SOURCE_COMMIT + profile).encode()
    ).hexdigest()
    return {
        "schema_version": 1, "stage": "p5", "action": "PLAN",
        "profile": profile, "status": BLOCKED, "scope": "SOURCE_ONLY",
        "source_reference": SOURCE_COMMIT, "vllm_version": "0.32.0",
        "host_api_port": 8000, "one_active_model_only": True,
        "manifest_integrity": manifest_integrity,
        "ple_loader_profile": {"profile_id": loader_id, **loader},
        "ple_asset": {"asset_id": PLE_ID,
                      "manifest": "runtimes/ple-assets.json",
                      "expected": ple_asset_spec()["layout"],
                      "metadata_verified": False, "runtime_mmap_status": NOT_RUN},
        "stages": [static,
                   _gate("bf16_direct_ple", NOT_RUN),
                   _gate("mtp_donor_31", NOT_RUN),
                   _gate("mtp_overlay", NOT_RUN, overlay_fingerprint=mtp_overlay_fingerprint(
                       load_manifest(VENDOR / "compatibility.json").target("orca-uncensored-bf16-mtp"))),
                   _gate("installed_vllm_032_abi", BLOCKED, "DGX_CONTAINER_ABI_NOT_VERIFIED"),
                   _gate("gpu_api_benchmark_rollback", NOT_RUN)],
        "preview_fingerprint_not_approval": fingerprint,
        "plan_id": None, "approval_accepted": False,
        "operations_enabled": False, "executed": False,
        "issues": ["P5_GPU_ABI_AND_ROLLBACK_UNQUALIFIED"],
        "requires_separate_dgx_downtime_approval": True,
    }


def cpu_only() -> dict:
    static = abi_source_audit()
    manifest_integrity = manifest_registry.validate()
    if static["status"] != PASS:
        result = _gate("cpu_fake_dgx", FAIL, "P5_SOURCE_CONTRACT_INVALID")
    else:
        try:
            run = subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests",
                 "-p", "test_p5_*_cpu.py", "-v"],
                cwd=ROOT, capture_output=True, text=True, timeout=240,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            cases = []
            for line in run.stderr.splitlines():
                match = re.fullmatch(
                    r"(test_[A-Za-z0-9_]+) \(test_p5_[^)]+\) \.\.\. (ok|FAIL|ERROR)",
                    line.strip(),
                )
                if match:
                    cases.append({"case": match.group(1),
                                  "status": PASS if match.group(2) == "ok" else FAIL})
            summary = next((line.strip() for line in reversed(run.stderr.splitlines())
                            if line.startswith("Ran ")), None)
            expected = re.fullmatch(r"Ran ([0-9]+) tests? in [0-9.]+s", summary or "")
            success = (run.returncode == 0 and "OK" in run.stderr
                       and expected is not None and int(expected.group(1)) == len(cases)
                       and bool(cases) and all(case["status"] == PASS for case in cases))
            result = _gate("cpu_fake_dgx", PASS if success else FAIL,
                           *([] if success else ["P5_CPU_TESTS_FAILED"]),
                           exit_code=run.returncode, test_summary=summary,
                           test_cases=cases,
                           failure_details=run.stderr[-5000:] if not success else None)
        except (OSError, subprocess.TimeoutExpired):
            result = _gate("cpu_fake_dgx", INCONCLUSIVE, "P5_CPU_RUNNER_UNAVAILABLE")
    return {
        "schema_version": 1, "stage": "p5", "mode": "cpu-only",
        "status": PASS if static["status"] == PASS and result["status"] == PASS
        and manifest_integrity["status"] == PASS else FAIL,
        "scope": "CPU_FAKE_DGX_ONLY", "manifest_integrity": manifest_integrity,
        "stages": [static, result,
                    _gate("dgx_read_only", NOT_RUN),
                    _gate("gpu_api_benchmark_rollback", NOT_RUN)],
        "executed": False, "approval_accepted": False,
        "operations_enabled": False, "gpu_verified": False,
        "issues": sorted(set(static["issues"] + result["issues"] +
                             manifest_integrity["issues"])),
    }


def read_only(*, roots: list[Path] | None = None,
              service_inspector: Callable[[], dict] | None = None) -> dict:
    static = abi_source_audit()
    manifest_integrity = manifest_registry.validate()
    loader_id = _recipe()["runtime"]["ple_loader_profile"]
    loader = manifest_registry.load("ple_loader_profiles")["profiles"][loader_id]
    ple = audit_ple(roots=roots)
    donor = audit_donor(roots=roots)
    idle_inspector = None
    if service_inspector is None:
        from scripts.manager.service_status import inspect_live_status
        from scripts.manager.service_manifest import inspect_service
        service_inspector = inspect_live_status
        idle_inspector = inspect_service
    try:
        live = service_inspector()
        if (idle_inspector is not None
            and live.get("status") != "LIVE_SERVICE_VERIFIED"
            and live.get("observed_model") is None):
            # No active API is normal on an idle development DGX. Do not
            # mistake a missing API for proof that all GPUs are free.
            raw_idle = idle_inspector()
            if (raw_idle.get("status") == "OBSERVED_UNQUALIFIED"
                and raw_idle.get("observed_model") is None
                and raw_idle.get("observed_state") == "NO_MANAGED_MODEL_RUNNING"
                and raw_idle.get("api_port_8000_listening") is False
                and raw_idle.get("issues") == []):
                live = raw_idle
        existing_27b = (live.get("status") == "LIVE_SERVICE_VERIFIED"
                        and live.get("observed_model") == "27b"
                        and live.get("expected_served_id") == "qwen3.8-27b"
                        and live.get("host_port") == 8000
                        and live.get("issues") == [])
        stopped = (live.get("status") == "OBSERVED_UNQUALIFIED"
                   and live.get("observed_state") == "NO_MANAGED_MODEL_RUNNING"
                   and live.get("api_port_8000_listening") is False
                   and live.get("issues") == [])
        safe = existing_27b or stopped
        svc = _gate("service_preflight", PASS if safe else BLOCKED,
                    *([] if safe else ["SINGLE_MODEL_PORT_8000_NOT_VERIFIED"]),
                    observed_model=live.get("observed_model") if existing_27b else None,
                    downtime_27b_permitted=True,
                    service_state=("27B_RUNNING" if existing_27b else
                                   "STOPPED_PORT_FREE" if stopped else "UNKNOWN"))
    except (OSError, ValueError, RuntimeError, TypeError, KeyError):
        svc = _gate("preserve_live_27b", INCONCLUSIVE, "LIVE_STATUS_UNAVAILABLE")
    gates = [static, ple, donor, svc, _gate("mtp_overlay", NOT_RUN),
             _gate("gpu_api_benchmark_rollback", NOT_RUN)]
    status = (PASS if manifest_integrity["status"] == PASS and
              all(g["status"] == PASS for g in gates[:4]) else BLOCKED)
    return {"schema_version": 1, "stage": "p5", "mode": "read-only",
            "scope": "DGX_READ_ONLY", "status": status, "stages": gates,
            "manifest_integrity": manifest_integrity,
            "ple_asset": ple,
            "ple_loader_profile": {"profile_id": loader_id, **loader},
            "issues": sorted(set([i for g in gates for i in g["issues"]] +
                                 manifest_integrity["issues"])),
            "executed": False, "approval_accepted": False,
            "operations_enabled": False, "gpu_verified": False,
            "production_released": False}


def stage_action(action: str, *, profile: str = "mtp0",
                 execute: bool = False, approve_plan: str | None = None) -> dict:
    if action not in ("status", "doctor", "recipe", "prepare", "start", "verify", "benchmark"):
        raise ValueError("UNKNOWN_P5_ACTION")
    plan = source_plan(profile)
    issues = list(plan["issues"])
    if execute or approve_plan:
        issues.append("UNVERIFIED_APPROVAL_CANNOT_EXECUTE")
    ple = (audit_ple() if action in ("status", "doctor", "recipe")
           else plan["ple_asset"])
    return {"schema_version": 1, "stage": "p5", "action": action,
            "status": BLOCKED if action != "status" else BLOCKED,
            "runtime": NOT_RUN, "profile": profile, "implementation": "SOURCE_ADAPTER_AVAILABLE",
            "source_audit": plan["stages"][0],
            "manifest_integrity": plan["manifest_integrity"],
            "ple_asset": ple,
            "ple_loader_profile": plan["ple_loader_profile"],
            "recipe_path": "recipes/qwen38-orcarouter.runtime.json",
            "checkpoint": ORCA_REPO, "revision": ORCA_REV,
            "served_id": _recipe()["profiles"][profile]["served_id"],
            "profile_preview": _recipe()["profiles"][profile],
            "overlay_fingerprint_not_approval": plan["stages"][3]["overlay_fingerprint"],
            "api_port": 8000, "issues": sorted(set(issues)),
            "plan_id": None, "executed": False,
            "operations_enabled": False, "approval_accepted": False,
            "gpu_verified": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="p5-one-shot-acceptance")
    mode = parser.add_mutually_exclusive_group(required=True)
    for option in ("--plan", "--cpu-only", "--read-only", "--gpu-trial"):
        mode.add_argument(option, action="store_true")
    parser.add_argument("--profile", choices=("mtp0", "mtp2"), default="mtp0")
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.gpu_trial or args.approve_plan or args.ack_downtime:
        plan = source_plan(args.profile)
        plan.update(action="GPU_TRIAL", status=BLOCKED,
                    issues=["P5_GPU_TRIAL_EXECUTOR_NOT_RELEASED",
                            "SEPARATE_APPROVAL_AND_VERIFIED_RESTORE_REQUIRED"],
                    approval_accepted=False, executed=False)
        doc = plan
    elif args.plan:
        doc = source_plan(args.profile)
    elif args.cpu_only:
        doc = cpu_only()
    else:
        doc = read_only()
    print(json.dumps(doc, ensure_ascii=False, indent=2 if args.json else None,
                     sort_keys=True))
    return 0 if doc["status"] == PASS else 3


if __name__ == "__main__":
    raise SystemExit(main())
