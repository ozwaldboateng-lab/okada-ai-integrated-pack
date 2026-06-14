# Request Metadata Mapping

Attach the following metadata when sending requests to LiteLLM:

- `complexity_proxy`: float
- `historical_route_success`: float
- `risk_class`: `low | standard | high`
- `budget_remaining`: float in [0, 1]
- `latency_load_state`: float in [0, 1]
- `recent_route`: string

This lets the Okada routing adapter make decisions without knowing provider-specific internals.
