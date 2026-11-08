"""P5 one-shot *development* DGX GPU trial: MTP0 only; NO automatic rollback.

prepare: build an isolated vLLM 0.32 image while preserving live 27B.
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
IMAGE_TAG = "blazux-p5-orcarouter:vllm032-mtp0"
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

def _candidate_label(img: dict) -> bool:
    labels = (img.get("Config") or {}).get("Labels") or {}
    return (img.get("Architecture") in ("arm64", "aarch64")
            and img.get("Os") == "linux"
            and labels.get("blazux.p5.vllm") == "0.32.0"
            and labels.get("blazux.p5.state") == "SOURCE_CANDIDATE_NOT_QUALIFIED")


def _local_base_ref(image_id: str) -> str:
    """Deterministic local *tag*, not an invalid FROM sha256:<image-id> ref."""
    if not isinstance(image_id, str) or not DIGEST.fullmatch(image_id):
        raise ValueError("SOURCE_IMAGE_ID_INVALID")
    return "blazux-p5-source:v032-" + image_id.removeprefix("sha256:")


def _ensure_local_base_tag(image_id: str) -> str:
    """Alias the exact installed image for BuildKit; never pull/overwrite.

    BuildKit's FROM cannot treat a standalone Docker image ID as a repository
    name; it can resolve an existing local tag. The image ID stays the strict
    provenance label and is verified immediately before and after tagging.
    """
    alias = _local_base_ref(image_id)
    inspected = command(["docker", "image", "inspect", "--format", "{{.Id}}", alias])
    if inspected.returncode == 0:
        if inspected.stdout.strip() != image_id:
            raise ValueError("LOCAL_BASE_IMAGE_ALIAS_COLLISION")
    elif inspected.returncode == 1:
        # Only an explicitly missing local alias may be created.
        # A failed Docker daemon or malformed inventory must not be overwritten.
        tagged = command(["docker", "tag", image_id, alias])
        if tagged.returncode != 0:
            raise ValueError("LOCAL_BASE_IMAGE_TAG_FAILED")
    else:
        raise ValueError("LOCAL_BASE_IMAGE_ALIAS_INSPECT_FAILED")
    if docker_json(alias, image=True).get("Id") != image_id:
        raise ValueError("LOCAL_BASE_IMAGE_ALIAS_IDENTITY_MISMATCH")
    return alias


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

def _plan_data() -> dict:
    issues, ple = _metadata_gate()
    details = {"source": None, "candidate_image_id": None, "git_head": None,
               "pinned_revision": ORCA_REV, "cache": str(CACHE), "profile": "mtp0",
               "served_id": ALIAS, "port": 8000}
    try:
        details["git_head"] = _git_head()
        src = _source()
        details["source"] = src
        target = docker_json(IMAGE_TAG, image=True)
        if not _candidate_label(target):
            issues.append("P5_ISOLATED_IMAGE_NOT_QUALIFIED_FOR_TRIAL")
        target_labels = (target.get("Config") or {}).get("Labels") or {}
        if target_labels.get("blazux.p5.base_image") != src["image_id"]:
            issues.append("P5_CANDIDATE_BASE_IMAGE_SOURCE_DRIFT")
        if not DIGEST.fullmatch(str(target.get("Id"))):
            issues.append("P5_IMAGE_DIGEST_UNVERIFIED")
        else:
            details["candidate_image_id"] = target["Id"]
        _target_absent()
        collisions = _gpu_collisions()
        if collisions:
            issues.append("OTHER_GPU_CONTAINERS_RUNNING")
        if not _port_open():
            issues.append("SOURCE_PORT_DISAPPEARED")
    except (OSError, RuntimeError, ValueError, KeyError, TypeError,
            subprocess.TimeoutExpired) as exc:
        issues.append(str(exc)[:100])
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
            "details": details,
            "ple_metadata_verified": ple.get("metadata_verified") is True,
            "automatic_restore": False, "preserve_source_images_and_cache": True,
            "executed": False, "gpu_verified": False, "production_released": False}

def prepare() -> dict:
    issues, ple = _metadata_gate()
    if issues:
        return {"status": "BLOCKED", "issues": issues, "executed": False}
    if not ple["metadata_verified"]:
        return {"status": "BLOCKED", "issues": ["PLE_AUDIT_UNVERIFIED"], "executed": False}
    source = _source()
    base = docker_json(source["image_id"], image=True)
    if base.get("Architecture") not in ("arm64", "aarch64"):
        return {"status": "BLOCKED", "issues": ["BASE_IMAGE_NOT_ARM64"], "executed": False}
    try:
        existing = docker_json(IMAGE_TAG, image=True)
        existing_labels = (existing.get("Config") or {}).get("Labels") or {}
        if (_candidate_label(existing)
            and existing_labels.get("blazux.p5.base_image") == source["image_id"]):
            return {"status": "PASS", "action": "prepare", "image_id": existing["Id"],
                    "already_prepared": True, "executed": False,
                    "gpu_verified": False}
        return {"status": "BLOCKED", "issues": ["CANDIDATE_IMAGE_TAG_ALREADY_OCCUPIED"],
                "executed": False}
    except ValueError:
        pass
    try:
        local_base = _ensure_local_base_tag(source["image_id"])
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        return {"status": "BLOCKED", "action": "prepare",
                "issues": [str(exc)[:100]], "executed": False,
                "gpu_verified": False}
    args = ["docker", "build", "--pull=false", "--network=none",
            "-f", "Dockerfile.p5.candidate",
            "--build-arg", "P5_QUALIFIED_BASE_IMAGE=" + local_base,
            "--build-arg", "P5_QUALIFIED_BASE_IMAGE_ID=" + source["image_id"],
            "-t", IMAGE_TAG, str(ROOT)]
    built = command(args, timeout=45 * 60)
    if built.returncode:
        return {"status": "BLOCKED", "action": "prepare",
                "issues": ["P5_CANDIDATE_IMAGE_BUILD_FAILED"],
                "build_log_tail": (built.stdout + built.stderr)[-6000:],
                "executed": True, "gpu_verified": False}
    img = docker_json(IMAGE_TAG, image=True)
    image_labels = (img.get("Config") or {}).get("Labels") or {}
    if (not _candidate_label(img)
        or not DIGEST.fullmatch(str(img.get("Id", "")))
        or image_labels.get("blazux.p5.base_image") != source["image_id"]):
        return {"status": "BLOCKED", "issues": ["BUILT_IMAGE_IDENTITY_INVALID"],
                "executed": True, "gpu_verified": False}
    return {"status": "PASS", "action": "prepare", "image_id": img["Id"],
            "source_image_id": source["image_id"],
            "executed": True, "gpu_verified": False,
            "notice": "Only candidate image built; 27B is still serving."}

def _args(image: str) -> list[str]:
    if not DIGEST.fullmatch(image):
        raise ValueError("TARGET_IMAGE_DIGEST_INVALID")
    return [
        "docker", "run", "-d", "--name", TARGET,
        "--restart", "no", "--gpus", "all", "--ipc=host", "--shm-size", "16g",
        "--label", "blazux.p5.trial=mtp0-no-rollback",
        "-p", "8000:8000",
        "-v", str(CACHE) + ":/hf:ro",
        "-e", "HF_HOME=/hf",
        "-e", "HF_HUB_OFFLINE=1",
        "-e", "VLLM_P5_ORCAROUTER=1",
        "-e", "VLLM_PLE_MMAP=1",
        "-e", "VLLM_PLE_MMAP_WORKERS=16",
        "-e", "VLLM_PLE_MMAP_PREWARM=0",
        image, MODEL_IN_CONTAINER,
        "--served-model-name", ALIAS,
        "--host", "0.0.0.0", "--port", "8000",
        "--load-format", "safetensors",
        "--max-model-len", "8192", "--max-num-seqs", "1",
        "--gpu-memory-utilization", "0.70",
        "--dtype", "bfloat16",
        "--kv-cache-dtype", "bfloat16",
        "--no-enable-prefix-caching",
        "--enable-chunked-prefill",
        "--enforce-eager",
        "--enable-auto-tool-choice",
        "--tool-call-parser", "qwen3_coder",
        "--reasoning-parser", "qwen3",
    ]

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
            report["source"] = plan["details"]["source"]
            report["target_image_id"] = plan["details"]["candidate_image_id"]
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
            proc = command(_args(plan["details"]["candidate_image_id"]), timeout=120)
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
