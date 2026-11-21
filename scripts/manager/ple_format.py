"""Generic PLE storage format/shape contract; CPU-only, no GPU or file conversion.

A PLE layout is not the inference model dtype, KV cache dtype, or the MTP donor
dtype. The on-disk representation and scale rule belong to each pinned asset.
Future formats may be registered without automatically qualifying a loader.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

STORAGE_DTYPES: dict[str, int] = {
    "BF16": 2, "F16": 2, "F32": 4,
    "F8_E4M3": 1, "F8_E4M3FN": 1, "F8_E5M2": 1,
    "I8": 1, "U8": 1,
}
SCALE_DTYPES = {"F16", "BF16", "F32"}
SCALE_MODES = {"NONE", "PER_TABLE", "PER_TENSOR", "PER_ROW", "PER_BLOCK"}
AUDIT_MODES = {
    "PINNED_REFERENCE_HEADER_AUDIT", "UNQUALIFIED_ADAPTER",
}
ASSET_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,95}$")
MODEL_ID = re.compile(r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$")
PIN = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class PLEFormat:
    dtype: str
    scale_mode: str
    scale_dtype: str | None
    payload_bytes: int
    scale_bytes: int | None
    expected_scale_tensors: int | None
    loader_qualified: bool

    def report(self) -> dict[str, Any]:
        return {
            "storage_dtype": self.dtype,
            "scale_mode": self.scale_mode,
            "scale_dtype": self.scale_dtype,
            "payload_bytes": self.payload_bytes,
            "estimated_scale_bytes": self.scale_bytes,
            "expected_scale_tensors": self.expected_scale_tensors,
            "loader_qualified": self.loader_qualified,
        }


def _positive_int(n: Any) -> bool:
    return type(n) is int and n > 0


def validate_asset(asset_id: str, spec: dict, *, registered_models: set[str] | None = None) -> PLEFormat:
    """Strict structural validation, independent of the YSLAB BF16 reference."""
    if not isinstance(asset_id, str) or not ASSET_ID.fullmatch(asset_id):
        raise ValueError("PLE_ASSET_ID_INVALID")
    if not isinstance(spec, dict):
        raise ValueError("PLE_ASSET_INVALID")
    owner = spec.get("owner_model")
    if not isinstance(owner, str) or not owner or (registered_models is not None and owner not in registered_models):
        raise ValueError("PLE_OWNER_MODEL_UNREGISTERED")
    src, layout, fmt, life, ver = (
        spec.get("source"), spec.get("layout"), spec.get("format"),
        spec.get("lifecycle"), spec.get("verification"),
    )
    if not all(isinstance(x, dict) for x in (src, layout, fmt, life, ver)):
        raise ValueError("PLE_ASSET_REQUIRED_FIELDS")
    if (spec.get("role") != "PLE_NGRAM_EMBEDDING"
        or src.get("kind") != "PINNED_HF_SNAPSHOT"
        or not isinstance(src.get("repo_id"), str)
        or not MODEL_ID.fullmatch(src["repo_id"])
        or not isinstance(src.get("revision"), str)
        or not PIN.fullmatch(src["revision"])):
        raise ValueError("PLE_SOURCE_IDENTITY_INVALID")
    profiles = spec.get("profiles")
    if (not isinstance(profiles, list) or not profiles
        or not all(isinstance(p, str) and p for p in profiles)
        or len(set(profiles)) != len(profiles)):
        raise ValueError("PLE_PROFILE_BINDING_INVALID")

    dtype, mode, scale_dtype = (fmt.get("storage_dtype"),
                                fmt.get("scale_mode"), fmt.get("scale_dtype"))
    if not isinstance(dtype, str) or dtype not in STORAGE_DTYPES:
        raise ValueError("PLE_STORAGE_DTYPE_UNSUPPORTED")
    if not isinstance(mode, str) or mode not in SCALE_MODES:
        raise ValueError("PLE_SCALE_MODE_UNSUPPORTED")
    if not isinstance(fmt.get("packing"), str) or fmt["packing"] != "ELEMENT_ALIGNED":
        raise ValueError("PLE_PACKING_UNQUALIFIED")
    if fmt.get("loader_qualified") is not False:
        raise ValueError("PLE_LOADER_QUALIFICATION_NOT_PROVEN")
    if mode == "NONE" and scale_dtype is not None:
        raise ValueError("PLE_SCALE_DTYPE_MUST_BE_NULL")
    if mode == "PER_TABLE" and dtype not in {"F8_E4M3", "F8_E4M3FN", "F8_E5M2", "I8", "U8"}:
        raise ValueError("PLE_GLOBAL_SCALE_MODE_UNSUPPORTED_FOR_DTYPE")
    if mode != "NONE" and (not isinstance(scale_dtype, str) or scale_dtype not in SCALE_DTYPES):
        raise ValueError("PLE_SCALE_DTYPE_UNSUPPORTED")
    if mode == "PER_BLOCK":
        shape = fmt.get("scale_block_shape")
        if (not isinstance(shape, list) or len(shape) != 2
            or any(not _positive_int(n) for n in shape)):
            raise ValueError("PLE_SCALE_BLOCK_SHAPE_REQUIRED")
    elif fmt.get("scale_block_shape") is not None:
        raise ValueError("PLE_UNEXPECTED_BLOCK_SHAPE")

    for name in ("tensor_count", "total_rows", "width", "split_parts", "layer_id", "mmap_bytes"):
        if not _positive_int(layout.get(name)):
            raise ValueError("PLE_LAYOUT_DIMENSION_INVALID_" + name.upper())
    if layout["tensor_count"] != layout["split_parts"]:
        raise ValueError("PLE_TENSOR_PART_COUNT_DRIFT")
    if layout.get("dtype") != dtype:
        raise ValueError("PLE_LAYOUT_DTYPE_MISMATCH")
    expected_bytes = layout["total_rows"] * layout["width"] * STORAGE_DTYPES[dtype]
    if layout["mmap_bytes"] != expected_bytes:
        raise ValueError("PLE_PAYLOAD_BYTES_MISMATCH")
    has_scale = mode != "NONE"
    if layout.get("weight_scale_present") is not has_scale:
        raise ValueError("PLE_SCALE_PRESENCE_MISMATCH")
    placement = spec.get("placement")
    if not isinstance(placement, dict):
        raise ValueError("PLE_PLACEMENT_REQUIRED")
    if (placement.get("table_memory") not in {"DISK_MMAP", "CPU_MMAP", "GPU"}
        or placement.get("offload_backend") not in {
            "MODEL_SPECIFIC_SOURCE", "NONE", "SOURCE_REFERENCE_ONLY"}
        or placement.get("prewarm") not in (True, False)
        or placement.get("tp1_executor_requirement") not in {
            "VERIFY_ON_TARGET_ENGINE", "NONE", "REQUIRE_MULTIPROC"}
        or placement.get("validated_on_gpu") is not False):
        raise ValueError("PLE_PLACEMENT_UNQUALIFIED")
    if (life.get("managed") is not True
        or life.get("source_checkpoint_immutable") is not True
        or life.get("cache_preserve") is not True
        or life.get("derived_view_separate") is not True
        or life.get("delete_requires_separate_approval") is not True
        or life.get("runtime_qualified") is not False
        or life.get("activation") != "NOT_RUN"):
        raise ValueError("PLE_ASSET_LIFECYCLE_UNSAFE")
    method = ver.get("method")
    if (method not in AUDIT_MODES
        or ver.get("sha256_whole_checkpoint") is not False
        or ver.get("gpu_runtime_verified") is not False):
        raise ValueError("PLE_VERIFICATION_SCOPE_UNSAFE")
    if method == "UNQUALIFIED_ADAPTER" and spec.get("reference") is not None:
        raise ValueError("PLE_UNQUALIFIED_ADAPTER_MUST_NOT_HAVE_A_REFERENCE")
    if method == "PINNED_REFERENCE_HEADER_AUDIT":
        r = spec.get("reference")
        if (not isinstance(r, dict) or not isinstance(r.get("manifest"), str)
            or not isinstance(r.get("target"), str)
            or not isinstance(r.get("mode"), str)):
            raise ValueError("PLE_PINNED_REFERENCE_REQUIRED")
    # In this schema, no integer/FP8 runtime loader is qualified by declaration.
    # Accurate scale payload sizes depend on the actual per-tensor/per-block metadata.
    scale_tensors = (0 if mode == "NONE" else
                     1 if mode == "PER_TABLE" else
                     layout["tensor_count"] if mode == "PER_TENSOR" else None)
    scale_bytes = (0 if mode == "NONE" else
                   scale_tensors * STORAGE_DTYPES[scale_dtype]
                   if scale_tensors is not None else None)
    return PLEFormat(dtype, mode, scale_dtype, expected_bytes,
                     scale_bytes, scale_tensors, False)


def transition_contract(source: dict | None, target: dict | None,
                        *, source_profile: str | None = None,
                        target_profile: str | None = None) -> dict[str, Any]:
    """Model/asset/profile changes always require teardown; never hot-swap a PLE map."""
    source_id = source.get("asset_id") if source else None
    target_id = target.get("asset_id") if target else None
    source_format = source.get("format") if source else None
    target_format = target.get("format") if target else None
    sd = source_format.get("storage_dtype") if isinstance(source_format, dict) else None
    td = target_format.get("storage_dtype") if isinstance(target_format, dict) else None
    if source_id is None and target_id is None:
        mode = "NO_PLE"
    elif source_id is None:
        mode = "LOAD_PLE"
    elif target_id is None:
        mode = "UNLOAD_PLE"
    elif source_id != target_id and sd != td:
        mode = "CHANGE_PLE_DTYPE"
    elif source_id != target_id:
        mode = "REPLACE_PLE_ASSET"
    elif source_profile != target_profile:
        mode = "RELOAD_PROFILE"
    else:
        mode = "SAME_ASSET"
    return {
        "transition": mode, "source_asset_id": source_id, "target_asset_id": target_id,
        "source_dtype": sd, "target_dtype": td,
        "source_profile": source_profile, "target_profile": target_profile,
        "source_scale_mode": (source_format or {}).get("scale_mode"),
        "target_scale_mode": (target_format or {}).get("scale_mode"),
        "hot_reuse_allowed": False,
        "require_stopped_source": True,
        "require_port_8000_free": True,
        "require_gpu_allocation_release": True,
        "require_ple_mmap_release": source_id is not None,
        "require_target_loader_abi": target_id is not None,
        "require_fresh_api_identity": True,
        "require_rollback_assets_preserved": True,
        "executed": False,
        "runtime_qualified": False,
    }
