# Lab-aware Validation Runbook

## Recommended flow
1. generate proposal from recent window
2. validate on recent window
3. if available, replay a stable fixture suite using `run_calibration_lab=true`
4. only promote/adopt if both:
   - online/recent window gate passes
   - calibration lab gate passes

## Good defaults
- routing: enable lab replay on every guarded proposal
- rag: enable lab replay on shadow challenger evaluation
- monitoring/drift: use lab replay only after a baseline fixture suite exists
- agent: use lab replay selectively until richer suites are available

## Failure handling
If lab replay is negative:
- keep proposal for inspection
- do not auto-adopt
- attach lab report to review ticket
