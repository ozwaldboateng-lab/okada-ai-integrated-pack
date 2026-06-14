# Runtime Acceptance Test Plan

## Goal
Validate that the kernel can be called from each target runtime and that its decisions affect execution flow.

## Acceptance levels

### A. Kernel API
- `/healthz` returns ok
- `/okada/diagnose` returns deterministic output for the same request
- `/okada/audit` persists records

### B. Dify integration
- HTTP Request node reaches kernel
- Code node extracts `recommended_action`
- branch changes when observables change

### C. LiteLLM integration
- pre-call hook changes model selection
- post-call hook emits audit payload
- proxy still serves requests when kernel is unavailable and fallback policy is enabled

### D. LangGraph integration
- governance node triggers continue / replan / interrupt / abort
- interrupted runs resume using the same thread_id

### E. Open WebUI integration
- Pipe can call the kernel and choose a target model
- Filter can append governance metadata or block according to policy

## Minimal evidence to collect
- request payload
- kernel response
- translated runtime decision
- resulting route / branch / interrupt
- audit record id
