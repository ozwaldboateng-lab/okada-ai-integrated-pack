# Implementation Rules

- Registry YAML is the source of truth.
- OpenAPI and JSON Schema define request/response validity.
- Markdown docs explain intent but do not override YAML.
- Deterministic mode must be supported for benchmark reproducibility.
- All adapters must expose the same internal contract.
- Every response must contain `audit_trace_id`.
- Every persisted audit record must contain raw + normalized + derived + decision.
