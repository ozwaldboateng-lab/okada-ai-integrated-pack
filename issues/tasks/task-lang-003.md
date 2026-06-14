# TASK-LANG-003: Expand LangGraph acceptance matrix for route contamination patterns

- **Epic:** EPIC-004
- **Priority:** p2
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** langgraph, tests, parallel-safe
- **Depends on:** none

## Problem
Agent contamination patterns need a clearer acceptance table tied to fixtures.

## Expected deliverable
Expanded acceptance matrix and matching tests/fixtures.

## Files/areas in scope
- `docs/40_langgraph_acceptance_matrix.md`
- `fixtures/e2e/agent_cases.jsonl`
- `apps/okada-kernel-service/tests/`

## Acceptance criteria
- [ ] matrix references fixture ids
- [ ] at least one type-I/II/III-flavored case exists conceptually
- [ ] tests cover expected actions

## Verification commands
```bash
cd apps/okada-kernel-service && pytest tests/test_langgraph_runtime.py -q
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
