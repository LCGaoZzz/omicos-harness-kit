import json
import tempfile
import unittest
from pathlib import Path

from ohf.scaffold import generate


class BundleCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ohf-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.root = self.directory / "bundle"
        self.manifest = generate("https://github.com/example/public-algorithm", "public_algorithm", self.root)
        self.skill = self.root / "agent-harness/omicos/skills/public_algorithm"
        self.workspace = self.directory / "workspace"
        self.workspace.mkdir()

    def write_manifest(self, value):
        (self.root / "harness-manifest.json").write_text(json.dumps(value), encoding="utf-8")

    def write_json(self, name, value):
        path = self.directory / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def request(self):
        return {"schema_version": "1.0", "analysis": "synthetic-contract-test",
                "input": {"path": "synthetic.txt"}, "output": {"directory": "results"}}
