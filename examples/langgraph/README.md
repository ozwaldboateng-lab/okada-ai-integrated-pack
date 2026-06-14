# LangGraph Example (Gateway Unified)

This graph calls only gateway endpoints:
- `POST /integrations/langgraph/step`
- `POST /integrations/langgraph/human-review`

The gateway owns state translation and mutated-state construction.

## State Schema

Use `state_schema.py::AgentState` as the shared state contract. The middleware
expects these checkpoint identifiers when available:

- `thread_id`
- `checkpoint_id`
- `run_id`

Pass the same `thread_id` into LangGraph config, for example with
`build_langgraph_config(thread_id=..., user_id=..., run_id=...)`.

## Step Payload

Call `POST /integrations/langgraph/step` with:

```json
{
  "payload": {
    "thread_id": "thread-1",
    "checkpoint_id": "checkpoint-1",
    "run_id": "run-1",
    "user_request": "...",
    "plan": "...",
    "current_step": "before_tool",
    "tool_name": "wiki_write",
    "planner_executor_mismatch": 0.0,
    "tool_disagreement": 0.0,
    "retry_count": 0,
    "unresolved_subgoal_count": 0,
    "route_split_frequency": 0.0,
    "retrieval_contradiction_rate": 0.0,
    "context_age_penalty": 0.0,
    "remaining_step_budget": 3,
    "human_confirmation_available": true,
    "high_risk_action_flag": false
  },
  "options": {
    "stage": "before_tool"
  }
}
```

The response `transformed_payload` contains `governance_action`,
`tool_policy`, `requires_interrupt`, and control flags such as
`should_replan`, `should_handoff`, and `should_abort`.

## Human Review Payload

Call `POST /integrations/langgraph/human-review` with:

```json
{
  "payload": {
    "state": {},
    "human_review": {
      "action": "constrained_continue",
      "notes": "allow read-only tools"
    }
  },
  "options": {
    "default_action": "human_handoff"
  }
}
```

The returned `transformed_payload` clears `requires_interrupt` and records
`human_review_action` / `human_review_notes`.

## Resume Demo Outcomes

`resume_outcomes.json` contains approve, edit, and abort examples for interrupted
states. Use it to verify that `thread_id`, `checkpoint_id`, `run_id`, and
`audit_trace_id` survive the review merge.

## Preflight

With the kernel running:

```bash
OKADA_BASE_URL=http://localhost:8080 python scripts/langgraph_preflight.py
```

The preflight checks required example files and calls both gateway endpoints.
