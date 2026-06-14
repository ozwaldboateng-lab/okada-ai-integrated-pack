from __future__ import annotations

from typing import Literal, TypedDict


class AgentState(TypedDict, total=False):
    # request / plan
    user_request: str
    plan: str
    current_step: str
    thread_id: str
    checkpoint_id: str
    run_id: str

    # tool execution
    tool_name: str
    tool_input: str
    tool_output: str
    tool_policy: dict[str, list[str]]

    # observables for OKD-AI-003
    planner_executor_mismatch: float
    tool_disagreement: float
    retry_count: int
    unresolved_subgoal_count: int
    route_split_frequency: float
    retrieval_contradiction_rate: float
    context_age_penalty: float
    stale_context_rounds: int
    prior_branch_failures: int

    # risk / resources
    high_risk_action_flag: bool
    human_confirmation_available: bool
    remaining_step_budget: int
    time_budget_seconds: float

    # governance outputs
    governance_action: str
    governance_regime: Literal["clean", "mixed", "contaminated"]
    route_integrity_score: float
    escalation_pressure_score: float
    requires_interrupt: bool
    allow_continue: bool
    should_abort: bool
    should_replan: bool
    should_handoff: bool
    human_review_action: str
    human_review_notes: str
    audit_trace_id: str

    # final output
    final_answer: str
