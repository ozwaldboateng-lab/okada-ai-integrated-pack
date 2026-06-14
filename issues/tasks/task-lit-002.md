# TASK-LIT-002: Add LiteLLM demo route matrix and acceptance smoke

- **Epic:** EPIC-002
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** litellm, tests, serial
- **Depends on:** TASK-LIT-001

## Problem
There is no issue-sized acceptance script proving multiple routing outcomes under LiteLLM-style metadata.

## Expected deliverable
A small route matrix demo with expected outcomes and instructions.

## Files/areas in scope
- `examples/litellm/`
- `fixtures/e2e/`
- `docs/`

## Acceptance criteria
- [ ] at least three route outcomes demonstrated
- [ ] expected route stored in fixture or docs
- [ ] smoke command documented
- [ ] results are auditable

## Verification commands
```bash
python scripts/integration_demo.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
