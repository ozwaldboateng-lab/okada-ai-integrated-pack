# TASK-OWUI-001: Package Open WebUI pipe and filter as operator-ready artifacts

- **Epic:** EPIC-005
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** openwebui, parallel-safe
- **Depends on:** none

## Problem
Open WebUI examples exist but operator packaging is still loose.

## Expected deliverable
A packaged pair of pipe/filter artifacts with environment and install notes.

## Files/areas in scope
- `examples/openwebui/`
- `docs/`
- `ops/openwebui/`

## Acceptance criteria
- [ ] pipe/filter env vars are documented
- [ ] README gives installation order
- [ ] operator console contract points to the packaged artifacts

## Verification commands
```bash
python scripts/openwebui_preflight.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
