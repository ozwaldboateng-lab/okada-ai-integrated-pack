# 30. LiteLLM Detailed Integration Design

## Goal
Make `OKD-AI-005 Multi-model / Multi-strategy Routing Governance` the first runnable external integration.

## Why this comes first
LiteLLM is the narrowest and cleanest chokepoint in the full system.
A single pre-call hook can turn an incoming request into an Okada routing decision.
A single post-call hook can emit audit records.

## Integration boundary
- **Before LiteLLM call**: call `/okada/route`
- **After LiteLLM call**: call `/okada/audit`
- **Do not** encode domain heuristics directly inside Dify app code if the logic is truly routing logic.

## Input contract from caller -> LiteLLM metadata
The following metadata keys are reserved for Okada routing:
- `complexity_proxy`
- `historical_route_success`
- `budget_remaining`
- `latency_load_state`
- `risk_class`
- `question_time_sensitivity`
- `recent_route`
- `previous_failures`
- `recent_fallback_count`

## Output contract from Okada -> LiteLLM handler
The routing handler consumes:
- `regime`
- `recommended_action`
- `type_class`
- `alternatives`
- `audit_trace_id`

## Action mapping layer
The route map is intentionally externalized in `examples/litellm/route_map.json`.
This keeps policy mapping editable without modifying the callback source.

## Deployment path
1. Start kernel service
2. Preflight the environment
3. Render a concrete LiteLLM config
4. Start LiteLLM with custom callback
5. Send smoke requests with metadata
