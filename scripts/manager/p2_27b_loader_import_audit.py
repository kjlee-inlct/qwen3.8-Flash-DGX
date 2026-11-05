"""Isolated CPU-only import audit: Qwen3.5 model and ModelOpt mixed config.

Does not initialize a vLLM engine, import a checkpoint, run inference, or use GPUs.
Restricted runc sandbox import failure is not proof of GPU incompatibility.
"""
from __future__ import annotations

import importlib
import json
from typing import Any, Callable

MODEL_MODULE = "vllm.model_executor.models.qwen3_5"
QUANT_MODULE = "vllm.model_executor.layers.quantization.modelopt"
ARCH = "Qwen3_5ForConditionalGeneration"
QUANT_CLASS = "ModelOptMixedPrecisionConfig"
NVFP4_CLASS = "ModelOptNvFp4Config"
QUANT_NAME = "modelopt_mixed"


def audit_installed_imports(*, importer: Callable[[str], Any] = importlib.import_module) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    issues: list[str] = []
    loaded: dict[str, Any] = {}
    for kind, name in (("qwen3_5", MODEL_MODULE), ("modelopt", QUANT_MODULE)):
        try:
            loaded[kind] = importer(name)
            checks[kind + "_module_imported"] = True
        except Exception as exc:
            loaded[kind] = None
            checks[kind + "_module_imported"] = False
            issues.append(kind.upper() + "_IMPORT_FAILED:" + type(exc).__name__)
    model, quant = loaded["qwen3_5"], loaded["modelopt"]
    checks["qwen3_5_class_present"] = (
        model is not None and isinstance(getattr(model, ARCH, None), type))
    mixed = getattr(quant, QUANT_CLASS, None) if quant is not None else None
    nvfp4 = getattr(quant, NVFP4_CLASS, None) if quant is not None else None
    checks["modelopt_mixed_class_present"] = isinstance(mixed, type)
    checks["modelopt_nvfp4_class_present"] = isinstance(nvfp4, type)
    found_name = None
    if isinstance(mixed, type):
        try:
            get_name = getattr(mixed, "get_name")
            found_name = get_name() if callable(get_name) else None
        except Exception as exc:
            issues.append("MODEL_OPT_NAME_LOOKUP_FAILED:" + type(exc).__name__)
    checks["modelopt_mixed_cli_name"] = found_name == QUANT_NAME
    issues.extend(name.upper() + "_MISSING" for name, passed in checks.items() if not passed)
    return {
        "schema_version": 1, "stage": "p2", "action": "loader-import-audit",
        "scope": "ISOLATED_CPU_PYTHON_IMPORT_NO_MODEL_LOAD_OR_GPU",
        "status": "IMPORT_SURFACES_PRESENT_UNQUALIFIED" if not issues else "BLOCKED",
        "checks": checks, "issues": sorted(set(issues)),
        "expected_quantization_name": QUANT_NAME,
        "observed_quantization_name": (
            found_name if isinstance(found_name, str) and len(found_name) < 80 else None),
        "gpu_verified": False, "runtime_qualified": False,
        "launch_authorized": False, "executed_gpu": False,
        "notice": ("CPU-only imports do not prove GPU kernels, checkpoint loading, memory fit, "
                   "API, performance, or rollback. Failures may be caused by the CPU sandbox."),
    }


def main() -> int:
    result = audit_installed_imports()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if not result["issues"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
