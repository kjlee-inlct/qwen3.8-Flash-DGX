"""P5 one-shot *development* DGX GPU trial: MTP0 only; NO automatic rollback.

prepare: inspect existing Blazux vLLM0.32 runtime image; never build/patch.
plan: strictly read-only, exact pinned image/source/service state + hash approval.
execute: with exact plan + downtime ack, stop 27B then start Orcarouter on :8000.
Failure leaves original STOPPED, with target retained for logs. No image/cache deletion.
Never confuse GPU trial/health success with production qualification.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import time
from urllib.request import Request, urlopen

from scripts.manager import manifest_registry
from scripts.manager.ple_assets import ASSET_ID, asset_spec, inspect_ple_asset
from scripts.manager.p5_orcarouter import ORCA_REPO, ORCA_REV
from scripts.manager.service_manifest import policy

ROOT = Path(__file__).resolve().parents[2]
STATE = Path.home() / ".local/state/blazux-wizard/p5-live-trial"
SOURCE = "qwen38-27b"
TARGET = "qwen38-orcarouter"
ALIAS = "qwen3.8-flash-next-orca-uncensored-bf16"
ACK = "I_ACCEPT_P5_NO_ROLLBACK"
CACHE = Path.home() / "Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache"
SNAPSHOT = CACHE / "hub" / "models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4" / "snapshots" / ORCA_REV
MODEL_IN_CONTAINER = "/hf/hub/models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4/snapshots/" + ORCA_REV
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
PLAN_ID = re.compile(r"[0-9a-f]{64}\Z")
RUN_TIMEOUT = 30 * 60

def command(argv: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, capture_output=True,
                          check=False, timeout=timeout)

def docker_json(name: str, *, image: bool = False) -> dict:
    argv = ["docker", "image", "inspect", name] if image else ["docker", "container", "inspect", name]
    p = command(argv)
    if p.returncode or len(p.stdout) > 262144:
        raise ValueError("DOCKER_INSPECT_FAILED")
    value = json.loads(p.stdout)
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
        raise ValueError("DOCKER_INSPECT_INVALID_JSON")
    return value[0]

def api(path: str, *, payload: dict | None = None, timeout: int = 8) -> dict:
    req = Request("http://127.0.0.1:8000" + path,
                  data=(json.dumps(payload).encode() if payload is not None else None),
                  headers=({"Content-Type": "application/json"} if payload is not None else {}),
                  method=("POST" if payload is not None else "GET"))
    with urlopen(req, timeout=timeout) as handle:
        if handle.status != 200:
            raise ValueError("API_STATUS_NOT_200")
        raw = handle.read(65537)
    if len(raw) > 65536 or not raw:
        raise ValueError("API_UNBOUNDED_RESPONSE")
    doc = json.loads(raw)
    if not isinstance(doc, dict):
        raise ValueError("API_JSON_NOT_OBJECT")
    return doc

def api_ids() -> list[str]:
    return [x["id"] for x in api("/v1/models")["data"]
            if isinstance(x, dict) and isinstance(x.get("id"), str)]

def _port_open() -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.7)
    try:
        return s.connect_ex(("127.0.0.1", 8000)) == 0
    finally:
        s.close()

def _trial_recipe() -> dict:
    """Single committed, strictly validated model/PLE/runtime recipe."""
    recipe = manifest_registry.load("orcarouter_recipe")
    trial = recipe["trial"]
    profile = recipe["profiles"][trial["profile"]]
    if (trial["runtime_strategy"] != "RECIPE_FIRST_EXISTING_VLLM032_IMAGE"
        or trial["require_image_build"] is not False
        or trial["allow_source_patch"] is not False
        or trial["image_source"] != "CURRENT_VERIFIED_27B_IMAGE_ID"
        or trial["profile"] != "mtp0"
        or profile["num_speculative_tokens"] != 0
        or profile["served_id"] != ALIAS
        or trial["p5_env"].get("VLLM_PLE_MMAP") != "1"
        or recipe["model"]["repo_id"] != ORCA_REPO
        or recipe["model"]["revision"] != ORCA_REV):
        raise ValueError("RECIPE_FIRST_MTP0_CONTRACT_CHANGED")
    return recipe


# No P5 image build or vLLM 0.32 source patches in the MTP0 trial.
# The existing, observed 27B Blazux image must already provide the BF16 PLE
# mmap hook. This bounded CPU-only probe checks for the capability without
# importing models or asking Docker for any GPU access.
_SOURCE_IMAGE_ABI_PROBE = r'''
import ast, importlib.metadata, json, pathlib
base=pathlib.Path("/usr/local/lib/python3.12/dist-packages")
ple=base/"vllm_ple_mmap.py"
ngram=base/"vllm/models/qwen4_exp/nvidia/ngram_embedding.py"
exists=ple.is_file() and ngram.is_file()
p=ple.read_text(encoding="utf-8") if exists else ""
n=ngram.read_text(encoding="utf-8") if exists else ""
syntax=False
if exists:
    ast.parse(p)
    ast.parse(n)
    syntax=True
report={
  "vllm_version":importlib.metadata.version("vllm"),
  "ple_mmap_hook": "_ple_mmap_apply(Qwen4ExpNGramEmbedding)" in n,
  "bf16_ple_table": '"BF16": torch.bfloat16' in p,
  "ple_custom_op": "ple_mmap_lookup_ids" in p,
  "source_syntax_valid": syntax,
}
print(json.dumps(report, sort_keys=True))
'''


def _inspect_existing_image(image_id: str) -> dict:
    """CPU-only inspection of immutable installed image; no Docker build/tag."""
    if not DIGEST.fullmatch(image_id):
        raise ValueError("RUNTIME_IMAGE_ID_INVALID")
    img = docker_json(image_id, image=True)
    labels = (img.get("Config") or {}).get("Labels") or {}
    if (img.get("Id") != image_id
        or img.get("Architecture") not in ("arm64", "aarch64")
        or img.get("Os") != "linux"
        or labels.get("qwen38.base") != "v0.32"):
        raise ValueError("EXISTING_BLAZUX_VLLM032_IMAGE_IDENTITY_UNVERIFIED")
    cmd = ["docker", "run", "--rm", "--network=none",
           "--entrypoint", "python3", image_id, "-c", _SOURCE_IMAGE_ABI_PROBE]
    proc = command(cmd, timeout=100)
    if proc.returncode or len(proc.stdout) > 4096:
        raise ValueError("EXISTING_IMAGE_CPU_ABI_PROBE_FAILED")
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("EXISTING_IMAGE_CPU_ABI_REPORT_INVALID") from exc
    if (not isinstance(report, dict)
        or report.get("vllm_version") != "0.32.0"
        or any(report.get(key) is not True for key in
               ("ple_mmap_hook", "bf16_ple_table", "ple_custom_op",
                "source_syntax_valid"))):
        raise ValueError("EXISTING_IMAGE_BF16_PLE_MMAP_UNAVAILABLE")
    return report


def _source_snapshot() -> bool:
    if SNAPSHOT.is_symlink() or not SNAPSHOT.is_dir():
        return False
    # The HF snapshot directory may contain symlinks to blobs *within* the cache.
    # The snapshot itself must remain inside the pinned cache root.
    return SNAPSHOT.resolve().is_relative_to(CACHE.resolve())

def _gpu_collisions() -> list[str]:
    p = command(["docker", "ps", "--format", "{{.Names}}"])
    if p.returncode:
        raise ValueError("DOCKER_RUNNING_INVENTORY_UNAVAILABLE")
    running = p.stdout.splitlines()
    conflicts = []
    for name in running:
        if name == SOURCE:
            continue
        doc = docker_json(name)
        cfg = doc.get("HostConfig") or {}
        env = (doc.get("Config") or {}).get("Env") or []
        visible = next((x.partition("=")[2] for x in env if x.startswith("NVIDIA_VISIBLE_DEVICES=")), "")
        if cfg.get("DeviceRequests") or (cfg.get("Runtime") == "nvidia"
                                         and visible not in ("none", "void")):
            conflicts.append(name)
    return conflicts

def _unmanaged_gpu_pids() -> list[str]:
    """NVML compute-process inventory; fail closed if unsupported on this host."""
    p = command(["nvidia-smi", "--query-compute-apps=pid",
                 "--format=csv,noheader"], timeout=12)
    if p.returncode:
        raise ValueError("GPU_NVML_PROCESS_INVENTORY_UNAVAILABLE")
    rows = [line.strip() for line in p.stdout.splitlines()
            if line.strip() and line.strip() not in (
                "No running processes found", "N/A", "[N/A]")]
    if any(not row.isdecimal() for row in rows):
        raise ValueError("GPU_NVML_PROCESS_LIST_UNTRUSTED")
    return rows


def _metadata_gate() -> tuple[list[str], dict]:
    issues = []
    registry = manifest_registry.validate()
    if registry["status"] != "PASS":
        issues.append("MANIFEST_BUNDLE_INVALID")
    try:
        spec = asset_spec(ASSET_ID)
        if spec["source"] != {"kind": "PINNED_HF_SNAPSHOT",
                             "repo_id": ORCA_REPO, "revision": ORCA_REV}:
            issues.append("PLE_SOURCE_PIN_DRIFT")
        if spec["format"]["storage_dtype"] != "BF16" or spec["format"]["scale_mode"] != "NONE":
            issues.append("PLE_FORMAT_CHANGED")
        if policy()["api"]["host_port"] != 8000:
            issues.append("PORT_POLICY_DRIFT")
    except (OSError, ValueError, KeyError, TypeError):
        issues.append("PLE_MANIFEST_INVALID")
    ple = inspect_ple_asset(roots=[CACHE])
    if ple.get("status") != "PASS" or not ple.get("metadata_verified"):
        issues.append("PINNED_PLE_METADATA_UNVERIFIED")
    if not _source_snapshot():
        issues.append("PINNED_SNAPSHOT_NOT_FOUND")
    return issues, ple

def _git_head() -> str:
    r = command(["git", "-C", str(ROOT), "rev-parse", "HEAD"])
    if r.returncode or not re.fullmatch("[a-f0-9]{40}", r.stdout.strip()):
        raise ValueError("GIT_HEAD_UNVERIFIED")
    return r.stdout.strip()

def _source() -> dict:
    doc = docker_json(SOURCE)
    image = doc.get("Image")
    if (not isinstance(doc.get("Id"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", doc["Id"])
        or not isinstance(image, str) or not DIGEST.fullmatch(image)
        or not (doc.get("State") or {}).get("Running")
        or doc.get("Name") != "/" + SOURCE):
        raise ValueError("EXPECTED_27B_SOURCE_NOT_RUNNING")
    ports = ((doc.get("HostConfig") or {}).get("PortBindings") or {}).get("8000/tcp")
    if not isinstance(ports, list) or not any(x.get("HostPort") == "8000" for x in ports):
        raise ValueError("SOURCE_8000_PORT_UNVERIFIED")
    if api_ids() != ["qwen3.8-27b"]:
        raise ValueError("SOURCE_API_MODEL_ID_MISMATCH")
    return {"container_id": doc["Id"], "image_id": image}

def _target_absent() -> None:
    p = command(["docker", "container", "inspect", TARGET])
    if p.returncode == 0:
        raise ValueError("ORCAROUTER_TARGET_CONTAINER_NAME_ALREADY_EXISTS")
    if p.returncode not in (1,):
        raise ValueError("TARGET_NAME_INVENTORY_UNVERIFIED")

def prepare() -> dict:
    """Recipe-first, no build/tag/source patch; only a CPU-only image probe."""
    result = {"schema_version": 1, "stage": "p5", "action": "prepare",
              "status": "BLOCKED", "executed": False, "image_built": False,
              "source_patched": False, "gpu_verified": False, "issues": []}
    issues, ple = _metadata_gate()
    result["issues"] = issues
    if issues or not ple.get("metadata_verified"):
        return result
    try:
        recipe = _trial_recipe()
        source = _source()
        capabilities = _inspect_existing_image(source["image_id"])
        result.update(status="PASS", issues=[],
                      image_id=source["image_id"],
                      image_source="EXISTING_VERIFIED_27B_IMAGE",
                      recipe_id=recipe["recipe_id"],
                      profile=recipe["trial"]["profile"],
                      capabilities=capabilities)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError,
            subprocess.TimeoutExpired) as exc:
        result["issues"] = [str(exc)[:120]]
    return result


def _plan_data() -> dict:
    issues, ple = _metadata_gate()
    details = {"source": None, "runtime_image_id": None, "git_head": None,
               "pinned_revision": ORCA_REV, "cache": str(CACHE), "profile": "mtp0",
               "served_id": ALIAS, "port": 8000,
               "strategy": "RECIPE_FIRST_EXISTING_VLLM032_IMAGE"}
    capabilities = None
    try:
        details["git_head"] = _git_head()
        recipe = _trial_recipe()
        src = _source()
        details["source"] = src
        capabilities = _inspect_existing_image(src["image_id"])
        details["runtime_image_id"] = src["image_id"]
        details["recipe_id"] = recipe["recipe_id"]
        _target_absent()
        collisions = _gpu_collisions()
        if collisions:
            issues.append("OTHER_GPU_CONTAINERS_RUNNING")
        if not _port_open():
            issues.append("SOURCE_PORT_DISAPPEARED")
    except (OSError, RuntimeError, ValueError, KeyError, TypeError,
            subprocess.TimeoutExpired) as exc:
        issues.append(str(exc)[:120])
    issues = sorted(set(issues))
    expiry = (int(time.time()) // 900 + 1) * 900
    identity = {**details, "expires_at": expiry,
                "operation": "P5_MTP0_STOP_27B_START_ORCAROUTER_NO_ROLLBACK"}
    approval = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return {"schema_version": 1, "stage": "p5", "action": "gpu-trial-plan",
            "status": "READY_TO_APPROVE" if not issues else "BLOCKED",
            "issues": issues, "plan_id": approval if not issues else None,
            "expires_at_epoch_seconds": expiry,
            "operation": identity["operation"],
            "details": details, "image_capabilities": capabilities,
            "ple_metadata_verified": ple.get("metadata_verified") is True,
            "automatic_restore": False, "preserve_source_images_and_cache": True,
            "image_built": False, "source_patched": False,
            "executed": False, "gpu_verified": False, "production_released": False}


def _args(image: str) -> list[str]:
    """Docker argv rendered only from the strictly validated MTP0 recipe."""
    if not DIGEST.fullmatch(image):
        raise ValueError("TARGET_IMAGE_DIGEST_INVALID")
    recipe = _trial_recipe()
    trial = recipe["trial"]
    profile = recipe["profiles"]["mtp0"]
    model = recipe["model"]
    runtime = recipe["runtime"]
    if (runtime["host_port"] != 8000
        or runtime["container_name"] != TARGET
        or model["repo_id"] != ORCA_REPO
        or model["revision"] != ORCA_REV
        or model["expected_ple"]["dtype"] != "BF16"
        or runtime["dtype"] != "bfloat16"
        or runtime["load_format"] != "safetensors"
        or model["quantization"] != "compressed-tensors"):
        raise ValueError("P5_RUNTIME_RECIPE_CHANGED")
    args = [
        "docker", "run", "-d", "--name", runtime["container_name"],
        "--restart", "no", "--gpus", "all", "--ipc=host", "--shm-size", "16g",
        "--label", "blazux.p5.trial=mtp0-no-rollback",
        "-p", f"{runtime['host_port']}:8000",
        "-v", str(CACHE) + ":/hf:ro",
    ]
    env = trial["p5_env"]
    for name, value in env.items():
        if (not isinstance(name, str) or not re.fullmatch(r"[A-Z0-9_]+", name)
            or not isinstance(value, str) or len(value) > 64):
            raise ValueError("P5_RUNTIME_ENV_INVALID")
        args.extend(("-e", name + "=" + value))
    snapshot = "/hf/hub/models--" + ORCA_REPO.replace("/", "--") + "/snapshots/" + ORCA_REV
    args.extend([
        image, snapshot,
        "--served-model-name", profile["served_id"],
        "--host", "0.0.0.0", "--port", "8000",
        "--load-format", runtime["load_format"],
        "--dtype", runtime["dtype"],
        "--max-model-len", str(profile["max_model_len_candidate"]),
        "--max-num-seqs", str(profile["max_num_seqs_candidate"]),
        "--gpu-memory-utilization",
        str(profile["gpu_memory_utilization_candidate"]),
        "--kv-cache-dtype", profile["kv_cache_dtype"],
        "--no-enable-prefix-caching",
        "--enable-chunked-prefill",
    ])
    if profile["enforce_eager"]:
        args.append("--enforce-eager")
    if profile["enable_native_tools"]:
        args.extend(["--enable-auto-tool-choice",
                     "--tool-call-parser", profile["tool_call_parser"],
                     "--reasoning-parser", profile["reasoning_parser"]])
    if profile["num_speculative_tokens"] != 0:
        raise ValueError("MTP0_CANNOT_ENABLE_SPECULATIVE_DECODING")
    return args


def _private_state() -> None:
    if STATE.is_symlink():
        raise ValueError("P5_STATE_DIR_SYMLINK")
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    if STATE.stat().st_mode & 0o077:
        raise ValueError("P5_STATE_PERMISSIONS_UNSAFE")

def _save(report: dict) -> str:
    _private_state()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    p = STATE / ("trial-" + stamp + ".json")
    data = (json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    return str(p)

def execute(approval: str | None, ack: str | None, *,
            readiness_seconds: int = RUN_TIMEOUT) -> dict:
    report = {"schema_version": 1, "stage": "p5", "action": "gpu-trial-execute",
              "status": "BLOCKED", "executed": False, "gpu_verified": False,
              "automatic_restore": False, "source_stopped": False,
              "target_started": False, "production_released": False,
              "issues": [], "api_model_id": ALIAS}
    if ack != ACK or not isinstance(approval, str) or not PLAN_ID.fullmatch(approval):
        report["issues"] = ["EXACT_PLAN_AND_NO_ROLLBACK_ACK_REQUIRED"]
        return report
    try:
        _private_state()
        with (STATE / "p5-trial.lock").open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            plan = _plan_data()
            report["plan_id"] = plan["plan_id"]
            if plan["status"] != "READY_TO_APPROVE" or approval != plan["plan_id"]:
                report["issues"] = ["PLAN_CHANGED_OR_EXPIRED", *plan["issues"]]
                return report
            # Render and validate the exact recipe-derived launch argv BEFORE
            # stopping 27B: a broken recipe must not cause avoidable downtime.
            launch_argv = _args(plan["details"]["runtime_image_id"])
            report["source"] = plan["details"]["source"]
            report["target_image_id"] = plan["details"]["runtime_image_id"]
            # Existing 27B remains as a stopped container and exact image.
            stopped = command(["docker", "stop", "--time", "45", SOURCE], timeout=75)
            if stopped.returncode:
                report["status"] = "FAIL_NO_ROLLBACK"
                report["issues"] = ["SOURCE_STOP_FAILED"]
                report["docker_stderr_tail"] = stopped.stderr[-1000:]
                report["executed"] = True
                return report
            report["source_stopped"] = True
            report["executed"] = True
            for _ in range(50):
                if not _port_open():
                    break
                time.sleep(1)
            if _port_open():
                report["status"] = "FAIL_NO_ROLLBACK"
                report["issues"] = ["PORT_8000_STILL_OCCUPIED"]
                return report
            # Docker-external GPU processes also block; no second model may
            # be started while the old CUDA runtime has not fully exited.
            for _ in range(30):
                if not _unmanaged_gpu_pids():
                    break
                time.sleep(1)
            if _unmanaged_gpu_pids():
                report["status"] = "FAIL_NO_ROLLBACK"
                report["issues"] = ["GPU_COMPUTE_PROCESS_STILL_RUNNING"]
                return report
            conflicts = _gpu_collisions()
            if conflicts:
                report["status"] = "FAIL_NO_ROLLBACK"
                report["issues"] = ["OTHER_GPU_CONTAINER_APPEARED"]
                return report
            proc = command(launch_argv, timeout=120)
            if proc.returncode:
                report["status"] = "FAIL_NO_ROLLBACK"
                report["issues"] = ["ORCAROUTER_DOCKER_RUN_FAILED"]
                report["docker_stderr_tail"] = proc.stderr[-2000:]
                return report
            report["target_started"] = True
            report["target_container_id"] = proc.stdout.strip()
            deadline = time.monotonic() + max(10, min(readiness_seconds, RUN_TIMEOUT))
            while time.monotonic() < deadline:
                running = docker_json(TARGET).get("State", {})
                if running.get("Running") is not True:
                    report["status"] = "FAIL_NO_ROLLBACK"
                    report["issues"] = ["ORCAROUTER_CONTAINER_EXITED"]
                    break
                try:
                    if api_ids() == [ALIAS]:
                        test = api("/v1/chat/completions", payload={
                            "model": ALIAS, "messages": [
                                {"role": "user", "content": "Reply with the word READY."}],
                            "temperature": 0, "max_tokens": 64, "stream": False,
                        }, timeout=90)
                        choices = test.get("choices")
                        if isinstance(choices, list) and choices:
                            report["status"] = "PASS_GPU_TRIAL"
                            report["gpu_verified"] = True
                            report["issues"] = []
                        else:
                            report["status"] = "FAIL_NO_ROLLBACK"
                            report["issues"] = ["CHAT_COMPLETION_EMPTY"]
                        break
                except (OSError, ValueError, KeyError, RuntimeError):
                    pass
                time.sleep(5)
            if report["status"] == "BLOCKED":
                report["status"] = "FAIL_NO_ROLLBACK"
                report["issues"] = ["API_MODEL_OR_CHAT_READINESS_TIMEOUT"]
            return report
    except (OSError, ValueError, KeyError, RuntimeError,
            BlockingIOError, subprocess.TimeoutExpired) as exc:
        report["status"] = "FAIL_NO_ROLLBACK" if report["executed"] else "BLOCKED"
        report["issues"] = ["P5_TRIAL_EXCEPTION:" + type(exc).__name__]
        return report
    finally:
        if report["executed"]:
            try:
                report["receipt"] = _save(report)
            except (OSError, ValueError):
                report["issues"].append("P5_TRIAL_RECEIPT_WRITE_FAILED")

def status() -> dict:
    value = {"schema_version": 1, "stage": "p5", "action": "gpu-trial-status",
             "status": "NOT_OBSERVED", "automatic_restore": False,
             "executed": False, "gpu_verified": False, "issues": []}
    try:
        target = docker_json(TARGET)
        value.update(status=("RUNNING" if target["State"]["Running"] else "STOPPED"),
                     target_image_id=target.get("Image"),
                     container_id=target.get("Id"),
                     container_status=target.get("State", {}).get("Status"))
        try:
            value["observed_model_ids"] = api_ids()
            value["api_identity_observed"] = value["observed_model_ids"] == [ALIAS]
            value["gpu_verified"] = False  # API identity alone is not GPU qualification
        except (OSError, RuntimeError, ValueError, KeyError):
            value["observed_model_ids"] = None
    except (OSError, RuntimeError, ValueError, KeyError):
        value["issues"] = ["TARGET_CONTAINER_NOT_OBSERVED"]
    return value

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "plan", "execute", "status"))
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "execute":
        result = execute(args.approve_plan, args.ack_downtime)
    elif args.approve_plan or args.ack_downtime:
        result = {"status": "BLOCKED", "issues": ["APPROVAL_FLAGS_ONLY_FOR_EXECUTE"]}
    elif args.action == "prepare":
        result = prepare()
    elif args.action == "plan":
        result = _plan_data()
    else:
        result = status()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True,
                     indent=2 if args.json else None))
    return 0 if result.get("status") in ("PASS", "READY_TO_APPROVE", "PASS_GPU_TRIAL", "RUNNING") else 3

if __name__ == "__main__":
    raise SystemExit(main())
