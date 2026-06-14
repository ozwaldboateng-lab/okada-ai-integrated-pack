# TASK-LANG-001: Stabilize LangGraph step middleware contract around gateway endpoints

- **Epic:** EPIC-004
- **Priority:** p0
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** langgraph, integration-gateway, parallel-safe
- **Depends on:** none

## Problem
LangGraph support is substantial but still needs one stable middleware contract that others can extend.

## Expected deliverable
A gateway-first LangGraph middleware contract for step and human-review calls.

## Files/areas in scope
- `examples/langgraph/`
- `apps/okada-kernel-service/app/integrations/`
- `docs/`

## Acceptance criteria
- [ ] state schema is referenced consistently
- [ ] step call payload is documented
- [ ] human review payload is documented
- [ ] thread/checkpoint requirements are explicit

## Verification commands
```bash
python scripts/langgraph_preflight.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
