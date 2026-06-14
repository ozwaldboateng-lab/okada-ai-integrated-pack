# Codegen Prompt: LangGraph Detailed Integration

Implement LangGraph-side runtime integration for `OKD-AI-003` using the files in `examples/langgraph/` as the source of truth.

## Requirements
- preserve the provided state schema
- call the Okada Kernel before and after tool execution
- support conditional edges for continue / replan / abort
- support `interrupt()` for `human_handoff`
- persist and reuse `audit_trace_id`
- make the human review payload conform to `human_review_contract.yaml`
- do not hard-code thresholds into the graph
- keep governance logic outside the graph when possible

## Output expectation
Generate:
- LangGraph nodes
- conditional edge functions
- runtime config helper
- human review adapter
- smoke tests for interrupt/resume
