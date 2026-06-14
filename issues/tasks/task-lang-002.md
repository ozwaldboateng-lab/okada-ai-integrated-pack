# TASK-LANG-002: Add governed-agent resume demo with interrupt outcomes

- **Epic:** EPIC-004
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** langgraph, serial, tests
- **Depends on:** TASK-LANG-001

## Problem
The repo should show a concrete resume path after interrupt for at least approve, edit, and abort outcomes.

## Expected deliverable
A resume-capable demo walkthrough and supporting code/example updates.

## Files/areas in scope
- `examples/langgraph/`
- `docs/`
- `fixtures/e2e/agent_cases.jsonl`

## Acceptance criteria
- [ ] approve/edit/abort are all represented
- [ ] runbook shows where thread_id is supplied
- [ ] audit path is described

## Verification commands
```bash
python scripts/langgraph_preflight.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
