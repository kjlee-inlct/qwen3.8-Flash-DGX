"""Repository-wide P5 handoff/document inventory consistency (CPU-only).

Protects current instructions from reverting to old P4/QSA-only runbooks.
No Docker/API/GPU operations.
"""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUDIT = "docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md"
NEW_COMMON = "docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md"
NEW_P5D_P6E = "docs/P5-D-P6-E-READ-ONLY-PROVENANCE-JOURNAL-V2-20261110.md"
# Intentional additions since the immutable 169-path original inventory.
# Do not silently let arbitrary new document-like files bypass this test.
INCREMENTAL_APPROVED = {
    "docs/GITHUB-ACTIONS-NO-RUN-INVESTIGATION-20261118.md",
    "docs/P3-P5-ONE-TURN-CLOSEOUT-20261118.md",
    "docs/P6-E-CPU-CI-FOLLOWUP-20261118.md",
    "docs/P6-E-UNTRUSTED-JSON-INGEST-FENCE-20261118.md",
    "handoff/CI-PUSH-TRIGGER-PROBE-20261118.md",
}
RUNBOOK = "docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md"
MARKER = "CURRENT P5 DOCUMENT SUPERSESSION"
SECONDARY = "current P5 v2 supersession"
ADAPTER = "qwen4exp-qsa62318-lmhead-v032-v2"
ADAPTER_V3 = "qwen4exp-qsa62318-lmhead-v032-v3"
README_LATEST = [
    "README.md",
    "recipes/README.md",
    "scripts/temporary/README.md",
    "docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md",
    "docs/MANIFEST-CONTRACTS.md",
    "docs/MODEL-RECIPE-WIZARD-PLAN.md",
    "docs/UNIFIED-MODEL-WIZARD-DESIGN.md",
    "docs/WIZARD-CLI-CONTRACT.md",
    "docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md",
    "docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md",
    "docs/HANDOFF-DOCUMENT-AUDIT-P5-20261108.md",
    "handoff/START-NEXT-P4A-20261108.md",
    "handoff/START-NEXT-WIZARD-LIFECYCLE-20261107.md",
]
PRIMARY = [
    "handoff/README.md",
    "handoff/CURRENT-STATE.md",
    "handoff/NEXT-ACTIONS.md",
    "handoff/EVIDENCE-LEDGER.md",
    "handoff/DECISIONS.md",
    "handoff/CHANGELOG.md",
    "handoff/OPERATING-RULES.md",
    "handoff/SESSION-START-PROMPT.md",
    "handoff/START-NEXT-P5-20261108.md",
    "docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md",
]
EXT = {".md", ".mdx", ".rst", ".adoc", ".json", ".yaml", ".yml", ".toml", ".txt"}
LINK = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)\)")


def _tracked_document_paths():
    """Audit the Git index, not private/ignored operator receipts on the host.

    An operator's ignored reports/transitions/*.json must not alter the
    version-controlled document inventory; missing tracked files still fail.
    """
    raw = subprocess.check_output(
        ["git", "ls-files", "--cached", "--full-name", "-z"],
        cwd=ROOT, timeout=20)
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError("TRACKED_FILE_LIST_TOO_LARGE")
    entries = raw.split(b"\0")
    if entries[-1] != b"":
        raise ValueError("INVALID_TRACKED_FILE_LIST")
    current = set()
    for item in entries[:-1]:
        path = Path(item.decode("utf-8"))
        if not path.parts or path.is_absolute() or ".." in path.parts:
            raise ValueError("INVALID_TRACKED_PATH")
        if not (ROOT / path).is_file():
            continue
        if path.suffix.lower() in EXT or path.name in ("LICENSE", "NOTICE"):
            current.add(path.as_posix())
    return current



