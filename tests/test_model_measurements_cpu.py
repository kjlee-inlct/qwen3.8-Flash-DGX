"""CPU-only model measurement, provenance and approval regression tests."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from scripts.manager import model_measurements as m
from scripts.manager import measurement_bench as b
from wizard.main import main as wizard_main

SPEC = {"checkpoint": "orcarouter/example", "served_id": "example-api",
        "container": "demo-container", "recipe_path": "recipes/example.json"}
CAT = {"models": {"orcarouter": SPEC}}
CID = "a" * 64


def resource():
    return {
        "model": "orcarouter", "status": "OBSERVED_PARTIAL",
        "timestamp_utc": "2026-11-12T00:00:00+00:00", "git_head": "b" * 40,
        "host_memory": {"MemTotal_bytes": 100000, "MemAvailable_bytes": 41000,
                        "Cached_bytes": 20000, "swap_used_bytes": 10},
        "pressure": {"memory": {"some": {"avg10": 0.4}}},
        "cpu_frequency": {"current_mhz_mean": 2808},
        "gpu": {"metrics": [{"utilization.gpu": 7.0, "temperature.gpu": 37.0}]},
        "docker": {
            "status": "OBSERVED", "container": {
                "id": CID, "name": "demo-container", "running": True},
            "cgroup_v2": {"metrics": {"memory.current": "27000", "memory.peak": "40000",
                                     "memory.swap.current": "0",
                                     "memory_stat_bytes": {"anon": 1000, "file": 21000,
                                                           "inactive_file": 15000}}},
            "process_smaps_rollup_bytes": {"Rss": 8000, "Pss": 7000},
            "ple_specific_resident_bytes": None,
        },
        "ple_declared_mmap_bytes": 102400491520,
    }


class MetricInventoryCPU(unittest.TestCase):
    def test_catalog_is_extensible_and_has_old_and_new_metrics(self):
        keys = m.metric_catalog()
        for key in ("host_mem_available_bytes", "cgroup_memory_peak_bytes",
                    "gpu_utilization_pct", "weight_load_reported_gib",
                    "kv_capacity_reported_tokens", "loaded_ttfc_seconds",
                    "loaded_generation_tps"):
            self.assertIn(key, keys)
        self.assertEqual(keys["host_mem_available_bytes"]["unit"], "B")

    def test_log_parses_engine_labels_without_ever_retaining_logs(self):
        raw = "SECRET PROMPT\nLoading model weights took 76.21 GiB\nGPU KV cache size: 221,000 tokens\nAvailable KV cache memory: 17.37 GiB\n"
        parsed = m.parse_runtime_log(raw)
        self.assertEqual(parsed["weight_load_reported_gib"]["value"], 76.21)
        self.assertEqual(parsed["kv_capacity_reported_tokens"]["value"], 221000)
        self.assertEqual(parsed["kv_available_reported_gib"]["value"], 17.37)
        self.assertNotIn("SECRET PROMPT", json.dumps(parsed))
        self.assertEqual(m.parse_runtime_log("")["kv_capacity_reported_tokens"]["status"], "NOT_OBSERVED")

    def test_launch_flag_parser_never_emits_secret_unrelated_flags(self):
        flags = m._flags(["vllm", "serve", "--max-model-len", "8192",
                          "--gpu-memory-utilization=0.7", "--enforce-eager",
                          "--api-key", "SENSITIVE"])
        self.assertEqual(flags["max-model-len"], "8192")
        self.assertEqual(flags["gpu-memory-utilization"], "0.7")
        self.assertTrue(flags["enforce-eager"])
        self.assertNotIn("api-key", flags)

    def test_exact_id_docker_logs_only_and_whitelisted_environment(self):
        called = []
        def fake(argv, **kwargs):
            called.append(argv)
            if argv[1] == "inspect":
                content = json.dumps({
                    "Id": CID, "Name": "/demo-container", "State": {"Running": True},
                    "Config": {"Entrypoint": ["vllm", "serve"], "Cmd": ["--max-model-len", "8192"],
                               "Env": ["VLLM_PLE_MMAP=1", "HF_TOKEN=SECRET"]}})
            else:
                content = "Loading model weights took 76.21 GiB\nGPU KV cache size: 3,000 tokens\nSECRET"
            return types.SimpleNamespace(returncode=0, stdout=content)
        doc = m._runtime({"id": CID, "name": "demo-container"}, runner=fake)
        self.assertEqual(doc["selected_env"], {"VLLM_PLE_MMAP": "1"})
        self.assertEqual(doc["launch_flags"]["max-model-len"], "8192")
        self.assertEqual(doc["log_metrics"]["kv_capacity_reported_tokens"]["value"], 3000)
        self.assertNotIn("SECRET", json.dumps(doc))
        self.assertEqual([c[1] for c in called], ["inspect", "logs"])
        self.assertEqual(called[1][-1], CID)

    def test_drift_stops_logs_and_does_not_claim_metrics(self):
        def fake(argv, **kwargs):
            return types.SimpleNamespace(returncode=0, stdout=json.dumps({
                "Id": "c" * 64, "Name": "/demo-container", "State": {"Running": True}}))
        doc = m._runtime({"id": CID, "name": "demo-container"}, runner=fake)
        self.assertEqual(doc["status"], "NOT_OBSERVED")
        self.assertEqual(doc["log_metrics"]["weight_load_reported_gib"]["status"], "NOT_OBSERVED")

    def test_inventory_keeps_all_existing_resource_telemetry(self):
        with patch.object(m, "model_catalog", return_value=CAT), \
             patch.object(m, "_candidate_profile", return_value={
                 "declared_profile": "mtp0", "runtime_settings_proven": False}), \
             patch.object(m, "_runtime", return_value={
                 "status": "OBSERVED_CONFIG", "launch_flags": {"max-model-len": "8192"},
                 "log_metrics": m.parse_runtime_log("Loading model weights took 70 GiB")}):
            doc = m.inventory("orcarouter", capture=lambda **_: resource())
        self.assertEqual(doc["metrics"]["host_mem_available_bytes"]["value"], 41000)
        self.assertEqual(doc["metrics"]["cgroup_memory_current_bytes"]["value"], 27000)
        self.assertEqual(doc["metrics"]["gpu_utilization_pct"]["value"], 7)
        self.assertEqual(doc["metrics"]["ple_mapped_declared_bytes"]["status"], "DECLARED_NOT_RESIDENT")
        self.assertEqual(doc["metrics"]["ple_resident_bytes"]["status"], "NOT_OBSERVED")
        self.assertEqual(doc["metrics"]["loaded_ttfc_seconds"]["status"], "NOT_OBSERVED")
        self.assertEqual(doc["resource_snapshot"]["docker"]["cgroup_v2"]["metrics"]["memory.peak"], "40000")
        self.assertFalse(doc["profile"]["runtime_settings_proven"])
        self.assertFalse(doc["inference_executed"])

    def test_save_history_private_and_independent(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(m, "model_catalog", return_value=CAT):
            doc = {"schema_version": 1, "model": "orcarouter", "action": "inventory",
                   "status": "READ_ONLY_PARTIAL", "timestamp_utc": "2026-11-12T00:00:00Z",
                   "container": {"id": CID}, "metrics": {"host_mem_available_bytes": {"value": 123}}}
            file = m.save_record(doc, directory=td)
            self.assertEqual(Path(file).stat().st_mode & 0o777, 0o600)
            listed = m.history("orcarouter", directory=td)
            self.assertEqual(listed["count"], 1)
            self.assertEqual(listed["records"][0]["summary"]["host_mem_available_bytes"], 123)
            self.assertFalse(listed["inference_executed"])
            Path(td, "orcarouter--20261112T010203000001Z--aaaaaaaaaaaa.json").write_text("BROKEN")
            self.assertEqual(m.history("orcarouter", directory=td)["count"], 1)

    def test_history_preserves_per_context_measurement_summary(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(m, "model_catalog", return_value=CAT):
            doc = {
                "schema_version": 1, "model": "orcarouter",
                "action": "benchmark-execute", "status": "COLLECTED_UNQUALIFIED",
                "container": {"id": CID},
                "timestamp_utc": "2026-11-12T00:00:00+00:00",
                "results": [{
                    "context_k": 4, "status": "MEASURED",
                    "tokenizer_input_tokens": 4096,
                    "metrics": {"ttft_seconds": 0.8, "ttfc_seconds": 1.4,
                                "generation_tps_after_first_token": 42.2,
                                "prompt_tokens_reported": 4100,
                                "completion_tokens_reported": 128},
                }],
            }
            m.save_record(doc, directory=td)
            rows = m.history("orcarouter", directory=td)["records"]
        self.assertEqual(rows[0]["benchmark_cases"][0]["context_k"], 4)
        self.assertEqual(rows[0]["benchmark_cases"][0]["ttfc_seconds"], 1.4)
        self.assertEqual(rows[0]["benchmark_cases"][0]["generation_tps"], 42.2)

    def test_inventory_cli_blocked_on_unknown_model(self):
        with patch.object(m, "model_catalog", return_value=CAT), \
             contextlib.redirect_stdout(io.StringIO()) as stdout:
            rc = m.main(["inventory", "--model", "not-installed", "--json"])
        self.assertEqual(rc, 3)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "BLOCKED")


class SyntheticBenchmarkCPU(unittest.TestCase):
    def test_contexts_bounded_and_deduplicated(self):
        self.assertEqual(b._contexts("1,4,8"), [1, 4, 8])
        for case in ("", "0", "257", "1,1", "1,a", ",".join(["1"] * 9)):
            with self.subTest(case=case), self.assertRaises(ValueError):
                b._contexts(case)

    def test_plan_does_not_use_live_api(self):
        with patch.object(b, "model_catalog", return_value=CAT), \
             patch.object(b, "_candidate_profile", return_value={}), \
             patch.object(b, "_json_request", side_effect=AssertionError("no network")):
            result = b.benchmark_plan("orcarouter", contexts_k="1,8")
        self.assertFalse(result["inference_executed"])
        self.assertEqual(result["requested_context_k"], [1, 8])
        self.assertEqual(result["requires_exact_ack"], b.ACK)

    def test_benchmark_exact_ack_blocks_every_live_probe(self):
        with patch.object(b, "model_catalog", return_value=CAT), \
             patch.object(b, "_candidate_profile", return_value={}), \
             patch.object(b, "_json_request", side_effect=AssertionError("no network")):
            doc = b.benchmark_execute("orcarouter", ack="wrong")
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertFalse(doc["inference_executed"])

    def test_synthetic_tokenizer_returns_observed_count(self):
        with patch.object(b, "_token_count", side_effect=lambda model, prompt:
                          (len(prompt) // len(b.PROMPT_PATTERN)) * 10):
            prompt, count = b._synthetic_prompt("example-api", 4096)
        self.assertTrue(prompt.startswith(b.PROMPT_PATTERN))
        self.assertLess(abs(count - 4096) / 4096, 0.03)

    def test_sse_ttft_reasoning_precedes_visible_content(self):
        lines = (
            b'data: {"choices":[{"delta":{"reasoning_content":"thinking"},"finish_reason":null}]}\n'
            b'data: {"choices":[{"delta":{"content":"answer"},"finish_reason":"stop"}]}\n'
            b'data: {"choices":[],"usage":{"prompt_tokens":1024,"completion_tokens":10}}\n'
            b'data: [DONE]\n'
        )
        with patch.object(b, "urlopen", return_value=io.BytesIO(lines)):
            result = b._stream_chat("example-api", "prompt", 12)
        self.assertTrue(result["stream_done_observed"])
        self.assertEqual(result["completion_tokens_reported"], 10)
        self.assertGreaterEqual(result["ttfc_seconds"], result["ttft_seconds"])
        self.assertNotIn("answer", json.dumps(result))
        self.assertIsNotNone(result["generation_tps_after_first_token"])

    def test_benchmark_cases_record_context_and_identity_without_prompts(self):
        before = resource()
        def gate(model):
            return SPEC, before, before["docker"]["container"], 8192
        with patch.object(b, "model_catalog", return_value=CAT), \
             patch.object(b, "_candidate_profile", return_value={"declared_profile": "mtp0"}):
            doc = b.benchmark_execute(
                "orcarouter", contexts_k="1,4,8", max_output_tokens=128,
                ack=b.ACK, identity_gate=gate,
                tokenize=lambda model, target: ("PRIVATE_PROMPT", target),
                chat=lambda *a: {"stream_done_observed": True,
                                 "ttfc_seconds": 1.3,
                                 "completion_tokens_reported": 64},
                capture=lambda **_: resource())
        self.assertEqual(doc["status"], "COLLECTED_UNQUALIFIED")
        self.assertEqual(doc["summary"]["measured_cases"], 2)
        self.assertEqual(doc["results"][-1]["status"], "SKIPPED_ACTIVE_CONTEXT_LIMIT")
        self.assertNotIn("PRIVATE_PROMPT", json.dumps(doc))
        self.assertFalse(doc["benchmark_verified"])

    def test_gate_rejects_inconsistent_api_identity(self):
        good_service = {"observed_model": "orcarouter", "status": "LIVE_P5_TRIAL_API_VERIFIED",
                        "expected_served_id": SPEC["served_id"], "issues": []}
        with patch.object(b, "model_catalog", return_value=CAT), \
             self.assertRaisesRegex(ValueError, "API_MODEL_IDENTITY_MISMATCH"):
            b._identity_gate("orcarouter",
                             service_probe=lambda: good_service,
                             capture=lambda **_: resource(),
                             http=lambda _: {"data": [{"id": "wrong-model", "max_model_len": 8192}]})

    def test_wizard_dry_run_explicitly_blocks_benchmark_execute(self):
        with patch.object(b, "_stream_chat", side_effect=AssertionError("must not infer")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            code = wizard_main(["operations", "measurements", "benchmark-execute",
                                "--model", "orcarouter", "--dry-run",
                                "--ack-live-inference", b.ACK, "--json"])
        self.assertEqual(code, 3)
        data = json.loads(output.getvalue())
        self.assertIn("DRY_RUN_INFERENCE_CONFLICT", data["issues"])
        self.assertFalse(data["inference_executed"])

    def test_wizard_routes_generic_measurements_without_inference(self):
        with patch.object(m, "model_catalog", return_value=CAT), \
             patch.object(b, "model_catalog", return_value=CAT), \
             patch.object(b, "_candidate_profile", return_value={}), \
             patch.object(b, "_json_request", side_effect=AssertionError("no network")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wizard_main(["operations", "measurements", "benchmark-plan",
                              "--model", "orcarouter", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "PLAN_ONLY_ACK_REQUIRED")


if __name__ == "__main__":
    unittest.main()
