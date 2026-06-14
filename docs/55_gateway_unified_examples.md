# Gateway-unified Examples

All OSS-side examples should call the integration gateway rather than kernel core endpoints.

Stable endpoint families:
- LiteLLM: `/integrations/litellm/*`
- Dify: `/integrations/dify/*`
- LangGraph: `/integrations/langgraph/*`
- Open WebUI: `/integrations/openwebui/*`

## Start-here path

1. Read `docs/53_operator_demo_flow.md`.
2. Bring up the preferred stack with
   `ops/integrated/docker-compose.kernel-gateway-ui.yml`.
3. Run `python scripts/e2e_stack_preflight.py`.
4. Run each integration preflight:
   - `python scripts/litellm_preflight.py`
   - `python scripts/dify_preflight.py`
   - `python scripts/langgraph_preflight.py`
   - `python scripts/openwebui_preflight.py`
5. Generate the benchmark artifact with `python scripts/e2e_compare.py --pretty`.

## Current example files

- LiteLLM: `examples/litellm/okada_custom_handler.py`, `examples/litellm/route_map.json`
- Dify: `examples/dify/import_manifest.yaml`, `examples/dify/http_request_payload_pre.json`, `examples/dify/http_request_payload_post.json`
- LangGraph: `examples/langgraph/okada_agent_graph.py`, `examples/langgraph/state_schema.py`
- Open WebUI: `examples/openwebui/pipes_manifest.yaml`, `examples/openwebui/okada_governance_pipe.py`, `examples/openwebui/okada_audit_filter.py`
