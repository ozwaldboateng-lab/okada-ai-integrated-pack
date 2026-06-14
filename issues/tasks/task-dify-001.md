# TASK-DIFY-001: Convert Dify HTTP request and code-node examples into a gateway-first import pack

- **Epic:** EPIC-003
- **Priority:** p0
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** dify, integration-gateway, parallel-safe
- **Depends on:** none

## Problem
Dify examples exist, but a user still has to infer how they fit together as an importable gateway-first workflow.

## Expected deliverable
A self-contained Dify import pack with pre/post retrieval payloads and code-node transforms.

## Files/areas in scope
- `examples/dify/`
- `apps/okada-kernel-service/app/integrations/`
- `docs/`

## Acceptance criteria
- [ ] import manifest references gateway endpoints only
- [ ] workflow variables doc aligns with payload JSON files
- [ ] fail-safe branch contract is explicit
- [ ] runbook gives an import order

## Verification commands
```bash
python scripts/dify_preflight.py
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
