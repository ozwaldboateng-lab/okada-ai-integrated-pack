# TASK-QA-001: Add kernel acceptance scenarios for first-wave adapters

- **Epic:** EPIC-001
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** tests, kernel, parallel-safe
- **Depends on:** TASK-KERNEL-001

## Problem
Unit tests exist, but issue-ready acceptance scenarios per adapter are thin.

## Expected deliverable
Acceptance-style fixture-driven tests for monitoring, drift, agent, rag, and routing adapters.

## Files/areas in scope
- `apps/okada-kernel-service/tests/`
- `fixtures/`

## Acceptance criteria
- [ ] fixture files expanded or added as needed
- [ ] at least one acceptance scenario per first-wave adapter
- [ ] test output remains deterministic
- [ ] README or docs point to acceptance command

## Verification commands
```bash
cd apps/okada-kernel-service && pytest -q
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
