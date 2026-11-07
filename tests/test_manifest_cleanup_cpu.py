"""Pure CPU, Fake-DGX tests for manifest-owned retirement of TWO old test
containers. Other managed model containers remain removable/reinstallable under
separate approved lifecycle actions; never model a global deletion ban.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.manager import manifest_cleanup as m
from scripts.manager.service_manifest import policy, manifest_from_observation
from wizard import main as wizard


SRC_ID = "a" * 64
IMAGE = m.EXPECTED_IMAGE
NOW = 1794031800
NAMES = [
    m.SOURCE_CONTAINER, m.FALLBACK_CONTAINER,
    *m.EXPECTED_NAMES,
]
CMD = [
    "/hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/" + m.REVISION,
    "--served-model-name", m.SERVED, "--quantization", "modelopt_mixed",
    "--chat-template", m.TOOL_CHAT_TEMPLATE,
    "--enable-auto-tool-choice", "--tool-call-parser", "qwen3_coder",
    "--reasoning-parser", "qwen3",
]


class FakeDocker:
    def __init__(self):
        self.names = list(NAMES)
        self.calls = []
        p = policy()["retired_containers"]["targets"]
        self.docs = {}
        for name in NAMES:
            found = next((e for e in p if e["name"] == name), None)
            doc = {
                "Name": "/" + name,
                "Id": (
                    SRC_ID if name == m.SOURCE_CONTAINER
                    else "b" * 64 if name == m.FALLBACK_CONTAINER
                    else found.get("expected_container_id", "c" * 64)
                ),
                "Image": IMAGE if name != m.FALLBACK_CONTAINER else "sha256:" + "d"*64,
                "State": {"Running": name == m.SOURCE_CONTAINER},
                "Config": {"Cmd": CMD, "Labels": (
                    found["expected_labels"] if found else {}
                )},
                "HostConfig": {"AutoRemove": False},
                "Mounts": [{"Destination": "/hf", "Source": "/fake/hf",
                            "RW": False, "Type": "bind"}],
            }
            self.docs[name] = doc

    def inspect(self, name):
        self.calls.append(("inspect", name))
        return self.docs[name]

    def run(self, args, timeout=35):
        self.calls.append(tuple(args))
        if args[:2] == ["docker", "ps"]:
            names = self.names if "-a" in args else [
                n for n in self.names if self.docs[n]["State"]["Running"]
            ]
            return SimpleNamespace(
                returncode=0, stdout="\n".join(names) + ("\n" if names else "")
            )
        if args[:2] == ["docker", "rm"]:
            self.names.remove(args[-1])
            return SimpleNamespace(returncode=0, stdout=args[-1])
        raise AssertionError("Unexpected container mutation: " + str(args))


class ManifestContainerCleanupCPU(unittest.TestCase):
    def test_both_canonical_models_are_removable_not_globally_protected(self):
        cfg = policy()
        for key in ("27b", "flash-next"):
            item = cfg["models"][key]["container_lifecycle"]
            self.assertTrue(item["removable"])
            self.assertTrue(item["reinstallable"])
            self.assertTrue(item["requires_explicit_approval"])
        self.assertEqual(
            [x["name"] for x in cfg["retired_containers"]["targets"]],
            list(m.EXPECTED_NAMES),
        )

    def test_manifest_inventory_shows_retired_candidates_separately(self):
        cfg = policy()
        inventory = {"errors": [], "observed_listen_ports": [8000], "containers": [
            {"name": m.SOURCE_CONTAINER, "status": "Up 10 min",
             "image_id": IMAGE, "ports": "0.0.0.0:8000->8000/tcp"},
            {"name": m.EXPECTED_NAMES[0], "status": "Exited (0)",
             "image_id": IMAGE, "ports": ""},
        ]}
        observed = manifest_from_observation(inventory, spec=cfg)
        self.assertEqual(observed["observed_model"], "27b")
        self.assertEqual(
            observed["retired_container_inventory"][0]["name"],
            m.EXPECTED_NAMES[0],
        )
        self.assertTrue(observed["managed_container_lifecycle"]["27b"]["removable"])
        self.assertFalse(observed["operations_enabled"])

    def test_exact_two_target_read_only_plan(self):
        d = FakeDocker()
        with TemporaryDirectory() as tmp, \
             patch.object(m, "_evidence", return_value=("PASS_RESTORED", "f" * 64)), \
             patch.object(m.p3, "_gpu_conflicts", return_value=[]):
            data = m.make_plan(
                run=d.run, inspect=d.inspect,
                active_status=lambda: {
                    "status": "LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED",
                    "issues": [],
                },
                root=Path(tmp) / "cleanup", now=NOW,
            )
        self.assertEqual(data["status"], m.READY, data["issues"])
        self.assertEqual([row["name"] for row in data["targets"]],
                         list(m.EXPECTED_NAMES))
        self.assertEqual(len(data["plan_id"]), 64)
        self.assertFalse(data["executed"])
        self.assertFalse(any(c[:2] == ("docker", "rm") for c in d.calls))

    def test_running_candidate_is_blocked(self):
        d = FakeDocker()
        name = m.EXPECTED_NAMES[0]
        d.docs[name]["State"]["Running"] = True
        with TemporaryDirectory() as tmp, \
             patch.object(m, "_evidence", return_value=("FAIL_RESTORED", "f"*64)), \
             patch.object(m.p3, "_gpu_conflicts", return_value=[]):
            result = m.make_plan(
                run=d.run, inspect=d.inspect,
                active_status=lambda: {
                    "status": "LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED",
                    "issues": [],
                },
                root=Path(tmp) / "cleanup", now=NOW,
            )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(any(c[:2] == ("docker", "rm") for c in d.calls))

    def test_wrong_approval_blocks_without_inspecting_or_deleting(self):
        d = FakeDocker()
        for sha, first, second in (
            ("0"*64, "bad", m.ACK_PRESERVE),
            ("0"*64, m.ACK, "bad"),
            ("not-a-hex", m.ACK, m.ACK_PRESERVE),
        ):
            code, result = m.execute(sha, first, second,
                                     run=d.run, inspect=d.inspect)
            self.assertEqual(code, 3)
            self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(d.calls, [])

    def test_wizard_cleanup_preview_routes_without_execute(self):
        with patch("scripts.manager.manifest_cleanup.main",
                   return_value=0) as entry, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wizard.main(
                ["service", "manager", "cleanup", "--plan"]), 0)
        entry.assert_called_once_with(["plan"])

    def test_wizard_cleanup_rejects_arbitrary_docker_name(self):
        with patch("scripts.manager.manifest_cleanup.main") as entry, \
             contextlib.redirect_stdout(io.StringIO()):
            status = wizard.main([
                "service", "manager", "cleanup", "qwen38-flash"
            ])
        self.assertEqual(status, 2)
        entry.assert_not_called()

    def test_wizard_dry_run_rejects_cleanup_execute(self):
        with patch("scripts.manager.manifest_cleanup.main") as entry, \
             contextlib.redirect_stdout(io.StringIO()):
            status = wizard.main([
                "service", "manager", "cleanup", "--execute", "--dry-run"
            ])
        self.assertEqual(status, 3)
        entry.assert_not_called()


if __name__ == "__main__":
    unittest.main()
