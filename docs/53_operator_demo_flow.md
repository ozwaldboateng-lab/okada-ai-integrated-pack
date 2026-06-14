# 53. Operator Demo Flow

## Goal
Demonstrate one end-to-end narrative for each major integration.

## Start here

Use the preferred integrated startup path:

```bash
docker compose -f ops/integrated/docker-compose.kernel-gateway-ui.yml --env-file ops/integrated/.env up -d
```

Then run the stack preflight:

```bash
OKADA_BASE_URL=http://okada-kernel-service:8080 \
LITELLM_MASTER_KEY=replace-me \
OPENAI_API_KEY=replace-me \
python scripts/e2e_stack_preflight.py
```

For local non-Docker demos, start only the kernel:

```bash
uvicorn app.main:app --app-dir apps/okada-kernel-service --host 0.0.0.0 --port 8080
```

## Suggested demo order

1. LiteLLM pre-route:
   - File: `examples/litellm/okada_custom_handler.py`
   - Preflight: `python scripts/litellm_preflight.py`
   - Show promotion or bounded hybrid routing through `/integrations/litellm/pre-route`.
2. Dify RAG post-retrieval:
   - Files: `examples/dify/http_request_payload_pre.json`, `examples/dify/http_request_payload_post.json`
   - Preflight: `OKADA_BASE_URL=http://localhost:8080 python scripts/dify_preflight.py`
   - Show stale/conflicting evidence producing abstain, deeper retrieval, or freshness-aware handling.
3. LangGraph step governance:
   - File: `examples/langgraph/okada_agent_graph.py`
   - Preflight: `OKADA_BASE_URL=http://localhost:8080 python scripts/langgraph_preflight.py`
   - Show interrupt, human review merge, or constrained tool policy on a risky action.
4. Open WebUI operator view:
   - Files: `examples/openwebui/okada_governance_pipe.py`, `examples/openwebui/okada_audit_filter.py`
   - Preflight: `OKADA_BASE_URL=http://localhost:8080 python scripts/openwebui_preflight.py`
   - Show selected model, trust metadata, and audit payload attached to operator-visible messages.
5. E2E benchmark report:
   - Command: `python scripts/e2e_compare.py --pretty`
   - Output: `data/benchmarks/e2e_summary.json`

## Success condition
The operator can show:
- regime
- recommended action
- transformed platform payload
- audit payload or trace ID
- generated benchmark summary
