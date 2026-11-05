"""Exact-approved one-shot Qwen3.8-27B GPU trial and Flash-Next restore.

WARNING: interrupts live :8000 and may fail to recover after power loss,
SIGKILL, Docker outage or host OOM. Never runs on plan; does not merge or switch.
"""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from urllib.request import Request, urlopen

from scripts.manager.p2_27b_launch_preview import (
    build_27b_launch_preview, _candidate_argv, _cache_path,
    IMAGE_RE, ORIGINAL_CONTAINER, ORIGINAL_ID, TARGET_CONTAINER, SERVED, REVISION,
)

LABEL = "blazux.27b-trial-plan"
ACK = "I_ACCEPT_FLASH_NEXT_DOWNTIME"
IGNORABLE = frozenset({
    "27B_GPU_KERNEL_AND_LOADER_NOT_VERIFIED",
    "27B_MEMORY_CONTEXT_PROFILE_NOT_VERIFIED",
    "P2_RUNTIME_EXECUTOR_NOT_ENABLED",
    "REGISTRY_IMAGE_DIGEST_NOT_OBSERVED",
    "SERVICE_TRANSITION_REQUIRES_SEPARATE_APPROVAL",
    "VERIFIED_IMAGE_RECIPE_AND_ROLLBACK_ABSENT",
})


def call(args, timeout=35):
    return subprocess.run(args, capture_output=True, text=True, check=False, timeout=timeout)


def docker_info(name, run=call):
    p = run(["docker", "inspect", "--format", "{{json .}}", name])
    if p.returncode or len(p.stdout) > 262144:
        raise RuntimeError("DOCKER_INSPECT_FAILED")
    obj = json.loads(p.stdout)
    if not isinstance(obj, dict):
        raise ValueError("INVALID_DOCKER_JSON")
    return obj


def original_issues(d, image):
    host = d.get("HostConfig") or {}
    ports = (host.get("PortBindings") or {}).get("8000/tcp")
    out = []
    if not (d.get("State") or {}).get("Running"):
        out.append("ORIGINAL_NOT_RUNNING")
    if not re.fullmatch(r"[0-9a-f]{64}", str(d.get("Id") or "")):
        out.append("ORIGINAL_ID_INVALID")
    if d.get("Image") != image:
        out.append("ORIGINAL_IMAGE_DIFFERENT")
    if host.get("AutoRemove") is not False:
        out.append("ORIGINAL_AUTOREMOVE_UNVERIFIED")
    if (host.get("RestartPolicy") or {}).get("Name") not in ("no", "unless-stopped"):
        out.append("ORIGINAL_RESTART_POLICY_UNSUPPORTED")
    if not isinstance(ports, list) or len(ports) != 1 or ports[0].get("HostPort") != "8000":
        out.append("ORIGINAL_PORT_MAPPING_UNVERIFIED")
    return out


