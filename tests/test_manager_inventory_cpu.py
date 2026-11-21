"""N2 deterministic CPU-only inventory tests: subprocess runner is always a stub."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.manager.inventory import DEFAULT_PORT, _under, inspect_host


class FakeRun:
    def __init__(self, *, names=None, listeners="", fail=None, mounts=None):
        self.calls = []
        self.names = names or []
        self.listeners = listeners
        self.fail = fail
        self.mounts = mounts or []

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        text = ""
        if args == ["docker", "ps", "-a", "--format", "{{json .}}"]:
            text = "\n".join(json.dumps(x) for x in self.names)
        elif args[:3] == ["docker", "inspect", "--format"]:
            text = json.dumps(self.mounts) if args[3] == "{{json .Mounts}}" else "sha256:" + "d" * 64
        elif args == ["ss", "-H", "-ltn"]:
            text = self.listeners
        else:
            raise AssertionError("unapproved command: " + str(args))
        return subprocess.CompletedProcess(args, 1 if args[0] == self.fail else 0, text, "")


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = Path(self.tmp.name) / "hf"
        self.disk = lambda _: (1000, 300, 700)

    def snapshot(self, fake=None, **kwargs):
        return inspect_host(cache_root=self.cache, run=fake or FakeRun(), disk_usage=self.disk, **kwargs)

    def test_read_only_unoccupied_plan(self):
        fake = FakeRun()
        doc = self.snapshot(fake)
        self.assertEqual(doc["status"], "PASS")
        self.assertTrue(doc["collision_free"])
        self.assertEqual(doc["proposed"]["port"], DEFAULT_PORT)
        self.assertEqual(doc["proposed"]["model_repo"], "nvidia/Qwen3.8-Flash-Next-NVFP4")
        self.assertFalse(doc["launch_authorized"])
        self.assertFalse(doc["checkpoint"]["snapshot_present"])
        self.assertEqual(doc["disk"]["free_bytes"], 700)
        self.assertTrue(all(x[0] in ("docker", "ss") for x in fake.calls))
        self.assertFalse(any(x[1] in ("run", "rm", "stop", "start", "pull", "build") for x in fake.calls))

    def test_socket_port_collision(self):
        fake = FakeRun(listeners="LISTEN 0 128 0.0.0.0:8000 0.0.0.0:*\n")
        doc = self.snapshot(fake)
        self.assertTrue(doc["port_conflict"])
        self.assertFalse(doc["collision_free"])

    def test_docker_port_collision_even_without_ss(self):
        fake = FakeRun(names=[{"Names": "other", "Ports": "0.0.0.0:8000->8000/tcp",
                               "Image": "other:latest", "Status": "Up"}])
        doc = self.snapshot(fake)
        self.assertTrue(doc["port_conflict"])
        self.assertFalse(doc["name_conflict"])

    def test_docker_name_collision_stopped(self):
        fake = FakeRun(names=[{"Names": "qwen38-flash", "Ports": "", "Image": "old", "Status": "Exited"}])
        self.assertTrue(self.snapshot(fake)["name_conflict"])

    def test_docker_unreachable_fails_closed(self):
        doc = self.snapshot(FakeRun(fail="docker"))
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertFalse(doc["collision_free"])

    def test_socket_unavailable_fails_closed(self):
        doc = self.snapshot(FakeRun(fail="ss"))
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertFalse(doc["collision_free"])

    def test_symlink_canonicalization(self):
        original = Path(self.tmp.name) / "original"
        original.mkdir()
        link = Path(self.tmp.name) / "link"
        link.symlink_to(original, target_is_directory=True)
        self.assertTrue(_under(link / "foo", original))
        self.assertFalse(_under(original / "foo", Path(self.tmp.name) / "unrelated"))

    def test_snapshot_detects_hybrid_flag_without_network(self):
        base = self.cache / "hub/models--nvidia--Qwen3.8-Flash-Next-NVFP4"
        rev = "a" * 40
        (base / "refs").mkdir(parents=True)
        (base / "refs/main").write_text(rev)
        prepared = base / "snapshots" / (rev + "-fp8hybrid") / ".prepared"
        prepared.parent.mkdir(parents=True)
        prepared.touch()
        (base / "snapshots" / rev).mkdir()
        doc = self.snapshot()
        self.assertEqual(doc["checkpoint"]["revision"], rev)
        self.assertTrue(doc["checkpoint"]["snapshot_present"])
        self.assertTrue(doc["checkpoint"]["hybrid_prepared"])

    def test_cache_mount_detected_as_shared(self):
        self.cache.mkdir()
        fake = FakeRun(names=[{"Names": "other", "Ports": "", "Image": "other",
                               "Status": "Up"}],
                       mounts=[{"Source": str(self.cache), "Destination": "/hf"}])
        doc = self.snapshot(fake)
        self.assertTrue(doc["containers"][0]["shares_hf_cache"])

    def test_invalid_target_rejected(self):
        with self.assertRaises(ValueError):
            self.snapshot(name="name with spaces")
        with self.assertRaises(ValueError):
            self.snapshot(port=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
