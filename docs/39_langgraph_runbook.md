# LangGraph Runbook

## Preconditions
- Okada Kernel service running
- `OKADA_BASE_URL` configured
- `OKADA_SHARED_TOKEN` configured if auth is enabled
- LangGraph runtime installed in the consuming application
- checkpointer enabled

## Local smoke flow
1. start the kernel service
2. set `OKADA_BASE_URL`
3. run the example graph with a thread config from `build_langgraph_config`
4. trigger a case that returns `human_handoff`
5. resume with a reviewer action payload
6. confirm the final state and audit trace

## Thread and checkpoint config

Supply `thread_id` at graph invocation time and carry it in state:

```python
config = build_langgraph_config(thread_id="demo-thread-001", user_id="operator-001", run_id="run-0001")
state = {
    "thread_id": "demo-thread-001",
    "checkpoint_id": "checkpoint-0001",
    "run_id": "run-0001",
}
```

Without `thread_id`, LangGraph cannot durably resume an interrupt.

## Resume demo outcomes

Use `examples/langgraph/resume_outcomes.json` for the three expected human review
paths:

1. approve: `action=continue`
2. edit: `action=constrained_continue` with `approved_tool_subset`
3. abort: `action=abort`

Each case starts from an interrupted state containing `audit_trace_id`, `thread_id`,
`checkpoint_id`, and `run_id`.

## Audit path

Before interrupt, `/integrations/langgraph/step` returns a transformed state with
`audit_trace_id`. After review, `/integrations/langgraph/human-review` merges
`human_review_action`, `human_review_notes`, and `human_reviewer_id`. The audit
payload from `build_audit_payload` preserves the action, tool policy, reviewer id,
and raw thread/checkpoint identifiers.

## Failure modes
- kernel timeout -> fail closed or fail safe depending on policy profile
- missing thread id -> no durable interrupt/resume
- repeated replans -> cap by remaining step budget
- reviewer silence -> timeout to abort or restricted continue

## Operational checks
- interrupt path exercised at least once in smoke tests
- audit trace id preserved before and after human review
- tool policy restrictions visible in state
