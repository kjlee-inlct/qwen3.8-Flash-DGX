"""Fake-DGX/CPU tests for non-mutating pinned NVIDIA Jinja render audit."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest

from scripts.manager import p2_27b_tool_template_audit as mod
from scripts.manager import p2_27b_tool_variant as variant


def probe_doc(**changes):
    value = {
        "status": "CPU_TEMPLATE_RENDER_VALIDATED_ONLY",
        "template_present": True,
        "tokenizer_auto_template_present": True,
        "template_sha256": "a" * 64,
        "transformers_version": "5.8.0",
        "tool_prompt_rendered": True,
        "tool_result_rendered": True,
        "no_thinking_rendered": True,
        "non_tool_prompt_rendered": True,
        "issues": [],
    }
    value.update(changes)
    return value


def fake_runner(payload=None, *, rc=0, exception=None):
    seen = []
    def run(command, **kwargs):
        seen.append((command, kwargs))
        if exception is not None:
            raise exception
        return SimpleNamespace(
            returncode=rc, stdout=json.dumps(
                probe_doc() if payload is None else payload
            ), stderr="",
        )
    return run, seen


class NativeToolTemplateAuditCPU(unittest.TestCase):
    def test_isolated_variant_uses_only_pinned_template(self):
        cmd = variant.variant_command(Path("/test/cache"), "sha256:" + "a" * 64)
        self.assertIn("--chat-template", cmd)
        index = cmd.index("--chat-template")
        self.assertEqual(cmd[index + 1], variant.TOOL_CHAT_TEMPLATE)
        self.assertIn("/snapshots/" + variant.REVISION + "/", cmd[index + 1])
        self.assertEqual(
            cmd[-3:], ["qwen3_coder", "--reasoning-parser", "qwen3"]
        )
        self.assertNotEqual(cmd[cmd.index("--name") + 1], variant.SOURCE_CONTAINER)

    def test_cpu_probe_does_not_require_gpu_or_network_or_write(self):
        run, seen = fake_runner()
        result = mod.inspect_template_cpu(run=run)
        self.assertEqual(result["status"], "CPU_TEMPLATE_RENDER_VALIDATED_ONLY")
        self.assertFalse(result["execution_enabled"])
        self.assertFalse(result["gpu_inference_executed"])
        self.assertFalse(result["docker_state_mutated"])
        self.assertIsNone(result["plan_id"])
        self.assertFalse(result["approval_accepted"])
        self.assertEqual(len(seen), 1)
        command, kw = seen[0]
        self.assertEqual(command[:3], ["docker", "exec", "-i"])
        self.assertIn("CUDA_VISIBLE_DEVICES=-1", command)
        self.assertIn("HF_HUB_OFFLINE=1", command)
        self.assertIn("PYTHONDONTWRITEBYTECODE=1", command)
        self.assertEqual(command[-4:], [
            variant.SOURCE_CONTAINER, "python3", "-B", "-"
        ][-4:])
        self.assertEqual(kw["timeout"], 90)
        self.assertIn("tok.apply_chat_template", kw["input"])
        self.assertTrue(kw["capture_output"])
        self.assertTrue(kw["text"])

    def test_missing_file_fails_closed(self):
        run, _ = fake_runner(probe_doc(
            status="BLOCKED", template_present=False,
            issues=["PINNED_CHAT_TEMPLATE_FILE_MISSING"]
        ))
        result = mod.inspect_template_cpu(run=run)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("PINNED_CHAT_TEMPLATE_FILE_MISSING", result["issues"])

    def test_tool_result_render_failure_fails_closed(self):
        run, _ = fake_runner(probe_doc(
            status="BLOCKED", tool_result_rendered=False,
            issues=["TEMPLATE_RENDER_FAILED_TOOL_RESULT_RENDERED"]
        ))
        result = mod.inspect_template_cpu(run=run)
        self.assertEqual(result["status"], "BLOCKED")

    def test_status_forgery_fails_closed(self):
        run, _ = fake_runner(probe_doc(status="MALFORMED"))
        result = mod.inspect_template_cpu(run=run)
        self.assertIn("CPU_TEMPLATE_NOT_VALIDATED", result["issues"])

    def test_nonzero_exit_fails_closed(self):
        run, _ = fake_runner(rc=125)
        result = mod.inspect_template_cpu(run=run)
        self.assertIn("DOCKER_EXEC_CPU_PROBE_NONZERO_EXIT", result["issues"])

    def test_timeout_fails_closed(self):
        run, _ = fake_runner(exception=subprocess.TimeoutExpired(
            ["docker", "exec"], 90))
        result = mod.inspect_template_cpu(run=run)
        self.assertIn("DOCKER_EXEC_CPU_PROBE_TIMEOUT", result["issues"])

    def test_malformed_json_fails_closed(self):
        def run(*args, **kwargs):
            return SimpleNamespace(returncode=0, stdout="{", stderr="")
        result = mod.inspect_template_cpu(run=run)
        self.assertEqual(result["status"], "BLOCKED")

    def test_invalid_issues_fail_closed(self):
        run, _ = fake_runner(probe_doc(issues="not-a-list"))
        result = mod.inspect_template_cpu(run=run)
        self.assertEqual(result["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
