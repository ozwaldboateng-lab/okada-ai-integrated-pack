# Codegen Prompt: Integrated Stack Expansion

Use this repository as the source of truth. Extend it without breaking existing interfaces.

## Immediate tasks
1. Preserve the Okada Kernel API contracts.
2. Keep `registry/*.yaml` and `api/*.yaml` as source-of-truth references.
3. Expand the integrated compose stack with real service-level wiring.
4. Keep Dify linkage external/manual unless the implementation includes the full official dependency stack.
5. Do not delete benchmark harness assets.
6. Add real environment validation and graceful failures.

## Deliverables
- improved compose files
- stronger LiteLLM integration
- Open WebUI operator pages or manifests
- benchmark harness expansions
- additional regression tests

## Constraints
- do not remove audit trace generation
- do not collapse Okada features into opaque heuristics
- keep deterministic mode available
- keep baseline-vs-Okada comparison executable
