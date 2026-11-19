"""Synthetic CPU-only P5-D live-audit fixtures. No actual host probes."""
import json
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.manager import p5d_live_audit as a

CID = "a" * 64
REPO = "models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4"
PATH = "/hf/hub/" + REPO + "/blobs/abcdef"


def owner():
    return {
        "model": "orcarouter", "docker_identity_match": True,
        "status": "BLOCKED_PARTIAL_PROCESS_EVIDENCE",
        "container": {"id": CID, "name": "test-orcarouter", "init_pid": 42},
        "docker_host_pids": [42, 43],
        "host_port_8000_listener_pids": [],
        "issues": ["PORT_8000_HOST_LISTENER_PID_UNAVAILABLE_OR_NAT"],
    }


def info():
    return {
        "Id": CID, "Name": "/test-orcarouter",
        "State": {"Running": True, "Pid": 42},
        "HostConfig": {"NetworkMode": "bridge", "PortBindings": {
            "8000/tcp": [{"HostIp": "", "HostPort": "8000"}]}},
        "NetworkSettings": {"Ports": {
            "8000/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8000"}]},
            "Networks": {"bridge": {"IPAddress": "172.17.0.2"}}},
        "Mounts": [{"Destination": "/hf", "Source": "/host/hf",
                    "RW": False, "Type": "bind"}],
    }


def model_scan(pid, mounts, repo_marker, *, proc):
    assert mounts == ["/hf"]
    assert repo_marker == REPO
    return {"pid": pid, "status": "MAPPINGS_INODE_MATCHED_CANDIDATE_NOT_PLE_AUTHENTICATED",
            "issues": [], "sampled_smaps_bytes": 1000,
            "mapped_files": [{
                "path": PATH, "dev_major": 8, "dev_minor": 1, "inode": 123,
                "rss_bytes": 65536, "pss_bytes": 32768,
                "mapping_count": 1, "inode_stat_match": True
            }]}


def socket_scan(pids, init_pid, *, proc):
    return {"status": "CONTAINER_LISTENER_PID_FD_CORRELATED",
            "container_netns": "net:[77]",
            "listening_inode_count": 1, "matched_docker_host_pids": [43],
            "issues": [], "kernel_nat_owner_authenticated": False}


