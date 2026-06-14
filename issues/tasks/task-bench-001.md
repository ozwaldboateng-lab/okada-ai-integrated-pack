# TASK-BENCH-001: Expand E2E fixtures beyond current happy-path utility wins

- **Epic:** EPIC-006
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** benchmark, parallel-safe
- **Depends on:** none

## Problem
Current E2E fixtures are intentionally small and favorable; stress and near-failure cases are underrepresented.

## Expected deliverable
A broader fixture pack including borderline and adverse cases.

## Files/areas in scope
- `fixtures/e2e/`
- `data/benchmarks/`
- `docs/48_e2e_benchmark_harness.md`

## Acceptance criteria
- [ ] new cases cover ambiguous routing, stale RAG, and agent derailment
- [ ] docs mention case families
- [ ] summary can still be generated

## Verification commands
```bash
python scripts/e2e_compare.py --pretty
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
