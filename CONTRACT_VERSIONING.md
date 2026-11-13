# Public contract versioning

The public bridge contract is intentionally small and implementation-neutral. It describes what an adapter receives and returns; it does not describe the private Omicos runtime.

## Compatibility rules

- `schema_version` uses a major/minor form such as `1.0`.
- A patch release may clarify wording or tighten validation without changing valid payload meaning.
- A minor release may add optional fields.
- A major release may remove or change fields and requires an explicit migration note.
- Generated manifests must record the contract version and the kit version.

Private deployments may reject a bundle whose contract version they do not recognize. A generated bundle must never claim production compatibility solely because its JSON validates.
