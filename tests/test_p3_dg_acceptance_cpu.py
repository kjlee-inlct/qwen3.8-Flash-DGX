"""P3-D/E/F/G unified draft runner CPU/Fake-DGX tests. Zero Docker/GPU work."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p3_dg_acceptance as dg
from scripts.manager import operational_switch as op

IDENT = "a" * 64
IMAGE = "sha256:" + "9" * 64


def observed_flash():
    checkpoint = ("/hf/hub/models--nvidia--Qwen3.8-Flash-Next-NVFP4/snapshots/"
                  "fc694b54fb0174e0913e6adf86691ef85a4ead47")
    return {
        "Name": "/qwen38-flash",
        "Id": IDENT,
        "Image": IMAGE,
        "State": {"Running": False},
        "HostConfig": {"DeviceRequests": [{"Count": -1, "Capabilities": [["gpu"]]}],
                       "PortBindings": {"8000/tcp": [{"HostPort": "8000"}]},
                       "ShmSize": 16 * 1024 ** 3, "IpcMode": "host"},
        "Config": {
            "Cmd": [checkpoint, "--host", "0.0.0.0", "--port", "8000",
                    "--served-model-name", "qwen3.8-flash-next"],
            "Env": ["HF_HOME=/hf", "HF_HUB_OFFLINE=1"],
            "Labels": {},
        },
        "Mounts": [{"Type": "bind", "Destination": "/hf",
                    "Source": "/home/inlc/.cache/huggingface", "RW": False}],
    }


def snapshot():
    return {"running": ["qwen38-27b"], "gpu_running": ["qwen38-27b"],
            "port_owners": ["qwen38-27b"],
            "containers": {"qwen38-27b": {"Id": IDENT},
                           "qwen38-flash": observed_flash()}}


def verified_live():
    return {"status": "LIVE_SERVICE_VERIFIED",
            "observed_model": "27b", "expected_served_id": "qwen3.8-27b",
            "issues": []}


class DraftUnifiedRunnerCPU(unittest.TestCase):
    def test_d_pass_with_independent_gpu_and_port_process_proof(self):
        calls = []
        def runner(args, timeout=12):
            calls.append(args)
            if args[0] == "ss":
                return SimpleNamespace(returncode=0,
                                       stdout='LISTEN 0 128 *:8000 *:* users:(("python",pid=14,fd=3))\n')
            if args[0] == "nvidia-smi":
                return SimpleNamespace(returncode=0, stdout="17, python\n")
            raise AssertionError("unexpected mutating process")
        out = dg.stage_d(snapshot(), verified_live(), run=runner,
                         proc_owner=lambda pid, cid: cid == IDENT and pid in (14, 17))
        self.assertEqual(out["status"], "READ_ONLY_PASS")
        self.assertTrue(out["gpu_process_exclusivity_verified"])
        self.assertTrue(out["port_process_ownership_verified"])
        self.assertEqual([x[0] for x in calls], ["ss", "nvidia-smi"])
        self.assertFalse(out["executed"])

    def test_d_accepts_ipv4_and_ipv6_same_qualified_container(self):
        def runner(args, timeout=12):
            if args[0] == "ss":
                return SimpleNamespace(
                    returncode=0, stdout=(
                        'LISTEN 0 4096 0.0.0.0:8000 0.0.0.0:* users:(("python",pid=14,fd=3))\\n'
                        'LISTEN 0 4096 [::]:8000 [::]:* users:(("python",pid=14,fd=5))\\n'))
            return SimpleNamespace(returncode=0, stdout="17, python\\n")
        out = dg.stage_d(snapshot(), verified_live(), run=runner,
                         proc_owner=lambda pid, cid: pid in (14, 17) and cid == IDENT)
        self.assertEqual(out["status"], "READ_ONLY_PASS")
        self.assertEqual(len(out["observed_port_listener_rows"]), 2)
        self.assertEqual(out["observed_port_pids"], [14])
        self.assertTrue(out["port_process_ownership_verified"])

    def test_d_rejects_dual_stack_unattributed_second_listener(self):
        def runner(args, timeout=12):
            if args[0] == "ss":
                return SimpleNamespace(
                    returncode=0, stdout=(
                        'LISTEN 0 4096 0.0.0.0:8000 0.0.0.0:* users:(("python",pid=14,fd=3))\\n'
                        'LISTEN 0 4096 [::]:8000 [::]:*\\n'))
            return SimpleNamespace(returncode=0, stdout="17, python\\n")
        out = dg.stage_d(snapshot(), verified_live(), run=runner,
                         proc_owner=lambda pid, cid: True)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("HOST_PORT_PROCESS_PID_UNAVAILABLE", out["issues"])

    def test_d_sockets_without_pid_never_report_pass(self):
        def runner(args, timeout=12):
            if args[0] == "ss":
                return SimpleNamespace(returncode=0, stdout=
                                       "LISTEN 0 4096 0.0.0.0:8000 0.0.0.0:*\\n")
            return SimpleNamespace(returncode=0, stdout="17, python\\n")
        out = dg.stage_d(snapshot(), verified_live(), run=runner,
                         proc_owner=lambda pid, cid: True)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("HOST_PORT_PROCESS_PID_UNAVAILABLE", out["issues"])

    def test_d_peer_8000_not_mistaken_as_local_listener(self):
        self.assertFalse(dg._ss_local_port_8000(
            "LISTEN 0 100 127.0.0.1:8080 127.0.0.1:8000"))
        self.assertTrue(dg._ss_local_port_8000(
            "LISTEN 0 100 [::]:8000 [::]:*"))

    def test_d_does_not_claim_success_when_ss_proxy_cannot_be_attributed(self):
        def runner(args, timeout=12):
            if args[0] == "ss":
                return SimpleNamespace(returncode=0,
                                       stdout='LISTEN 0 128 *:8000 *:* users:(("docker-proxy",pid=5,fd=3))\n')
            return SimpleNamespace(returncode=0, stdout="17, python\n")
        out = dg.stage_d(snapshot(), verified_live(), run=runner,
                         proc_owner=lambda pid, cid: pid == 17)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("HOST_PORT_PROCESS_CONTAINER_OWNERSHIP_UNVERIFIED", out["issues"])

    def test_d_gpu_unknown_cannot_be_interpreted_as_pass(self):
        def runner(args, timeout=12):
            if args[0] == "ss":
                return SimpleNamespace(returncode=0,
                                       stdout='LISTEN 0 128 *:8000 *:* users:(("python",pid=14,fd=3))\n')
            return SimpleNamespace(returncode=1, stdout="")
        out = dg.stage_d(snapshot(), verified_live(), run=runner,
                         proc_owner=lambda pid, cid: True)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("GPU_COMPUTE_PROCESS_QUERY_UNAVAILABLE", out["issues"])
        self.assertFalse(out["gpu_process_exclusivity_verified"])

    def test_d_unmanaged_gpu_container_is_blocked(self):
        fake = snapshot()
        fake["gpu_running"].append("foreign_gpu")
        def runner(args, timeout=12):
            return SimpleNamespace(returncode=0,
                                   stdout=('LISTEN *:8000 pid=14\n'
                                           if args[0] == "ss" else '17, python\n'))
        out = dg.stage_d(fake, verified_live(), run=runner,
                         proc_owner=lambda pid, cid: True)
        self.assertIn("DOCKER_GPU_EXCLUSIVITY_NOT_VERIFIED", out["issues"])

    def test_proc_cgroup_needs_real_docker_identity_match(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "55").mkdir()
            (root / "55" / "cgroup").write_text("0::/system.slice/docker-" + IDENT + ".scope\n")
            self.assertTrue(dg.proc_belongs(55, IDENT, root=root))
            self.assertFalse(dg.proc_belongs(55, "b"*64, root=root))
            self.assertFalse(dg.proc_belongs(54, IDENT, root=root))

    def test_e_pins_observation_but_no_flash_canonical_reinstall_qualification(self):
        history = {"status": "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED",
                   "records": {"a": {"flash_id": IDENT, "flash_image": IMAGE}},
                   "issues": []}
        out = dg.stage_e(snapshot(), historical=history)
        self.assertEqual(out["status"], "DRAFT_REVIEW_REQUIRED")
        self.assertFalse(out["canonical_recipe_registered"])
        self.assertEqual(out["observed_candidate"]["container_id"], IDENT)
        self.assertIn("FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED", out["issues"])

    def test_e_legacy_vllm_command_does_not_erase_flash_candidate(self):
        legacy = snapshot()
        cmd = legacy["containers"]["qwen38-flash"]["Config"]["Cmd"]
        legacy["containers"]["qwen38-flash"]["Config"]["Cmd"] = [
            "vllm", "serve", *cmd, "--enable-chunked-prefill"]
        history = {"status": "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED",
                   "records": {"a": {"flash_id": IDENT, "flash_image": IMAGE}},
                   "issues": []}
        out = dg.stage_e(legacy, historical=history)
        self.assertEqual(out["status"], "DRAFT_REVIEW_REQUIRED")
        self.assertEqual(out["issues"], ["FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED"])
        self.assertEqual(out["observed_candidate"]["cmd_normalized"], False)
        self.assertIn("FLASH_LEGACY_COMMAND_NEEDS_MODEL_SPECIFIC_NORMALIZER",
                      out["advisories"])
        self.assertIn("vllm", out["observed_candidate"]["raw_cmd"])

    def test_e_legacy_writable_hf_mount_is_a_review_advisory(self):
        legacy = snapshot()
        legacy["containers"]["qwen38-flash"]["Mounts"][0]["RW"] = True
        history = {"status": "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED",
                   "records": {"a": {"flash_id": IDENT, "flash_image": IMAGE}},
                   "issues": []}
        out = dg.stage_e(legacy, historical=history)
        self.assertEqual(out["status"], "DRAFT_REVIEW_REQUIRED")
        self.assertIn("FLASH_LEGACY_HF_MOUNT_WRITABLE_REINSTALL_REVIEW",
                      out["advisories"])
        self.assertEqual(out["observed_candidate"]["hf_mount"]["read_only"], False)

    def test_e_wrong_flash_model_path_and_served_id_still_block(self):
        legacy = snapshot()
        legacy["containers"]["qwen38-flash"]["Config"]["Cmd"] = [
            "/hf/hub/models--other--model/snapshots/" + "1"*40,
            "--served-model-name", "unknown", "--port", "8000"]
        history = {"status": "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED",
                   "records": {"a": {"flash_id": IDENT, "flash_image": IMAGE}},
                   "issues": []}
        out = dg.stage_e(legacy, historical=history)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("FLASH_CHECKPOINT_REVISION_UNVERIFIED", out["issues"])
        self.assertIn("FLASH_SERVED_ID_NOT_QUALIFIED", out["issues"])

    def test_e_rejects_unrecognized_flash_docker_recreation(self):
        history = {"status": "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED",
                   "records": {"a": {"flash_id": "b"*64, "flash_image": IMAGE}},
                   "issues": []}
        out = dg.stage_e(snapshot(), historical=history)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("FLASH_HISTORICAL_PROVENANCE_UNVERIFIED", out["issues"])

    def test_f_cpu_suite_pass_with_captured_unittest_counts(self):
        requested = []
        def runner(args, **kwargs):
            requested.append(args[-2])
            return SimpleNamespace(returncode=0, stdout="",
                                   stderr="Ran 3 tests in 0.3s\n\nOK\n")
        out = dg.stage_f(suites=(dg.CPU_SUITES[0], dg.CPU_SUITES[1]),
                         test_runner=runner)
        self.assertEqual(out["status"], "SOURCE_CPU_PASS_NOT_RELEASED")
        self.assertEqual(out["passed_test_count"], 6)
        self.assertFalse(out["production_lifecycle_released"])

    def test_f_cpu_suite_failure_blocks(self):
        out = dg.stage_f(suites=(dg.CPU_SUITES[0],),
                         test_runner=lambda args, **kwargs: SimpleNamespace(
                             returncode=1, stdout="", stderr="Ran 3 tests in 0.1s\nFAILED"))
        self.assertEqual(out["status"], "BLOCKED")

    def test_g_preview_only_not_real_mutation_or_rollback(self):
        seen = []
        def planner(target):
            seen.append(target)
            return {"status": op.READY, "issues": [], "source_model": "27b",
                    "target_model": "flash-next", "source_lineage": "CANONICAL_RECIPE",
                    "target_lineage": "HISTORICAL_P3_INSTANCE",
                    "current_ids_from_live_docker": True}
        out = dg.stage_g(verified_live(), planner=planner,
                         auditor=lambda: {"status": "VERIFIED",
                                          "phase": "COMMITTED", "issues": []})
        self.assertEqual(seen, ["flash-next"])
        self.assertEqual(out["status"], "PREVIEW_PASS_REAL_SWITCH_NOT_RUN")
        self.assertFalse(out["real_bidirectional_switch_executed"])
        self.assertFalse(out["real_fault_injection_and_rollback_verified"])

    def test_g_dirty_journal_fails_closed(self):
        out = dg.stage_g(verified_live(),
                         planner=lambda target: {"status": op.READY, "issues": []},
                         auditor=lambda: {"status": "BLOCKED",
                                          "issues": ["UNRESOLVED_OPERATING_SWITCH_JOURNAL"]})
        self.assertEqual(out["status"], "BLOCKED")

    def test_unified_runner_continues_after_d_failed_and_reaches_cpu_and_g(self):
        called = []
        out = dg.acceptance(
            snapshot_fn=snapshot, live_fn=verified_live,
            p3_fn=lambda: {"status": "VERIFIED"},
            d_fn=lambda a, b: dg.result("P3-D", "BLOCKED", issues=["SENSOR_UNAVAILABLE"]),
            e_fn=lambda a, historical: dg.result("P3-E", "DRAFT_REVIEW_REQUIRED"),
            f_fn=lambda: (called.append("F") or dg.result(
                "P3-F", "SOURCE_CPU_PASS_NOT_RELEASED")),
            g_fn=lambda live: (called.append("G") or dg.result(
                "P3-G", "PREVIEW_PASS_REAL_SWITCH_NOT_RUN")))
        self.assertEqual(called, ["F", "G"])
        self.assertEqual(out["status"], "BLOCKED")
        self.assertFalse(out["acceptance_complete"])

    def test_cpu_only_never_accesses_docker_or_network(self):
        out = dg.acceptance(cpu_only=True,
                            snapshot_fn=lambda: self.fail("Docker inspected"),
                            live_fn=lambda: self.fail("API queried"),
                            p3_fn=lambda: self.fail("receipts read"),
                            f_fn=lambda: dg.result("P3-F", "SOURCE_CPU_PASS_NOT_RELEASED"))
        self.assertEqual(out["status"], "CPU_ONLY_SOURCE_PASS_NOT_DGX")
        self.assertEqual(out["stages"]["P3-G"]["status"], "NOT_RUN_CPU_ONLY")
        self.assertFalse(out["acceptance_complete"])

    def test_cli_plan_does_not_probe_or_allow_execute(self):
        with patch.object(dg, "acceptance", side_effect=AssertionError("live probe")):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(dg.main(["--plan"]), 0)
            self.assertEqual(json.loads(output.getvalue())["status"], "PLAN_ONLY")
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    dg.main(["--execute"])
        self.assertFalse(json.loads(output.getvalue())["executed"])

    def test_report_is_explicit_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "result.json")
            with patch.object(dg, "acceptance",
                              return_value={"status": "CPU_ONLY_SOURCE_PASS_NOT_DGX",
                                            "acceptance_complete": False,
                                            "executed": False}):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(dg.main(["--cpu-only", "--report", path]), 0)
                self.assertFalse(json.loads(Path(path).read_text())["executed"])
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(FileExistsError):
                        dg.main(["--cpu-only", "--report", path])


if __name__ == "__main__":
    unittest.main()
