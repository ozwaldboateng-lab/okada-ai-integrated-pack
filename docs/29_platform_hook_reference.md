# Platform Hook Reference

## Dify
Primary touchpoints:
- HTTP Request node
- Code node
- Conditional branch node

Kernel calls:
- `/okada/diagnose` before or after retrieval
- `/okada/intervene` before final answer if high-risk branch exists

## LiteLLM
Primary touchpoints:
- `async_pre_call_hook`
- `async_post_call_success_hook`
- optional `async_post_call_failure_hook`

Kernel calls:
- `/okada/route` before model invocation
- `/okada/audit` after response or failure

## LangGraph
Primary touchpoints:
- governance node before tool call
- governance node after tool call
- `interrupt()` for handoff

Kernel calls:
- `/okada/intervene` at each decision boundary

## Open WebUI
Primary touchpoints:
- Pipe for route-aware custom model exposure
- Filter for inlet/outlet audit or blocking

Kernel calls:
- `/okada/route` from Pipe
- `/okada/diagnose` from Filter
