# TASK-KERNEL-002: Add policy parameter registry and environment-backed overrides

- **Epic:** EPIC-001
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** kernel, ops, parallel-safe, good-first-task
- **Depends on:** none

## Problem
Threshold names exist in specs but not as a central runtime registry.

## Expected deliverable
A single policy parameter registry loaded from defaults plus environment overrides.

## Files/areas in scope
- `apps/okada-kernel-service/app/config/`
- `apps/okada-kernel-service/app/core/`
- `ops/`

## Acceptance criteria
- [ ] policy defaults live in one module/file
- [ ] env vars can override selected thresholds
- [ ] integration routes read policy through the registry
- [ ] docs add a threshold override example

## Verification commands
```bash
cd apps/okada-kernel-service && pytest tests/test_api.py -q
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