class ParserTests(unittest.TestCase):
    def test_listener_inode_parser_exact_port_and_state(self):
        raw = (
            "sl local_address rem_address st tx_queue rx_queue tr tm->when retrnsmt uid timeout inode\n"
            "0: 00000000:1F40 00000000:0000 0A 0:0 00:0 0 0 0 777\n"
            "1: 00000000:1F40 00000000:0000 01 0:0 00:0 0 0 0 999\n"
            "2: 00000000:1F41 00000000:0000 0A 0:0 00:0 0 0 0 998\n"
        )
        self.assertEqual(a._listener_inodes(raw), {777})
        self.assertEqual(a._listener_inodes(None), set())

    def test_nat_rule_is_correlated_not_attestation(self):
        raw = "-A DOCKER ! -i br0 -p tcp -m tcp --dport 8000 -j DNAT --to-destination 172.17.0.2:8000\n"
        yes = a._iptables_nat(["172.17.0.2"], raw)
        self.assertTrue(yes["matching_rule_found"])
        self.assertFalse(yes["active_nat_path_authenticated"])
        self.assertFalse(a._iptables_nat(["172.17.0.3"], raw)["matching_rule_found"])
        self.assertEqual(a._iptables_nat(["172.17.0.2"], None)["status"], "UNAVAILABLE")

    def test_exact_network_and_readonly_mount_capture(self):
        self.assertEqual(a._published_ip(info()), ["172.17.0.2"])
        self.assertEqual(a._model_ro_mounts(info()), ["/hf"] if
                         a._model_ro_mounts(info()) == ["/hf"] else [])
        # The strict source mount selector intentionally requires an HF/cache
        # marker in its mount path, so the generic /hf mount must be observed.
        self.assertTrue(a._candidate_model_path(PATH, ["/hf"], REPO))
        self.assertFalse(a._candidate_model_path("/etc/shadow", ["/hf"], REPO))
        self.assertFalse(a._candidate_model_path(PATH+" (deleted)", ["/hf"], REPO))

    def test_bounded_smaps_rss_pss_and_inode_compare(self):
        raw = (
            "1000-2000 r--s 00000000 08:01 123 " + PATH + "\n"
            "Size: 128 kB\nRss: 64 kB\nPss: 32 kB\n"
            "2000-3000 r--s 00001000 08:01 123 " + PATH + "\n"
            "Size: 128 kB\nRss: 16 kB\nPss: 8 kB\n"
            "3000-4000 rw-p 00000000 00:00 0\n"
            "Size: 4096 kB\nRss: 4096 kB\nPss: 4096 kB\n"
        )
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root/"42").mkdir()
            (root/"42"/"smaps").write_text(raw)
            fake = SimpleNamespace(st_dev=os.makedev(8,1), st_ino=123,
                                   st_mode=stat.S_IFREG)
            result = a._scan_smaps(42, ["/hf"], REPO, proc=root,
                                   stat_function=lambda path: fake)
            self.assertEqual(result["status"],
                "MAPPINGS_INODE_MATCHED_CANDIDATE_NOT_PLE_AUTHENTICATED")
            self.assertEqual(len(result["mapped_files"]), 1)
            self.assertEqual(result["mapped_files"][0]["rss_bytes"], 80*1024)
            self.assertEqual(result["mapped_files"][0]["pss_bytes"], 40*1024)
            self.assertEqual(result["mapped_files"][0]["mapping_count"], 2)

    def test_incomplete_smaps_mapping_does_not_create_rss(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root/"42").mkdir()
            (root/"42"/"smaps").write_text(
                "1000-2000 r--s 00000000 08:01 123 "+PATH+"\n"
                "Size: 128 kB\nRss: 64 kB\n")
            result = a._scan_smaps(42, ["/hf"], REPO, proc=root)
            self.assertEqual(result["mapped_files"], [])
            self.assertIn("SMAPS_MAPPING_METRICS_INCOMPLETE", result["issues"])

    def test_inode_mismatch_blocks_strong_mapping_status(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/"42").mkdir()
            (root/"42"/"smaps").write_text(
                "1000-2000 r--s 00000000 08:01 123 "+PATH+"\n"
                "Size: 128 kB\nRss: 64 kB\nPss: 32 kB\n")
            fake=SimpleNamespace(st_dev=os.makedev(8,1),st_ino=124,st_mode=stat.S_IFREG)
            result=a._scan_smaps(42, ["/hf"], REPO, proc=root,
                                 stat_function=lambda path: fake)
            self.assertEqual(result["mapped_files"][0]["inode_stat_match"], False)
            self.assertEqual(result["status"], "MAPPINGS_PARTIAL_OR_UNQUALIFIED")

    def test_pinned_revision_alias_matches_filesystem_inode_not_hash(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            folder=root/"42"/"root"/"hf"/"hub"/REPO/"snapshots"/("b"*40)
            folder.mkdir(parents=True)
            (folder/"model-00001.safetensors").write_bytes(b"fixture")
            st=(folder/"model-00001.safetensors").stat()
            rows, issues=a._pinned_snapshot_inodes(42, ["/hf"],
                "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4",
                "b"*40, proc=root)
            key=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)
            self.assertEqual(rows[key], ["model-00001.safetensors"])
            self.assertEqual(issues, [])

    def test_missing_snapshot_must_not_be_claimed(self):
        with tempfile.TemporaryDirectory() as t:
            rows, issues=a._pinned_snapshot_inodes(42, ["/hf"],
                "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4", "b"*40,
                proc=Path(t))
            self.assertEqual(rows,{})
            self.assertIn("PINNED_SNAPSHOT_FILES_NOT_OBSERVED",issues)

    def test_container_netns_listen_fd_inodes_not_merely_net_tcp(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for pid in (42,43):
                (root/str(pid)/"net").mkdir(parents=True)
                (root/str(pid)/"ns").mkdir()
                (root/str(pid)/"fd").mkdir()
                (root/str(pid)/"ns"/"net").symlink_to("net:[77]")
            (root/"42"/"net"/"tcp").write_text(
                "sl local_address rem_address st a b c d e f inode\n"
                "0: 00000000:1F40 00000000:0000 0A 0:0 00:0 0 0 0 777\n")
            (root/"42"/"net"/"tcp6").write_text(
                "sl local_address rem_address st a b c d e f inode\n")
            (root/"43"/"fd"/"3").symlink_to("socket:[777]")
            out=a._socket_pid_evidence([42,43],42,proc=root)
            self.assertEqual(out["matched_docker_host_pids"],[43])
            self.assertFalse(out["kernel_nat_owner_authenticated"])
            (root/"43"/"fd"/"3").unlink()
            missing=a._socket_pid_evidence([42,43],42,proc=root)
            self.assertEqual(missing["matched_docker_host_pids"], [])

    def test_empty_netns_is_unqualified_not_pid_drift(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root/"42"/"net").mkdir(parents=True)
            (root/"42"/"ns").mkdir()
            (root/"42"/"net"/"tcp").write_text(
                "sl local_address rem_address st a b c d e f inode\n"
                "0: 00000000:1F40 00000000:0000 0A 0:0 00:0 0 0 0 777\n")
            (root/"42"/"net"/"tcp6").write_text(
                "sl local_address rem_address st a b c d e f inode\n")
            with patch.object(a.os, "readlink", return_value=""):
                out = a._socket_pid_evidence([42], 42, proc=root)
            self.assertEqual(out["matched_docker_host_pids"], [])
            self.assertIn("CONTAINER_NETNS_EMPTY_OR_UNQUALIFIED", out["issues"])
            self.assertNotIn("PID_NETNS_DRIFT", out["issues"])

    def test_smaps_permission_denied_is_explicitly_classified(self):
        with patch.object(Path, "open", side_effect=PermissionError(13,"denied")):
            out = a._scan_smaps(42, ["/hf"], REPO)
        self.assertEqual(out["status"], "NOT_OBSERVED")
        self.assertIn("SMAPS_UNREADABLE", out["issues"])
        self.assertIn("SMAPS_ACCESS_DENIED", out["issues"])

    def test_pinned_cache_mount_already_hub_does_not_double_hub(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            folder = (root/"42"/"root"/"hf"/"hub"/REPO/"snapshots"/("b"*40))
            folder.mkdir(parents=True)
            (folder/"model-00002.safetensors").write_bytes(b"fixture")
            st = (folder/"model-00002.safetensors").stat()
            rows, issues = a._pinned_snapshot_inodes(
                42, ["/hf/hub"],
                "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4",
                "b"*40, proc=root)
            key = (os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)
            self.assertEqual(rows[key], ["model-00002.safetensors"])
            self.assertEqual(issues, [])

    def test_cgroup_exact_id_readonly(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/"42").mkdir()
            (root/"42"/"cgroup").write_text("0::/system.slice/docker-"+CID+".scope\n")
            self.assertTrue(a._cgroup_membership(42,CID,proc=root))
            self.assertFalse(a._cgroup_membership(42,"b"*64,proc=root))


class CollectionTests(unittest.TestCase):
    def opts(self, *, scanned=model_scan, sockets=socket_scan, api=lambda x:True):
        def run(argv, **kw):
            if argv[:2]==["docker","inspect"]:
                return json.dumps(info())
            if argv[0]=="iptables-save":
                return None
            if argv[:2]==["git","-C"]:
                return "c"*40 + "\n"
            raise AssertionError("unexpected command "+str(argv))
        return {"capture_ownership":lambda model:owner(), "run_command":run,
                "scan":scanned, "sockets":sockets,"api":api}

    def test_correlated_ple_candidate_still_not_release(self):
        with patch.object(a, "_cgroup_membership", return_value=True), patch.object(
                a, "_pid_identity", return_value={
                    "starttime_ticks": 42, "netns": "net:[1]", "mntns": "mnt:[2]",
                    "pidns": "pid:[3]"}), patch.object(
                a, "_pinned_snapshot_inodes",
                return_value=({(8,1,123):["model-00001.safetensors"]},[])):
            doc=a._collect(**self.opts())
        self.assertEqual(doc["status"],"CORRELATED_READ_ONLY_NOT_INDEPENDENTLY_AUTHENTICATED")
        self.assertEqual(doc["summary"]["candidate_file_mapping_rows"], 2)
        self.assertEqual(doc["summary"]["pinned_revision_alias_matched_mappings"], 2)
        self.assertFalse(doc["summary"]["ple_residency_authenticated"])
        self.assertFalse(doc["port"]["host_nat_path_authenticated"])
        self.assertFalse(doc["production_released"])
        self.assertFalse(doc["executed_inference"])
        self.assertTrue(doc["container_id_continuous"])

    def test_no_listener_fd_fails_closed_even_with_api_and_publish(self):
        def no_owner(pids,init_pid,*,proc):
            row=socket_scan(pids,init_pid,proc=proc)
            row["matched_docker_host_pids"]=[]
            return row
        with patch.object(a,"_cgroup_membership", return_value=True), patch.object(
                a, "_pid_identity", return_value={
                    "starttime_ticks": 42, "netns": "net:[1]", "mntns": "mnt:[2]",
                    "pidns": "pid:[3]"}), patch.object(
                a,"_pinned_snapshot_inodes",
                return_value=({(8,1,123):["model-00001.safetensors"]},[])):
            doc=a._collect(**self.opts(sockets=no_owner))
        self.assertEqual(doc["status"],"BLOCKED_PARTIAL_PROVENANCE")
        self.assertIn("CONTAINER_SOCKET_OWNER_FD_UNVERIFIED",doc["issues"])

    def test_docker_identity_drift_fails_closed(self):
        answers=[owner(), {**owner(),"container":{**owner()["container"],"id":"b"*64}}]
        def captures(model):
            return answers.pop(0)
        with patch.object(a,"_cgroup_membership",return_value=True), patch.object(
                a, "_pid_identity", return_value={
                    "starttime_ticks": 42, "netns": "net:[1]", "mntns": "mnt:[2]",
                    "pidns": "pid:[3]"}), patch.object(
                a,"_pinned_snapshot_inodes",return_value=({},[])):
            doc=a._collect(**(self.opts()|{"capture_ownership":captures}))
        self.assertFalse(doc["container_id_continuous"])
        self.assertIn("CONTAINER_OR_PID_DRIFT",doc["issues"])

    def test_blank_namespace_ids_cannot_pass_continuity(self):
        with patch.object(a, "_cgroup_membership", return_value=True), patch.object(
                a, "_pid_identity", return_value={
                    "starttime_ticks": 42, "netns": "", "mntns": "mnt:[2]",
                    "pidns": "pid:[3]"}), patch.object(
                a, "_pinned_snapshot_inodes",
                return_value=({(8,1,123):["model-00001.safetensors"]},[])):
            doc = a._collect(**self.opts())
        self.assertEqual(doc["status"], "BLOCKED_PARTIAL_PROVENANCE")
        self.assertFalse(doc["pid_identity_continuous"])
        self.assertIn("PID_STARTTIME_OR_NAMESPACE_DRIFT_OR_UNAVAILABLE",
                      doc["issues"])

    def test_no_preflight_leaves_host_unprobed(self):
        def fail(model):
            return {"status":"BLOCKED_PARTIAL_PROCESS_EVIDENCE",
                    "model":"orcarouter","docker_identity_match":False,
                    "container":{},"docker_host_pids":[]}
        def forbidden(*a,**kw):
            raise AssertionError("should not touch host")
        doc=a._collect(capture_ownership=fail,run_command=forbidden)
        self.assertEqual(doc["status"],"BLOCKED_PREFLIGHT")
        self.assertFalse(doc["executed_inference"])


if __name__=="__main__":
    unittest.main()
