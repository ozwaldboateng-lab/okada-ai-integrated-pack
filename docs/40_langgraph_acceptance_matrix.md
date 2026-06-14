# LangGraph Acceptance Matrix

| Scenario | Fixture ID | Type Flavor | Expected Regime | Expected Action | Expected Graph Effect |
|---|---|---|---|---|---|
| clean linear plan | `agent-clean-linear-plan` | Type I | clean | continue | tool executes, final answer emitted |
| mild tool disagreement | `agent-recoverable-noise` | Type II | clean | continue | tool executes without unnecessary interrupt |
| route derailment with human path | `agent-derailment-no-human-risk` | Type III | contaminated | human_handoff | interrupt fired |
| unsafe contradiction loop | `agent-contradiction-loop` | Type III | contaminated | abort | graph terminates before final tool action |

Source: `fixtures/e2e/agent_cases.jsonl`

## Minimum acceptance conditions
- interrupt path works with preserved `audit_trace_id`
- replan branch is reachable and resumable
- abort does not emit unsafe tool action
- post-tool governance can still override earlier decisions

## Resume outcome matrix

Source: `examples/langgraph/resume_outcomes.json`

| Resume case | Human action | Expected graph effect |
|---|---|---|
| `resume-approve` | `continue` | Clears interrupt and allows normal continuation. |
| `resume-edit` | `constrained_continue` | Clears interrupt and applies `approved_tool_subset`. |
| `resume-abort` | `abort` | Clears interrupt and routes to final abort behavior. |
