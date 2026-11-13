import json
import tempfile
import unittest
from pathlib import Path
from ohf.scaffold import generate
from ohf.validate import validate

class ScaffoldTests(unittest.TestCase):
    def test_generate_and_validate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "bundle"
            manifest = generate("https://github.com/example/public-algorithm", "public_algorithm", root)
            self.assertEqual(manifest["execution"]["production_deployed"], False)
            result = validate(root)
            self.assertTrue(result["ok"], result)
            loaded = json.loads((root / "harness-manifest.json").read_text(encoding="utf-8"))
            self.assertFalse(loaded["provenance"]["source_copied"])

if __name__ == "__main__":
    unittest.main()
