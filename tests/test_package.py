import hashlib
import json
import os
import tarfile

from ohf.package import content_hash, package
from ohf.install import install
from ohf.validate import validate
from support import BundleCase


class PackageTests(BundleCase):
    def test_archives_are_reproducible_and_hashes_match_actual_bytes(self):
        first = package(self.root, self.directory / "one.tar.gz")
        os.utime(self.skill / "SKILL.md", (10, 10))
        second = package(self.root, self.directory / "another-name.tar.gz")
        self.assertEqual(first["archive_sha256"], second["archive_sha256"])
        data = (self.directory / "one.tar.gz").read_bytes()
        self.assertEqual(first["archive_sha256"], hashlib.sha256(data).hexdigest())
        with tarfile.open(first["archive"], "r:gz") as archive:
            actual = {item.name: hashlib.sha256(archive.extractfile(item).read()).hexdigest() for item in archive.getmembers()}
        self.assertEqual(actual, first["files_sha256"])
        self.assertEqual(first["content_sha256"], content_hash(actual))
        self.assertFalse(first["validation"]["runtime_ready"])

    def test_invalid_manifest_and_boundary_findings_block_packaging(self):
        self.write_manifest({})
        output = self.directory / "invalid.tar.gz"
        with self.assertRaises(ValueError):
            package(self.root, output)
        self.assertFalse(output.exists())
        self.write_manifest(self.manifest)
        (self.root / ".env").write_text("gh" + "p_" + "a" * 32)
        self.assertFalse(validate(self.root)["ok"])
        with self.assertRaises(ValueError):
            package(self.root, output)
        self.assertFalse(output.exists())

    def test_symlink_resources_block_validate_package_and_install(self):
        outside = self.directory / "outside.txt"; outside.write_text("synthetic outside data")
        (self.skill / "references/link.txt").symlink_to(outside)
        self.assertFalse(validate(self.root)["ok"])
        with self.assertRaises(ValueError):
            package(self.root, self.directory / "linked.tar.gz")
        with self.assertRaises(ValueError):
            install(self.root, self.workspace)
        self.assertFalse((self.workspace / "skills").exists())

    def test_archive_output_inside_bundle_and_existing_output_are_rejected(self):
        with self.assertRaises(ValueError):
            package(self.root, self.root / "recursive.tar.gz")
        existing = self.directory / "existing.tar.gz"; existing.write_text("do not overwrite")
        with self.assertRaises(FileExistsError):
            package(self.root, existing)
        self.assertEqual(existing.read_text(), "do not overwrite")

    def test_runtime_readiness_can_be_required_at_packaging(self):
        with self.assertRaises(ValueError):
            package(self.root, self.directory / "not-ready.tar.gz", require_runtime_ready=True)
