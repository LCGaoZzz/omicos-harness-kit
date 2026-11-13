# Public/private boundary

## Public repository

The public repository may publish:

- an implementation-neutral bridge contract;
- a generator that creates a scaffold from a public algorithm URL;
- a validator and provenance recorder;
- generic agent and skill templates;
- synthetic examples and documentation;
- a local installer that copies the generated bundle into a user-selected workspace.

## Private Omicos deployment

The private side decides whether a bundle is admitted, which runtime executes it, how agents are scheduled, which MCP tools are exposed, and whether production deployment is allowed. Those implementation details are intentionally not represented in this repository.

## Generated bundle boundary

A generated bundle may contain the public URL, a pinned commit, license evidence, schemas, a reviewed command or module reference, and adapter-level limitations. It must not contain the algorithm source, user data, secrets, private paths, or internal deployment instructions.

## Why the URL is not enough

A GitHub URL can identify a source project. It cannot prove its accepted file formats, semantic assumptions, reproducibility, numerical stability, or license compatibility. The generated manifest therefore starts with `UNRESOLVED` fields and requires evidence before execution.
