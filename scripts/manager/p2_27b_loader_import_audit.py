"""Isolated CPU-only import and quantization registry audit for Qwen3.5/ModelOpt.

Does not construct a quantization config, load model weights, create a vLLM
engine, run inference, or access GPUs. The registered vLLM factory is the
authority for quantization names; get_name(self) is NOT a class method.
A restricted runc import failure is not GPU incompatibility evidence.
"""
from __future__ import annotations

import importlib
import json
from typing import Any, Callable

MODEL_MODULE = "vllm.model_executor.models.qwen3_5"
QUANT_MODULE = "vllm.model_executor.layers.quantization.modelopt"
REGISTRY_MODULE = "vllm.model_executor.layers.quantization"
ARCH = "Qwen3_5ForConditionalGeneration"
QUANT_CLASS = "ModelOptMixedPrecisionConfig"
NVFP4_CLASS = "ModelOptNvFp4Config"
QUANT_NAME = "modelopt_mixed"


def audit_installed_imports(*, importer: Callable[[str], Any] = importlib.import_module) -> dict[str, Any]:
    """Check installed symbols and public quantization factory without weights or GPU."""
    checks: dict[str, bool] = {}
    issues: list[str] = []
    loaded: dict[str, Any] = {}
    for kind, name in (
        ("qwen3_5", MODEL_MODULE),
        ("modelopt", QUANT_MODULE),
        ("quant_registry", REGISTRY_MODULE),
    ):
        try:
            loaded[kind] = importer(name)
            checks[kind + "_module_imported"] = True
        except Exception as exc:
            loaded[kind] = None
            checks[kind + "_module_imported"] = False
            # Exception type only: environment paths and exception messages stay local.
            issues.append(kind.upper() + "_IMPORT_FAILED:" + type(exc).__name__)

    model, quant, registry = (
        loaded["qwen3_5"], loaded["modelopt"], loaded["quant_registry"])
    checks["qwen3_5_class_present"] = (
        model is not None and isinstance(getattr(model, ARCH, None), type))
    mixed = getattr(quant, QUANT_CLASS, None) if quant is not None else None
    nvfp4 = getattr(quant, NVFP4_CLASS, None) if quant is not None else None
    checks["modelopt_mixed_class_present"] = isinstance(mixed, type)
    checks["modelopt_nvfp4_class_present"] = isinstance(nvfp4, type)

    # Never call ModelOptMixedPrecisionConfig.get_name() on the class: in
    # vLLM 0.32 its declaration is def get_name(self), requiring an instance.
    # Creating an instance here would initialize a model-specific config;
    # instead, the public registry maps the CLI spelling to the config class.
    factory = (getattr(registry, "get_quantization_config", None)
               if registry is not None else None)
    checks["quant_registry_factory_present"] = callable(factory)
    registered_class = None
    if callable(factory) and isinstance(mixed, type):
        try:
            registered_class = factory(QUANT_NAME)
        except Exception as exc:
            issues.append("MODEL_OPT_REGISTRY_LOOKUP_FAILED:" + type(exc).__name__)
    registry_matches = (
        isinstance(mixed, type)
        and isinstance(registered_class, type)
        and registered_class is mixed)
    checks["modelopt_mixed_registry_class_matches"] = registry_matches
    # Preserve the original check field for machine consumers, but its meaning
    # is now "registered under CLI name", not a zero-argument get_name call.
    checks["modelopt_mixed_cli_name"] = registry_matches
    issues.extend(name.upper() + "_MISSING" for name, passed in checks.items() if not passed)

    return {
        "schema_version": 2, "stage": "p2", "action": "loader-import-audit",
        "scope": "ISOLATED_CPU_PYTHON_IMPORT_AND_REGISTRY_NO_MODEL_LOAD_OR_GPU",
        "status": "IMPORT_AND_REGISTRY_PRESENT_UNQUALIFIED" if not issues else "BLOCKED",
        "checks": checks, "issues": sorted(set(issues)),
        "expected_quantization_name": QUANT_NAME,
        "observed_quantization_name": QUANT_NAME if registry_matches else None,
        "quantization_name_verification": "public_registry_factory_class_identity",
        "gpu_verified": False, "runtime_qualified": False,
        "launch_authorized": False, "executed_gpu": False,
        "notice": (
            "A vLLM import and quantization registry pass is not proof of GPU kernels, "
            "weights loading, memory fit, CLI startup, API behavior or rollback. "
            "An import failure may result from the restricted CPU environment."
        ),
    }


def main() -> int:
    result = audit_installed_imports()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if not result["issues"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
