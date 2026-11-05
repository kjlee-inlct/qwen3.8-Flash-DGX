"""P2 read-only static-image source audit unit tests (no Docker/GPU)."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts.manager.p2_27b_image_audit import audit_image_source

class P2ImageSourceCPU(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, p, s):
        f = self.root / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(s)

    def setup_valid(self):
        self.write("vllm/model_executor/models/registry.py",
                   """REG={'Qwen3_5ForConditionalGeneration': ('qwen3_5','Qwen3_5ForConditionalGeneration')}""")
        self.write("vllm/model_executor/models/qwen3_5.py",
                   "class Qwen3_5ForConditionalGeneration: pass")
        self.write("vllm/model_executor/layers/quantization/modelopt.py",
                   "class ModelOptMixedPrecisionConfig: pass\n"
                   "class ModelOptNvFp4Config: pass\n"
                   "ALGO=('NVFP4','FP8','MIXED_PRECISION')")

    def test_all_source_symbols_do_not_authorize_gpu(self):
        self.setup_valid()
        res = audit_image_source(self.root)
        self.assertEqual(res["status"], "SOURCE_SURFACES_PRESENT_UNQUALIFIED")
        self.assertFalse(res["runtime_qualified"])
        self.assertFalse(res["launch_authorized"])
        self.assertTrue(all(res["checks"].values()))
        json.dumps(res)

    def test_comments_not_accepted_as_registry(self):
        self.setup_valid()
        self.write("vllm/model_executor/models/registry.py",
                   "# Qwen3_5ForConditionalGeneration\nR={}")
        self.assertFalse(audit_image_source(self.root)["checks"]["model_registry_27b_architecture"])

    def test_missing_class_fails_closed(self):
        self.setup_valid()
        self.write("vllm/model_executor/models/qwen3_5.py", "class Other: pass")
        self.assertIn("QWEN3_5_CLASS_MISSING", audit_image_source(self.root)["issues"])

    def test_missing_quant_algorithm_fails_closed(self):
        self.setup_valid()
        self.write("vllm/model_executor/layers/quantization/modelopt.py",
                   "class ModelOptMixedPrecisionConfig: pass\n"
                   "class ModelOptNvFp4Config: pass\n"
                   "ALGO=('NVFP4','FP8')")
        self.assertFalse(audit_image_source(self.root)["checks"]["modelopt_nvfp4_fp8_mixed_algorithms"])

    def test_malformed_source_fails_closed(self):
        self.setup_valid()
        self.write("vllm/model_executor/models/qwen3_5.py", "def broken(")
        self.assertEqual(audit_image_source(self.root)["files"]["qwen3_5"]["status"],
                         "INVALID_OR_UNREADABLE")

    def test_oversized_source_fails_closed(self):
        self.setup_valid()
        self.write("vllm/model_executor/models/qwen3_5.py", " " * (4*1024*1024 + 1))
        self.assertEqual(audit_image_source(self.root)["files"]["qwen3_5"]["status"],
                         "SIZE_REJECTED")

    def test_vllm_new_registry_layout(self):
        self.setup_valid()
        a = self.root / "vllm/model_executor/models/registry.py"
        b = self.root / "vllm/models/registry.py"
        b.parent.mkdir(parents=True, exist_ok=True)
        a.rename(b)
        self.assertTrue(all(audit_image_source(self.root)["checks"].values()))

    def test_cpu_sandbox_shell_static_contract(self):
        p = "scripts/temporary/p2-27b-image-audit.sh"
        script = Path(p).read_text()
        subprocess.run(["bash", "-n", p], check=True, timeout=5)
        for arg in ("--runtime runc", "--network none", "--read-only", "--pull never"):
            self.assertIn(arg, script)
        for forbidden in ("docker stop", "docker rm -f", "docker system prune", "--gpus all"):
            self.assertNotIn(forbidden, script)

if __name__ == "__main__":
    unittest.main()
