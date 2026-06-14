# TASK-DOC-001: Refresh operator-facing walkthrough after unified gateway migration

- **Epic:** EPIC-006
- **Priority:** p2
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** docs, parallel-safe, good-first-task
- **Depends on:** none

## Problem
User-facing walkthroughs need one coherent narrative after gateway unification.

## Expected deliverable
A refreshed operator/demo walkthrough referencing the preferred startup path.

## Files/areas in scope
- `docs/53_operator_demo_flow.md`
- `docs/55_gateway_unified_examples.md`
- `docs/59_dual_agent_handoff.md`
- `README.md`

## Acceptance criteria
- [ ] one start-here narrative exists
- [ ] operator steps reference current files
- [ ] README points to it

## Verification commands
```bash
python scripts/dev_status.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
