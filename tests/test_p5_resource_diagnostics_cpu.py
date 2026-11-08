"""Synthetic CPU-only tests for non-mutating P5 resource diagnostics."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import types
import unittest

from scripts.manager import resource_diagnostics as r


class ResourceDiagnosticsCPU(unittest.TestCase):
    def test_meminfo_kib_and_swap_are_not_gpu_double_counted(self):
        result = r._kv_bytes("MemAvailable: 102400 kB\nSwapTotal: 4096 kB\nSwapFree: 1024 kB\n")
        self.assertEqual(result["MemAvailable"], 102400 * 1024)
        self.assertEqual(result["SwapTotal"] - result["SwapFree"], 3072 * 1024)

    def test_pressure_parser_and_missing_file_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "memory"
            self.assertEqual(r._pressure(p)["status"], "UNSUPPORTED")
            p.write_text("some avg10=2.00 avg60=1.00 avg300=0.50 total=99\n"
                         "full avg10=0.00 avg60=0.00 avg300=0.00 total=0\n")
            self.assertEqual(r._pressure(p)["some"]["avg10"], 2.0)

    def test_cpu_khz_conversion_and_governor_are_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            cp = Path(tmp) / "devices/system/cpu/cpu0/cpufreq"
            cp.mkdir(parents=True)
            (cp / "scaling_cur_freq").write_text("2100000\n")
            (cp / "scaling_governor").write_text("schedutil\n")
            info = r._cpu(Path(tmp))
            self.assertEqual(info["current_mhz_mean"], 2100)
            self.assertEqual(info["governors"], ["schedutil"])
            self.assertFalse(info["throttling_verified"])

    def test_docker_never_queries_non_allowlisted_containers(self):
        recipe = {"trial": {"container_name": "qwen38-orcarouter-qsa62318-lmhead-v3"},
                  "runtime": {"container_name": "qwen38-orcarouter"}}
        called = []
        def fake(args, **kwargs):
            called.append(args)
            return types.SimpleNamespace(returncode=0, stdout="portainer\nopen-webui\n")
        info = r._docker(recipe, Path("/unused"), Path("/unused"), fake)
        self.assertEqual(info["status"], "NOT_OBSERVED")
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0][1], "ps")

    def test_cgroup_v2_metrics_fail_closed_on_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "proc/234").mkdir(parents=True)
            (root / "proc/234/cgroup").write_text("0::/user.slice/docker-234.scope\n")
            cg = root / "sys/fs/cgroup/user.slice/docker-234.scope"
            cg.mkdir(parents=True)
            (cg / "memory.current").write_text("9876\n")
            (cg / "memory.events").write_text("oom 0\noom_kill 0\n")
            doc = r._cgroup(root / "proc", root / "sys", 234)
            self.assertEqual(doc["status"], "OBSERVED")
            self.assertEqual(doc["metrics"]["memory.current"], "9876")

    def test_snapshot_marks_preflight_uncalibrated_and_no_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "proc/pressure").mkdir(parents=True)
            (root / "proc/meminfo").write_text(
                "MemTotal: 120000000 kB\nMemAvailable: 80000000 kB\n"
                "SwapTotal: 1024 kB\nSwapFree: 1024 kB\n")
            recipe = {"model": {"repo_id": "orcarouter/test", "revision": "a" * 40,
                        "expected_ple": {"mmap_bytes": 102400491520}},
                      "profiles": {"mtp0": {"served_id": "orcarouter-test"}},
                      "trial": {"container_name": "qwen38-orcarouter-qsa62318-lmhead-v3"},
                      "runtime": {"container_name": "qwen38-orcarouter"},
                      "resource_policy": {"min_mem_available_gib_for_start": None}}
            commands = []
            def fake(args, **kwargs):
                commands.append(args)
                return types.SimpleNamespace(returncode=1, stdout="")
            s = r.snapshot(proc=root / "proc", sysfs=root / "sys",
                           runner=fake, recipe=recipe)
            self.assertEqual(s["status"], "OBSERVED_PARTIAL")
            self.assertFalse(s["resource_limits_changed"])
            self.assertFalse(s["model_identity_verified_by_api"])
            self.assertEqual(s["host_memory"]["swap_used_bytes"], 0)
            self.assertEqual(r.admission(s)["status"], "BLOCKED_UNCALIBRATED")
            self.assertTrue(all(x[0] in ("docker", "nvidia-smi", "git") for x in commands))
            self.assertFalse(any("start" in x or "stop" in x or "update" in x
                                 for x in commands))

    def test_admission_never_claims_launch_authority(self):
        doc = {"recipe_resource_policy": {"min_mem_available_gib_for_start": 100},
               "host_memory": {"MemAvailable_bytes": 110 * r.GIB}}
        result = r.admission(doc)
        self.assertEqual(result["status"], "CAPACITY_CHECK_PASS_NOT_LAUNCH_APPROVAL")
        self.assertFalse(result["launch_authorized"])
        doc["host_memory"]["MemAvailable_bytes"] = 90 * r.GIB
        self.assertEqual(r.admission(doc)["status"], "BLOCKED_CAPACITY")


if __name__ == "__main__":
    unittest.main()
