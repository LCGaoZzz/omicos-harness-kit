# Omicos Harness Kit

**Public tooling for creating, validating and installing reviewable algorithm skill bundles.**

Give an agent a public algorithm GitHub URL and the kit's [Harness Builder skill](skills/omicos-harness-builder/SKILL.md). The agent researches the public algorithm and fills its contract; the CLI generates and validates the bundle. A URL alone does not supply an algorithm implementation.

The kit publishes an implementation-neutral contract and original templates. Product execution, account permissions, discovery refresh and agent management remain the responsibility of the receiving Omicos deployment. No proprietary runtime is included or required by this repository.

## What works in 0.2

- Generate a standard `SKILL.md` with references, schemas, a reproducibility contract and an explicitly dry-run script.
- Validate manifests and request/result payloads with JSON Schema, parse metadata safely, and reject missing resources, unsafe paths and symlinks.
- Install the **complete skill** under an existing workspace's `skills/<name>/`, including a skill-local manifest. Other workspace files are preserved.
- Refuse skill-name conflicts unless `--replace` is supplied. Replacement preserves a reinstallable backup and restores the previous directory if publishing the replacement fails.
- Validate before packaging and installation. Generate deterministic archives with per-file, content-set and archive SHA-256 digests.
- Report structural validity, declared runtime readiness and live integration verification separately.

## Read the status correctly

| Field | Meaning |
|---|---|
| `scaffold_valid` | Manifest, metadata, referenced schemas/resources and boundary checks passed. An unresolved draft can satisfy this. |
| `runtime_ready` | Required runtime declarations and a referenced review/evidence file are present. Its scope is explicitly `declared_contract_and_recorded_evidence_only`; the validator does not execute or independently verify that evidence. |
| `integration_verified` | Always `false` in this CLI. A receiving product must perform its own discovery, resource access, execution and result checks. |
| `discovery_verified` | Installation receipts report `false`: copying files does not prove a live product has refreshed or admitted the skill. |

Generated bundles start with `scaffold_valid=true`, `runtime_ready=false`, and `integration_verified=false`. The generated runner only validates a request and emits `status: dry_run`; it has no algorithm implementation and advertises no packaged execution entrypoint.

`inspect` creates an **inspection plan** from the supplied URL. It does not fetch repository contents, infer input formats, install the algorithm or execute its code.

## Install the CLI in the actual execution environment

Python 3.10 or newer is required. From a reviewed checkout of this repository:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
ohf --version
```

For a remote Omicos workspace, run this in the remote execution environment. Installing on a local laptop does not install the CLI on the server. Once installed, `ohf` works from outside the repository checkout; bundled schemas and the runner template are included in the wheel.

## Create and install an algorithm skill

Use explicit paths for your intended bundle and active workspace. These example directories are relative to your current shell directory:

```bash
ohf inspect https://github.com/StatBiomed/UniTVelo --output inspection.json
ohf init --repo https://github.com/StatBiomed/UniTVelo --name unitvelo --output unitvelo-harness

# Review the root manifest and algorithm-specific references, then validate.
ohf validate unitvelo-harness

# The workspace already exists; it may contain other files and skills.
ohf install unitvelo-harness --workspace ./my-workspace

# Optional transfer archive. Invalid bundles cannot be packaged.
ohf package unitvelo-harness --output unitvelo-harness.tar.gz
```

The default install is useful for reviewing a scaffold inside the product. It does not make the unimplemented algorithm runnable. For a process that accepts only fully declared runtime contracts, add `--require-runtime-ready` to `validate`, `install` or `package`.

Payload validation is explicit:

```bash
ohf validate unitvelo-harness --request request.json --result result.json
```

After installation, the CLI prints the actual destination and a refresh instruction. Open or refresh skills in the **same active workspace**. Account capability and product-side import/discovery support are checked by the receiving product; the public CLI does not grant them.

## Installed layout

The transfer bundle retains `agent-harness/omicos/skills/<name>/`. The installer maps that subtree to the workspace's discoverable location:

```text
my-workspace/
  skills/
    unitvelo/
      SKILL.md
      harness-manifest.json
      installation-receipt.json
      references/input-contract.md
      references/interpretation.md
      schemas/request.schema.json
      schemas/result.schema.json
      contracts/reproducibility.v1.json
      scripts/run_adapter.py
```

The root bundle manifest is authoritative before installation. The installer creates a skill-local copy with resource paths rebased to that skill directory. Copying only `SKILL.md` loses required resources and is unsupported for these bundles.

Optional files under `agent-harness/omicos/agents/` are **not installed**. Custom agents are a separate product capability and require a separate management/import flow.

## Replacement and recovery

```bash
ohf install unitvelo-harness --workspace ./my-workspace --replace
```

An existing skill is backed up under `skills/.ohf-backups/<name>/<revision>/`; staging and backup directories do not put another `SKILL.md` at the direct discovery level. The receipt reports the backup path. To restore a backup, reinstall that directory with the same command and `--replace`; this also preserves the version being replaced. Do not edit the source bundle while an install or archive operation is running.

The historical `scripts/install_public_bundle.py BUNDLE --destination WORKSPACE` flag remains as a deprecated wrapper. The destination now denotes a workspace, and the complete skill is installed under `skills/<name>/`. Prefer `ohf install`.

## Use the Harness Builder itself

The repository's `skills/omicos-harness-builder/SKILL.md` follows the same workspace convention. It is discoverable when the repository root is the active workspace and the product admits project skills. For another workspace, copy the entire builder skill directory into that workspace's `skills/` directory and install/check `ohf` separately in its execution environment.

A nested repository checkout is not automatically a skill installation. Pip-installing the CLI does not register the builder skill, and copying the builder Markdown does not install the CLI.

## Public boundary and validation

Source inspection does not execute third-party code or copy algorithm source or user data. The text boundary scanner detects selected credential patterns and publication hazards; it is a heuristic, not a proof that arbitrary content is safe to publish. Binary files are not text-scanned. The package/import pipeline rejects invalid contracts and detected boundary problems; unresolved scaffolds can be transferred with their status preserved.

Algorithm execution requires a separately reviewed environment and implementation. Product authentication, filesystem isolation, resource limits and account permissions remain active. See [security model](docs/security-model.md), [public/private boundary](docs/public-private-boundary.md), [manifest reference](docs/manifest-reference.md) and [workflow](docs/workflow.md).

Run the offline regression suite after installing dependencies:

```bash
python -m unittest discover -s tests -v
ohf boundary-scan .
```

The suite builds and installs a wheel in a separate environment, exercises imported resources from outside the source checkout, and checks schema failures, conflict/backup recovery and deterministic archives. These are kit tests, not a claim of production Omicos integration or scientific equivalence of an algorithm.

## Version and license

The public contract is versioned independently from receiving products. See [CONTRACT_VERSIONING.md](CONTRACT_VERSIONING.md). The kit's original code/templates use Apache-2.0; algorithm licensing and attribution remain separate. See [LICENSE_POLICY.md](LICENSE_POLICY.md).
