# LiteLLM Example (Gateway Unified)

This example calls only integration-gateway endpoints:
- `POST /integrations/litellm/pre-route`
- `POST /integrations/litellm/post-audit`

The LiteLLM-side glue no longer builds canonical kernel payloads.
The gateway owns translation, routing policy application, and audit payload construction.

## Local Runnable Path

Start the Okada kernel:

```bash
uvicorn app.main:app --app-dir apps/okada-kernel-service --reload --port 8080
```

Set the LiteLLM integration environment:

```bash
OKADA_BASE_URL=http://localhost:8080
OKADA_SHARED_TOKEN=change-me
OKADA_POLICY_PROFILE=default
OKADA_DETERMINISTIC_MODE=true
OKADA_ROUTE_MAP_PATH=examples/litellm/route_map.json
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_KEY=replace-me
LITELLM_MASTER_KEY=replace-me
CHEAP_MODEL_NAME=openai/gpt-4o-mini
STRONG_MODEL_NAME=openai/gpt-4.1
```

Run preflight:

```bash
python scripts/litellm_preflight.py
```

The preflight checks required environment variables, kernel health, route map
loading, and a gateway smoke flow that calls both `pre-route` and `post-audit`.

## Route Map

`OKADA_ROUTE_MAP_PATH` points to a JSON object keyed by Okada recommended action.
Each entry can set:

- `target_model`
- `strategy`

If `OKADA_ROUTE_MAP_PATH` is not set, the gateway uses the in-code default route
map from `app.integrations.litellm_runtime`.

## Demo Route Matrix

`route_matrix.json` contains LiteLLM-style payloads with expected routing
outcomes:

- `cheap_route`
- `bounded_hybrid`
- `promote_strong_model`

Run the acceptance smoke:

```bash
python scripts/integration_demo.py
```

The script calls `/integrations/litellm/pre-route` for each matrix row and
checks the expected action, selected model, and audit trace id.
