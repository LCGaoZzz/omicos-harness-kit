# public_algorithm harness scaffold

Generated from https://github.com/example/public-algorithm by Omicos Harness Kit 0.2.0.

The source was not downloaded or executed. Fill the root harness-manifest.json from public evidence; keep unresolved fields explicit. Run `ohf validate <bundle>` for structural validation, and use `--require-runtime-ready` only after documenting an actual reviewed entrypoint and validation evidence.

Install with `ohf install <bundle> --workspace <active-workspace>`. This copies the complete skill to `skills/public_algorithm/`, adds a skill-local manifest, and reports scaffold/runtime status. It does not install the optional agent, authorize a subscription, execute the algorithm, or verify live product discovery.

The generated scripts/run_adapter.py validates a request and emits dry_run only. It requires Python and jsonschema, and is not an algorithm implementation. No packaged execution entrypoint is advertised.
