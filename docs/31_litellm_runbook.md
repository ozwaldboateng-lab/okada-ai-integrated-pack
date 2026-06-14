# 31. LiteLLM Runbook

## Local run order
Use this path for LiteLLM-only callback work. For the operator-visible stack,
use the preferred integrated compose path in `docs/47_integrated_runbook.md`:
`ops/integrated/docker-compose.kernel-gateway-ui.yml`.

1. Copy `ops/litellm/.env.example` to `.env` in the same directory and fill values.
2. Start the kernel service.
3. Run `python scripts/litellm_preflight.py`.
4. Render config with `python scripts/render_litellm_config.py --template examples/litellm/proxy_config.template.yaml --route-map examples/litellm/route_map.json --output /tmp/litellm.config.yaml`.
5. Start LiteLLM using the rendered config.
6. Send a request with metadata.

## Compose paths
- Local-only LiteLLM: `ops/litellm/docker-compose.litellm.yml`
- Preferred integrated stack: `ops/integrated/docker-compose.kernel-gateway-ui.yml`
- Legacy compatibility template: `ops/docker-compose.integration.yml`

Both active compose paths use `OKADA_BASE_URL`, `OKADA_SHARED_TOKEN`,
`OKADA_ROUTE_MAP_PATH`, `CHEAP_MODEL_NAME`, and `STRONG_MODEL_NAME`.

## Minimal smoke request requirements
The request should include a `metadata` object with at least:
- `complexity_proxy`
- `budget_remaining`
- `historical_route_success`

## Expected first success signal
- LiteLLM returns a model response.
- Request metadata is enriched with `okada_*` keys.
- Kernel audit store receives an audit record.

## First things to inspect if routing looks wrong
- route map JSON
- metadata values actually present at request time
- kernel `/healthz`
- gateway `/integrations/litellm/pre-route` response for the same payload


## Import path note
Set `PYTHONPATH` so the callback can import `app.*` from `apps/okada-kernel-service`.