class P5HandoffFullDocumentCPU(unittest.TestCase):
    def test_full_inventory_resolves_every_original_document(self):
        mark = chr(96)
        text = (ROOT / AUDIT).read_text(encoding="utf-8")
        original = [
            line[3:-1] for line in text.splitlines()
            if line.startswith("- " + mark) and line.endswith(mark)
        ]
        self.assertEqual(len(original), 169)
        self.assertEqual(len(set(original)), 169)
        missing = [p for p in original if not (ROOT / p).is_file()]
        self.assertFalse(missing, missing)
        current = _tracked_document_paths()
        self.assertEqual(current - set(original), {AUDIT, NEW_COMMON, NEW_P5D_P6E} | INCREMENTAL_APPROVED)
        self.assertEqual(set(original) - current, set())

    def test_git_tracked_inventory_ignores_local_private_operator_reports(self):
        from unittest.mock import patch

        raw = (b"docs/P3-P5-ONE-TURN-CLOSEOUT-20261118.md\0"
               b"reports/transitions/flash-next--to--27b/private-receipt.json\0"
               b"tests/test_p5_document_integrity_cpu.py\0")
        with patch("subprocess.check_output", return_value=raw):
            found = _tracked_document_paths()
        self.assertIn("docs/P3-P5-ONE-TURN-CLOSEOUT-20261118.md", found)
        # The mocked receipt path is not an on-disk file, so a local report
        # never gets accepted on the basis of a glob-like directory scan.
        self.assertNotIn("reports/transitions/flash-next--to--27b/private-receipt.json", found)

    def test_tracked_inventory_rejects_unsafe_git_paths(self):
        from unittest.mock import patch

        with patch("subprocess.check_output", return_value=b"../escape.json\0"):
            with self.assertRaises(ValueError):
                _tracked_document_paths()

    def test_latest_p3_p5_scope_is_non_authorizing(self):
        p = ROOT / "docs/P3-P5-ONE-TURN-CLOSEOUT-20261118.md"
        text = p.read_text(encoding="utf-8")
        for token in ("P3", "P4", "P5", "CI_UNVERIFIED",
                      "PRODUCTION_BLOCKED", "P5", "NOT ACCEPTED"):
            self.assertIn(token, text)

    def test_primary_and_secondary_docs_have_current_override(self):
        for path in PRIMARY:
            with self.subTest(path=path):
                content = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn(MARKER, content, path)
                self.assertTrue(ADAPTER in content or ADAPTER_V3 in content, path)
                self.assertIn("lm_head.weight_scale", content, path)
        for path in README_LATEST:
            with self.subTest(path=path):
                content = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn(SECONDARY, content, path)
                self.assertIn(ADAPTER, content, path)

    def test_all_markdown_relative_document_links_resolve(self):
        # Verify repository-wide local Markdown paths, not just handoff headers.
        missing = []
        inspected = 0
        for page in ROOT.rglob("*.md"):
            if ".git" in page.parts:
                continue
            for link in LINK.findall(page.read_text(encoding="utf-8")):
                if link.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                target = (page.parent / link).resolve()
                inspected += 1
                if not target.is_relative_to(ROOT) or not target.is_file():
                    missing.append((page.relative_to(ROOT).as_posix(), link))
        self.assertGreaterEqual(inspected, 100)
        self.assertFalse(missing, missing[:30])

    def test_new_runbook_is_distinct_and_isolated(self):
        runbook = (ROOT / RUNBOOK).read_text(encoding="utf-8")
        self.assertIn("lm_head.weight_scale", runbook)
        self.assertIn(ADAPTER, runbook)
        self.assertIn("I_ACCEPT_P5_NO_ROLLBACK", runbook)
        self.assertIn("quantization_config", runbook)
        self.assertIn("gpu_verified=false", runbook)
        self.assertIn("Dockerfile.p5.qsa62318-lmhead", runbook)
        self.assertIn("no automatic", runbook.lower())

    def test_new_supersession_links_resolve(self):
        for name in PRIMARY + README_LATEST:
            p = ROOT / name
            header = p.read_text(encoding="utf-8")
            urls = LINK.findall(header)
            self.assertGreaterEqual(len(urls), 2, name)
            for rel in urls:
                if rel.startswith(("https://", "http://")):
                    # External pinned research links are not local files.
                    continue
                target = (p.parent / rel).resolve()
                with self.subTest(doc=name, link=rel):
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.is_file())


if __name__ == "__main__":
    unittest.main()
