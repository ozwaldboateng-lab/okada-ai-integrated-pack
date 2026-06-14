# LangGraph Detailed Integration

## Scope
This document details how **OKD-AI-003 Agentic AI Route Contamination and Escalation Governance** is inserted into a LangGraph-based agent runtime.

## Primary insertion points
1. after planning
2. before tool execution
3. after tool execution
4. before final answer emission

## Recommended runtime split
- LangGraph handles stateful execution and interruption.
- Okada Kernel handles regime diagnosis and action recommendation.
- Human reviewer handles final authority for `human_handoff`, `abort`, or other escalated cases.

## Required state fields
- request / plan context
- current tool selection
- retry / unresolved subgoal counts
- planner-executor mismatch
- tool disagreement
- context age / contradiction indicators
- remaining step budget
- human confirmation availability

## Decision mapping
- `continue` / `constrained_continue`: keep the graph moving
- `replan`: branch to a replanning node
- `human_handoff`: invoke `interrupt()` and wait for reviewer response
- `abort`: terminate early with audit trace preserved

## Persistence requirement
Detailed human review requires a checkpointer. Development may use memory persistence. Production should use a durable checkpointer.
