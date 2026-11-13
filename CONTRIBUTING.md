# Contributing

Contributions should improve the public compiler, neutral contracts, security guardrails, documentation, or test coverage.

Do not submit private Omicos runtime code, internal catalog entries, proprietary prompts, private MCP schemas, credentials, private paths, user data, or copied third-party algorithm source.

Before opening a pull request:

```bash
python -m compileall -q src
python -m unittest discover -s tests -v
python -m ohf boundary-scan .
```

Keep generated examples synthetic and small. If a proposed feature depends on a private deployment detail, describe the public interface it needs instead of publishing the private implementation.
