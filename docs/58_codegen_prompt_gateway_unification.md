# Codegen Prompt: Gateway Unification

Refactor OSS integration examples so they call only integration-gateway endpoints.
Do not call `/okada/diagnose`, `/okada/route`, `/okada/intervene`, or `/okada/audit` directly from example glue code.
Use `OkadaGatewayClient` and keep fail-safe defaults local.
