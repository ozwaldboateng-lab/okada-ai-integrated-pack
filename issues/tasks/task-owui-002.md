# TASK-OWUI-002: Add manual evaluation and audit-view workflow for Open WebUI

- **Epic:** EPIC-005
- **Priority:** p2
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** openwebui, docs, serial
- **Depends on:** TASK-OWUI-001

## Problem
There is no single operator workflow that covers route-aware usage plus audit inspection.

## Expected deliverable
A manual evaluation workflow with expected artifacts.

## Files/areas in scope
- `docs/`
- `examples/openwebui/`
- `fixtures/e2e/`

## Acceptance criteria
- [ ] workflow names expected screens/artifacts
- [ ] links to audit outputs
- [ ] includes at least one routing and one RAG case

## Verification commands
```bash
python scripts/openwebui_preflight.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
