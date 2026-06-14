# Gateway Migration Runbook

Goal: remove direct `/okada/*` calls from example glue code.

Checklist:
1. Replace direct kernel HTTP calls with `OkadaGatewayClient`.
2. Send `IntegrationPayload` shape: `{payload, options}`.
3. Read `IntegrationResponse.transformed_payload`.
4. Read `IntegrationResponse.audit_payload` when present.
5. Keep local fail-safe defaults for missing gateway output.
