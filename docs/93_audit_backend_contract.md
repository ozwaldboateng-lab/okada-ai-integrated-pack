# Audit Backend Contract

The runtime audit store uses a small backend interface so local JSONL storage can
remain the default while production deployments can add a database-backed
implementation later.

## Default Backend

Set:

```bash
OKADA_AUDIT_BACKEND=jsonl
OKADA_AUDIT_DIR=./data/audit
```

The JSONL backend writes `audit_records.jsonl` under `OKADA_AUDIT_DIR`.

## Swap Point

Audit backends implement:

- `write(record: AuditRecord) -> AuditRecord`
- `list_records() -> list[AuditRecord]`

`app.audit.store.AuditStore` delegates to that backend. Future database-backed
storage should add a backend implementation and register it in
`build_audit_backend()` without changing kernel service call sites.

## Required Semantics

- `write` must persist the complete `AuditRecord` payload.
- `list_records` must return records as `AuditRecord` models.
- Returned records must preserve `audit_trace_id`, raw inputs, normalized inputs,
  derived features, decision fields, alternatives, and policy snapshot.
- The backend must not drop the Okada decomposition fields `H_dom`, `H_hist`, and
  `H_comp` when present.
