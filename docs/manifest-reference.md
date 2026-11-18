# Public manifest and validation reference

`harness-manifest.json` follows the bundled/public Draft 2020-12 [schema](../schemas/harness-manifest.schema.json). The CLI uses its installed package resources, so validation does not depend on a checkout-relative schemas directory or network retrieval.

## Fields

| Field | Contract |
|---|---|
| `manifest_version`, `contract_version` | Supported value `1.0`; unsupported versions are rejected. |
| `kit_version` | Version that generated the bundle. |
| `layout` | `bundle` before import; `skill` for the self-contained installed directory. Older bundles without this field use `bundle`. |
| `id`, `name` | Public identity and skill name. Names contain 1-64 lowercase letters, digits, underscores or hyphens and start with a letter. |
| `source` | Public source URL, owner/repository, ref, pinned commit and license evidence. |
| `entrypoint` | `UNRESOLVED`, `command`, or `python_module`; contract metadata never causes automatic execution. |
| `contracts` | Request/result/reproducibility schema paths, all confined to the skill directory. Bundle paths are root-relative; installed paths are skill-relative. |
| `execution` | Dry-run/reviewed mode, network policy, review status, and optional declared resource limits and review evidence. `production_deployed` is always false for public bundles. |
| `provenance` | The kit does not copy source or user data. Archive/install receipts supply actual file digests; a nullable legacy digest is not treated as verified evidence. |
| `unresolved` | Explicit list of remaining decisions. Allowed in a valid scaffold, blocks runtime readiness. |

Referenced schemas must be Draft 2020-12 JSON objects. Only local JSON-pointer references are supported; external/remote references are rejected so validation stays offline. Validate payloads with `ohf validate BUNDLE --request REQUEST.json --result RESULT.json`.

## Readiness requirements

`scaffold_valid` checks structure, schema definitions, resources, safe YAML metadata and the boundary scanner. A default generated bundle can pass while remaining entirely unimplemented.

`runtime_ready` additionally requires:

- `execution.mode = reviewed` and `execution.source_execution = reviewed`;
- a pinned source commit and confirmed license evidence;
- a nonempty command or valid Python module declaration;
- no `unresolved` entries;
- positive `execution.resource_limits.cpu_seconds`, `memory_mb`, and `wall_seconds`;
- `execution.validation` with `environment`, `tested_at` (date-time), and `evidence_path` referencing a nonempty file inside the skill directory.

This is **declared contract and recorded evidence readiness**, not independent verification of that evidence. The validator does not import the algorithm, run its command, prove numerical correctness, authorize a subscription or confirm live product integration. `integration_verified` remains false. A product integration test must produce its own evidence.

## Digests

Package receipts include `files_sha256` (relative path to content SHA-256), `content_sha256` (SHA-256 of the UTF-8 canonical JSON of that map with sorted keys and compact separators), and `archive_sha256` (SHA-256 of the actual archive bytes). Tar ownership/timestamps and gzip timestamps/filename are normalized; executable versus non-executable file modes are preserved in canonical form. Reproducible archive bytes assume the same file contents, executable flags and Python/compression toolchain; the content-set digest remains independent of tar/gzip metadata.

Install receipts use the same file/content digest definition. `installation-receipt.json` is excluded from its own digest map to avoid a circular checksum. Absolute destination/backup paths are printed as local operation results and are not copied into public bundle manifests.
