# TASK-KERNEL-001: Stabilize core scoring and normalization contracts

- **Epic:** EPIC-001
- **Priority:** p0
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** kernel, tests, parallel-safe
- **Depends on:** none

## Problem
Current scoring and normalization are bootstrap-grade placeholders. Runtime integrations need deterministic and adapter-aware scoring semantics.

## Expected deliverable
Adapter-aware normalization helpers and stable score contracts with tests.

## Files/areas in scope
- `apps/okada-kernel-service/app/core/`
- `apps/okada-kernel-service/app/adapters/`
- `apps/okada-kernel-service/tests/`

## Acceptance criteria
- [ ] core scoring functions have explicit typed helper APIs
- [ ] each first-wave adapter has a normalization function
- [ ] tests cover clean/mixed/contaminated boundary behavior per adapter
- [ ] docs mention the calibrated placeholders still requiring empirical tuning

## Verification commands
```bash
cd apps/okada-kernel-service && pytest tests/test_adapters.py tests/test_api.py -q
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
