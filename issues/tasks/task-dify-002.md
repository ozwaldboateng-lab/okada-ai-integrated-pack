# TASK-DIFY-002: Add Dify live RAG demo walkthrough and expected decision matrix

- **Epic:** EPIC-003
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** dify, docs, serial
- **Depends on:** TASK-DIFY-001

## Problem
The operator path for demonstrating clean/mixed/contaminated retrieval decisions is not yet one compact walkthrough.

## Expected deliverable
A demo walkthrough with expected decision outcomes per case.

## Files/areas in scope
- `docs/`
- `examples/dify/`
- `fixtures/e2e/rag_cases.jsonl`

## Acceptance criteria
- [ ] at least one clean, one mixed, one contaminated RAG case documented
- [ ] operator steps are numbered
- [ ] acceptance matrix links to fixtures

## Verification commands
```bash
python scripts/e2e_compare.py --pretty
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
