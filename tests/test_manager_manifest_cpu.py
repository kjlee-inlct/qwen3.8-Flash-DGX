"""N1 source-only validator tests: no Docker, network, model downloads or GPU."""
from copy import deepcopy
import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest

from scripts.manager.manifest import RecipeError, load_recipe, main, validate_recipe

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests/fixtures/recipe-valid.synthetic.yaml"
CANDIDATE = ROOT / "recipes/qwen38-27b.candidate.yaml"


class ManifestValidationCPU(unittest.TestCase):
    def setUp(self):
        self.valid = load_recipe(VALID)

    def test_valid_synthetic_schema_only(self):
        self.assertEqual(validate_recipe(self.valid), [])
        self.assertEqual(self._cli(VALID), 0)

    def test_27b_placeholder_fails_closed(self):
        issues = validate_recipe(load_recipe(CANDIDATE))
        self.assertGreaterEqual(len(issues), 4)
        self.assertEqual(self._cli(CANDIDATE), 2)

    def test_unsupported_engine_rejected(self):
        invalid = deepcopy(self.valid)
        invalid["engine"] = "sglang"
        self.assertTrue(validate_recipe(invalid))

    def test_missing_revision_and_digest_rejected(self):
        invalid = deepcopy(self.valid)
        del invalid["model"]["revision"]
        del invalid["runtime"]["image_digest"]
        self.assertTrue(validate_recipe(invalid))

    def test_mutable_image_tag_and_wrong_digest_rejected(self):
        invalid = deepcopy(self.valid)
        invalid["runtime"]["image_ref"] = "vllm:v0.32.0"
        self.assertTrue(validate_recipe(invalid))
        invalid["runtime"]["image_ref"] = self.valid["runtime"]["image_ref"]
        invalid["runtime"]["image_digest"] = "sha256:" + "d" * 64
        self.assertIn("semantic:runtime/image_ref:image_digest_mismatch", validate_recipe(invalid))

    def test_protected_runtime_guards(self):
        invalid = deepcopy(self.valid)
        invalid["service"]["container_name"] = "qwen38-flash-orca-uncensored-bf16-mtp"
        invalid["service"]["port"] = 8000
        issues = validate_recipe(invalid)
        self.assertIn("semantic:service/container_name:protected_name", issues)
        self.assertIn("semantic:service/port:protected_port", issues)

    def test_approval_controls_cannot_be_enabled(self):
        invalid = deepcopy(self.valid)
        invalid["checks"]["allow_launch_without_gpu_approval"] = True
        invalid["lifecycle"]["allow_delete_without_approval"] = True
        self.assertTrue(validate_recipe(invalid))

    def test_mtp_boolean_token_consistency(self):
        invalid = deepcopy(self.valid)
        invalid["model"]["mtp"]["enabled"] = True
        self.assertTrue(validate_recipe(invalid))
        invalid["model"]["mtp"]["num_speculative_tokens"] = 2
        self.assertFalse(validate_recipe(invalid))

    def test_additional_properties_rejected(self):
        invalid = deepcopy(self.valid)
        invalid["runtime"]["privileged"] = True
        self.assertTrue(validate_recipe(invalid))

    def test_duplicate_yaml_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "duplicate.yaml"
            p.write_text("engine: vllm\nengine: sglang\n")
            with self.assertRaises(RecipeError):
                load_recipe(p)

    def test_unsafe_yaml_tag_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "unsafe.yaml"
            p.write_text("!!python/object/apply:os.system ['echo unsafe']\n")
            with self.assertRaises(RecipeError):
                load_recipe(p)

    def test_non_string_container_name_fails_as_validation_error(self):
        invalid = deepcopy(self.valid)
        invalid["service"]["container_name"] = ["bad"]
        self.assertTrue(validate_recipe(invalid))

    def test_alias_or_anchor_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "alias.yaml"
            p.write_text("model: &model value\nother: *model\n")
            with self.assertRaises(RecipeError):
                load_recipe(p)

    def test_malformed_yaml_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "malformed.yaml"
            p.write_text("a: [1, 2\n")
            self.assertEqual(self._cli(p), 2)

    def test_missing_file_is_blocked_not_pass(self):
        self.assertEqual(self._cli(Path("/does-not-exist/recipe.yaml")), 3)

    @staticmethod
    def _cli(path):
        with redirect_stdout(io.StringIO()):
            return main(["validate", str(path)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
