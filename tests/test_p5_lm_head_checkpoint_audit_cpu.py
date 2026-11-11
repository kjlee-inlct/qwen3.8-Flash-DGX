"""Offline P5 pinned FP8 LM-head metadata and no-GPU plan gate regressions."""
from __future__ import annotations

import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.manager import p5_lm_head_checkpoint_audit as audit
from scripts.manager import p5_live_trial as live


def build_fixture(root: Path, *, ignore=None, target="lm_head",
                  weight_dtype="F8_E4M3", scale=True):
    snap = root / "snapshots" / "pinned"
    snap.mkdir(parents=True)
    cfg = {
        "quantization_config": {
            "quant_method": "compressed-tensors",
            "format": "dense",
            "ignore": ignore or [],
            "config_groups": {
                "group_head": {
                    "targets": [target],
                    "weights": {"type": "float", "num_bits": 8,
                                "strategy": "channel"},
                },
            },
        },
    }
    (snap / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    keys = {"lm_head.weight": {
        "dtype": weight_dtype,
        "shape": [32, 16], "data_offsets": [0, 512],
    }}
    if scale:
        keys["lm_head.weight_scale"] = {
            "dtype": "F32", "shape": [32], "data_offsets": [512, 640],
        }
    header = json.dumps(keys).encode()
    (snap / "model-00017-of-00017.safetensors").write_bytes(
        struct.pack("<Q", len(header)) + header + bytes(640)
    )
    (snap / "model.safetensors.index.json").write_text(json.dumps({
        "weight_map": {key: "model-00017-of-00017.safetensors"
                       for key in keys}
    }), encoding="utf-8")
    return snap


class P5LMHeadCheckpointAuditCPU(unittest.TestCase):
    def test_metadata_is_read_only_and_pass_is_not_gpu_verified(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            snap = build_fixture(root)
            before = {p.name: p.read_bytes() for p in snap.iterdir()}
            result = audit.inspect(snap, root)
            self.assertEqual(result["status"], "PASS", result)
            self.assertTrue(result["checkpoint_metadata_verified"])
            self.assertFalse(result["weight_registration_verified"])
            self.assertFalse(result["gpu_verified"])
            self.assertFalse(result["executed"])
            self.assertEqual(result["lm_head"]["weight_scale"]["dtype"], "F32")
            self.assertEqual(before, {p.name: p.read_bytes()
                                     for p in snap.iterdir()})

    def test_scale_present_but_ignore_hard_blocks(self):
        for ignored in ("lm_head", "re:.*lm_head$"):
            with self.subTest(ignore=ignored), TemporaryDirectory() as d:
                root = Path(d)
                snap = build_fixture(root, ignore=[ignored])
                result = audit.inspect(snap, root)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIn("P5_LMHEAD_SCALE_PRESENT_BUT_HEAD_IGNORED",
                              result["issues"])

    def test_generic_linear_group_does_not_prove_head_target(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            snap = build_fixture(root, target="Linear")
            result = audit.inspect(snap, root)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIn("P5_LMHEAD_FP8_QUANT_TARGET_UNVERIFIED",
                          result["issues"])

    def test_missing_scale_and_non_fp8_are_blocked(self):
        for kw, code in [
            ({"scale": False}, "P5_LMHEAD_WEIGHT_SCALE_INDEX_MISSING"),
            ({"weight_dtype": "BF16"}, "P5_LMHEAD_WEIGHT_NOT_FP8"),
            ({"target": "lm_head", "ignore": ["re:.*lm_head$"]},
             "P5_LMHEAD_SCALE_PRESENT_BUT_HEAD_IGNORED"),
        ]:
            with self.subTest(kw=kw), TemporaryDirectory() as d:
                root = Path(d)
                result = audit.inspect(build_fixture(root, **kw), root)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIn(code, result["issues"])

    def test_index_path_escape_and_header_mismatch_fail_closed(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            snap = build_fixture(root)
            index = snap / "model.safetensors.index.json"
            data = json.loads(index.read_text())
            data["weight_map"]["lm_head.weight"] = "../outside.safetensors"
            index.write_text(json.dumps(data))
            result = audit.inspect(snap, root)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIn("P5_LMHEAD_SHARD_FILENAME_UNVERIFIED",
                          result["issues"])
        with TemporaryDirectory() as d:
            root = Path(d)
            snap = build_fixture(root)
            shard = snap / "model-00017-of-00017.safetensors"
            shard.write_bytes(b"BAD")
            self.assertEqual(audit.inspect(snap, root)["status"], "BLOCKED")

    def test_missing_snapshot_and_oversize_index_fail_closed(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(
                audit.inspect(root / "absent", root)["status"], "BLOCKED"
            )
            snap = build_fixture(root)
            with patch.object(audit, "MAX_INDEX", 10):
                result = audit.inspect(snap, root)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIn("P5_LMHEAD_METADATA_SIZE_EXCEEDED",
                          result["issues"])

    def test_live_trial_metadata_gate_blocks_without_checkpoint_pass(self):
        ple = {"status": "PASS", "metadata_verified": True}
        spec = {"source": {"kind": "PINNED_HF_SNAPSHOT",
                           "repo_id": live.ORCA_REPO,
                           "revision": live.ORCA_REV},
                "format": {"storage_dtype": "BF16", "scale_mode": "NONE"}}
        with patch.object(live.manifest_registry, "validate",
                          return_value={"status": "PASS"}), \
             patch.object(live, "asset_spec", return_value=spec), \
             patch.object(live, "policy", return_value={
                 "api": {"host_port": 8000}}), \
             patch.object(live, "inspect_ple_asset", return_value=ple), \
             patch.object(live, "_source_snapshot", return_value=True), \
             patch.object(live, "inspect_lm_head_checkpoint", return_value={
                 "status": "BLOCKED",
                 "issues": ["P5_LMHEAD_SCALE_PRESENT_BUT_HEAD_IGNORED"],
                 "checkpoint_metadata_verified": False}):
            issues, details = live._metadata_gate()
        self.assertIn("P5_LMHEAD_SCALE_PRESENT_BUT_HEAD_IGNORED", issues)
        self.assertFalse(details["lm_head_checkpoint"][
            "checkpoint_metadata_verified"])


if __name__ == "__main__":
    unittest.main()
