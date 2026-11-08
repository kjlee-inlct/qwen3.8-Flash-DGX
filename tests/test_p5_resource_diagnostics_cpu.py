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

    def test_nvme_observation_delta_has_correct_units(self):
        a = {"timestamp_utc": "2026-11-08T00:00:00+00:00",
             "nvme": {"drives": {"nvme0n1": {"read_ios": 2, "read_sectors": 10,
                       "write_ios": 1, "write_sectors": 4,
                       "read_time_ms": 10, "write_time_ms": 5}}},
             "host_memory": {"MemAvailable_bytes": 100},
             "pressure": {"memory": {"some": {"avg10": 3.0}}}}
        b = {"timestamp_utc": "2026-11-08T00:00:10+00:00",
             "nvme": {"drives": {"nvme0n1": {"read_ios": 4, "read_sectors": 30,
                       "write_ios": 2, "write_sectors": 14,
                       "read_time_ms": 30, "write_time_ms": 15}}},
             "host_memory": {"MemAvailable_bytes": 90},
             "pressure": {"memory": {"some": {"avg10": 4.0}}}}
        summary = r.observation_summary([a, b])
        self.assertEqual(summary["status"], "OBSERVED_INTERVAL")
        self.assertEqual(summary["nvme_rates"]["nvme0n1"]["read_bytes_per_second"], 1024)
        self.assertEqual(summary["nvme_rates"]["nvme0n1"]["avg_read_time_ms_per_io"], 10)
        self.assertEqual(summary["min_mem_available_bytes"], 90)

    def test_advisory_warnings_never_change_cpu_or_memory_limits(self):
        snapshot = {"recipe_resource_policy": {
            "max_memory_psi_some_avg10_pct_warn": 5.0,
            "max_swap_used_gib_warn": 2.0},
            "pressure": {"memory": {"some": {"avg10": 10.0}}},
            "host_memory": {"swap_used_bytes": 3 * r.GIB}}
        result = r.evaluate_warnings(snapshot)
        self.assertEqual(result["status"], "WARNING")
        self.assertEqual(len(result["issues"]), 2)
        self.assertFalse(result["resource_limits_changed"])

    def test_host_cpu_utilization_from_cumulative_proc_ticks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stat").write_text("cpu 100 0 100 700 100 0 0 0\n")
            out = r._cpu_usage_counters(root)
            self.assertEqual(out["total_ticks"], 1000)
            self.assertEqual(out["idle_ticks"], 800)

    def test_cgroup_stat_explains_docker_cli_cache_subtraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "proc/42").mkdir(parents=True)
            (root / "proc/42/cgroup").write_text("0::/container\n")
            folder = root / "sys/fs/cgroup/container"
            folder.mkdir(parents=True)
            (folder / "memory.current").write_text("1000000000\n")
            (folder / "memory.stat").write_text(
                "anon 150000000\nfile 850000000\ninactive_file 700000000\n"
                "file_mapped 300000000\npgmajfault 17\nworkingset_refault_file 10\n")
            (folder / "memory.swap.current").write_text("4096\n")
            result = r._cgroup(root / "proc", root / "sys", 42)
            metrics = result["metrics"]
            self.assertEqual(metrics["docker_cli_derived_usage_bytes"], 300000000)
            self.assertEqual(metrics["memory_stat_bytes"]["file_mapped"], 300000000)
            self.assertEqual(metrics["memory_stat_counters"]["pgmajfault"], 17)
            self.assertEqual(metrics["memory.swap.current"], "4096")
            self.assertFalse((folder / "memory.max").exists())

    def test_vmstat_swap_activity_is_rate_not_accumulated_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "vmstat").write_text("pswpin 100\npswpout 30\npgmajfault 900\n")
            observed = r._vmstat(root)
            self.assertEqual(observed["counters"]["pswpin"], 100)
            before = {"timestamp_utc": "2026-11-08T00:00:00+00:00",
                      "vmstat": {"counters": {"pswpin": 100, "pswpout": 30,
                                             "pgmajfault": 900}}}
            after = {"timestamp_utc": "2026-11-08T00:00:10+00:00",
                     "vmstat": {"counters": {"pswpin": 130, "pswpout": 30,
                                            "pgmajfault": 905}}}
            interval = r.observation_summary([before, after])
            self.assertEqual(interval["host_vmstat_rates"]["pswpin_per_second"], 3.0)
            self.assertEqual(interval["host_vmstat_rates"]["pswpout_per_second"], 0.0)
            self.assertIsNone(interval["cgroup_fault_deltas"]["pgmajfault_delta"])

    def test_wizard_resources_route_is_read_only(self):
        from unittest.mock import patch
        from wizard.main import main as wizard_main
        with patch("scripts.manager.resource_diagnostics.main", return_value=0) as mock_main:
            rc = wizard_main(["operations", "resources", "snapshot", "--json"])
        self.assertEqual(rc, 0)
        mock_main.assert_called_once_with(["snapshot", "--json"])

    def test_admission_never_claims_launch_authority(self):
        doc = {"recipe_resource_policy": {"min_mem_available_gib_for_start": 100},
               "host_memory": {"MemAvailable_bytes": 110 * r.GIB}}
        result = r.admission(doc)
        self.assertEqual(result["status"], "CAPACITY_CHECK_PASS_NOT_LAUNCH_APPROVAL")
        self.assertFalse(result["launch_authorized"])
        doc["host_memory"]["MemAvailable_bytes"] = 90 * r.GIB
        self.assertEqual(r.admission(doc)["status"], "BLOCKED_CAPACITY")


    def test_cgroup_interval_requires_same_observed_docker_identity(self):
        def row(timestamp, cid, major, oom):
            return {"timestamp_utc": timestamp,
                    "docker": {"container": {"id": cid},
                               "cgroup_v2": {"metrics": {
                                   "memory_stat_counters": {
                                       "pgmajfault": major,
                                       "workingset_refault_file": major + 2},
                                   "memory.events": {"oom": oom, "oom_kill": 0}}}}}
        a = row("2026-11-09T00:00:00+00:00", "a" * 64, 10, 0)
        b = row("2026-11-09T00:00:10+00:00", "a" * 64, 13, 1)
        report = r.observation_summary([a, b])
        self.assertTrue(report["cgroup_container_identity_continuous"])
        self.assertEqual(report["cgroup_fault_deltas"]["pgmajfault_delta"], 3)
        self.assertEqual(report["cgroup_memory_event_deltas"]["oom_delta"], 1)
        b["docker"]["container"]["id"] = "b" * 64
        report = r.observation_summary([a, b])
        self.assertFalse(report["cgroup_container_identity_continuous"])
        self.assertTrue(report["cgroup_identity_discontinuity_detected"])
        self.assertIsNone(report["cgroup_fault_deltas"]["pgmajfault_delta"])
        self.assertIsNone(report["cgroup_memory_event_deltas"]["oom_delta"])

    def test_missing_container_identity_does_not_claim_valid_fault_deltas(self):
        a = {"timestamp_utc": "2026-11-09T00:00:00+00:00",
             "docker": {"cgroup_v2": {"metrics": {
                 "memory_stat_counters": {"pgmajfault": 20}}}}}
        b = {"timestamp_utc": "2026-11-09T00:00:10+00:00",
             "docker": {"cgroup_v2": {"metrics": {
                 "memory_stat_counters": {"pgmajfault": 25}}}}}
        report = r.observation_summary([a, b])
        self.assertIsNone(report["cgroup_container_identity_continuous"])
        self.assertIsNone(report["cgroup_fault_deltas"]["pgmajfault_delta"])



if __name__ == "__main__":
    unittest.main()
