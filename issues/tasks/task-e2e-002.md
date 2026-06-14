# TASK-E2E-002: Automate baseline-vs-okada benchmark report generation

- **Epic:** EPIC-006
- **Priority:** p1
- **Status:** ready
- **Suggested owner:** shared
- **Labels:** benchmark, tests, serial
- **Depends on:** TASK-E2E-001, TASK-LIT-001, TASK-DIFY-001, TASK-LANG-001, TASK-OWUI-001

## Problem
Benchmark comparison exists, but report generation should be more turnkey and tied to fixtures and outputs.

## Expected deliverable
One command that emits a reproducible benchmark summary artifact.

## Files/areas in scope
- `scripts/e2e_compare.py`
- `apps/okada-kernel-service/app/benchmark/`
- `data/benchmarks/`
- `docs/54_e2e_reporting.md`

## Acceptance criteria
- [ ] command writes output file under data/benchmarks or similar
- [ ] docs show command and output location
- [ ] fixture path resolution is robust

## Verification commands
```bash
python scripts/e2e_compare.py --pretty
```

## Notes to agent
- Keep the change set scoped to this task.
- Preserve source-of-truth alignment with specs and docs.
- Update tests and docs if behavior changes.
