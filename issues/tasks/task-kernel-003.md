# TASK-KERNEL-003: Promote audit storage from JSONL-only bootstrap to pluggable backend contract

- **Epic:** EPIC-001
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** kernel, audit, parallel-safe
- **Depends on:** none

## Problem
Current JSONL audit storage is acceptable for local development but too thin as the only contract.

## Expected deliverable
A backend interface with JSONL implementation and a documented path for future DB-backed storage.

## Files/areas in scope
- `apps/okada-kernel-service/app/audit/`
- `apps/okada-kernel-service/tests/`
- `docs/`

## Acceptance criteria
- [ ] audit store has explicit backend interface
- [ ] JSONL backend remains default
- [ ] tests cover write/read semantics through the interface
- [ ] docs explain backend swap points

## Verification commands
```bash
cd apps/okada-kernel-service && pytest tests/test_audit.py -q
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
