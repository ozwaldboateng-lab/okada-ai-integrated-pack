# CLAUDE.md

This repository contains a specification-driven implementation scaffold for the **Okada Governance Kernel**.
Read this file before making changes.

## Mission
Implement an external governance kernel that can be attached to existing AI application stacks.
The kernel should diagnose and intervene using the Okada decomposition rather than opaque heuristics.

## Read first
Start with these files in order:
1. `README.md`
2. `AGENTS.md`
3. `docs/61_dual_standalone_usage.md`
4. `specs/okada-ai-spec/registry/spec_registry.yaml`
5. `specs/okada-ai-spec/registry/core/okd-ai-core-001.yaml`
6. `docs/46_integrated_stack_overview.md`
7. `docs/51_integration_gateway.md`
8. relevant adapter YAML under `specs/okada-ai-spec/registry/adapters/`

## Repository working style
- Treat YAML registry files as source-of-truth.
- Treat examples as integration templates, not authoritative behavior.
- Preserve auditability at every layer.
- Prefer explicit interfaces over implicit coupling.
- Keep OSS-specific glue code minimal; centralize policy in the gateway/kernel.

## Important operating assumption
This repo is being used in **standalone comparison mode**.
You are not coordinating with another agent in the same working tree.
Your job is to complete the requested task cleanly inside your own copy.

Do not assume branch-sharing, worktree coordination, or subsystem division unless explicitly asked.

## Current implementation state
The repo already includes:
- FastAPI kernel service skeleton
- integration gateway endpoints
- LiteLLM / Dify / LangGraph / Open WebUI examples
- tests and fixtures
- E2E comparison harness

The repo does **not** yet represent a fully calibrated production system.
Thresholds, weights, and benchmark coverage still need refinement.

## Priority work
Choose tasks that move the system toward one of these:
- stronger API/schema fidelity
- more realistic adapter behavior
- more complete gateway integrations
- better baseline-vs-Okada benchmark coverage
- improved operator/audit workflows

## Do not do these by default
- rename major public files or directories
- remove decomposition fields from responses
- flatten all adapters into one monolithic decision function
- convert everything into one notebook or one giant markdown file
- add infrastructure complexity without a direct benchmark or integration payoff

## Testing expectation
For code changes, run relevant tests. At minimum, prefer:
```bash
pytest apps/okada-kernel-service/tests -q
```
For behavior that affects benchmark logic, also run:
```bash
python scripts/e2e_compare.py --pretty
```

## Output expectation
When handing back work, state:
- changed files
- design impact
- tests run
- remaining uncertainties
