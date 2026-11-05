"""Bounded read-only local API health + served-model identity inspection.

Never submits inference requests, changes Docker, launches GPU workloads or
accepts arbitrary URLs. This is API identity evidence, not GPU qualification.
"""
from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from scripts.manager.service_manifest import inspect_service, policy

API_BASE = "http://127.0.0.1:8000"
MAX_RESPONSE = 64 * 1024
MAX_MODELS = 32
TIMEOUT = 3


def _get(url: str, opener) -> tuple[int, bytes]:
    # URL constructed exclusively from trusted, fixed local API path.
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    with opener(request, timeout=TIMEOUT) as response:
        status = int(response.status)
        body = response.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE:
            raise ValueError("API_RESPONSE_TOO_LARGE")
        return status, body


def inspect_api_health(*, service: dict[str, Any] | None = None,
                       opener=urlopen) -> dict[str, Any]:
    if service is None:
        try:
            service = inspect_service()
        except (OSError, ValueError, RuntimeError) as exc:
            service = {"status": "BLOCKED", "observed_model": None,
                       "issues": ["SERVICE_OBSERVATION_FAILED:" + type(exc).__name__]}
    result: dict[str, Any] = {
        "schema_version": 1, "stage": "svc", "scope": "LOCAL_API_READ_ONLY",
        "status": "BLOCKED", "executed": False,
        "operations_enabled": False, "api_host_port": 8000,
        "observed_model": service.get("observed_model"),
        "api_identity_verified": False,
        "gpu_exclusivity_verified": False,
        "health_http_ok": False, "model_ids": [],
        "issues": list(service.get("issues", [])),
        "notice": "Local HTTP API evidence only; GPU and transition readiness are not verified.",
    }
    if service.get("status") != "OBSERVED_UNQUALIFIED":
        result["issues"].append("SERVICE_MANIFEST_UNVERIFIED")
        return result
    if not service.get("api_port_8000_listening"):
        result["issues"].append("API_PORT_NOT_LISTENING")
        return result
    selected = service.get("observed_model")
    config = policy()
    expected_id = config.get("models", {}).get(selected or "", {}).get("served_id")
    if not isinstance(expected_id, str) or not expected_id:
        result["issues"].append("EXPECTED_SERVED_ID_UNQUALIFIED")
        return result
    result["expected_model_id"] = expected_id
    try:
        health_code, _ = _get(API_BASE + "/health", opener)
        models_code, payload = _get(API_BASE + "/v1/models", opener)
        result["health_http_ok"] = health_code == 200
        if health_code != 200 or models_code != 200:
            result["issues"].append("HTTP_NOT_OK")
            return result
        data = json.loads(payload)
        models = data.get("data") if isinstance(data, dict) else None
        if not isinstance(models, list) or len(models) > MAX_MODELS:
            result["issues"].append("INVALID_MODELS_PAYLOAD")
            return result
        ids = [m.get("id") for m in models if isinstance(m, dict)]
        if any(not isinstance(v, str) or len(v) > 128 for v in ids):
            result["issues"].append("INVALID_MODEL_ID")
            return result
        result["model_ids"] = sorted(set(ids))
        result["api_identity_verified"] = expected_id in ids
        if not result["api_identity_verified"]:
            result["issues"].append("SERVED_MODEL_ID_MISMATCH")
            return result
        result["status"] = "API_IDENTITY_CONFIRMED"
    except (HTTPError, URLError, OSError, TimeoutError, ValueError,
            UnicodeError, json.JSONDecodeError) as exc:
        result["issues"].append("API_OBSERVATION_FAILED:" + type(exc).__name__)
    result["issues"] = sorted(set(result["issues"]))
    return result
