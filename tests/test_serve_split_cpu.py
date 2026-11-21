"""CPU-only regression: legacy and model-specific serve script entrypoints."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

def shell(path,*args):
    return subprocess.run(["bash",str(ROOT/path),*args],
                          text=True,capture_output=True,timeout=10,
                          env={"PATH":os.environ.get("PATH","/usr/bin:/bin"),
                               "HOME":os.environ.get("HOME","/tmp")})

class ServeSplitCPU(unittest.TestCase):
    def test_shell_syntax(self):
        subprocess.run(["bash","-n",*[str(ROOT/p) for p in (
            "flash","scripts/serve.sh","scripts/serve_flash-next.sh",
            "scripts/serve_27b.sh")]],check=True,timeout=10)

    def test_default_and_explicit_dispatch(self):
        dispatch=(ROOT/"scripts/serve.sh").read_text()
        self.assertIn('model="flash-next"',dispatch)
        self.assertIn('exec "$HERE/serve_flash-next.sh"',dispatch)
        self.assertIn('exec "$HERE/serve_27b.sh" "$@"',dispatch)

    def test_flash_wrapper_calls_flash_next_directly(self):
        src=(ROOT/"flash").read_text()
        self.assertIn('exec "$HERE/scripts/serve_flash-next.sh"',src)

    def test_flash_next_old_engine_intact(self):
        src=(ROOT/"scripts/serve_flash-next.sh").read_text()
        for word in ("VLLM_PLE_MMAP=1","VLLM_QSA_EXACT_TOPK",
                     "VLLM_MTP_DRAFT_VOCAB","docker run -d",
                     "refusing implicit replacement"):
            self.assertIn(word,src)

    def test_27b_plan_only_no_hidden_docker_invocation(self):
        src=(ROOT/"scripts/serve_27b.sh").read_text()
        self.assertIn("--launch-preview",src)
        self.assertIn("--inspect-runtime",src)
        self.assertNotIn("docker run",src.lower())
        self.assertNotIn("docker stop",src.lower())
        self.assertNotIn("VLLM_PLE_MMAP=1",src)

    def test_27b_execution_blocked(self):
        cases=(("scripts/serve_27b.sh","--execute"),
               ("scripts/serve_27b.sh","start"),
               ("scripts/serve.sh","27b","--execute"),
               ("scripts/serve.sh","--model","27b","--execute"))
        for path,*args in cases:
            with self.subTest(path=path,args=args):
                r=shell(path,*args)
                self.assertEqual(r.returncode,3,r.stdout+r.stderr)
                self.assertIn("BLOCKED",r.stderr)

    def test_help_never_launches(self):
        for path in ("scripts/serve.sh","scripts/serve_27b.sh"):
            r=shell(path,"--help")
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn("27b",r.stdout.lower())

    def test_unknown_selection_blocks(self):
        cases=(("--model",),("--model","unknown"),
               ("flash-next","--execute"),("--random",))
        for args in cases:
            self.assertEqual(shell("scripts/serve.sh",*args).returncode,2)
        self.assertEqual(shell("scripts/serve_27b.sh","--invalid").returncode,2)

    def test_no_27b_via_flash_next_legacy_override(self):
        src=(ROOT/"scripts/serve_flash-next.sh").read_text()
        self.assertIn('if [[ "$MODEL" == "nvidia/Qwen3.8-27B-NVFP4" ]]',src)
        self.assertIn("scripts/serve_27b.sh",src)

    def test_27b_read_only_preview_cannot_start(self):
        p=(ROOT/"scripts/manager/p2_27b_launch_preview.py").read_text()
        self.assertIn('"operations_enabled": False',p)
        self.assertIn('"plan_id": None',p)
        self.assertIn('"status": "BLOCKED"',p)

if __name__=="__main__":
    unittest.main()
