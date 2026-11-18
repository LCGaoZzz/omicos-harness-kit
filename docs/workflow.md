# Review, install and verify workflow

1. Confirm the active execution environment and workspace. Check `ohf --version` there. A local installation is not a remote installation.
2. Run `ohf inspect URL --output PLAN.json`. This creates a plan; the agent/human must read public algorithm documentation and record actual evidence.
3. Run `ohf init --repo URL --name NAME --output BUNDLE`. Use an explicit output path and preserve unresolved assumptions.
4. Complete the manifest and references from evidence. Implement and separately test a real adapter before claiming that the algorithm runs. The generated script remains a dry-run example.
5. Run `ohf validate BUNDLE`, and supply `--request`/`--result` for payload validation. Read all three readiness fields, not only `ok`.
6. Run `ohf install BUNDLE --workspace WORKSPACE`. The workspace may already contain data and other skills. The installer maps the complete skill subtree, rebases the local manifest and reports the exact destination. Agent templates remain uninstalled.
7. Refresh skills in the receiving product at that same workspace. Check parse diagnostics, account capability, local/remote filesystem identity and resource access if it does not appear. The CLI does not mark discovery as verified.
8. Perform a product-level test: discover the skill, read a resource, run the reviewed entrypoint through authorized tools, validate its result and confirm the output artifact. Record the deployed product version. A successful dry-run is only a contract check.

For replacement use `--replace`; the returned backup can be restored with `ohf install BACKUP --workspace WORKSPACE --replace`. For transferring drafts, use `ohf package BUNDLE --output ARCHIVE.tar.gz`. For processes requiring completed runtime declarations, append `--require-runtime-ready` to validate/package/install.
