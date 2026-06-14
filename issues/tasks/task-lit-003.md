# TASK-LIT-003: Unify LiteLLM compose and root compose references

- **Epic:** EPIC-002
- **Priority:** p2
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** litellm, ops, parallel-safe
- **Depends on:** none

## Problem
Compose files and runbooks mention overlapping but not fully aligned LiteLLM startup paths.

## Expected deliverable
One consistent documented path from local-only LiteLLM to integrated stack.

## Files/areas in scope
- `ops/litellm/`
- `ops/integrated/`
- `docker-compose.yml`
- `docs/`

## Acceptance criteria
- [ ] runbook references one preferred path
- [ ] compose files cross-reference clearly
- [ ] env files point to matching variable names

## Verification commands
```bash
python scripts/dev_status.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
