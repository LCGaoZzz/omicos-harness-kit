import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from ohf.install import install
from ohf.validate import validate
from support import BundleCase


class InstallTests(BundleCase):
    def test_installs_complete_skill_into_populated_workspace(self):
        preserved = self.workspace / "existing.txt"
        preserved.write_text("keep me")
        report = install(self.root, self.workspace)
        target = Path(report["destination"])
        self.assertEqual(target, self.workspace / "skills/public_algorithm")
        self.assertEqual(preserved.read_text(), "keep me")
        for relative in ("SKILL.md", "scripts/run_adapter.py", "references/input-contract.md", "references/interpretation.md", "schemas/request.schema.json", "schemas/result.schema.json", "contracts/reproducibility.v1.json", "harness-manifest.json", "installation-receipt.json"):
            self.assertTrue((target / relative).is_file(), relative)
        local = json.loads((target / "harness-manifest.json").read_text())
        self.assertEqual(local["layout"], "skill")
        self.assertTrue(all((target / p).is_file() for p in local["contracts"].values()))
        self.assertTrue(validate(target)["ok"])
        self.assertFalse(report["agents_installed"])
        self.assertFalse(report["validation"]["runtime_ready"])
        self.assertFalse(report["discovery_verified"])
        self.assertFalse((self.workspace / "agents").exists())
        self.assertEqual(list((self.workspace / "skills").glob("*/SKILL.md")), [target / "SKILL.md"])

    def test_conflict_preserves_existing_skill(self):
        first = install(self.root, self.workspace)
        target = Path(first["destination"])
        marker = target / "keep.txt"; marker.write_text("existing")
        with self.assertRaises(FileExistsError):
            install(self.root, self.workspace)
        self.assertEqual(marker.read_text(), "existing")

    def test_replace_backs_up_and_backup_can_be_reinstalled(self):
        first = install(self.root, self.workspace)
        target = Path(first["destination"])
        old_text = (target / "references/interpretation.md").read_text()
        (self.skill / "references/interpretation.md").write_text("Reviewed new text\n")
        replaced = install(self.root, self.workspace, replace=True)
        backup = Path(replaced["backup"])
        self.assertEqual((backup / "references/interpretation.md").read_text(), old_text)
        self.assertEqual((target / "references/interpretation.md").read_text(), "Reviewed new text\n")
        restored = install(backup, self.workspace, replace=True)
        self.assertTrue(restored["ok"])
        self.assertEqual((target / "references/interpretation.md").read_text(), old_text)
        self.assertEqual(list((self.workspace / "skills").glob("*/SKILL.md")), [target / "SKILL.md"])

    def test_failed_replacement_restores_previous_directory(self):
        first = install(self.root, self.workspace)
        target = Path(first["destination"])
        original = (target / "SKILL.md").read_bytes()
        real_replace = os.replace
        def fail_publish(source, destination):
            if Path(destination) == target and ".ohf-staging" in Path(source).parts:
                raise OSError("synthetic publish failure")
            return real_replace(source, destination)
        with mock.patch("ohf.install.os.replace", side_effect=fail_publish), self.assertRaises(OSError):
            install(self.root, self.workspace, replace=True)
        self.assertEqual((target / "SKILL.md").read_bytes(), original)
        self.assertEqual(list((self.workspace / "skills/.ohf-staging").iterdir()), [])

    def test_invalid_bundle_and_strict_readiness_do_not_mutate_workspace(self):
        with self.assertRaises(ValueError):
            install(self.root, self.workspace, require_runtime_ready=True)
        self.assertFalse((self.workspace / "skills").exists())
        self.write_manifest({})
        with self.assertRaises(ValueError):
            install(self.root, self.workspace)
        self.assertFalse((self.workspace / "skills").exists())

    def test_failed_restoration_reports_the_preserved_backup(self):
        first = install(self.root, self.workspace)
        target = Path(first["destination"])
        original = (target / "SKILL.md").read_bytes()
        real_replace = os.replace
        def fail_writes_to_target(source, destination):
            if Path(destination) == target:
                raise OSError("synthetic destination unavailable")
            return real_replace(source, destination)
        with mock.patch("ohf.install.os.replace", side_effect=fail_writes_to_target):
            with self.assertRaisesRegex(ValueError, "previous version remains in backup"):
                install(self.root, self.workspace, replace=True)
        backups = list((self.workspace / "skills/.ohf-backups/public_algorithm").glob("*/SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)

    def test_symlink_skill_root_is_rejected_without_writing_elsewhere(self):
        outside = self.directory / "outside"; outside.mkdir()
        (self.workspace / "skills").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            install(self.root, self.workspace)
        self.assertEqual(list(outside.iterdir()), [])

    def test_legacy_destination_flag_routes_through_validated_installer(self):
        checkout = Path(__file__).resolve().parents[1]
        legacy_destination = self.directory / "legacy-workspace"
        env = os.environ.copy(); env["PYTHONPATH"] = str(checkout / "src")
        run = subprocess.run([sys.executable, str(checkout / "scripts/install_public_bundle.py"), str(self.root), "--destination", str(legacy_destination)], env=env, cwd=self.directory, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue((legacy_destination / "skills/public_algorithm/SKILL.md").is_file())
        self.assertIn("deprecated", run.stderr)
        self.assertFalse(json.loads(run.stdout)["production_deployed"])
