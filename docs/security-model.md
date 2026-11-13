# Security model

The kit uses four simple controls:

1. **No implicit execution.** URL inspection never runs third-party code.
2. **No implicit copying.** A generated bundle records source identity but does not copy source or user data.
3. **Workspace confinement.** Contracts declare input and output paths; private deployment adds its own stronger sandbox.
4. **Fail-closed review.** Secrets, private paths, missing license evidence, and unresolved entry points remain visible and block public packaging until reviewed.

The controls are guardrails. The private Omicos deployment must still enforce its own authentication, isolation, resource limits, and admission review.
