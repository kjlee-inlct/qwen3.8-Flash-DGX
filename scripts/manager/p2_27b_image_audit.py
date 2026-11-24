"""No-GPU, no-import static audit of the installed vLLM 0.32 source tree."""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path

ARCH = "Qwen3_5ForConditionalGeneration"
SITES = ("/usr/local/lib/python3.12/dist-packages",
         "/usr/local/lib/python3.12/site-packages")
SURFACES = {
    "registry": ("vllm/model_executor/models/registry.py",
                 "vllm/models/registry.py"),
    "qwen3_5": ("vllm/model_executor/models/qwen3_5.py",
                "vllm/models/qwen3_5.py"),
    "modelopt": ("vllm/model_executor/layers/quantization/modelopt.py",),
}
MAX_FILE_BYTES = 4 * 1024 * 1024

def _parse(root: Path, paths: tuple[str, ...]) -> dict:
    for name in paths:
        file = root / name
        try:
            if not file.is_file():
                continue
            size = file.stat().st_size
            if not 0 < size <= MAX_FILE_BYTES:
                return {"status": "SIZE_REJECTED", "path": name}
            tree = ast.parse(file.read_text(encoding="utf-8"))
            return {"status": "PARSED", "path": name,
                    "strings": {n.value for n in ast.walk(tree)
                                if isinstance(n, ast.Constant) and isinstance(n.value, str)},
                    "classes": {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}}
        except (OSError, UnicodeError, SyntaxError, MemoryError, RecursionError):
            return {"status": "INVALID_OR_UNREADABLE", "path": name}
    return {"status": "MISSING"}

def audit_image_source(root: Path) -> dict:
    found = {kind: _parse(root, paths) for kind, paths in SURFACES.items()}
    reg, model, quant = (found[kind] for kind in ("registry","qwen3_5","modelopt"))
    checks = {
        "model_registry_27b_architecture": reg["status"] == "PARSED" and ARCH in reg["strings"],
        "qwen3_5_class": model["status"] == "PARSED" and ARCH in model["classes"],
        "modelopt_nvfp4_mixed_config_classes": quant["status"] == "PARSED" and {
            "ModelOptMixedPrecisionConfig", "ModelOptNvFp4Config"
        }.issubset(quant["classes"]),
        "modelopt_nvfp4_fp8_mixed_algorithms": quant["status"] == "PARSED" and {
            "NVFP4", "FP8", "MIXED_PRECISION"
        }.issubset(quant["strings"]),
    }
    issues = [k.upper()+"_MISSING" for k,v in checks.items() if not v]
    return {
        "schema_version": 1, "stage": "p2", "action": "image-source-audit",
        "scope": "STATIC_SOURCE_NO_IMPORT_OR_GPU",
        "status": "SOURCE_SURFACES_PRESENT_UNQUALIFIED" if not issues else "BLOCKED",
        "checks": checks, "issues": issues, "files": {
            k: {a:b for a,b in v.items() if a in ("status","path")}
            for k,v in found.items()},
        "gpu_verified": False, "runtime_qualified": False,
        "launch_authorized": False, "executed_gpu": False,
        "notice": "Presence of vLLM source symbols does not prove import, kernel, model load or API behavior.",
    }

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", type=Path)
    args = parser.parse_args(argv)
    roots = [args.site_root] if args.site_root else [Path(p) for p in SITES]
    root = next((p for p in roots if (p / "vllm").is_dir()), roots[0])
    data = audit_image_source(root)
    print(json.dumps(data, sort_keys=True, indent=2))
    return 0 if not data["issues"] else 3

if __name__ == "__main__":
    raise SystemExit(main())
