import json
from pathlib import Path


def test_manifest_is_non_deploying():
    manifest = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
    assert manifest["execution"]["production_deployed"] is False
    assert manifest["provenance"]["source_copied"] is False
