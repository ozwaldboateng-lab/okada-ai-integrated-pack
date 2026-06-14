# 33. Codegen Prompt: LiteLLM First Real Integration

Use the existing repository as the source of truth.
Implement the LiteLLM integration first.
Do not redesign the project.
Work within the current structure.

## Tasks
1. Keep `apps/okada-kernel-service` as the service boundary.
2. Preserve `examples/litellm/okada_custom_handler.py` as the entrypoint callback.
3. Use `app.integrations.litellm_runtime` for all pure routing/audit helper logic.
4. Do not hardcode model names in the callback; load them via route map/config.
5. Add tests before changing behavior.
6. Keep route decisions auditable.

## Deliverables
- callback handler
- route map loader
- config rendering script
- preflight script
- tests
- minimal runbook update
