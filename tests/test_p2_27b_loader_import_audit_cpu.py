"""Realistic CPU-only ModelOpt vLLM 0.32 import and registry unit tests."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest

from scripts.manager.p2_27b_loader_import_audit import (
    audit_installed_imports, MODEL_MODULE, QUANT_MODULE, REGISTRY_MODULE,
)


def fake_modules():
    class Qwen3_5ForConditionalGeneration:
        pass

    class ModelOptMixedPrecisionConfig:
        # The *actual* vLLM 0.32 signature has a self parameter.
        # The audit must never instantiate the class or invoke get_name().
        def get_name(self):
            raise AssertionError("get_name(self) may not be invoked by CPU audit")

    class ModelOptNvFp4Config:
        pass

    model = SimpleNamespace(Qwen3_5ForConditionalGeneration=Qwen3_5ForConditionalGeneration)
    quant = SimpleNamespace(ModelOptMixedPrecisionConfig=ModelOptMixedPrecisionConfig,
                            ModelOptNvFp4Config=ModelOptNvFp4Config)

    def lookup(name):
        if name == "modelopt_mixed":
            return ModelOptMixedPrecisionConfig
        raise ValueError("bad quantization name")

    registry = SimpleNamespace(get_quantization_config=lookup)
    modules = {MODEL_MODULE: model, QUANT_MODULE: quant,
               REGISTRY_MODULE: registry}
    return modules


def importer_for(modules):
    def importer(name):
        if name not in modules:
            raise ImportError("unexpected module")
        return modules[name]
    return importer


class P2LoaderImportCPU(unittest.TestCase):
    def test_instance_get_name_not_called_and_registration_passes(self):
        r = audit_installed_imports(importer=importer_for(fake_modules()))
        self.assertEqual(r["status"], "IMPORT_AND_REGISTRY_PRESENT_UNQUALIFIED")
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(r["observed_quantization_name"], "modelopt_mixed")
        self.assertEqual(r["quantization_name_verification"],
                         "public_registry_factory_class_identity")
        self.assertFalse(r["runtime_qualified"])
        self.assertFalse(r["launch_authorized"])
        self.assertFalse(r["executed_gpu"])
        json.dumps(r)

    def test_model_import_exception_sanitized_and_blocked(self):
        modules = fake_modules()
        del modules[MODEL_MODULE]
        r = audit_installed_imports(importer=importer_for(modules))
        self.assertEqual(r["status"], "BLOCKED")
        self.assertIn("QWEN3_5_IMPORT_FAILED:ImportError", r["issues"])

    def test_quant_import_failure(self):
        modules = fake_modules()
        del modules[QUANT_MODULE]
        r = audit_installed_imports(importer=importer_for(modules))
        self.assertIn("MODELOPT_IMPORT_FAILED:ImportError", r["issues"])

    def test_registry_import_failure(self):
        modules = fake_modules()
        del modules[REGISTRY_MODULE]
        r = audit_installed_imports(importer=importer_for(modules))
        self.assertIn("QUANT_REGISTRY_IMPORT_FAILED:ImportError", r["issues"])
        self.assertFalse(r["checks"]["modelopt_mixed_cli_name"])

    def test_missing_factory_fails_closed(self):
        modules = fake_modules()
        modules[REGISTRY_MODULE] = SimpleNamespace()
        r = audit_installed_imports(importer=importer_for(modules))
        self.assertFalse(r["checks"]["quant_registry_factory_present"])
        self.assertIsNone(r["observed_quantization_name"])

    def test_wrong_registry_class_does_not_pass(self):
        modules = fake_modules()
        modules[REGISTRY_MODULE].get_quantization_config = lambda name: type("OtherConfig", (), {})
        r = audit_installed_imports(importer=importer_for(modules))
        self.assertIn("MODELOPT_MIXED_REGISTRY_CLASS_MATCHES_MISSING", r["issues"])
        self.assertFalse(r["checks"]["modelopt_mixed_cli_name"])

    def test_registry_lookup_error_does_not_leak_message(self):
        modules = fake_modules()

        def fail(name):
            raise ValueError("secret-looking-message")

        modules[REGISTRY_MODULE].get_quantization_config = fail
        r = audit_installed_imports(importer=importer_for(modules))
        self.assertEqual(r["status"], "BLOCKED")
        self.assertIn("MODEL_OPT_REGISTRY_LOOKUP_FAILED:ValueError", r["issues"])
        self.assertNotIn("secret-looking-message", json.dumps(r))

    def test_registry_called_with_exact_name_only(self):
        modules = fake_modules()
        called = []
        original = modules[REGISTRY_MODULE].get_quantization_config

        def traced(name):
            called.append(name)
            return original(name)

        modules[REGISTRY_MODULE].get_quantization_config = traced
        r = audit_installed_imports(importer=importer_for(modules))
        self.assertEqual(called, ["modelopt_mixed"])
        self.assertTrue(r["checks"]["modelopt_mixed_cli_name"])

    def test_missing_architecture_class(self):
        modules = fake_modules()
        delattr(modules[MODEL_MODULE], "Qwen3_5ForConditionalGeneration")
        r = audit_installed_imports(importer=importer_for(modules))
        self.assertIn("QWEN3_5_CLASS_PRESENT_MISSING", r["issues"])

    def test_cpu_shell_constraints(self):
        path = Path("scripts/temporary/p2-27b-loader-import-audit.sh")
        src = path.read_text()
        subprocess.run(["bash", "-n", str(path)], check=True, timeout=10)
        for item in ("--runtime runc", "--network none", "--read-only",
                     "--pull never", "--cap-drop ALL", "--pids-limit 128",
                     "--memory 2g", "--cpus 2", "--execute-cpu-only"):
            self.assertIn(item, src)
        for item in ("--gpus all", "--privileged", "docker stop", "docker rm -f",
                     "-p 8000:8000", "HF_CACHE"):
            self.assertNotIn(item, src)

    def test_python_module_does_not_instantiate_engine_or_quant_config(self):
        src = Path("scripts/manager/p2_27b_loader_import_audit.py").read_text()
        for item in ("import torch", "LLM(", "load_model(", "subprocess",
                     "mixed.get_name(", "mixed("):
            self.assertNotIn(item, src)


if __name__ == "__main__":
    unittest.main()
