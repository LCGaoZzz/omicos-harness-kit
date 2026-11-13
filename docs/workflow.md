# Recommended workflow

1. **Inspect** the public repository without executing it. Record the public URL and the evidence needed to resolve the contract.
2. **Generate** the scaffold with `ohf init`.
3. **Review** the manifest, license, entry point, input/output contract, resource profile, and scientific limitations.
4. **Fill** only fields supported by public documentation or a reproducible test record.
5. **Validate** the bundle and boundary scan. A valid JSON file is not a scientific validation.
6. **Optionally smoke-test** in an isolated, network-disabled environment after explicit authorization.
7. **Package** the bundle and transfer it to an authorized private Omicos workspace. The public kit cannot mark a production deployment complete.
