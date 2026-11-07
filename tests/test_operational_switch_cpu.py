"""Fake-DGX CPU acceptance for the independent read-only operating switch."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import operational_switch as op
from scripts.manager import p3_persistent_switch as p3
from wizard import console
from wizard import main as router

FLASH = "f" * 64
MODEL27 = "b" * 64
IMAGE = "sha256:" + "9" * 64
PLAN = "a" * 64
P2 = "c" * 64


def docker_doc(model: str, running: bool, *, identity: str | None = None) -> dict:
    name = p3.NAMES[model]
    return {
        "Name": "/" + name,
        "Id": identity or (FLASH if model == "flash-next" else MODEL27),
        "Image": IMAGE,
        "State": {"Running": running},
        "HostConfig": {"AutoRemove": False, "RestartPolicy": {"Name": "no"},
                       "PortBindings": {"8000/tcp": [{"HostPort": "8000"}]}},
        "Config": {"Labels": {p3.LABEL: PLAN}, "Env": []},
    }


def live(model: str, *, good: bool = True) -> dict:
    return {"status": "LIVE_SERVICE_VERIFIED" if good else "BLOCKED",
            "observed_model": model,
            "expected_served_id": p3.IDS[model], "issues": []}


class FakeDGX(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.p3_root = self.root / "p3"
        self.p3_root.mkdir(mode=0o700)
        self.ops = self.root / "new-operations"
        self.commands: list[list[str]] = []
        self.docs = {
            p3.NAMES["flash-next"]: docker_doc("flash-next", False),
            p3.NAMES["27b"]: docker_doc("27b", True),
        }
        self._receipts()

    def tearDown(self):
        self.temp.cleanup()

    def _receipts(self):
        for i, stage in enumerate("abc"):
            source, target = p3.DIRECTIONS[stage]
            receipt = {
                "schema_version": 1, "stage": stage, "status": "PASS",
                "live_verified": True, "executed": True,
                "plan_id": PLAN, "source_model": source,
                "target_model": target, "flash_id": FLASH,
                "id_27b": MODEL27, "flash_image": IMAGE, "image_27b": IMAGE,
                "p2_receipt_sha256": P2,
                "finished_at_utc": f"2026-11-07T0{i}:00:00+00:00",
            }
            p3._write_once(self.p3_root, "stage-" + stage + ".json", receipt)

    def run(self, cmd: list[str], timeout: int = 35):
        self.commands.append(cmd)
        if cmd[:3] == ["docker", "ps", "-a"]:
            return SimpleNamespace(returncode=0,
                                   stdout="\n".join(self.docs) + "\n")
        if cmd[:2] == ["docker", "ps"]:
            active = [k for k, value in self.docs.items()
                      if value["State"]["Running"]]
            return SimpleNamespace(returncode=0, stdout="\n".join(active) + "\n")
        raise AssertionError("Unexpected Docker mutation: " + str(cmd))

    def plan(self, target="flash-next", *, current="27b", good=True, now=1000):
        return op.make_plan(target, live=lambda: live(current, good=good),
                            run=self.run, inspect=lambda name: self.docs[name],
                            p3_root=self.p3_root, root=self.ops, now=now)

    def test_verified_historical_a_b_c_and_source_27b_to_flash(self):
        doc = self.plan()
        self.assertEqual(doc["status"], op.READY)
        self.assertEqual(doc["source_model"], "27b")
        self.assertEqual(doc["target_model"], "flash-next")
        self.assertEqual(len(doc["plan_id"]), 64)
        self.assertFalse(doc["execution_supported"])
        self.assertFalse(doc["operations_enabled"])
        self.assertFalse(doc["executed"])
        self.assertEqual(doc["api_host_port"], 8000)
        self.assertTrue(all(cmd[:2] == ["docker", "ps"] for cmd in self.commands))

    def test_flash_to_27b_ready_only_when_preserved_target_stopped(self):
        self.docs[p3.NAMES["flash-next"]]["State"]["Running"] = True
        self.docs[p3.NAMES["27b"]]["State"]["Running"] = False
        self.assertEqual(self.plan("27b", current="flash-next")["status"], op.READY)

    def test_current_target_does_not_offer_downtime(self):
        doc = self.plan("27b")
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIn("MODEL_ALREADY_ACTIVE_NO_SWITCH_NEEDED", doc["issues"])
        self.assertIsNone(doc["plan_id"])
        self.assertEqual(self.commands, [])

    def test_no_local_p3_receipts_is_not_fabricated_pass(self):
        (self.p3_root / "stage-c.json").unlink()
        data = self.plan()
        self.assertEqual(data["status"], "BLOCKED")
        self.assertIn("P3_IMMUTABLE_STAGE_RECEIPTS_UNAVAILABLE", data["issues"])

    def test_cross_stage_lineage_change_is_rejected(self):
        path = self.p3_root / "stage-b.json"
        doc = json.loads(path.read_text())
        doc["image_27b"] = "sha256:" + "1" * 64
        path.write_text(json.dumps(doc))
        result = self.plan()
        self.assertIn("P3_STAGE_PINNED_LINEAGE_MISMATCH:image_27b", result["issues"])

    def test_actual_dgx_wrong_api_id_blocks_preview(self):
        doc = self.plan(good=False)
        self.assertIn("SOURCE_API_AND_MANIFEST_UNVERIFIED", doc["issues"])
        self.assertIsNone(doc["plan_id"])

    def test_pinned_target_id_drift_blocks(self):
        self.docs[p3.NAMES["flash-next"]]["Id"] = "e" * 64
        self.assertIn("CONTAINER_ID_MISMATCH", self.plan()["issues"])

    def test_competing_gpu_model_blocks(self):
        foreign = "foreign-gpu-container"
        self.docs[foreign] = {
            "Name": "/" + foreign, "Id": "d" * 64, "Image": IMAGE,
            "State": {"Running": True},
            "HostConfig": {"DeviceRequests": [{"Driver": "nvidia"}]},
            "Config": {"Env": []},
        }
        self.assertIn("OTHER_GPU_CONTAINER_RUNNING", self.plan()["issues"])

    def test_unresolved_journal_blocks_switch(self):
        from scripts.manager.service_journal import append_transition
        journal = self.ops / "journal"
        first = append_transition(journal, phase="OBSERVED",
                                  from_model="27b", to_model="flash-next",
                                  observed_model="27b", expected_previous_hash=None,
                                  plan_id=PLAN)
        append_transition(journal, phase="PLANNED",
                          from_model="27b", to_model="flash-next",
                          observed_model="27b", expected_previous_hash=first["event_hash"],
                          plan_id=PLAN)
        doc = self.plan()
        self.assertIn("UNRESOLVED_OPERATING_SWITCH_JOURNAL", doc["issues"])

    def test_expiring_fingerprint_rotates_without_old_id_reuse(self):
        first = self.plan(now=10)["plan_id"]
        second = self.plan(now=610)["plan_id"]
        self.assertNotEqual(first, second)

    def test_orcarouter_is_not_runtime_qualified(self):
        doc = self.plan("orcarouter")
        self.assertIn("UNSUPPORTED_OR_UNQUALIFIED_MODEL", doc["issues"])
        self.assertEqual(self.commands, [])

    def test_execute_cli_rejects_before_backend_observation(self):
        with patch.object(op, "make_plan") as plan, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = op.main(["--target", "flash-next", "--execute",
                          "--approve-plan", PLAN, "--ack-downtime", "yes"])
        self.assertEqual(rc, 3)
        plan.assert_not_called()
        doc = json.loads(output.getvalue())
        self.assertFalse(doc["executed"])
        self.assertIn("GENERAL_OPERATING_SWITCH_EXECUTOR_NOT_QUALIFIED", doc["issues"])

    def test_existing_router_operational_preview(self):
        with patch.object(op, "make_plan", return_value={
                "status": op.READY, "executed": False, "issues": [],
                "plan_id": PLAN}) as planner, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(router.main([
                "switch", "flash-next-27b", "operational",
                "--target", "flash-next", "--plan", "--json"]), 0)
        planner.assert_called_once_with("flash-next")
        self.assertIn(op.READY, output.getvalue())

    def test_user_model_menu_can_review_without_execute(self):
        with patch.object(op, "make_plan", return_value={
                "status": op.READY, "source_model": "27b",
                "issues": [], "plan_id": PLAN}) as planner, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            console._switch_preview("flash-next")
        planner.assert_called_once_with("flash-next")
        self.assertIn("NOT an executable approval", output.getvalue())
        self.assertIn("No service stopped", output.getvalue())


if __name__ == "__main__":
    unittest.main()
