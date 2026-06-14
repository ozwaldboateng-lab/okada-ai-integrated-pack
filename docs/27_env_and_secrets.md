# Environment and Secrets

## Core kernel service
Required:
- `OKADA_AUDIT_PATH`
- `OKADA_AUDIT_BACKEND`
- `OKADA_DEFAULT_PROFILE`
- `OKADA_SERVICE_NAME`

Optional:
- `OKADA_REQUIRE_AUTH`
- `OKADA_SHARED_TOKEN`
- `OKADA_POLICY_THRESHOLD_T_CLEAN`
- `OKADA_POLICY_THRESHOLD_T_CONTAM`
- `OKADA_POLICY_THRESHOLD_HIGH_RISK_BONUS`

Example threshold override:

```bash
OKADA_POLICY_THRESHOLD_T_CLEAN=0.50
```

## Dify
Store in Dify secrets or environment:
- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`

## LiteLLM
Store in proxy environment:
- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`

## LangGraph
Store in agent runtime environment:
- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`
- `LANGGRAPH_THREAD_PREFIX`

## Open WebUI
Store as pipe/filter valves or server env:
- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`

## Secret handling rule
Never hardcode API tokens into workflow exports, plugin files, or prompt packs.
