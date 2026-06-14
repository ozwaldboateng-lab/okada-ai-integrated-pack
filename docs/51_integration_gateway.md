# 51. Integration Gateway

## Purpose
The kernel service now exposes **integration endpoints** so external platforms do not need to understand the full Okada request schema.

## Endpoints
- `POST /integrations/litellm/pre-route`
- `POST /integrations/litellm/post-audit`
- `POST /integrations/dify/rag/pre-retrieval`
- `POST /integrations/dify/rag/post-retrieval`
- `POST /integrations/dify/fail-safe`
- `POST /integrations/langgraph/step`
- `POST /integrations/langgraph/human-review`
- `POST /integrations/openwebui/pipe`
- `POST /integrations/openwebui/filter`

## Rationale
This gateway reduces the amount of handwritten glue code inside Dify, LiteLLM, LangGraph, and Open WebUI.  
The external platform sends its native payload; the gateway converts it into an Okada request, runs the kernel, and returns a transformed payload plus audit material.
