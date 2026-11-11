"""Fake-DGX-only one-shot 27B Native Tools trial safety regression.

Uses in-memory Docker adapter and local tmp dirs. Never runs actual Docker/GPU.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import unittest

from scripts.manager import p2_27b_tool_live_trial as mod
from scripts.manager.p2_27b_tool_variant import variant_command, VARIANT_CONTAINER
from scripts.manager.p2_27b_tool_template_audit import EXPECTED_TEMPLATE_SHA256

NOW = 1794024000
SRC_ID = "a" * 64
SRC_IMAGE = "sha256:" + "b" * 64
FLASH_ID = "c" * 64
FLASH_IMAGE = "sha256:" + "d" * 64
PLAN_SHA = "e" * 64


def docs():
    source = {
        "Name": "/" + mod.SOURCE_CONTAINER,
        "Id": SRC_ID, "Image": SRC_IMAGE,
        "State": {"Running": True},
        "Config": {"Cmd": ["some-pinned-snapshot", "--served-model-name", mod.SERVED]},
        "HostConfig": {
            "AutoRemove": False, "RestartPolicy": {"Name": "no"},
            "PortBindings": {"8000/tcp": [{"HostPort": "8000"}]},
            "DeviceRequests": [{"Count": -1}],
        },
        "Mounts": [{"Destination": "/hf", "Source": "/fake/hf",
                    "RW": False, "Type": "bind"}],
    }
    flash = {
        "Name": "/" + mod.FALLBACK_CONTAINER,
        "Id": FLASH_ID, "Image": FLASH_IMAGE,
        "State": {"Running": False},
        "Config": {"Cmd": []},
        "HostConfig": {"AutoRemove": False, "RestartPolicy": {"Name": "no"},
                       "DeviceRequests": []},
    }
    return {mod.SOURCE_CONTAINER: source, mod.FALLBACK_CONTAINER: flash}


class FakeDocker:
    def __init__(self, *, start_error=False, tool_error=False, restore_error=False,
                 stream_error=False, foreign_gpu=False):
        self.state = docs()
        self.calls = []
        self.start_error = start_error
        self.tool_error = tool_error
        self.restore_error = restore_error
        self.stream_error = stream_error
        self.foreign_gpu = foreign_gpu

    def inspect(self, name):
        self.calls.append(("inspect", name))
        return deepcopy(self.state[name])

    def run(self, args, timeout=35):
        self.calls.append(tuple(args))
        if args[:3] == ["docker", "ps", "-a"]:
            return SimpleNamespace(returncode=0, stdout="\n".join(self.state) + "\n")
        if args[:2] == ["docker", "ps"]:
            names = [name for name, d in self.state.items()
                     if d["State"]["Running"]]
            if self.foreign_gpu:
                names.append("foreign")
                self.state["foreign"] = {
                    "Name": "/foreign", "Id": "f" * 64,
                    "Image": "sha256:" + "0" * 64,
                    "HostConfig": {"DeviceRequests": [{"Count": 1}]},
                    "Config": {"Env": []},
                    "State": {"Running": True},
                }
            return SimpleNamespace(returncode=0, stdout="\n".join(names) + ("\n" if names else ""))
        if args[:2] == ["docker", "stop"]:
            name = args[-1]
            self.state[name]["State"]["Running"] = False
            return SimpleNamespace(returncode=0, stdout="")
        if args[:2] == ["docker", "start"]:
            if self.restore_error:
                return SimpleNamespace(returncode=1, stdout="")
            self.state[args[-1]]["State"]["Running"] = True
            return SimpleNamespace(returncode=0, stdout="")
        if args[:3] == ["docker", "inspect", "--format"]:
            name = args[-1]
            return SimpleNamespace(
                returncode=0,
                stdout=str(self.state[name]["State"]["Running"]).lower() + "\n",
            )
        if args[:3] == ["ss", "-H", "-ltn"]:
            busy = any(d["State"]["Running"] and name in (
                mod.SOURCE_CONTAINER, mod.VARIANT_CONTAINER,
            ) for name, d in self.state.items())
            output = ("LISTEN 0 128 0.0.0.0:8000 0.0.0.0:*\n" if busy else "")
            return SimpleNamespace(returncode=0, stdout=output)
        if args[:3] == ["docker", "run", "-d"]:
            if self.start_error:
                return SimpleNamespace(returncode=1, stdout="")
            image_ix = args.index(SRC_IMAGE)
            labels = {}
            for i in range(0, image_ix):
                if args[i] == "--label":
                    k, v = args[i + 1].split("=", 1)
                    labels[k] = v
            target = deepcopy(self.state[mod.SOURCE_CONTAINER])
            target["Name"] = "/" + mod.VARIANT_CONTAINER
            target["Id"] = "9" * 64
            target["State"]["Running"] = True
            target["Config"]["Labels"] = labels
            target["Config"]["Cmd"] = args[image_ix + 1:]
            self.state[mod.VARIANT_CONTAINER] = target
            return SimpleNamespace(returncode=0, stdout="9" * 64 + "\n")
        raise AssertionError("UNEXPECTED_DOCKER_OR_MUTATION " + str(args))

    def wait(self, name, served, seconds, run=None):
        self.calls.append(("wait", name))
        return (
            served == mod.SERVED and name in self.state
            and self.state[name]["State"]["Running"]
        )

    def chat(self, model):
        self.calls.append(("chat", model))
        return model == mod.SERVED and self.state[mod.SOURCE_CONTAINER]["State"]["Running"]

    def tools(self):
        self.calls.append(("tools",))
        return {"status": "BLOCKED" if self.tool_error else "LOCAL_STRUCTURED_TOOL_CYCLE_PASS",
                "structured_tool_call": not self.tool_error,
                "tool_result_continuation": not self.tool_error,
                "issues": ["SYNTHETIC_TOOL_FAIL"] if self.tool_error else []}

    def stream(self):
        self.calls.append(("stream",))
        return {"status": "BLOCKED" if self.stream_error else "LOCAL_STREAMED_TOOL_CALL_PASS",
                "streamed_tool_call": not self.stream_error,
                "issues": ["SYNTHETIC_STREAM_FAIL"] if self.stream_error else []}


def make_ready():
    return {
        "status": mod.READY, "plan_id": PLAN_SHA,
        "expires_at_epoch_seconds": NOW + 300,
        "source_container_id": SRC_ID, "source_image": SRC_IMAGE,
        "fallback_id": FLASH_ID, "fallback_image": FLASH_IMAGE,
        "command_private_for_guarded_executor":
            variant_command(Path("/fake/hf"), SRC_IMAGE),
    }


class NativeToolsLiveTrialCPU(unittest.TestCase):
    def trial(self, fake=None, *, approval=PLAN_SHA, ack=mod.ACK,
              target=mod.ACK_TARGET):
        d = fake or FakeDocker()
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            code, result = mod.execute(
                approval, ack, target,
                root=base / "tools", operating_root=base / "operating",
                planner=lambda **kw: make_ready(),
                run=d.run, inspect=d.inspect, waiter=d.wait,
                probe=d.tools, streamed=d.stream, chat=d.chat,
                now=lambda: NOW,
            )
            files = sorted(p.name for p in (base / "tools").glob("*"))
            return code, result, d, files

    def test_success_uses_distinct_variant_then_restores_exact_original(self):
        code, result, d, files = self.trial()
        self.assertEqual(code, 0, result)
        self.assertEqual(result["status"], "PASS_RESTORED")
        self.assertTrue(result["structured_tool_call"])
        self.assertTrue(result["tool_result_continuation"])
        self.assertTrue(result["streamed_tool_call"])
        self.assertTrue(result["original_restored"])
        self.assertEqual(d.state[mod.SOURCE_CONTAINER]["Id"], SRC_ID)
        self.assertTrue(d.state[mod.SOURCE_CONTAINER]["State"]["Running"])
        self.assertEqual(d.state[mod.VARIANT_CONTAINER]["Id"], "9" * 64)
        self.assertFalse(d.state[mod.VARIANT_CONTAINER]["State"]["Running"])
        self.assertTrue(d.state[mod.FALLBACK_CONTAINER]["Id"] == FLASH_ID)
        self.assertIn("attempt-" + PLAN_SHA + ".json", files)
        self.assertIn("result-" + PLAN_SHA + ".json", files)
        calls = d.calls
        stop_source = next(i for i, c in enumerate(calls)
                           if c[:2] == ("docker", "stop") and c[-1] == mod.SOURCE_CONTAINER)
        start_variant = next(i for i, c in enumerate(calls)
                             if c[:3] == ("docker", "run", "-d"))
        stop_variant = next(i for i, c in enumerate(calls)
                            if c[:2] == ("docker", "stop") and c[-1] == mod.VARIANT_CONTAINER)
        start_original = next(i for i, c in enumerate(calls)
                              if c[:2] == ("docker", "start") and c[-1] == mod.SOURCE_CONTAINER)
        self.assertLess(stop_source, start_variant)
        self.assertLess(start_variant, stop_variant)
        self.assertLess(stop_variant, start_original)
        self.assertFalse(any(c[:2] == ("docker", "rm") for c in calls))
        self.assertFalse(any(c[:2] == ("docker", "rmi") for c in calls))

    def test_wrong_plan_or_ack_cannot_touch_docker(self):
        for a, b, c in (
            ("0" * 64, mod.ACK, mod.ACK_TARGET),
            (PLAN_SHA, "NOT_APPROVED", mod.ACK_TARGET),
            (PLAN_SHA, mod.ACK, "NOT_APPROVED"),
        ):
            code, result, d, files = self.trial(approval=a, ack=b, target=c)
            self.assertEqual(code, 3)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(d.calls, [])
            self.assertFalse(any(name.startswith("attempt-") for name in files))

    def test_failed_variant_start_restores_original(self):
        code, result, d, files = self.trial(FakeDocker(start_error=True))
        self.assertEqual(result["status"], "FAIL_RESTORED")
        self.assertTrue(result["original_restored"])
        self.assertTrue(d.state[mod.SOURCE_CONTAINER]["State"]["Running"])
        self.assertNotIn(mod.VARIANT_CONTAINER, d.state)

    def test_failed_structured_tools_restores_and_reports(self):
        code, result, d, _ = self.trial(FakeDocker(tool_error=True))
        self.assertEqual(result["status"], "FAIL_RESTORED")
        self.assertFalse(result["structured_tool_call"])
        self.assertFalse(result["streamed_tool_call"])
        self.assertTrue(result["original_restored"])
        self.assertTrue(d.state[mod.SOURCE_CONTAINER]["State"]["Running"])

    def test_partial_stream_failure_is_not_full_pass(self):
        code, result, d, _ = self.trial(FakeDocker(stream_error=True))
        self.assertEqual(result["status"], "PARTIAL_RESTORED")
        self.assertTrue(result["structured_tool_call"])
        self.assertFalse(result["streamed_tool_call"])
        self.assertTrue(result["original_restored"])

    def test_restore_failure_is_not_success(self):
        code, result, d, _ = self.trial(FakeDocker(restore_error=True))
        self.assertEqual(result["status"], "RECOVERY_FAILED")
        self.assertFalse(result["original_restored"])
        self.assertFalse(d.state[mod.SOURCE_CONTAINER]["State"]["Running"])

    def test_foreign_gpu_fails_before_stop(self):
        code, result, d, _ = self.trial(FakeDocker(foreign_gpu=True))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["executed"])
        self.assertFalse(any(
            c[:2] == ("docker", "stop") for c in d.calls
        ))

    def test_preexisting_attempt_blocks_planning(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ("attempt-" + PLAN_SHA + ".json")).write_text("{}")
            self.assertTrue(mod._prior_attempts(root))

    def test_read_only_plan_requires_real_template_and_p3_lineage(self):
        src = docs()[mod.SOURCE_CONTAINER]
        flash = docs()[mod.FALLBACK_CONTAINER]
        def preview():
            return {
                "read_only_preflight_pass": True, "issues": [],
                "candidate_command_NOT_EXECUTABLE":
                    variant_command(Path("/fake/hf"), SRC_IMAGE),
            }
        def template():
            return {
                "status": "CPU_TEMPLATE_RENDER_VALIDATED_ONLY", "issues": [],
                "template_sha256": EXPECTED_TEMPLATE_SHA256,
                "tool_prompt_rendered": True, "tool_result_rendered": True,
                "non_tool_prompt_rendered": True, "no_thinking_rendered": True,
                "thinking_prompt_rendered": True,
            }
        def historical():
            return {
                "status": "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED", "issues": [],
                "records": {"a": {
                    "id_27b": SRC_ID, "image_27b": SRC_IMAGE,
                    "flash_id": FLASH_ID, "flash_image": FLASH_IMAGE,
                }},
                "receipt_sha256": {"a": "1" * 64, "b": "2" * 64, "c": "3" * 64},
            }
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = mod.make_plan(
                preview=preview, template=template,
                historical=historical,
                journal=lambda _: {"status": "VERIFIED", "issues": [],
                                   "phase": "COMMITTED", "last_event_hash": "4" * 64},
                inspect=lambda n: deepcopy(src if n == mod.SOURCE_CONTAINER else flash),
                root=root / "tools", operating_root=root / "ops",
                now=NOW,
            )
            self.assertEqual(plan["status"], mod.READY, plan["issues"])
            self.assertEqual(len(plan["plan_id"]), 64)
            self.assertFalse(plan["execution_enabled"])
            self.assertTrue(plan["restore_original_after_trial"])
            self.assertIn("command_private_for_guarded_executor", plan)
            (root / "tools").mkdir()
            (root / "tools" / ("attempt-" + plan["plan_id"] + ".json")).write_text("{}")
            blocked = mod.make_plan(
                preview=preview, template=template, historical=historical,
                journal=lambda _: {"status": "VERIFIED", "issues": [],
                                   "phase": "COMMITTED", "last_event_hash": "4" * 64},
                inspect=lambda n: deepcopy(src if n == mod.SOURCE_CONTAINER else flash),
                root=root / "tools", operating_root=root / "ops", now=NOW,
            )
            self.assertEqual(blocked["status"], "BLOCKED")
            self.assertIn("PRIOR_TOOLS_TRIAL_REQUIRES_MANUAL_RECONCILIATION",
                          blocked["issues"])


if __name__ == "__main__":
    unittest.main()
