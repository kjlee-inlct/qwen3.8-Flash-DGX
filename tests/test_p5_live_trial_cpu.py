"""Bounded CPU/Fake-DGX tests for P5's recipe-scoped upstream #62318 adapter."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p5_live_trial as live
from wizard.main import main as wizard

SOURCE_IMAGE = "sha256:" + "9"*64
ADAPTER_IMAGE = "sha256:" + "a"*64
CID = "c"*64
READY = "b"*64


def completed(argv, rc=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(argv, rc, stdout, stderr)


def source(running=False):
    return {"container_id": CID, "image_id": SOURCE_IMAGE,
            "state": "RUNNING_27B" if running else "IDLE_27B_STOPPED_AFTER_P5",
            "running": running}


def image_doc():
    return {"Id": ADAPTER_IMAGE, "Os": "linux", "Architecture": "arm64",
            "Config": {"Labels": {
                "qwen38.base": "v0.32",
                "blazux.p5.state": "SOURCE_CANDIDATE_NOT_QUALIFIED",
                "blazux.p5.vllm": "0.32.0",
                "blazux.p5.adapter": live.ADAPTER,
                "blazux.p5.base_image": SOURCE_IMAGE,
                "blazux.p5.production_release": "false",
            }}}


def compat():
    return {"vllm_version": "0.32.0", "source_syntax_valid": True,
            "qkv_mapping_exact": True, "upstream_62318_guard": True}


def plan(running=False):
    return {"status": "READY_TO_APPROVE", "plan_id": READY, "issues": [],
            "details": {"source": source(running),
                        "runtime_image_id": ADAPTER_IMAGE}}


class P5QSA62318Trial(unittest.TestCase):
    def test_recipe_version_pin_and_target_isolation(self):
        self.assertEqual(live.TARGET, "qwen38-orcarouter-qsa62318")
        self.assertEqual(live.FAILED_PREVIOUS_TARGET, "qwen38-orcarouter")
        self.assertEqual(live.IMAGE_TAG, "blazux-p5-orcarouter:qsa62318-v032")
        self.assertEqual(live.ALIAS, "qwen3.8-flash-next-orca-uncensored-bf16")
        self.assertEqual(live.ACK, "I_ACCEPT_P5_NO_ROLLBACK")
        self.assertEqual(live.ADAPTER, "qwen4exp-qsa-62318-v032-v1")

    def test_recipe_binds_exact_upstream_fix_not_global_patch(self):
        recipe = live._trial_recipe()
        t = recipe["trial"]
        a = recipe["compatibility_adapter"]
        self.assertEqual(recipe["vllm_version"], "0.32.0")
        self.assertEqual(t["adapter"], a["id"])
        self.assertEqual(t["container_name"], live.TARGET)
        self.assertTrue(t["allow_idle_source_after_failed_p5"])
        self.assertTrue(a["apply_only_in_derived_image"])
        self.assertTrue(a["preserve_original_27b_image"])
        self.assertEqual(a["upstream_pr"],
                         "https://github.com/vllm-project/vllm/pull/62318")
        self.assertEqual(recipe["model"]["expected_ple"]["dtype"], "BF16")
        self.assertFalse(recipe["launch_allowed"])

    def test_argv_from_recipe_uses_derived_digest_no_source_env(self):
        cmd = live._args(ADAPTER_IMAGE)
        self.assertEqual(cmd[:3], ["docker", "run", "-d"])
        self.assertEqual(cmd[cmd.index("--name")+1], live.TARGET)
        self.assertEqual(cmd[cmd.index("-p")+1], "8000:8000")
        self.assertEqual(cmd[cmd.index("--max-model-len")+1], "8192")
        self.assertEqual(cmd[cmd.index("--max-num-seqs")+1], "1")
        self.assertEqual(cmd[cmd.index("--gpu-memory-utilization")+1], "0.7")
        self.assertIn("HF_HUB_OFFLINE=1", cmd)
        self.assertIn("VLLM_PLE_MMAP=1", cmd)
        self.assertIn("--enable-auto-tool-choice", cmd)
        self.assertIn("qwen3_coder", cmd)
        self.assertIn("--enforce-eager", cmd)
        self.assertIn("--dtype", cmd)
        self.assertIn("bfloat16", cmd)
        self.assertIn(live.ALIAS, cmd)
        self.assertNotIn("VLLM_P5_ORCAROUTER=1", cmd)
        self.assertNotIn("--speculative-config", cmd)
        self.assertEqual(cmd[cmd.index("-v")+1], str(live.CACHE)+":/hf:ro")
        at = cmd.index(ADAPTER_IMAGE)
        self.assertEqual(cmd[at+1],
           "/hf/hub/models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4/snapshots/"
           + live.ORCA_REV)

    def test_invalid_image_digest_fails_before_any_docker(self):
        with self.assertRaises(ValueError):
            live._args("some-image:latest")

    def test_existing_27b_stopped_is_source_without_api(self):
        instance = {"Id": CID, "Name": "/qwen38-27b", "Image": SOURCE_IMAGE,
                    "State": {"Running": False, "Status": "exited", "ExitCode": 0},
                    "HostConfig": {"PortBindings": {
                        "8000/tcp": [{"HostIp":"0.0.0.0","HostPort":"8000"}]}}}
        with patch.object(live, "docker_json", return_value=instance), \
             patch.object(live, "_port_open", return_value=False), \
             patch.object(live, "api_ids",
                          side_effect=AssertionError("must not query stopped API")):
            result=live._source()
        self.assertFalse(result["running"])
        self.assertEqual(result["state"], "IDLE_27B_STOPPED_AFTER_P5")

    def test_running_27b_requires_exact_live_api(self):
        instance = {"Id": CID, "Name": "/qwen38-27b", "Image": SOURCE_IMAGE,
                    "State": {"Running": True, "Status": "running"},
                    "HostConfig": {"PortBindings": {
                        "8000/tcp": [{"HostPort":"8000"}]}}}
        with patch.object(live, "docker_json", return_value=instance), \
             patch.object(live, "_port_open", return_value=True), \
             patch.object(live, "api_ids", return_value=["qwen3.8-27b"]):
            self.assertTrue(live._source()["running"])

    def test_stopped_source_port_occupied_blocks(self):
        instance = {"Id": CID, "Name": "/qwen38-27b", "Image": SOURCE_IMAGE,
                    "State": {"Running": False, "Status": "exited", "ExitCode": 0},
                    "HostConfig": {"PortBindings": {"8000/tcp":[{"HostPort":"8000"}]}}}
        with patch.object(live, "docker_json", return_value=instance), \
             patch.object(live, "_port_open", return_value=True):
            with self.assertRaisesRegex(ValueError, "IDLE_SOURCE_PORT_8000_OCCUPIED"):
                live._source()

    def test_source_stopped_with_nonzero_exit_fails_closed(self):
        instance = {"Id": CID, "Name": "/qwen38-27b", "Image": SOURCE_IMAGE,
                    "State": {"Running": False, "Status": "exited", "ExitCode": 1},
                    "HostConfig": {"PortBindings":{"8000/tcp":[{"HostPort":"8000"}]}}}
        with patch.object(live, "docker_json", return_value=instance):
            with self.assertRaisesRegex(ValueError,"P5_27B_SOURCE_STATE_UNVERIFIED"):
                live._source()

    def test_candidate_image_label_is_exact_and_version_bound(self):
        image=image_doc()
        self.assertTrue(live._scoped_image_labels(image,SOURCE_IMAGE))
        image["Config"]["Labels"]["blazux.p5.base_image"]="sha256:"+"b"*64
        self.assertFalse(live._scoped_image_labels(image,SOURCE_IMAGE))
        image["Config"]["Labels"]["blazux.p5.base_image"]=SOURCE_IMAGE
        image["Config"]["Labels"]["blazux.p5.adapter"]="other"
        self.assertFalse(live._scoped_image_labels(image,SOURCE_IMAGE))

    def test_candidate_probe_does_not_use_gpu_or_network(self):
        observed=[]
        def run(argv,timeout=30):
            observed.append(argv)
            return completed(argv,stdout=json.dumps(compat()))
        with patch.object(live,"docker_json",return_value=image_doc()), \
             patch.object(live,"command",side_effect=run):
            result=live._scoped_image(SOURCE_IMAGE)
        self.assertEqual(result["image_id"],ADAPTER_IMAGE)
        self.assertEqual(observed[0][:6],
          ["docker","run","--rm","--network=none","--entrypoint","python3"])
        self.assertEqual(observed[0][6],ADAPTER_IMAGE)
        self.assertNotIn("--gpus",observed[0])
        self.assertNotIn("tag",observed[0])

    def test_candidate_probe_fails_when_fix_is_missing(self):
        failing={**compat(),"upstream_62318_guard":False}
        with patch.object(live,"docker_json",return_value=image_doc()), \
             patch.object(live,"command",return_value=completed(
                 [],stdout=json.dumps(failing))):
            with self.assertRaisesRegex(ValueError,"P5_QSA62318_UPSTREAM_FIX_NOT_CONFIRMED"):
                live._scoped_image(SOURCE_IMAGE)

    def test_local_base_alias_identity_collision_refused(self):
        with patch.object(live,"command",return_value=completed(
                [],stdout="sha256:"+"b"*64)) as run:
            with self.assertRaisesRegex(ValueError,"P5_BASE_ALIAS_COLLISION"):
                live._verified_local_base_alias(SOURCE_IMAGE)
        run.assert_called_once()

    def test_local_base_alias_tag_only_missing_alias(self):
        calls=[]
        def run(argv,timeout=30):
            calls.append(argv)
            if argv[:3]==["docker","image","inspect"]:
                return completed(argv,rc=1,stderr="No such image")
            if argv[:2]==["docker","tag"]:
                return completed(argv)
            raise AssertionError(argv)
        with patch.object(live,"command",side_effect=run), \
             patch.object(live,"docker_json",return_value={"Id":SOURCE_IMAGE}):
            alias=live._verified_local_base_alias(SOURCE_IMAGE)
        self.assertEqual(calls[1],["docker","tag",SOURCE_IMAGE,alias])
        self.assertFalse(any(x[:2] in (["docker","rm"],["docker","rmi"],
                                          ["docker","stop"]) for x in calls))

    def test_prepare_scoped_image_build_offline_and_not_source(self):
        state={"done":False}
        calls=[]
        def get_img(name,image=False):
            if name==live.IMAGE_TAG and not state["done"]:
                raise ValueError("DOCKER_INSPECT_FAILED")
            return image_doc()
        def run(argv,timeout=30):
            calls.append(argv)
            if argv[:3]==["docker","image","inspect"]:
                return completed(argv,rc=1,stderr="No such image")
            if argv[:2]==["docker","build"]:
                state["done"]=True
                self.assertIn("--pull=false",argv)
                self.assertIn("--network=none",argv)
                self.assertIn("Dockerfile.p5.qsa62318",argv)
                self.assertIn("P5_BASE_IMAGE_ID="+SOURCE_IMAGE,argv)
                return completed(argv)
            raise AssertionError(argv)
        with patch.object(live,"_scoped_image",side_effect=ValueError("missing")), \
             patch.object(live,"command",side_effect=run), \
             patch.object(live,"_verified_local_base_alias",
                          return_value=live._local_base_alias(SOURCE_IMAGE)):
            # Deliberately fails closed on unreadable post-build image.
            with self.assertRaises(ValueError):
                live._prepare_scoped_image(SOURCE_IMAGE)
        self.assertEqual(len([x for x in calls if x[:2]==["docker","build"]]),1)

    def test_prepare_already_built_candidate_no_mutation(self):
        candidate={"image_id":ADAPTER_IMAGE,"base_image_id":SOURCE_IMAGE,
                   "adapter":live.ADAPTER,"capabilities":compat()}
        with patch.object(live,"_scoped_image",return_value=candidate), \
             patch.object(live,"command",
                          side_effect=AssertionError("no Docker changes")):
            result=live._prepare_scoped_image(SOURCE_IMAGE)
        self.assertFalse(result["image_built"])
        self.assertEqual(result["image_id"],ADAPTER_IMAGE)

    def test_prepare_reports_scoped_patch_only_in_derived_image(self):
        candidate={"image_id":ADAPTER_IMAGE,"base_image_id":SOURCE_IMAGE,
                   "adapter":live.ADAPTER,"capabilities":compat(),
                   "image_built":True}
        with patch.object(live,"_metadata_gate",
                          return_value=([],{"metadata_verified":True})), \
             patch.object(live,"_source",return_value=source()), \
             patch.object(live,"_inspect_existing_image",
                          return_value={"vllm_version":"0.32.0"}), \
             patch.object(live,"_prepare_scoped_image",return_value=candidate):
            result=live.prepare()
        self.assertEqual(result["status"],"PASS")
        self.assertTrue(result["image_built"])
        self.assertFalse(result["original_engine_patched"])
        self.assertFalse(result["gpu_verified"])
        self.assertEqual(result["base_image_id"],SOURCE_IMAGE)

    def test_plan_works_without_restarting_27b_after_failed_trial(self):
        candidate={"image_id":ADAPTER_IMAGE,"base_image_id":SOURCE_IMAGE,
                   "adapter":live.ADAPTER,"capabilities":compat()}
        with patch.object(live,"_metadata_gate",
                          return_value=([],{"metadata_verified":True})), \
             patch.object(live,"_source",return_value=source()), \
             patch.object(live,"_inspect_existing_image",
                          return_value={"vllm_version":"0.32.0"}), \
             patch.object(live,"_scoped_image",return_value=candidate), \
             patch.object(live,"_target_absent",return_value=None), \
             patch.object(live,"_gpu_collisions",return_value=[]), \
             patch.object(live,"_port_open",return_value=False), \
             patch.object(live,"_unmanaged_gpu_pids",return_value=[]), \
             patch.object(live,"_git_head",return_value="a"*40):
            doc=live._plan_data()
        self.assertEqual(doc["status"],"READY_TO_APPROVE")
        self.assertEqual(doc["details"]["runtime_image_id"],ADAPTER_IMAGE)
        self.assertFalse(doc["details"]["source"]["running"])
        self.assertEqual(doc["details"]["adapter"],live.ADAPTER)
        self.assertFalse(doc["original_engine_patched"])
        self.assertTrue(doc["adapter_backport_in_derived_image"])

    def test_plan_blocks_when_adapter_image_missing(self):
        with patch.object(live,"_metadata_gate",
                          return_value=([],{"metadata_verified":True})), \
             patch.object(live,"_source",return_value=source()), \
             patch.object(live,"_inspect_existing_image",
                          return_value={"vllm_version":"0.32.0"}), \
             patch.object(live,"_scoped_image",
                          side_effect=ValueError("DOCKER_INSPECT_FAILED")), \
             patch.object(live,"_git_head",return_value="a"*40):
            doc=live._plan_data()
        self.assertEqual(doc["status"],"BLOCKED")
        self.assertIsNone(doc["plan_id"])

    def test_plan_blocks_if_idle_gpu_in_use(self):
        candidate={"image_id":ADAPTER_IMAGE,"base_image_id":SOURCE_IMAGE,
                   "adapter":live.ADAPTER,"capabilities":compat()}
        with patch.object(live,"_metadata_gate",
                          return_value=([],{"metadata_verified":True})), \
             patch.object(live,"_source",return_value=source()), \
             patch.object(live,"_inspect_existing_image",
                          return_value={"vllm_version":"0.32.0"}), \
             patch.object(live,"_scoped_image",return_value=candidate), \
             patch.object(live,"_target_absent",return_value=None), \
             patch.object(live,"_gpu_collisions",return_value=[]), \
             patch.object(live,"_port_open",return_value=False), \
             patch.object(live,"_unmanaged_gpu_pids",return_value=["1234"]), \
             patch.object(live,"_git_head",return_value="a"*40):
            self.assertIn("IDLE_SOURCE_GPU_PROCESS_OCCUPIED",live._plan_data()["issues"])

    def test_execute_rejects_wrong_ack_without_docker(self):
        with patch.object(live,"command",side_effect=AssertionError("no Docker")):
            report=live.execute(READY,"invalid")
        self.assertEqual(report["status"],"BLOCKED")
        self.assertFalse(report["executed"])

    def test_execute_stopped_27b_launches_new_target_and_no_restore(self):
        calls=[]
        def runner(argv,timeout=30):
            calls.append(argv)
            if argv[:2]==["docker","run"]:
                self.assertEqual(argv[argv.index("--name")+1],live.TARGET)
                return completed(argv,rc=1,stderr="simulated failure")
            raise AssertionError(argv)
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live,"STATE",Path(temp)), \
                 patch.object(live,"_private_state",return_value=None), \
                 patch.object(live,"_save",return_value="/tmp/receipt.json"), \
                 patch.object(live,"_plan_data",return_value=plan()), \
                 patch.object(live,"_args",return_value=live._args(ADAPTER_IMAGE)), \
                 patch.object(live,"_port_open",return_value=False), \
                 patch.object(live,"_unmanaged_gpu_pids",return_value=[]), \
                 patch.object(live,"_gpu_collisions",return_value=[]), \
                 patch.object(live,"docker_json",return_value={
                     "State":{"Running":False},"Image":SOURCE_IMAGE}), \
                 patch.object(live,"command",side_effect=runner):
                result=live.execute(READY,live.ACK)
        self.assertEqual(result["status"],"FAIL_NO_ROLLBACK")
        self.assertTrue(result["source_already_stopped"])
        self.assertTrue(result["source_stopped"])
        self.assertTrue(result["executed"])
        self.assertTrue(result["original_engine_patched"] is False)
        self.assertEqual(result["target_image_id"],ADAPTER_IMAGE)
        self.assertFalse(any(x[:2]==["docker","stop"] for x in calls))
        self.assertFalse(any(x[:2]==["docker","start"] for x in calls))
        self.assertFalse(any(x[:2]==["docker","rm"] for x in calls))

    def test_execute_running_27b_stop_before_target(self):
        calls=[]
        def runner(argv,timeout=30):
            calls.append(argv)
            if argv[:2]==["docker","stop"]:
                return completed(argv,stdout="qwen38-27b\n")
            if argv[:2]==["docker","run"]:
                return completed(argv,rc=1,stderr="simulated failure")
            raise AssertionError(argv)
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live,"STATE",Path(temp)), \
                 patch.object(live,"_private_state",return_value=None), \
                 patch.object(live,"_save",return_value="/tmp/receipt.json"), \
                 patch.object(live,"_plan_data",return_value=plan(True)), \
                 patch.object(live,"_port_open",return_value=False), \
                 patch.object(live,"_unmanaged_gpu_pids",return_value=[]), \
                 patch.object(live,"_gpu_collisions",return_value=[]), \
                 patch.object(live,"command",side_effect=runner):
                result=live.execute(READY,live.ACK)
        self.assertEqual(result["status"],"FAIL_NO_ROLLBACK")
        self.assertFalse(result["source_already_stopped"])
        self.assertEqual([x[1] for x in calls],["stop","run"])

    def test_recipe_invalid_before_stop_or_target(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live,"STATE",Path(temp)), \
                 patch.object(live,"_private_state",return_value=None), \
                 patch.object(live,"_plan_data",return_value=plan(True)), \
                 patch.object(live,"_args",
                              side_effect=ValueError("P5_RUNTIME_RECIPE_CHANGED")), \
                 patch.object(live,"command",
                              side_effect=AssertionError("not allowed")):
                result=live.execute(READY,live.ACK)
        self.assertEqual(result["status"],"BLOCKED")
        self.assertFalse(result["source_stopped"])

    def test_changed_plan_aborts_without_source_stop(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live,"STATE",Path(temp)), \
                 patch.object(live,"_private_state",return_value=None), \
                 patch.object(live,"_plan_data",return_value=plan(True)), \
                 patch.object(live,"command",
                              side_effect=AssertionError("not allowed")):
                result=live.execute("c"*64,live.ACK)
        self.assertEqual(result["status"],"BLOCKED")
        self.assertFalse(result["source_stopped"])

    def test_trial_router_status_plan_no_hidden_execute(self):
        val={"status":"READY_TO_APPROVE","executed":False,"plan_id":READY}
        with patch.object(live,"_plan_data",return_value=val), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc=wizard(["p5","trial","plan","--json"])
        self.assertEqual(rc,0)
        self.assertEqual(json.loads(out.getvalue())["status"],"READY_TO_APPROVE")

    def test_wizard_dry_run_refuses_build(self):
        with patch.object(live,"prepare",side_effect=AssertionError("no build")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc=wizard(["p5","trial","prepare","--dry-run","--json"])
        self.assertEqual(rc,3)
        self.assertEqual(json.loads(out.getvalue())["status"],"BLOCKED")


if __name__=="__main__":
    unittest.main()
