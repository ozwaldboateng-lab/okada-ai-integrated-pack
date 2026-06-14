# Code Generation Instructions

## Goal
Generate implementation skeletons for `okada-governance-service` based on the structured spec pack.

## Read order
1. `registry/spec_registry.yaml`
2. `registry/core/okd-ai-core-001.yaml`
3. `registry/adapters/*.yaml`
4. `api/okada-governance.openapi.yaml`
5. `schemas/*.json`
6. `docs/20_codegen_handoff.md`

## Required outputs
- API server skeleton
- adapter abstraction layer
- monitoring / drift / agent / rag / routing adapter stubs
- audit persistence layer
- test skeleton loading fixtures

## Constraints
- Do not invent new endpoints.
- Do not remove audit logging.
- Do not hard-code thresholds that appear as `T_*` identifiers.
- Use config or policy profile for tunable parameters.
- Keep domain-specific meaning inside adapters, not inside the shared kernel.
