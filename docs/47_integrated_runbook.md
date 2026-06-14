# Integrated Runbook (v1.0)

## Purpose
Bring up the first operational path:

1. Okada Kernel Service
2. LiteLLM Proxy
3. Open WebUI
4. Optional Dify linkage
5. Optional LangGraph linkage
6. E2E harness validation

Preferred compose path:

```bash
ops/integrated/docker-compose.kernel-gateway-ui.yml
```

LiteLLM-only callback development can still use
`ops/litellm/docker-compose.litellm.yml`, but this runbook treats the
integrated compose file above as the single preferred operator-visible path.
`ops/docker-compose.integration.yml` is retained only as a legacy compatibility
template.

## 1. Prepare environment
Copy environment examples:

```bash
cp .env.example .env
cp ops/integrated/.env.example ops/integrated/.env
cp ops/openwebui/.env.example ops/openwebui/.env
```

Fill the model provider keys and base URLs before running the integrated stack.
The integrated env file uses the same runtime names as the code:

- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`
- `CHEAP_MODEL_NAME`
- `STRONG_MODEL_NAME`
- `LITELLM_MASTER_KEY`
- `OPENAI_API_KEY`
- `OPENWEBUI_OKADA_CHEAP_MODEL_ID`
- `OPENWEBUI_OKADA_STRONG_MODEL_ID`

## 2. Start kernel service only
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --app-dir apps/okada-kernel-service --host 0.0.0.0 --port 8080
```

Health check:
```bash
curl http://localhost:8080/healthz
```

## 3. Start kernel + LiteLLM + Open WebUI via compose
This is the preferred integrated startup path.

```bash
docker compose -f ops/integrated/docker-compose.kernel-gateway-ui.yml --env-file ops/integrated/.env up -d
```

Then run:
```bash
OKADA_BASE_URL=http://okada-kernel-service:8080 \
LITELLM_MASTER_KEY=replace-me \
OPENAI_API_KEY=replace-me \
python scripts/e2e_stack_preflight.py
```

## 4. LiteLLM route validation
Render proxy config if needed:
```bash
python scripts/render_litellm_config.py \
  --template examples/litellm/proxy_config.template.yaml \
  --route-map examples/litellm/route_map.json \
  --output ops/integrated/generated.proxy_config.yaml
```

Run preflight:
```bash
python scripts/litellm_preflight.py
```

## 5. Open WebUI operator path
Install the Pipe and Filter examples from `examples/openwebui/` into your Open WebUI runtime.
Use the operator console contract as the minimum manual operations surface.

## 6. Dify linkage
Use the assets in `examples/dify/` and the Dify runbook in `docs/35_dify_runbook.md`.
Dify is intentionally treated as an external/manual linkage target in this pack.

## 7. LangGraph linkage
Use `examples/langgraph/okada_agent_graph.py` as the initial runtime graph and bind it to the kernel service URL from the integrated env file.

## 8. Run the E2E benchmark harness
```bash
python scripts/e2e_compare.py --pretty
```

Optional JSON output:
```bash
python scripts/e2e_compare.py --output data/benchmarks/e2e_summary.json --pretty
```

## 9. Acceptance gate
Minimum acceptance for this phase:
- kernel health passes
- stack preflight passes
- tests pass
- E2E harness runs and produces a summary
- at least one routing and one RAG scenario show Okada > baseline utility in the harness fixtures
