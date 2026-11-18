import json
import subprocess
import sys
from pathlib import Path

from ohf.contracts import load_schema, schema_errors
from ohf.scaffold import generate
from ohf.validate import validate
from support import BundleCase


class ContractTests(BundleCase):
    def test_generated_manifest_matches_published_schema_and_is_only_scaffold(self):
        self.assertEqual(schema_errors(self.manifest, load_schema("harness-manifest.schema.json"), "manifest"), [])
        checked = validate(self.root)
        self.assertTrue(checked["ok"], checked)
        self.assertEqual(checked["status"], "scaffold_valid")
        self.assertFalse(checked["runtime_ready"])
        self.assertFalse(checked["integration_verified"])
        self.assertFalse(validate(self.root, require_runtime_ready=True)["ok"])

    def test_empty_non_object_and_malformed_manifests_fail(self):
        for value in ({}, [], None, 1, "text", {"manifest_version": "1.0"}):
            with self.subTest(value=value):
                self.write_manifest(value)
                self.assertFalse(validate(self.root)["ok"])
        (self.root / "harness-manifest.json").write_text("{", encoding="utf-8")
        self.assertFalse(validate(self.root)["ok"])

    def test_request_and_result_are_validated_against_real_schemas(self):
        request = self.write_json("request.json", self.request())
        result = self.write_json("result.json", {"schema_version": "1.0", "status": "dry_run", "artifacts": [], "warnings": [], "limitations": []})
        self.assertTrue(validate(self.root, request=request, result=result)["ok"])
        request.write_text('{}', encoding="utf-8")
        self.assertFalse(validate(self.root, request=request)["ok"])
        data = json.loads(result.read_text()); data["unexpected"] = True
        result.write_text(json.dumps(data), encoding="utf-8")
        self.assertFalse(validate(self.root, result=result)["ok"])

    def test_generated_dry_run_output_matches_its_schema_and_invalid_input_fails(self):
        request = self.write_json("request.json", self.request())
        command = [sys.executable, str(self.skill / "scripts/run_adapter.py"), "--request", str(request)]
        run = subprocess.run(command, cwd=self.workspace, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(schema_errors(result, load_schema("result.schema.json"), "result"), [])
        request.write_text('{}', encoding="utf-8")
        run = subprocess.run(command, cwd=self.workspace, text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertNotIn("Traceback", run.stderr)

    def test_names_are_checked_before_any_writes(self):
        for i, name in enumerate(("../escape", "a/b", "BadName", "", "a" * 65, str(self.directory / "escape"))):
            output = self.directory / ("invalid-" + str(i))
            with self.subTest(name=name), self.assertRaises(ValueError):
                generate("https://github.com/example/public-algorithm", name, output)
            self.assertFalse(output.exists())
        self.assertFalse((self.directory / "escape").exists())

    def test_resource_paths_must_stay_inside_the_skill(self):
        for path in ("../outside.json", "/absolute.json", "schemas\\request.json", "README.md"):
            with self.subTest(path=path):
                self.manifest["contracts"]["request_schema"] = path
                self.write_manifest(self.manifest)
                self.assertFalse(validate(self.root)["ok"])

    def test_yaml_keyword_names_remain_string_metadata(self):
        for name in ("on", "off", "yes", "no", "true", "false", "null", "x"):
            output = self.directory / ("keyword-" + name)
            with self.subTest(name=name):
                generate("https://github.com/example/public-algorithm", name, output)
                checked = validate(output)
                self.assertTrue(checked["ok"], checked)

    def test_missing_resources_invalid_schema_and_external_references_fail(self):
        path = self.skill / "schemas/request.schema.json"
        original = path.read_text()
        for content in ('{}', '{"$schema":"https://json-schema.org/draft/2020-12/schema","type":42}',
                        '{"$schema":"https://json-schema.org/draft/2020-12/schema","$ref":"https://invalid.example/schema.json"}'):
            with self.subTest(content=content):
                path.write_text(content)
                self.assertFalse(validate(self.root)["ok"])
        path.write_text(original); path.unlink()
        self.assertFalse(validate(self.root)["ok"])

    def test_yaml_metadata_is_parsed_safely(self):
        path = self.skill / "SKILL.md"
        for content in ("---\nname: public_algorithm\ndescription: [broken\n---\n", "---\nname: public_algorithm\nname: public_algorithm\ndescription: demo\n---\n", "---\nname: other\ndescription: demo\n---\n"):
            with self.subTest(content=content):
                path.write_text(content)
                self.assertFalse(validate(self.root)["ok"])
        path.write_text("---\nname: public_algorithm\ndescription: |\n  A valid multiline\n  description.\n---\nBody\n")
        self.assertTrue(validate(self.root)["ok"])

    def test_packaged_schemas_match_public_copies(self):
        published = Path(__file__).resolve().parents[1] / "schemas"
        for path in published.glob("*.json"):
            self.assertEqual(json.loads(path.read_text()), load_schema(path.name))

    def test_recorded_readiness_never_claims_integration(self):
        self.manifest["source"]["commit"] = "a" * 40
        self.manifest["source"]["license"] = {"status": "confirmed", "evidence": "https://github.com/example/public-algorithm/blob/" + "a" * 40 + "/LICENSE"}
        self.manifest["entrypoint"] = {"kind": "python_module", "module": "reviewed_example", "command": None, "arguments": []}
        self.manifest["unresolved"] = []
        self.manifest["execution"].update({"mode": "reviewed", "source_execution": "reviewed", "resource_limits": {"cpu_seconds": 1, "memory_mb": 32, "wall_seconds": 3}, "validation": {"evidence_path": "references/runtime-validation.md", "environment": "synthetic recorded fixture only", "tested_at": "2026-11-18T00:00:00Z"}})
        (self.skill / "references/runtime-validation.md").write_text("Synthetic metadata fixture; this test does not execute an algorithm.\n")
        self.write_manifest(self.manifest)
        checked = validate(self.root, require_runtime_ready=True)
        self.assertTrue(checked["ok"], checked)
        self.assertTrue(checked["runtime_ready"])
        self.assertEqual(checked["runtime_readiness_basis"], "declared_contract_and_recorded_evidence_only")
        self.assertFalse(checked["integration_verified"])