def make_plan(preview_func=build_27b_launch_preview, inspect=docker_info,
              run=call, now=None):
    try:
        v = preview_func()
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
        v = {"issues": ["PREVIEW_UNAVAILABLE"]}
    issues = [str(x) for x in v.get("issues", []) if x not in IGNORABLE]
    source = v.get("observed_source") or {}
    image = v.get("local_image_id")
    if not isinstance(image, str) or not IMAGE_RE.fullmatch(image) or source.get("container_image_id") != image:
        issues.append("IMAGE_ID_NOT_STABLE")
    if source.get("api_identity_confirmed") is not True or source.get("model") != "flash-next" or source.get("container") != ORIGINAL_CONTAINER:
        issues.append("SOURCE_API_IDENTITY_UNVERIFIED")
    if v.get("source_revision") != REVISION or v.get("source_checkpoint_status") != "SOURCE_FILES_PRESENT_PINNED_CANDIDATE":
        issues.append("PINNED_CHECKPOINT_UNVERIFIED")
    if (v.get("source_quantization") or {}).get("algorithms") != {"FP8": 208, "NVFP4": 193}:
        issues.append("PINNED_MODEL_OPT_CHANGED")
    if not v.get("command_preview"):
        issues.append("CANDIDATE_PREVIEW_MISSING")
    source_id = None
    if not issues:
        try:
            doc = inspect(ORIGINAL_CONTAINER)
            source_id = doc.get("Id")
            issues.extend(original_issues(doc, image))
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
            issues.append("SOURCE_CONTAINER_INSPECT_FAILED")
    try:
        p = run(["docker", "ps", "-a", "--format", "{{.Names}}"])
        if p.returncode:
            issues.append("DOCKER_NAME_INVENTORY_FAILED")
        elif TARGET_CONTAINER in p.stdout.splitlines():
            issues.append("TARGET_CONTAINER_NAME_OCCUPIED")
    except (OSError, subprocess.TimeoutExpired):
        issues.append("DOCKER_NAME_INVENTORY_UNAVAILABLE")
    # Enforce one GPU-enabled Docker model at a time. OpenWebUI/proxy containers
    # without GPU requests are allowed. Unknown runtime/DeviceRequests block.
    try:
        p = run(["docker", "ps", "--format", "{{.Names}}"])
        if p.returncode:
            issues.append("RUNNING_CONTAINER_INVENTORY_FAILED")
        else:
            running_names = p.stdout.splitlines()
            if ORIGINAL_CONTAINER not in running_names:
                issues.append("ORIGINAL_NOT_IN_RUNNING_CONTAINERS")
            for other in running_names:
                if other == ORIGINAL_CONTAINER:
                    continue
                other_doc = inspect(other)
                hc = other_doc.get("HostConfig") or {}
                cfg = other_doc.get("Config") or {}
                env = cfg.get("Env") or []
                nvidia_env = next((v.split("=", 1)[1] for v in env
                                   if isinstance(v, str) and v.startswith("NVIDIA_VISIBLE_DEVICES=")), "")
                if hc.get("DeviceRequests") or (hc.get("Runtime") == "nvidia"
                    and nvidia_env not in ("none", "void")):
                    issues.append("OTHER_GPU_CONTAINER_RUNNING")
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
        issues.append("OTHER_RUNNING_GPU_INVENTORY_UNVERIFIED")
    window = int(time.time() if now is None else now) // 600
    facts = {
        "operation": "one-shot-27b-gpu-trial", "source_container_id": source_id,
        "source_image": source.get("container_image_id"), "source_api": ORIGINAL_ID,
        "target_image": image, "target_api": SERVED, "revision": REVISION,
        "profile": v.get("profile"), "window": window, "port": 8000,
    }
    pid = hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest() if not issues else None
    return {
        "status": "BLOCKED" if issues else "READY_TO_REQUEST_TRIAL_APPROVAL",
        "action": "Qwen3.8-27B-experimental-GPU-trial",
        "issues": sorted(set(issues)), "plan_id": pid,
        "expires_at_epoch_seconds": (window + 1) * 600,
        "source_container_id": source_id, "image_id": image,
        "required_downtime_acknowledgement": ACK,
        "executed": False, "gpu_verified": False,
        "restoration": "stop/remove only trial-owned 27B; docker start original qwen38-flash; check /health and /v1/models",
        "notice": ("EXPERIMENTAL. Will stop original Flash-Next API :8000. "
                   "Even auto-rollback can fail on host/Docker/power failure. "
                   "Run execute only after reviewing downtime and exact plan."),
    }


def running(name, run=call):
    p = run(["docker", "inspect", "--format", "{{.State.Running}}", name])
    if p.returncode or p.stdout.strip().lower() not in ("true", "false"):
        raise RuntimeError("RUNNING_STATE_UNAVAILABLE")
    return p.stdout.strip().lower() == "true"


def port_free(run=call):
    p = run(["ss", "-H", "-ltn"], timeout=10)
    if p.returncode:
        return False
    return not any(len(x := line.split()) >= 4 and x[3].rsplit(":", 1)[-1] == "8000"
                   for line in p.stdout.splitlines())


def api_ready(model):
    try:
        for path in ("/health", "/v1/models"):
            with urlopen(Request("http://127.0.0.1:8000" + path, method="GET"), timeout=3) as response:
                if response.status != 200:
                    return False
                if path.endswith("models"):
                    b = response.read(65537)
                    if len(b) > 65536:
                        return False
                    obj = json.loads(b)
                    if not any(x.get("id") == model for x in obj.get("data", [])
                               if isinstance(x, dict)):
                        return False
        return True
    except (OSError, RuntimeError, ValueError, TimeoutError):
        return False


def wait_for(name, model, seconds, *, run=call, api=api_ready, sleep=time.sleep, clock=time.monotonic):
    deadline = clock() + seconds
    while clock() < deadline:
        if not running(name, run):
            return False
        if api(model):
            return True
        sleep(5)
    return False


