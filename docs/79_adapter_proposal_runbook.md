# Adapter Proposal Generator Runbook

## What changed
Proposal generation now depends on adapter semantics rather than generic `R_diag`-only adjustments.

## Operator expectations
- Proposal notes should mention the generator that was used.
- RAG proposals should mention freshness/conflict/stale-answer pressure.
- Routing proposals should mention promotion pressure.
- Agent proposals should mention escalation pressure.

## Validation path
Always run `propose -> validate` before adoption. Do not auto-adopt suggest_only profiles.
