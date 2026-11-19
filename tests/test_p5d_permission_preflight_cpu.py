"""Synthetic P5-D permission preflight CPU tests. No real Docker/host probes."""
from __future__ import annotations

import contextlib
import errno
import io
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.manager import p5d_permission_preflight as p
from scripts.manager.generic_operations import main as operations_main

CID = "a" * 64
REV = "3a3b63161c0745390e5270179af42e46efc70799"
FOLDER = "models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4"


def owner():
    return {"model": "orcarouter", "docker_identity_match": True,
            "container": {"id": CID, "name": "qwen38-orcarouter-qsa62318-lmhead-v3",
                          "init_pid": 42}, "docker_host_pids": [42, 43]}


def inspect(argv):
    assert argv[:2] == ["docker", "inspect"]
    return json.dumps({"Id": CID, "Name": "/qwen38-orcarouter-qsa62318-lmhead-v3",
                       "State": {"Running": True, "Pid": 42},
                       "Mounts": [{"RW": False, "Destination": "/hf"}]})


def fixture(root):
    (root / "sys/kernel/yama").mkdir(parents=True)
    (root / "sys/kernel/yama/ptrace_scope").write_text("1\n")
    parent = root / "realroot"
    (parent / "hf/hub" / FOLDER / "snapshots" / REV).mkdir(parents=True)
    for pid in (42, 43):
        folder = root / str(pid)
        (folder / "ns").mkdir(parents=True)
        (folder / "fd").mkdir()
        (folder / "status").write_text("Uid:\t1000\t1000\t1000\t1000\n")
        (folder / "stat").write_text(str(pid) + " (worker name) "
                                     + " ".join(["S"] + ["0"] * 18 + ["123"]) + "\n")
        (folder / "smaps").write_bytes(b"synthetic sample; not live evidence")
        for kind in ("net", "mnt", "pid"):
            (folder / "ns" / kind).symlink_to(kind + ":[44]")
        (folder / "fd/3").symlink_to("socket:[77]")
    (root / "42/root").symlink_to(parent)


class PermissionCPU(unittest.TestCase):
    def test_readable_synthetic_fixture_still_never_attests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); fixture(root)
            report = p.permission_preflight(
                "orcarouter", capture=lambda model: owner(),
                run_command=inspect, proc=root)
        self.assertEqual(report["status"], "READABLE_PROCFS_PREFLIGHT_NOT_ATTESTED")
        self.assertTrue(report["ready_for_full_readonly_audit"])
        self.assertFalse(report["ple_residency_authenticated"])
        self.assertFalse(report["host_nat_owner_authenticated"])
        self.assertFalse(report["production_released"])

    def test_smaps_eacces_is_not_zero_measured_rss(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); fixture(root)
            original = p._smaps
            def denied(path):
                return p._error(PermissionError(errno.EACCES, "denied"))
            with patch.object(p, "_smaps", side_effect=denied):
                report = p.permission_preflight(
                    "orcarouter", capture=lambda m: owner(),
                    run_command=inspect, proc=root)
        self.assertEqual(report["status"], "BLOCKED_PERMISSION_PREFLIGHT")
        self.assertEqual(report["smaps_access_denied_pid_count"], 2)
        self.assertIn("SMAPS_ACCESS_DENIED", report["issues"])
        self.assertNotIn("rss_bytes", report)

    def test_namespace_missing_is_unqualified_not_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); fixture(root)
            (root / "43/ns/net").unlink()
            report = p.permission_preflight("orcarouter",
                capture=lambda m: owner(), run_command=inspect, proc=root)
        self.assertIn("NAMESPACE_GONE", report["issues"])
        self.assertFalse(report["ready_for_full_readonly_audit"])

    def test_manifest_fails_before_any_live_probe(self):
        with patch.object(p, "source_binding", return_value={"status": "BLOCKED"}):
            def forbidden(m): raise AssertionError("unexpected host capture")
            report = p.permission_preflight("orcarouter", capture=forbidden)
        self.assertIn("MANIFEST_SOURCE_BINDING_UNQUALIFIED", report["issues"])

    def test_docker_identity_drift_aborts_before_procfs(self):
        def wrong(argv):
            obj = json.loads(inspect(argv)); obj["Id"] = "b" * 64
            return json.dumps(obj)
        with tempfile.TemporaryDirectory() as tmp:
            report = p.permission_preflight("orcarouter",
                capture=lambda m: owner(), run_command=wrong, proc=Path(tmp))
        self.assertIn("FRESH_DOCKER_INSPECT_IDENTITY_UNQUALIFIED", report["issues"])
        self.assertNotIn("pids", report)

    def test_non_orcarouter_model_never_probes_host(self):
        with patch.object(p, "source_binding", return_value={
                "status": "DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED"}):
            def forbidden(m): raise AssertionError("unexpected live probe")
            report = p.permission_preflight("future", capture=forbidden)
        self.assertIn("ONLY_ORCAROUTER_LIVE_AUDIT_IMPLEMENTED", report["issues"])

    def test_wizard_json_blocks_and_returns_rc3(self):
        with patch.object(p, "permission_preflight", return_value={
                "status": "BLOCKED_PERMISSION_PREFLIGHT",
                "issues": ["SMAPS_ACCESS_DENIED"], "production_released": False}), \
                contextlib.redirect_stdout(io.StringIO()) as stdout:
            rc = operations_main(["p5d-permission-preflight",
                                  "--model", "orcarouter", "--json"])
        self.assertEqual(rc, 3)
        self.assertIn("SMAPS_ACCESS_DENIED", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