def one_inference():
    request = Request("http://127.0.0.1:8000/v1/chat/completions",
        data=json.dumps({"model": SERVED,
            "messages": [{"role": "user", "content": "Reply with the word ready."}],
            "temperature": 0, "max_tokens": 24}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=90) as response:
            body = response.read(65537)
            if response.status != 200 or len(body) > 65536:
                return False
            doc = json.loads(body)
            choices = doc.get("choices") if isinstance(doc, dict) else None
            usage = doc.get("usage") if isinstance(doc, dict) else None
            generated = (usage.get("completion_tokens", 0)
                         if isinstance(usage, dict) else 0)
            if not isinstance(choices, list) or not choices:
                return False
            return bool((isinstance(generated, int) and generated > 0)
                        or any(isinstance(c, dict) and isinstance(c.get("message"), dict)
                               and any(isinstance(c["message"].get(k), str)
                                       and c["message"][k] for k in
                                       ("content", "reasoning_content"))
                               for c in choices))
    except (OSError, RuntimeError, ValueError, TimeoutError):
        return False


def trial_command(image, plan):
    cmd = _candidate_argv(_cache_path(None), image)
    cmd[cmd.index(image):cmd.index(image)] = ["--pull", "never", "--restart", "no",
                                            "--label", LABEL + "=" + plan]
    return cmd


def recover(source_id, image, plan, *, run=call, inspect=docker_info,
            waiter=wait_for):
    issues = []
    # An inspect error is NOT proof that the target is absent. Obtain a fresh
    # full Docker name list; a Docker daemon failure forbids dual-GPU restart.
    try:
        names = run(["docker", "ps", "-a", "--format", "{{.Names}}"])
        if names.returncode:
            return {"status": "RECOVERY_FAILED", "issues": ["TARGET_NAME_INVENTORY_FAILED"]}
        if TARGET_CONTAINER in names.stdout.splitlines():
            target = inspect(TARGET_CONTAINER)
        else:
            target = None
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
        return {"status": "RECOVERY_FAILED", "issues": ["TARGET_STATE_UNVERIFIED"]}
    if target is not None:
        labels = (target.get("Config") or {}).get("Labels") or {}
        if labels.get(LABEL) != plan or target.get("Name") != "/" + TARGET_CONTAINER or target.get("Image") != image:
            return {"status": "RECOVERY_FAILED", "issues": ["FOREIGN_TARGET_CANNOT_TOUCH"]}
        if (target.get("State") or {}).get("Running") and run(
                ["docker", "stop", "--time", "30", TARGET_CONTAINER], timeout=55).returncode:
            issues.append("TARGET_STOP_FAILED")
        try:
            target_still_running = running(TARGET_CONTAINER, run)
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            return {"status": "RECOVERY_FAILED", "issues": ["TARGET_RUNNING_STATE_UNVERIFIED"]}
        if target_still_running:
            issues.append("TARGET_STILL_RUNNING")
        elif run(["docker", "rm", TARGET_CONTAINER]).returncode:
            issues.append("TARGET_REMOVAL_FAILED")
    if issues:
        return {"status": "RECOVERY_FAILED", "issues": issues}
    try:
        original = inspect(ORIGINAL_CONTAINER)
        if original.get("Id") != source_id or original.get("Image") != image:
            issues.append("ORIGINAL_ID_CHANGED_DURING_TRIAL")
        elif not (original.get("State") or {}).get("Running"):
            if run(["docker", "start", ORIGINAL_CONTAINER], timeout=90).returncode:
                issues.append("ORIGINAL_RESTART_FAILED")
        if not issues and not waiter(ORIGINAL_CONTAINER, ORIGINAL_ID, 240, run=run):
            issues.append("ORIGINAL_API_RESTORE_NOT_VERIFIED")
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
        issues.append("ORIGINAL_RESTORE_UNAVAILABLE")
    return {"status": "RESTORED" if not issues else "RECOVERY_FAILED", "issues": issues}


def execute(plan, acknowledge, *, planner=make_plan, run=call,
            inspect=docker_info, waiter=wait_for, inference=one_inference,
            recoverer=recover, state_dir=None):
    if not isinstance(plan, str) or not re.fullmatch(r"[0-9a-f]{64}", plan) or acknowledge != ACK:
        return 3, {"status": "BLOCKED", "executed": False,
                   "issues": ["PLAN_AND_DOWNTIME_ACK_REQUIRED"]}
    state = Path(state_dir or Path.home() / ".local/state/blazux-wizard/p2")
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / "27b-gpu-trial.lock").open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 3, {"status": "BLOCKED", "executed": False,
                       "issues": ["TRIAL_LOCK_HELD"]}
        fresh = planner()
        if fresh["status"] != "READY_TO_REQUEST_TRIAL_APPROVAL" or fresh["plan_id"] != plan:
            return 3, {"status": "BLOCKED", "executed": False,
                       "issues": ["APPROVAL_STALE_OR_PREFLIGHT_CHANGED"] + fresh.get("issues", [])}
        source_id, image = fresh["source_container_id"], fresh["image_id"]
        journal = state / (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + plan[:12] + ".json")
        fd = os.open(journal, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        audit = {"model": "nvidia/Qwen3.8-27B-NVFP4", "plan_id": plan, "trial": "NOT_RUN"}
        stop_attempted = False
        try:
            orig = inspect(ORIGINAL_CONTAINER)
            if orig.get("Id") != source_id or original_issues(orig, image):
                raise RuntimeError("ORIGINAL_CHANGED_AT_EXECUTION")
            stop_attempted = True
            if run(["docker", "stop", "--time", "45", ORIGINAL_CONTAINER], timeout=80).returncode:
                raise RuntimeError("ORIGINAL_STOP_FAILED")
            if running(ORIGINAL_CONTAINER, run):
                raise RuntimeError("ORIGINAL_STILL_RUNNING")
            for _ in range(20):
                if port_free(run):
                    break
                time.sleep(1)
            else:
                raise RuntimeError("PORT_8000_NOT_RELEASED")
            if run(trial_command(image, plan), timeout=90).returncode:
                raise RuntimeError("TARGET_START_COMMAND_FAILED")
            if not waiter(TARGET_CONTAINER, SERVED, 600, run=run):
                raise RuntimeError("TARGET_API_NOT_READY")
            audit["target_api_ready"] = True
            audit["inference_ok"] = bool(inference())
            audit["trial"] = "PASS" if audit["inference_ok"] else "INFERENCE_FAILED"
        except (KeyboardInterrupt, SystemExit):
            audit["trial"] = "INTERRUPTED"
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
            audit["trial"] = "FAILED"
            audit["error_type"] = type(exc).__name__
            audit["error_code"] = str(exc) if isinstance(exc, RuntimeError) else "EXECUTION_ERROR"
        finally:
            # Preserve bounded target startup evidence LOCALLY before retiring the
            # trial container; never upload production/model logs to GitHub.
            # This is best effort and MUST NOT prevent service restoration.
            if stop_attempted:
                try:
                    logs = run(["docker", "logs", "--tail", "120",
                                TARGET_CONTAINER], timeout=20)
                    if logs.returncode == 0:
                        logfile = journal.with_suffix(".target.log")
                        fd = os.open(logfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                        with os.fdopen(fd, "w", encoding="utf-8") as stream:
                            stream.write((logs.stdout + logs.stderr)[-65536:])
                        audit["target_log"] = str(logfile)
                except (OSError, ValueError, subprocess.TimeoutExpired):
                    audit["target_log_capture"] = "UNAVAILABLE"
                try:
                    restoration = recoverer(source_id, image, plan, run=run, inspect=inspect, waiter=waiter)
                except Exception as exc:
                    restoration = {"status": "RECOVERY_FAILED",
                                   "issues": ["RECOVERY_EXCEPTION:" + type(exc).__name__]}
            else:
                restoration = {"status": "NOT_NEEDED", "issues": []}
            audit["restoration"] = restoration
            audit["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            try:
                journal.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
            except OSError:
                audit["evidence_write_failed"] = True
        status = ("PASS_RESTORED" if audit["trial"] == "PASS" and restoration["status"] == "RESTORED"
                  else "RECOVERY_FAILED" if restoration["status"] == "RECOVERY_FAILED"
                  else "FAIL_RESTORED" if restoration["status"] == "RESTORED" else "BLOCKED")
        return (0 if status == "PASS_RESTORED" else 4), {
            "status": status, "trial": audit["trial"],
            "target_api_ready": audit.get("target_api_ready", False),
            "inference_ok": audit.get("inference_ok", False),
            "restoration": restoration, "evidence": str(journal),
            "target_log": audit.get("target_log"),
            "executed": stop_attempted,
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Explicit one-shot 27B GPU trial")
    parser.add_argument("mode", nargs="?", choices=("plan", "execute"), default="plan")
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    options = parser.parse_args(argv)
    if options.mode == "plan":
        if options.approve_plan or options.ack_downtime:
            parser.error("plan cannot accept approval")
        result = make_plan()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] != "BLOCKED" else 3
    # A normal SIGTERM (e.g. shell disconnect) raises KeyboardInterrupt in
    # the trial so the finally block can attempt restoration. SIGKILL/power
    # loss cannot be handled and require manual operator recovery.
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    rc, result = execute(options.approve_plan, options.ack_downtime)
    print(json.dumps(result, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main())
