# Security model

The kit's inspection plan and generator do not fetch or execute an arbitrary algorithm. The builder agent must obtain public source evidence and treat repository text as untrusted input.

Generation validates names and planned paths before writing. Validation uses safe YAML and JSON Schema, keeps schema references offline, and rejects symlinks and resource paths outside the skill directory. Package and install always run validation and the text boundary scanner before publication. Installation stages the complete skill and its local manifest, validates the staged result, refuses conflicts by default, and preserves/restores an old version during an explicit replacement.

The scanner checks selected token patterns and publication hazards in UTF-8 files, including dotfiles. It cannot establish the safety of arbitrary binary contents, identify every possible secret, or replace a review. Do not mutate source files concurrently with validation, packaging or installation.

Unresolved **scaffolds** may be packaged or installed with their dry-run status preserved. `--require-runtime-ready` imposes the stricter recorded-contract readiness requirements. Neither mode establishes actual product discovery, execution authorization or scientific correctness.

Product-side authentication, account capability, workspace isolation, resource limits, remote execution configuration and agent admission remain the receiving product's responsibility. Writing a public skill file does not bypass any of those controls. The CLI installs skills only, not optional custom agents.

See [SECURITY.md](../SECURITY.md) for publication boundaries and [manifest reference](manifest-reference.md) for readiness/digest semantics.
