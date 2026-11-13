---
name: public_algorithm
description: Run the reviewed public adapter contract for public_algorithm.
---

# public_algorithm skill

## Inputs

Read `harness-manifest.json` and validate the request against `schemas/request.schema.json`. The input path must be inside the approved workspace. Do not accept credentials, arbitrary output paths, or undocumented fields.

## Execution

The generated adapter starts in dry-run mode. It must remain dry-run until the entry point, license, input contract, output contract, resource limits, and isolation plan have been reviewed.

## Outputs

Write only to the declared output directory. Produce a result manifest, an environment record, and a reproducibility record. Do not claim that a process exit code proves scientific validity.

## Interpretation

Use `references/interpretation.md` and preserve the algorithm's own limitations. A result is an adapter execution result, not an Omicos deployment claim.
