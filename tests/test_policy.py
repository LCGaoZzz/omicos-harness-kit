import tempfile
import unittest
from pathlib import Path
from ohf.policy import scan_tree

class PolicyTests(unittest.TestCase):
    def test_clean_tree(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "README.md"
            p.write_text("public contract only\n", encoding="utf-8")
            self.assertTrue(scan_tree(Path(d))["ok"])

    def test_secret_detection(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.txt"
            p.write_text("gh" + "p_" + "abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
            result = scan_tree(Path(d))
            self.assertFalse(result["ok"])
            self.assertTrue(result["findings"])

if __name__ == "__main__":
    unittest.main()
