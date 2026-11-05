"""P2 isolated CPU import source contract (fake modules, no Docker/GPU)."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest

from scripts.manager.p2_27b_loader_import_audit import (
    audit_installed_imports, MODEL_MODULE, QUANT_MODULE,
)


def fake_import(name):
    class Qwen3_5ForConditionalGeneration:
        pass

    class ModelOptMixedPrecisionConfig:
        @classmethod
        def get_name(cls):
            return "modelopt_mixed"

    class ModelOptNvFp4Config:
        pass

    if name == MODEL_MODULE:
        return SimpleNamespace(Qwen3_5ForConditionalGeneration=Qwen3_5ForConditionalGeneration)
    if name == QUANT_MODULE:
        return SimpleNamespace(ModelOptMixedPrecisionConfig=ModelOptMixedPrecisionConfig,
                               ModelOptNvFp4Config=ModelOptNvFp4Config)
    raise ImportError("unknown")


class P2LoaderImportCPU(unittest.TestCase):
    def test_valid_imports_do_not_grant_launch(self):
        r = audit_installed_imports(importer=fake_import)
        self.assertEqual(r["status"], "IMPORT_SURFACES_PRESENT_UNQUALIFIED")
        self.assertTrue(all(r["checks"].values()))
        self.assertFalse(r["runtime_qualified"])
        self.assertFalse(r["launch_authorized"])
        self.assertFalse(r["executed_gpu"])
        json.dumps(r)

    def test_model_import_exception_sanitized_and_blocked(self):
        def broken(name):
            if name == MODEL_MODULE:
                raise ImportError("secret-looking-message")
            return fake_import(name)
        r = audit_installed_imports(importer=broken)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertIn("QWEN3_5_IMPORT_FAILED:ImportError", r["issues"])
        self.assertNotIn("secret-looking-message", json.dumps(r))

    def test_quant_import_failure(self):
        def broken(name):
            if name == QUANT_MODULE:
                raise RuntimeError("test")
            return fake_import(name)
        r = audit_installed_imports(importer=broken)
        self.assertIn("MODELOPT_IMPORT_FAILED:RuntimeError", r["issues"])

    def test_wrong_name_fails(self):
        def wrong(name):
            o = fake_import(name)
            if name == QUANT_MODULE:
                o.ModelOptMixedPrecisionConfig.get_name = classmethod(lambda cls: "wrong")
            return o
        r = audit_installed_imports(importer=wrong)
        self.assertIn("MODELOPT_MIXED_CLI_NAME_MISSING", r["issues"])

    def test_missing_architecture_class(self):
        def wrong(name):
            o = fake_import(name)
            if name == MODEL_MODULE:
                delattr(o, "Qwen3_5ForConditionalGeneration")
            return o
        r = audit_installed_imports(importer=wrong)
        self.assertIn("QWEN3_5_CLASS_PRESENT_MISSING", r["issues"])

    def test_name_lookup_exception(self):
        def wrong(name):
            o = fake_import(name)
            if name == QUANT_MODULE:
                o.ModelOptMixedPrecisionConfig.get_name = classmethod(
                    lambda cls: (_ for _ in ()).throw(ValueError("bad")))
            return o
        r = audit_installed_imports(importer=wrong)
        self.assertIn("MODEL_OPT_NAME_LOOKUP_FAILED:ValueError", r["issues"])

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

    def test_python_module_does_not_instantiate_engine(self):
        src = Path("scripts/manager/p2_27b_loader_import_audit.py").read_text()
        for item in ("import torch", "LLM(", "load_model(", "subprocess"):
            self.assertNotIn(item, src)


if __name__ == "__main__":
    unittest.main()
