# Integrated Stack Overview (v1.0)

## Goal
Provide a single startup pack that lets a developer bring up the Okada Kernel together with the first operational surfaces needed to start integration work:

- Okada Kernel Service
- LiteLLM Proxy
- Open WebUI
- Dify linkage templates
- LangGraph linkage templates
- E2E comparison harness

## Reality of this pack
This pack is intentionally honest about what is and is not fully containerized.

### Included as directly startup-oriented assets
- Okada Kernel Service runtime
- LiteLLM integration config templates
- Open WebUI integration templates
- integrated docker compose for kernel + gateway + operator UI
- benchmark harness for baseline vs Okada comparisons

### Included as external/manual linkage assets
- Dify workflow templates and runbooks
- LangGraph graph examples and runbooks

The reason is simple: Dify and LangGraph are not single-binary drop-ins in the same way as the kernel service, and the correct first step is to stabilize the kernel/gateway/UI path first while keeping Dify/LangGraph link points explicit.

## Included topology

```text
User / Operator
  -> Open WebUI
      -> LiteLLM Proxy
          -> Okada Kernel Service
          -> Model Providers

Dify Workflow
  -> Okada Kernel Service
  -> LiteLLM Proxy

LangGraph Runtime
  -> Okada Kernel Service
  -> LiteLLM Proxy
```

## Deliverables in this pack
- integrated compose templates
- env examples
- stack preflight
- e2e benchmark harness
- acceptance matrix
- codegen prompt for expanding the integrated stack
