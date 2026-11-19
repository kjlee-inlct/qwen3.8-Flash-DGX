"""CPU-only fake GitHub response contract tests; never calls GitHub or DGX."""
import io
import unittest
from unittest.mock import patch

from scripts.manager.github_actions_readonly_audit import collect, main

SHA = "a" * 40


def evidence(path, *, token=None):
    if path.endswith("/actions/workflows/406361282"):
        return {"http_status": 200, "data": {"state": "active"}}
    if path.endswith("/actions/permissions"):
        return {"http_status": 403, "data": None, "issue": "HTTP_UNAVAILABLE"}
    if "/contents/.github/workflows/" in path:
        return {"http_status": 404 if path.endswith("ref=main") else 200,
                "data": None if path.endswith("ref=main") else {"name": "recipe-manifest-cpu.yml"}}
    if "/actions/runs?" in path:
        return {"http_status": 200, "data": {"workflow_runs": [
            {"head_sha": "b" * 40, "created_at": "2026-11-12T00:00:00Z",
             "event": "push", "status": "completed", "conclusion": "success"}]}}
    if "/check-runs?" in path:
        return {"http_status": 200, "data": {"total_count": 0, "check_runs": []}}
    raise AssertionError("Unexpected endpoint " + path)


class ActionsAuditCPU(unittest.TestCase):
    def test_active_workflow_without_latest_run_is_not_ci_pass(self):
        doc = collect(sha=SHA, fetch=evidence)
        self.assertEqual(doc["finding"], "NO_MATCHING_RUN_IN_LATEST_BRANCH_PAGE")
        self.assertEqual(doc["workflow_state"], "active")
        self.assertFalse(doc["default_branch_workflow_present"])
        self.assertTrue(doc["feature_branch_workflow_present"])
        self.assertIsNone(doc["repository_actions_enabled"])
        self.assertEqual(doc["exact_sha_runs_in_latest_page"], 0)
        self.assertFalse(doc["ci_verified"])
        self.assertFalse(doc["production_released"])

    def test_disabled_workflow_is_an_observation_not_an_authorization(self):
        def disabled(path, *, token=None):
            row = evidence(path, token=token)
            if path.endswith("/actions/workflows/406361282"):
                row["data"] = {"state": "disabled_manually"}
            return row
        doc = collect(sha=SHA, fetch=disabled)
        self.assertEqual(doc["finding"], "WORKFLOW_DISABLED_OBSERVED")
        self.assertFalse(doc["mutated_github_or_dgx"])

    def test_exact_sha_run_does_not_infer_passed_ci(self):
        def with_run(path, *, token=None):
            row = evidence(path, token=token)
            if "/actions/runs?" in path:
                row["data"] = {"workflow_runs": [
                    {"head_sha": SHA, "event": "push", "status": "queued",
                     "conclusion": None}]}
            return row
        doc = collect(sha=SHA, fetch=with_run)
        self.assertEqual(doc["finding"], "WORKFLOW_RUN_OBSERVED_NOT_CI_ATTESTED")
        self.assertEqual(doc["exact_sha_runs_in_latest_page"], 1)
        self.assertFalse(doc["ci_verified"])

    def test_missing_runs_response_does_not_mean_no_runs(self):
        def no_runs(path, *, token=None):
            row = evidence(path, token=token)
            if "/actions/runs?" in path:
                return {"http_status": 403, "data": None}
            return row
        doc = collect(sha=SHA, fetch=no_runs)
        self.assertEqual(doc["finding"], "INCOMPLETE_API_EVIDENCE")
        self.assertIsNone(doc["exact_sha_runs_in_latest_page"])

    def test_bounded_repo_branch_and_sha_scope(self):
        for data in (
            {"repo": "https://evil.invalid/a"},
            {"branch": "../main"},
            {"branch": "x?y"},
            {"sha": "short"},
            {"workflow_id": True},
        ):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    kwargs = {"sha": SHA}
                    kwargs.update(data)
                    collect(fetch=evidence, **kwargs)

    def test_authenticated_complete_with_default_branch_404_is_rc_zero(self):
        def authorized(path, *, token=None):
            row = evidence(path, token=token)
            if path.endswith("/actions/permissions"):
                return {"http_status": 200, "data": {"enabled": True}}
            return row

        receipt = collect(sha=SHA, fetch=authorized)
        self.assertTrue(receipt["audit_evidence_complete"])
        self.assertEqual(receipt["endpoint_http_status"]["default_file"], 404)
        self.assertFalse(receipt["default_branch_workflow_present"])
        self.assertFalse(receipt["ci_verified"])

        with patch("scripts.manager.github_actions_readonly_audit.collect",
                   return_value=receipt), patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(main(["--sha", SHA, "--json"]), 0)

    def test_missing_permissions_stays_rc_three(self):
        receipt = collect(sha=SHA, fetch=evidence)
        self.assertFalse(receipt["audit_evidence_complete"])
        with patch("scripts.manager.github_actions_readonly_audit.collect",
                   return_value=receipt), patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(main(["--sha", SHA, "--json"]), 3)

    def test_http_success_without_required_fields_does_not_pass_audit(self):
        def missing_data(path, *, token=None):
            row = evidence(path, token=token)
            if path.endswith("/actions/permissions"):
                return {"http_status": 200, "data": {}}
            return row

        receipt = collect(sha=SHA, fetch=missing_data)
        self.assertIsNone(receipt["repository_actions_enabled"])
        self.assertFalse(receipt["audit_evidence_complete"])

    def test_token_not_in_report(self):
        doc = collect(sha=SHA, fetch=evidence, token="sensitive-placeholder")
        self.assertNotIn("sensitive-placeholder", str(doc))


if __name__ == "__main__":
    unittest.main()
