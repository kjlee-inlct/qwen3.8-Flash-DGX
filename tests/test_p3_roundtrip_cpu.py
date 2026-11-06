"""Pure-CPU P3 two-cycle acceptance checks. No Docker, HTTP or GPU."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

from scripts.manager import p3_27b_roundtrip as p3
from scripts.manager import p2_27b_gpu_trial as trial
from wizard import main as wizard


def base():
    return {"status":"READY_TO_REQUEST_TRIAL_APPROVAL","plan_id":"1"*64,
            "source_container_id":"2"*64, "image_id":"sha256:"+"3"*64,
            "issues":[], "executed":False}


def receipt():
    return {"path": "/private/benchmark.json", "sha256":"4"*64}, None


class P3RoundtripCPU(unittest.TestCase):
    def test_no_p2_benchmark_receipt_blocks_entire_p3_plan(self):
        doc = p3.make_plan(base_planner=base,
                           receipt_reader=lambda:(None,"P2_BENCHMARK_RECEIPT_NOT_FOUND"))
        self.assertEqual(doc["status"],"BLOCKED")
        self.assertIsNone(doc["plan_id"])
        self.assertIn("P2_BENCHMARK_RECEIPT_NOT_FOUND",doc["issues"])

    def test_p3_id_binds_p2_result_and_is_not_old_trial_approval(self):
        one = p3.make_plan(base_planner=base,receipt_reader=receipt)
        self.assertEqual(one["status"],"READY_TO_REQUEST_TRIAL_APPROVAL")
        self.assertNotEqual(one["plan_id"],"1"*64)
        self.assertEqual(one["cycles"],2)
        other = p3.make_plan(base_planner=base,
                             receipt_reader=lambda:({"sha256":"5"*64,"path":"/private/b"},None))
        self.assertNotEqual(one["plan_id"],other["plan_id"])

    def test_private_receipt_read_and_fail_closed_on_bad_or_newer_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            good = {
                "status":"BENCH_PASS_RESTORED_VERIFIED",
                "benchmark":{"status":"PASS",
                             "benchmark_version":"p2-27b-api-benchmark-v1"},
                "restoration":{"status":"RESTORED","issues":[]},
                "post_restore_wizard_status":{
                    "status":"LIVE_SERVICE_VERIFIED",
                    "observed_model":"flash-next",
                    "expected_served_id":trial.ORIGINAL_ID, "issues":[]},
            }
            path = root/"20261106T100000Z-111111111111.benchmark.json"
            path.write_text(json.dumps(good))
            found, error=p3.latest_p2_benchmark(root)
            self.assertIsNone(error)
            self.assertEqual(found["path"],str(path))
            newer=root/"20261106T110000Z-111111111111.benchmark.json"
            newer.write_text(json.dumps({**good,"status":"BENCH_PARTIAL_RESTORED"}))
            found,error=p3.latest_p2_benchmark(root)
            self.assertIsNone(found)
            self.assertEqual(error,"P2_BENCHMARK_NOT_QUALIFIED")

    def test_untrusted_symlinked_receipt_is_not_opened(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            external=root/"external.txt"
            external.write_text("{}")
            link=root/"newest.benchmark.json"
            link.symlink_to(external)
            doc,issue=p3.latest_p2_benchmark(root)
            self.assertIsNone(doc)
            self.assertEqual(issue,"P2_BENCHMARK_RECEIPT_UNTRUSTED")

    def test_wrong_ack_or_stale_plan_never_calls_core(self):
        fail=lambda *a,**kw:self.fail("core must not run")
        rc,out=p3.execute("bad",trial.ACK,core=fail)
        self.assertEqual(rc,3)
        self.assertFalse(out["executed"])
        rc,out=p3.execute("a"*64,"WRONG_ACK",core=fail)
        self.assertEqual(rc,3)
        rc,out=p3.execute("a"*64,trial.ACK,
                          planner=lambda:{"status":"BLOCKED","issues":["STALE"]},
                          core=fail)
        self.assertEqual(rc,3)
        self.assertIn("P3_APPROVAL_STALE_OR_PREFLIGHT_CHANGED",out["issues"])

    def test_two_cycles_each_restore_same_original_before_next(self):
        with tempfile.TemporaryDirectory() as temp:
            planned=p3.make_plan(base_planner=base,receipt_reader=receipt)
            count=[]
            def core(approved, ack, **kwargs):
                self.assertEqual(approved,planned["plan_id"])
                self.assertEqual(ack,trial.ACK)
                self.assertEqual(kwargs["state_dir"],Path(temp))
                self.assertIs(kwargs["inference"],trial.one_inference)
                count.append(1)
                return 0,{"status":"PASS_RESTORED","target_api_ready":True,
                         "inference_ok":True, "executed":True,
                         "restoration":{"status":"RESTORED","issues":[]},
                         "evidence":"/private/roundtrip-"+str(len(count))+".json"}
            check=[]
            def verifier(original_id):
                self.assertEqual(original_id,"2"*64)
                check.append(1)
                return {"status":"PASS","source_container_id_preserved":True}
            rc,record=p3.execute(planned["plan_id"],trial.ACK,
                                 planner=lambda:planned,core=core,
                                 verifier=verifier,state_root=Path(temp))
            self.assertEqual(rc,0)
            self.assertEqual(len(count),2)
            self.assertEqual(len(check),2)
            self.assertEqual(record["completed_cycles"],2)
            self.assertEqual(record["status"],"P3_TEMPORARY_ROUNDTRIP_PASS")
            self.assertFalse(record["permanent_switch_qualified"])
            self.assertTrue(Path(record["evidence"]).is_file())

    def test_failed_first_restore_does_not_start_second_cycle(self):
        with tempfile.TemporaryDirectory() as temp:
            planned=p3.make_plan(base_planner=base,receipt_reader=receipt)
            count=[]
            def core(*args,**kwargs):
                count.append(1)
                return 4,{"status":"RECOVERY_FAILED","executed":True,
                          "restoration":{"status":"RECOVERY_FAILED",
                                         "issues":["ORIGINAL_RESTART_FAILED"]}}
            rc,record=p3.execute(planned["plan_id"],trial.ACK,
                                 planner=lambda:planned,core=core,
                                 verifier=lambda *a:self.fail("should not verify"),
                                 state_root=Path(temp))
            self.assertEqual(rc,4)
            self.assertEqual(len(count),1)
            self.assertEqual(record["completed_cycles"],1)
            self.assertEqual(record["status"],"P3_INCOMPLETE_OR_BLOCKED")

    def test_postrestore_unverified_blocks_second_cycle(self):
        with tempfile.TemporaryDirectory() as temp:
            planned=p3.make_plan(base_planner=base,receipt_reader=receipt)
            count=[]
            def core(*args,**kwargs):
                count.append(1)
                return 0,{"status":"PASS_RESTORED","executed":True,
                          "restoration":{"status":"RESTORED","issues":[]}}
            rc,record=p3.execute(planned["plan_id"],trial.ACK,
                                 planner=lambda:planned,core=core,
                                 verifier=lambda *args:{"status":"BLOCKED"},
                                 state_root=Path(temp))
            self.assertEqual(rc,4)
            self.assertEqual(len(count),1)

    def test_verify_source_id_and_api_identity_both_required(self):
        with patch("scripts.manager.p3_27b_roundtrip.inspect_live_status",
                   return_value={"status":"LIVE_SERVICE_VERIFIED",
                                 "observed_model":"flash-next",
                                 "expected_served_id":trial.ORIGINAL_ID,
                                 "host_port":8000,"issues":[]}), \
             patch("scripts.manager.p3_27b_roundtrip.trial.docker_info",
                   return_value={"Id":"a"*64,"State":{"Running":True}}):
            self.assertEqual(p3.verify_original_after_cycle("a"*64)["status"],"PASS")
            self.assertEqual(p3.verify_original_after_cycle("b"*64)["status"],"BLOCKED")

    def test_wizard_routes_explicit_p3_plan_but_not_unapproved_verify(self):
        with patch("scripts.manager.p3_27b_roundtrip.main",return_value=0) as f, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wizard.main(["switch","flash-next-27b",
                                          "roundtrip","--plan","--json"]),0)
            f.assert_called_once_with(["plan"])
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            rc=wizard.main(["switch","flash-next-27b","roundtrip","--plan",
                            "--approve-plan","b"*64,"--json"])
        self.assertEqual(rc,2)
        self.assertEqual(json.loads(stream.getvalue())["status"],"BLOCKED")
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            rc=wizard.main(["switch","flash-next-27b","roundtrip","--execute",
                            "--dry-run","--json"])
        self.assertEqual(rc,3)
        self.assertEqual(json.loads(stream.getvalue())["status"],"BLOCKED")


if __name__=="__main__":
    unittest.main()
