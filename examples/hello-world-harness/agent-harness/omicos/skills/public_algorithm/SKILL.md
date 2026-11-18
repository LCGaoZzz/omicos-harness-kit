---
name: "public_algorithm"
description: Review and use the public adapter contract for public_algorithm; the generated runner is a dry run until an algorithm implementation is supplied.
---

# public_algorithm skill

## Readiness

After importing with `ohf install`, read the skill-local `harness-manifest.json`. Before import, the authoritative manifest is at the bundle root. If the local manifest is missing, import the complete bundle instead of copying SKILL.md alone.

If execution.mode is dry-run or unresolved fields remain, explain what still needs implementation. Do not claim an algorithm run. The generated scripts/run_adapter.py only checks the request contract and emits dry_run.

## Inputs and execution

Validate requests against `schemas/request.schema.json`. Read `references/input-contract.md` for algorithm-specific requirements. Use only the reviewed entrypoint and the active execution environment's authorized tools and resource limits. Keep input and output paths inside the approved workspace.

## Outputs and interpretation

Validate results against `schemas/result.schema.json`. Produce a reproducibility record matching `contracts/reproducibility.v1.json`. Use `references/interpretation.md`; report diagnostics, limitations, and whether an algorithm actually ran. Contract validation does not verify live product integration or scientific correctness.
