# TASK-LIT-001: Wire LiteLLM callback to the integration gateway in runnable local mode

- **Epic:** EPIC-002
- **Priority:** p0
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** litellm, integration-gateway, parallel-safe
- **Depends on:** none

## Problem
LiteLLM examples are close but still template-heavy. A local runnable path should be explicit.

## Expected deliverable
A documented runnable LiteLLM callback path using the integration gateway endpoints.

## Files/areas in scope
- `examples/litellm/`
- `apps/okada-kernel-service/app/integrations/`
- `ops/litellm/`

## Acceptance criteria
- [ ] callback reads gateway base URL from env
- [ ] pre-route and post-audit both exercised in smoke flow
- [ ] route map loading is documented
- [ ] preflight script verifies missing env clearly

## Verification commands
```bash
python scripts/litellm_preflight.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
