"""Source-only GPU-trial regressions. Does not run Docker or GPU."""
import unittest
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from scripts.manager import p2_27b_gpu_trial as t

IMAGE="sha256:"+"a"*64
CID="b"*64

def preview():
    return {
        "issues":list(t.IGNORABLE), "source_revision":t.REVISION,
        "source_checkpoint_status":"SOURCE_FILES_PRESENT_PINNED_CANDIDATE",
        "source_quantization":{"algorithms":{"FP8":208,"NVFP4":193}},
        "local_image_id":IMAGE, "profile":{"quantization":"modelopt_mixed"},
        "observed_source":{"container":"qwen38-flash","model":"flash-next",
            "api_identity_confirmed":True,"container_image_id":IMAGE},
        "command_preview":["docker","run"],
    }

def original(running=True):
    return {
        "Id":CID, "Image":IMAGE, "State":{"Running":running},
        "HostConfig":{"AutoRemove":False,
            "RestartPolicy":{"Name":"unless-stopped"},
            "PortBindings":{"8000/tcp":[{"HostPort":"8000"}]}}
    }

def completed(stdout="",code=0):
    return SimpleNamespace(stdout=stdout,returncode=code)

class GPUTrialCPU(unittest.TestCase):
    def plan(self, val=None, doc=None, ps="qwen38-flash\n"):
        return t.make_plan(preview_func=lambda: preview() if val is None else val,
            inspect=lambda name: original() if doc is None else doc,
            run=lambda argv: completed(ps),now=1700000000)

    def test_ready_requires_an_exact_approval(self):
        p=self.plan()
        self.assertEqual(p["status"],"READY_TO_REQUEST_TRIAL_APPROVAL")
        self.assertEqual(len(p["plan_id"]),64)
        self.assertFalse(p["executed"])

    def test_unexpected_issues_block(self):
        p=preview()
        p["issues"]+=["AN_UNEXPECTED_PROBLEM"]
        self.assertIn("AN_UNEXPECTED_PROBLEM",self.plan(val=p)["issues"])
        self.assertIsNone(self.plan(val=p)["plan_id"])

    def test_wrong_original_image_blocks(self):
        o=original()
        o["Image"]="sha256:"+"c"*64
        self.assertIn("ORIGINAL_IMAGE_DIFFERENT",self.plan(doc=o)["issues"])

    def test_target_name_collision_blocks(self):
        self.assertIn("TARGET_CONTAINER_NAME_OCCUPIED",
            self.plan(ps="qwen38-flash\nqwen38-27b\n")["issues"])

    def test_plan_id_binds_current_container_identity(self):
        p1=self.plan()
        o=original()
        o["Id"]="c"*64
        p2=self.plan(doc=o)
        self.assertNotEqual(p1["plan_id"],p2["plan_id"])

    def test_bad_approval_never_calls_docker(self):
        rc,r=t.execute(None,None,run=lambda *args,**kw:self.fail("docker called"))
        self.assertEqual(rc,3)
        self.assertFalse(r["executed"])

    def test_stale_approval_never_calls_docker(self):
        with TemporaryDirectory() as d:
            rc,r=t.execute("a"*64,t.ACK,
                planner=lambda:{"status":"BLOCKED","plan_id":None,"issues":["STALE"]},
                run=lambda *a,**k:self.fail("docker called"),state_dir=d)
        self.assertEqual(rc,3)
        self.assertFalse(r["executed"])

    def test_launch_command_is_dedicated_modelopt_no_mtp(self):
        a=t.trial_command(IMAGE,"d"*64)
        self.assertIn("modelopt_mixed",a)
        self.assertIn(t.REVISION," ".join(a))
        self.assertNotIn("VLLM_PLE_MMAP"," ".join(a))
        self.assertNotIn("--speculative-config",a)
        self.assertIn(t.LABEL+"="+"d"*64,a)
        self.assertEqual(a[a.index("--restart")+1],"no")

    def test_foreign_target_protects_original(self):
        def inspect(name):
            return {"Name":"/qwen38-27b","Config":{"Labels":{}},
                    "Image":IMAGE,"State":{"Running":True}}
        calls=[]
        def run(args,**kwargs):
            calls.append(args)
            return completed()
        r=t.recover(CID,IMAGE,"d"*64,run=run,inspect=inspect)
        self.assertEqual(r["status"],"RECOVERY_FAILED")
        self.assertEqual(calls,[])

    def test_no_existing_target_restores_same_original_container(self):
        calls=[]
        def run(args,**kwargs):
            calls.append(args)
            if args[0:2]==["docker","inspect"]:
                return completed("false\n")
            return completed()
        def inspect(name):
            if name==t.TARGET_CONTAINER:
                raise RuntimeError("absent")
            return original(running=False)
        r=t.recover(CID,IMAGE,"d"*64,run=run,inspect=inspect,
                    waiter=lambda *args,**kw:True)
        self.assertEqual(r["status"],"RESTORED")
        self.assertIn(["docker","start","qwen38-flash"],calls)
        self.assertNotIn(["docker","rm","qwen38-flash"],calls)

    def test_checkpoint_is_qwen38_not_qwen35(self):
        self.assertEqual(t.SERVED,"qwen3.8-27b")
        self.assertEqual(t.REVISION,"482ca0f3832238542f8f5295dde86b5f22711d80")

if __name__=="__main__":
    unittest.main()
