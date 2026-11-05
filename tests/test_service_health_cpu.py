"""No real HTTP, Docker or GPU: service health observation contract tests."""
from __future__ import annotations

import io
import json
import unittest
from unittest.mock import Mock

from scripts.manager.service_health import inspect_api_health


class Response(io.BytesIO):
    def __init__(self, data=b"", status=200):
        super().__init__(data)
        self.status = status


class HealthCPU(unittest.TestCase):
    def setUp(self):
        self.service = {
            "status": "OBSERVED_UNQUALIFIED",
            "observed_model": "flash-next",
            "api_port_8000_listening": True, "issues": [],
            "download_running": True,
        }
        self.calls = []

    def opener(self, request, *, timeout):
        self.assert_url(request)
        self.calls.append(request.full_url)
        if request.full_url.endswith("/health"):
            return Response()
        return Response(json.dumps({"data": [
            {"id": "qwen3.8-flash-next"},
        ]}).encode())

    def assert_url(self, request):
        self.assertTrue(request.full_url.startswith("http://127.0.0.1:8000/"))
        self.assertEqual(request.get_method(), "GET")

    def test_api_healthy_even_when_checkpoint_download_running(self):
        result = inspect_api_health(service=self.service, opener=self.opener)
        self.assertEqual(result["status"], "API_IDENTITY_CONFIRMED")
        self.assertEqual(len(self.calls), 2)
        self.assertTrue(result["api_identity_verified"])
        self.assertTrue(result["health_http_ok"])
        self.assertFalse(result["gpu_exclusivity_verified"])
        self.assertFalse(result["executed"])

    def test_unverified_container_inventory_performs_no_http(self):
        service = {**self.service, "status": "BLOCKED"}
        opener = Mock(side_effect=AssertionError("HTTP not allowed"))
        result = inspect_api_health(service=service, opener=opener)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("SERVICE_MANIFEST_UNVERIFIED", result["issues"])
        opener.assert_not_called()

    def test_unbound_port_performs_no_http(self):
        service = {**self.service, "api_port_8000_listening": False}
        opener = Mock(side_effect=AssertionError("HTTP not allowed"))
        result = inspect_api_health(service=service, opener=opener)
        self.assertIn("API_PORT_NOT_LISTENING", result["issues"])
        opener.assert_not_called()

    def test_wrong_served_model_id_fails_closed(self):
        def wrong(request, *, timeout):
            if request.full_url.endswith("/health"):
                return Response()
            return Response(b'{"data":[{"id":"other"}]}')
        result = inspect_api_health(service=self.service, opener=wrong)
        self.assertFalse(result["api_identity_verified"])
        self.assertIn("SERVED_MODEL_ID_MISMATCH", result["issues"])

    def test_large_payload_is_bounded(self):
        def huge(request, *, timeout):
            if request.full_url.endswith("/health"):
                return Response()
            return Response(b"x" * (64 * 1024 + 1))
        result = inspect_api_health(service=self.service, opener=huge)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("API_OBSERVATION_FAILED:ValueError", result["issues"])

    def test_orcarouter_unqualified_never_queries_api(self):
        service = {**self.service, "observed_model": "orcarouter"}
        opener = Mock(side_effect=AssertionError("HTTP not allowed"))
        result = inspect_api_health(service=service, opener=opener)
        self.assertIn("EXPECTED_SERVED_ID_UNQUALIFIED", result["issues"])
        opener.assert_not_called()


if __name__ == "__main__":
    unittest.main()
