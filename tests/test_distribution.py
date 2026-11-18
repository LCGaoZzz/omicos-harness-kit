"""Exercise the installed wheel from a cwd outside the source checkout."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


class DistributionTests(unittest.TestCase):
    def test_wheel_has_resources_and_installs_a_self_contained_skill(self):
        checkout = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="ohf-wheel-test-") as directory:
            directory = Path(directory)
            wheels = directory / "wheels"; wheels.mkdir()
            env = os.environ.copy(); env.pop("PYTHONPATH", None)
            def run(command, cwd=directory):
                result = subprocess.run([str(x) for x in command], cwd=cwd, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result
            run([sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "--no-index", "--wheel-dir", wheels, checkout])
            wheel = next(wheels.glob("*.whl"))
            with zipfile.ZipFile(wheel) as archive:
                names = archive.namelist()
                self.assertIn("ohf/schemas/harness-manifest.schema.json", names)
                self.assertIn("ohf/runner_template.py", names)
                self.assertEqual(len([p for p in names if p.startswith("ohf/schemas/")]), 4)
            environment = directory / "environment"
            run([sys.executable, "-m", "venv", "--system-site-packages", environment])
            python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            cli = environment / ("Scripts/ohf.exe" if os.name == "nt" else "bin/ohf")
            run([python, "-m", "pip", "install", "--no-deps", "--no-index", "--force-reinstall", wheel])
            loaded_from = Path(run([python, "-c", "import ohf; print(ohf.__file__)"]).stdout.strip())
            self.assertTrue(loaded_from.is_relative_to(environment), str(loaded_from))
            self.assertEqual(run([cli, "--version"]).stdout.strip(), "0.2.0")
            bundle = directory / "bundle"
            workspace = directory / "workspace"; workspace.mkdir()
            (workspace / "existing.txt").write_text("preserved")
            run([cli, "init", "--repo", "https://github.com/example/public-algorithm", "--name", "wheel_example", "--output", bundle])
            installed = json.loads(run([cli, "install", bundle, "--workspace", workspace]).stdout)
            target = Path(installed["destination"])
            self.assertTrue((target / "references/input-contract.md").is_file())
            request = directory / "request.json"
            request.write_text(json.dumps({"schema_version": "1.0", "analysis": "wheel fixture", "input": {"path": "synthetic.txt"}, "output": {"directory": "results"}}))
            result = directory / "result.json"
            result.write_text(run([python, target / "scripts/run_adapter.py", "--request", request]).stdout)
            checked = json.loads(run([cli, "validate", target, "--request", request, "--result", result]).stdout)
            self.assertTrue(checked["scaffold_valid"])
            self.assertFalse(checked["runtime_ready"])
            self.assertFalse(checked["integration_verified"])
            self.assertEqual(json.loads(result.read_text())["status"], "dry_run")
            self.assertEqual((workspace / "existing.txt").read_text(), "preserved")
