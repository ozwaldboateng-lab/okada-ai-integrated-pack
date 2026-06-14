# TASK-DIFY-003: Package Dify fail-safe behavior for offline or gateway-error mode

- **Epic:** EPIC-003
- **Priority:** p2
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** dify, parallel-safe, good-first-task
- **Depends on:** none

## Problem
Gateway failure handling exists conceptually but needs a cleaner packaged contract for Dify workflow authors.

## Expected deliverable
A fail-safe packaging note plus example variables/branches.

## Files/areas in scope
- `examples/dify/`
- `apps/okada-kernel-service/app/integrations/`
- `docs/`

## Acceptance criteria
- [ ] fallback variables documented
- [ ] code-node transform includes fallback example
- [ ] runbook mentions offline behavior

## Verification commands
```bash
python scripts/dify_preflight.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
