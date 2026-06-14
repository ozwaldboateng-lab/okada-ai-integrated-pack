# TASK-E2E-001: Make integrated compose bring-up path consistent and reproducible

- **Epic:** EPIC-006
- **Priority:** p0
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** ops, integration-gateway, serial
- **Depends on:** none

## Problem
There are several startup paths; one reproducible integrated bring-up path should be designated as preferred.

## Expected deliverable
A single preferred integrated startup path with explicit prerequisites.

## Files/areas in scope
- `ops/integrated/`
- `docs/47_integrated_runbook.md`
- `docker-compose.yml`
- `.env.example`

## Acceptance criteria
- [ ] one compose path marked preferred
- [ ] runbook and env examples match
- [ ] preflight script references the same path

## Verification commands
```bash
python scripts/e2e_stack_preflight.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
