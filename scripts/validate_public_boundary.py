#!/usr/bin/env python3
"""Standalone boundary scanner for CI and users without an editable install."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ohf.policy import scan_tree

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
result = scan_tree(root)
print(json.dumps(result, indent=2, ensure_ascii=False))
raise SystemExit(0 if result["ok"] else 2)
