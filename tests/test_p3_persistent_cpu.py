"""CPU-only P3 persistent switch simulation. No Docker, GPU, API or network."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p3_persistent_switch as p3
from scripts.manager.p3_p1_evidence_gate import assess_p1


FLASH = "f" * 64
B27 = "b" * 64
IMAGE = "sha256:" + "9" * 64
A_PLAN = "a" * 64


def inspect_doc(name: str, active: bool):
    return {
        "Name": "/" + name,
        "Id": FLASH if name == p3.NAMES["flash-next"] else B27,
        "Image": IMAGE,
        "State": {"Running": active},
        "HostConfig": {"AutoRemove": False, "RestartPolicy": {"Name": "no"},
                       "PortBindings": {"8000/tcp": [{"HostPort": "8000"}]}},
        "Config": {"Labels": {p3.LABEL: A_PLAN}, "Env": []},
    }


def live(model):
    return {"status": "LIVE_SERVICE_VERIFIED", "observed_model": model,
            "expected_served_id": p3.IDS[model], "issues": []}


def fake_p2():
    return {"status": "READY_TO_REQUEST_TRIAL_APPROVAL",
            "issues": [], "source_container_id": FLASH,
            "image_id": IMAGE}


def write_stage(root, stage, **changes):
    doc = {"schema_version": 1, "stage": stage, "status": "PASS",
           "plan_id": A_PLAN, "live_verified": True,
           "source_model": "flash-next" if stage == "a" else "27b",
           "target_model": "27b" if stage == "a" else "flash-next",
           "flash_id": FLASH, "flash_image": IMAGE,
           "id_27b": B27, "image_27b": IMAGE,
           "p2_receipt_sha256": "c" * 64,
           "finished_at_utc": "2026-11-06T06:00:00+00:00",
           **changes}
    p3._write_once(root, "stage-" + stage + ".json", doc)


class P3StagedPlanCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.receipt = lambda: ({"sha256": "c" * 64, "path": "private"}, None)

    def tearDown(self):
        self.temp.cleanup()

    def plan(self, stage, observed, **kwargs):
        name = p3.NAMES[observed]
        def run(argv, timeout=35):
            if argv[1] == "ps":
                return SimpleNamespace(returncode=0, stdout="qwen38-flash\nqwen38-27b\n")
            raise AssertionError("unexpected command: " + str(argv))
        result = p3.make_plan(
            stage, root=self.root, reader=self.receipt,
            live=lambda: live(observed), trial_planner=fake_p2,
            inspect=lambda n: inspect_doc(n, n == name),
            run=run, now=1793935000, **kwargs)
        return result

    def test_a_requires_no_p2_auto_progression(self):
        # A requires receipt, verified Flash source, and a free 27B name.
        out = self.plan("a", "flash-next")
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("P3_A_TARGET_CONTAINER_ALREADY_EXISTS", out["issues"])
        self.assertIsNone(out["plan_id"])
        self.assertFalse(out["operations_enabled"])

    def test_a_happy_plan_only_with_explicit_entry_contract(self):
        def run(argv, timeout=35):
            return SimpleNamespace(returncode=0, stdout="qwen38-flash\n")
        with patch.object(p3, "_gpu_conflicts", return_value=[]):
            out = p3.make_plan(
                "a", root=self.root, reader=self.receipt,
                live=lambda: live("flash-next"), trial_planner=fake_p2,
                inspect=lambda n: inspect_doc(n, True), run=run, now=1793935000)
        self.assertEqual(out["status"], p3.SUCCESS, out["issues"])
        self.assertRegex(out["plan_id"], r"^[0-9a-f]{64}$")
        self.assertEqual(out["required_p3_entry_acknowledgement"], p3.ENTRY_ACK)
        self.assertFalse(out["operations_enabled"])
        self.assertFalse(out["executed"])

    def test_b_requires_stage_a_receipt_and_27b_source(self):
        out = self.plan("b", "27b")
        self.assertEqual(out["status"], "BLOCKED")
        self.assertTrue(any("P3_LOCAL_EVIDENCE" in i for i in out["issues"]))
        self.root.mkdir(exist_ok=True)
        write_stage(self.root, "a")
        with patch.object(p3, "_gpu_conflicts", return_value=[]):
            out = self.plan("b", "27b")
        self.assertEqual(out["status"], p3.SUCCESS, out["issues"])
        self.assertEqual(out["source_model"], "27b")
        self.assertEqual(out["target_model"], "flash-next")
        self.assertEqual(out["target_container_id"], FLASH)

    def test_c_blocked_until_p1_evidence_after_b(self):
        write_stage(self.root, "a")
        write_stage(self.root, "b")
        with patch.object(p3, "_gpu_conflicts", return_value=[]):
            out = self.plan("c", "flash-next")
        self.assertEqual(out["status"], "BLOCKED")
        self.assertTrue(any(i.startswith("P1_") for i in out["issues"]))
        self.assertIsNone(out["plan_id"])

    def test_c_passes_when_injected_p1_gate_passes(self):
        write_stage(self.root, "a")
        write_stage(self.root, "b")
        with patch.object(p3, "_gpu_conflicts", return_value=[]):
            out = self.plan("c", "flash-next", p1_gate=lambda **_:
                           {"status": "PASS", "issues": [], "evidence_hashes": {
                               "verify": "d"*64, "benchmark": "e"*64, "diagnostics": "f"*64}})
        self.assertEqual(out["status"], p3.SUCCESS, out["issues"])
        self.assertEqual(out["target_container_id"], B27)
        self.assertEqual(out["target_model"], "27b")

    def test_attempt_marker_blocks_replay(self):
        (self.root / "attempt-a.json").write_text("{}")
        out = self.plan("a", "flash-next")
        self.assertIn("P3_STAGE_ALREADY_ATTEMPTED", out["issues"])

    def test_mismatched_p2_receipt_blocks_b(self):
        write_stage(self.root, "a")
        with patch.object(p3, "_gpu_conflicts", return_value=[]):
            out = p3.make_plan("b", root=self.root,
                reader=lambda: ({"sha256": "1"*64}, None),
                live=lambda: live("27b"), trial_planner=fake_p2,
                inspect=lambda n: inspect_doc(n, n == p3.NAMES["27b"]),
                run=lambda cmd, **kw: SimpleNamespace(returncode=0, stdout="qwen38-flash\nqwen38-27b\n"),
                now=1793935000)
        self.assertIn("P2_RECEIPT_CHANGED_SINCE_STAGE_A", out["issues"])


class P3ExecuteCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.states = {"qwen38-flash": True, "qwen38-27b": False}
        self.commands = []
        self.stageA_created = False

    def tearDown(self):
        self.temp.cleanup()

    def _inspect(self, name):
        return inspect_doc(name, self.states.get(name, False))

    def _run(self, cmd, timeout=35):
        self.commands.append(cmd[:])
        if cmd[:3] == ["docker", "ps", "-a"]:
            names = ["qwen38-flash"] + (["qwen38-27b"] if self.stageA_created else [])
            return SimpleNamespace(returncode=0, stdout=chr(10).join(names) + chr(10))
        if cmd[:2] == ["docker", "stop"]:
            self.states[cmd[-1]] = False
        if cmd[:2] == ["docker", "start"]:
            self.states[cmd[-1]] = True
        if cmd[:2] == ["docker", "run"]:
            self.states["qwen38-27b"] = True
            self.stageA_created = True
        return SimpleNamespace(returncode=0, stdout="")

    def _planner(self, stage, root):
        source, target = p3.DIRECTIONS[stage]
        return {"status": p3.SUCCESS, "plan_id": A_PLAN, "issues": [],
                "source_container_id": FLASH if source == "flash-next" else B27,
                "source_image": IMAGE, "target_image": IMAGE,
                "flash_id": FLASH, "flash_image": IMAGE,
                "image_27b": IMAGE, "id_27b": B27 if stage != "a" else None,
                "target_container_id": None if stage == "a" else (FLASH if target == "flash-next" else B27),
                "p3_a_plan_id": A_PLAN if stage != "a" else None,
                "p2_receipt_sha256": "c"*64, "p1_evidence": None}

    def test_exact_plan_and_downtime_and_separate_entry_required(self):
        for plan, ack, entry in [(None, p3.ACK, p3.ENTRY_ACK),
                                 (A_PLAN, "wrong", p3.ENTRY_ACK),
                                 (A_PLAN, p3.ACK, None)]:
            rc, out = p3.execute("a", plan, ack, entry, root=self.root,
                                 planner=self._planner, run=self._run)
            self.assertEqual(rc, 3)
            self.assertFalse(out["executed"])
        self.assertEqual(self.commands, [])

    def test_happy_a_keeps_27b_active_and_flash_preserved(self):
        with patch.object(p3, "_record") as journal, \
             patch.object(p3.gpu, "trial_command", return_value=["docker", "run", "target"]), \
             patch.object(p3.gpu, "running", side_effect=lambda name, run: self.states[name]), \
             patch.object(p3.gpu, "port_free", return_value=True):
            rc, out = p3.execute("a", A_PLAN, p3.ACK, p3.ENTRY_ACK,
                root=self.root, planner=self._planner,
                run=self._run, inspect=self._inspect,
                waiter=lambda name, model, seconds, run: self.states[name],
                live=lambda: live("27b"))
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["status"], "PASS")
        self.assertTrue(self.states["qwen38-27b"])
        self.assertFalse(self.states["qwen38-flash"])
        self.assertTrue((self.root / "stage-a.json").exists())
        self.assertIn("COMMITTED", [c.args[1] for c in journal.call_args_list])

    def test_failed_target_api_restores_source_and_blocks_retry(self):
        def fake_restore(*args, **kwargs):
            self.states["qwen38-27b"] = False
            self.states["qwen38-flash"] = True
            return {"status": "RESTORED", "issues": []}
        with patch.object(p3, "_record"), \
             patch.object(p3, "_restore", side_effect=fake_restore), \
             patch.object(p3.gpu, "trial_command", return_value=["docker", "run", "target"]), \
             patch.object(p3.gpu, "running", side_effect=lambda name, run: self.states[name]), \
             patch.object(p3.gpu, "port_free", return_value=True):
            rc, out = p3.execute("a", A_PLAN, p3.ACK, p3.ENTRY_ACK,
                root=self.root, planner=self._planner, run=self._run,
                inspect=self._inspect, waiter=lambda *a, **kw: False,
                live=lambda: live("flash-next"))
        self.assertEqual(rc, 4)
        self.assertEqual(out["status"], "FAIL_RESTORED")
        self.assertTrue((self.root / "attempt-a.json").exists())
        self.assertFalse((self.root / "stage-a.json").exists())


    def test_stage_b_keeps_original_flash_running_and_preserves_27b(self):
        self.stageA_created = True
        self.states = {"qwen38-flash": False, "qwen38-27b": True}
        with patch.object(p3, "_record") as journal, \
             patch.object(p3.gpu, "running", side_effect=lambda name, run: self.states[name]), \
             patch.object(p3.gpu, "port_free", return_value=True):
            rc, out = p3.execute("b", A_PLAN, p3.ACK, root=self.root,
                planner=self._planner, run=self._run, inspect=self._inspect,
                waiter=lambda name, model, seconds, run: self.states[name],
                live=lambda: live("flash-next"))
        self.assertEqual(rc, 0, out)
        self.assertFalse(self.states["qwen38-27b"])
        self.assertTrue(self.states["qwen38-flash"])
        self.assertEqual(json.loads((self.root / "stage-b.json").read_text())["target_id"], FLASH)
        self.assertEqual(journal.call_args_list[-1].args[1], "COMMITTED")

    def test_stage_c_preserves_flash_and_ends_on_27b(self):
        self.stageA_created = True
        self.states = {"qwen38-flash": True, "qwen38-27b": False}
        with patch.object(p3, "_record"), \
             patch.object(p3.gpu, "running", side_effect=lambda name, run: self.states[name]), \
             patch.object(p3.gpu, "port_free", return_value=True):
            rc, out = p3.execute("c", A_PLAN, p3.ACK, root=self.root,
                planner=self._planner, run=self._run, inspect=self._inspect,
                waiter=lambda name, model, seconds, run: self.states[name],
                live=lambda: live("27b"))
        self.assertEqual(rc, 0, out)
        self.assertFalse(self.states["qwen38-flash"])
        self.assertTrue(self.states["qwen38-27b"])
        self.assertEqual(out["active_model"], "27b")
        self.assertEqual(json.loads((self.root / "stage-c.json").read_text())["target_id"], B27)

    def test_stage_c_refuses_foreign_preserved_27b_target_before_start(self):
        self.stageA_created = True
        self.states = {"qwen38-flash": True, "qwen38-27b": False}
        def inspect_changed(name):
            doc = self._inspect(name)
            if name == "qwen38-27b":
                doc["Id"] = "9" * 64
            return doc
        with patch.object(p3, "_record"), \
             patch.object(p3.gpu, "running", side_effect=lambda name, run: self.states[name]), \
             patch.object(p3.gpu, "port_free", return_value=True):
            rc, out = p3.execute("c", A_PLAN, p3.ACK, root=self.root,
                planner=self._planner, run=self._run, inspect=inspect_changed,
                waiter=lambda *a, **kw: False, live=lambda: live("flash-next"))
        self.assertEqual(rc, 4)
        self.assertIn("PRESERVED_TARGET_CHANGED_BEFORE_START", out["error_code"])
        self.assertFalse(any(cmd[:2] == ["docker", "start"] and cmd[-1] == "qwen38-27b"
                             for cmd in self.commands))


class P3RecoveryForeignGPUGuardCPU(unittest.TestCase):
    def _simulate_recovery(self, foreign: bool):
        calls = []
        def run(args, timeout=35):
            calls.append(args[:])
            if args[:3] == ["docker", "ps", "-a"]:
                return SimpleNamespace(returncode=0,
                    stdout=chr(10).join(("qwen38-flash", "qwen38-27b")) + chr(10))
            if args[:2] == ["docker", "ps"]:
                return SimpleNamespace(returncode=0,
                    stdout="foreign-inference" + chr(10) if foreign else "")
            return SimpleNamespace(returncode=0, stdout="")

        def inspect(name):
            if name == "foreign-inference":
                return {"HostConfig": {"DeviceRequests": [{"Driver": "nvidia"}]},
                        "Config": {"Env": []}}
            return inspect_doc(name, False)
        with patch.object(p3.gpu, "port_free", return_value=True):
            result = p3._restore("a", "flash-next", "27b",
                FLASH, IMAGE, IMAGE, A_PLAN, run=run, inspect=inspect,
                waiter=lambda *a, **kw: True, live=lambda: live("flash-next"))
        return result, calls

    def test_unexpected_gpu_container_blocks_original_restart(self):
        result, calls = self._simulate_recovery(foreign=True)
        self.assertEqual(result["status"], "RECOVERY_FAILED")
        self.assertIn("RESTORE_FOREIGN_GPU_CONSUMER", result["issues"])
        self.assertIn("OTHER_GPU_CONTAINER_RUNNING", result["issues"])
        self.assertNotIn(["docker", "start", "qwen38-flash"], calls)

    def test_no_foreign_gpu_allows_identity_verified_restore(self):
        result, calls = self._simulate_recovery(foreign=False)
        self.assertEqual(result["status"], "RESTORED", result["issues"])
        self.assertIn(["docker", "start", "qwen38-flash"], calls)


class P1GateCPU(unittest.TestCase):
    def test_no_new_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)
            result = assess_p1(stage_b={"finished_at_utc": "2026-11-06T06:00:00+00:00"},
                               flash_image=IMAGE, p1_root=path / "p1", p3_root=path)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("P1_VERIFY_RECEIPT_NOT_FOUND", result["issues"])
        self.assertIn("P1_BENCHMARK_RECEIPT_NOT_FOUND", result["issues"])
        self.assertIn("P1_HISTORIC_RC3_DIAGNOSTIC_EVIDENCE_MISSING", result["issues"])


    def _positive_p1_fixture(self, home, *, benchmark_tokens_per_sec=12.25,
                             p1_finished="2026-11-06T08:00:00+00:00"):
        home.mkdir(parents=True, exist_ok=True)
        state = home / "p3"
        state.mkdir()
        common = {"executed": True, "approval": "explicit_plan_id",
                  "status": "PASS", "model_repo": "nvidia/Qwen3.8-Flash-Next-NVFP4",
                  "served_model": "qwen3.8-flash-next", "image_id": IMAGE,
                  "finished_at_utc": p1_finished}
        verify = {"action": "verify", **common,
                  "result": {"status": "PASS", "identity": {"health": "PASS", "models": ["qwen3.8-flash-next"]},
                             "baseline_status": "PASS", "extended_status": "PASS",
                             "probes": {key: {"status": "PASS"} for key in
                                        ("default_completion", "chat", "tools", "vision")}}}
        bench = {"action": "benchmark", **common,
                 "result": {"status": "PASS",
                            "benchmark": {"status": "PASS",
                                          "samples": [{"completion_tokens": 64, "ttft_sec": 0.2}] * 3,
                                          "metrics": {"latency_p50_sec": 5.9,
                                                      "ttft_p50_sec": 0.2,
                                                      "mean_tokens_per_sec": benchmark_tokens_per_sec}}}}
        collision = {
            "scope": "SOURCE", "dry_run": True, "status": "PASS",
            "name_conflict": True, "port_conflict": True,
            "collision_free": False, "errors": [],
            "proposed": {"container_name": "qwen38-flash", "port": 8000,
                         "served_model_name": "qwen3.8-flash-next"},
            "containers": [{"name": "qwen38-flash", "image_id": IMAGE,
                            "status": "Up About an hour",
                            "ports": "0.0.0.0:8000->8000/tcp"}],
        }
        diagnosis = {"status": "PASS", "doctor_exit_code": 3,
                     "inventory_plan_exit_code": 3,
                     "doctor_output": collision,
                     "inventory_plan_output": collision,
                     "historical_rc3_disposition":
                         "Historical rc=3 reasons reviewed against full raw active-source collision output.",
                     "finished_at_utc": p1_finished}
        for path, value in ((home / "verify.json", verify),
                            (home / "bench.json", bench),
                            (state / "p1-diagnostics.json", diagnosis)):
            path.write_text(json.dumps(value))
            path.chmod(0o600)
        return home, state

    def test_real_shaped_post_b_p1_receipts_qualify_c_without_gpu(self):
        with tempfile.TemporaryDirectory() as directory:
            p1, p3root = self._positive_p1_fixture(Path(directory) / "p1")
            status = assess_p1(stage_b={"finished_at_utc": "2026-11-06T06:00:00+00:00"},
                               flash_image=IMAGE, p1_root=p1, p3_root=p3root)
        self.assertEqual(status["status"], "PASS", status["issues"])
        self.assertEqual(set(status["evidence_hashes"]), {"verify", "benchmark", "diagnostics"})

    def test_wrong_p1_served_id_in_real_identity_blocks_stage_c(self):
        with tempfile.TemporaryDirectory() as directory:
            p1, p3root = self._positive_p1_fixture(Path(directory) / "p1")
            file = p1 / "verify.json"
            receipt = json.loads(file.read_text())
            receipt["result"]["identity"]["models"] = ["foreign-id"]
            file.write_text(json.dumps(receipt))
            status = assess_p1(stage_b={"finished_at_utc": "2026-11-06T06:00:00+00:00"},
                               flash_image=IMAGE, p1_root=p1, p3_root=p3root)
        self.assertEqual(status["status"], "BLOCKED")
        self.assertIn("P1_FUNCTIONAL_PROBES_INCOMPLETE", status["issues"])

    def test_missing_numerical_throughput_blocks_c(self):
        with tempfile.TemporaryDirectory() as directory:
            p1, p3root = self._positive_p1_fixture(Path(directory) / "p1",
                                                    benchmark_tokens_per_sec=None)
            status = assess_p1(stage_b={"finished_at_utc": "2026-11-06T06:00:00+00:00"},
                               flash_image=IMAGE, p1_root=p1, p3_root=p3root)
        self.assertEqual(status["status"], "BLOCKED")
        self.assertIn("P1_ACTUAL_BENCHMARK_METRICS_INCOMPLETE", status["issues"])

    def test_p1_legacy_pass_before_b_does_not_qualify_c(self):
        with tempfile.TemporaryDirectory() as directory:
            p1, p3root = self._positive_p1_fixture(
                Path(directory) / "p1", p1_finished="2026-11-06T05:00:00+00:00")
            status = assess_p1(stage_b={"finished_at_utc": "2026-11-06T06:00:00+00:00"},
                               flash_image=IMAGE, p1_root=p1, p3_root=p3root)
        self.assertEqual(status["status"], "BLOCKED")
        self.assertIn("P1_VERIFY_RECEIPT_UNQUALIFIED", status["issues"])
        self.assertIn("P1_BENCHMARK_RECEIPT_UNQUALIFIED", status["issues"])
        self.assertIn("P1_HISTORIC_RC3_DISPOSITION_NOT_VERIFIED", status["issues"])


    def _recheck_mutated_collision(self, mutate):
        with tempfile.TemporaryDirectory() as directory:
            p1, p3root = self._positive_p1_fixture(Path(directory) / "p1")
            diag_path = p3root / "p1-diagnostics.json"
            doc = json.loads(diag_path.read_text())
            mutate(doc)
            diag_path.write_text(json.dumps(doc))
            status = assess_p1(stage_b={"finished_at_utc": "2026-11-06T06:00:00+00:00"},
                               flash_image=IMAGE, p1_root=p1, p3_root=p3root)
        self.assertEqual(status["status"], "BLOCKED", status)
        self.assertIn("P1_HISTORIC_RC3_DISPOSITION_NOT_VERIFIED",
                      status["issues"])

    def test_rc3_without_actual_json_output_does_not_qualify(self):
        self._recheck_mutated_collision(
            lambda doc: doc.pop("doctor_output"))

    def test_rc3_with_inventory_errors_does_not_qualify(self):
        def corrupt(doc):
            doc["doctor_output"]["errors"] = ["docker_inventory_incomplete:ValueError"]
        self._recheck_mutated_collision(corrupt)

    def test_rc3_foreign_image_does_not_qualify(self):
        def corrupt(doc):
            doc["doctor_output"]["containers"][0]["image_id"] = "sha256:" + "f"*64
        self._recheck_mutated_collision(corrupt)

    def test_rc3_wrong_port_does_not_qualify(self):
        def corrupt(doc):
            doc["doctor_output"]["proposed"]["port"] = 7000
        self._recheck_mutated_collision(corrupt)

    def test_rc0_launch_probe_does_not_prove_running_source(self):
        def corrupt(doc):
            doc["doctor_exit_code"] = 0
            doc["inventory_plan_exit_code"] = 0
        self._recheck_mutated_collision(corrupt)


if __name__ == "__main__":
    unittest.main()
