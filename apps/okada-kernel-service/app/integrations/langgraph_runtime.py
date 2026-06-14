from __future__ import annotations

from copy import deepcopy
from typing import Any

SAFE_CONTINUE_ACTIONS = {"continue", "constrained_continue", "replan"}
INTERRUPT_ACTIONS = {"human_handoff", "abort", "intermediate_confirmation"}
TOOL_RESTRICTING_ACTIONS = {"constrained_continue", "replan", "human_handoff", "abort"}


def build_agent_governance_payload(
    *,
    state: dict[str, Any],
    stage: str,
    policy_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the canonical OKD-AI-003 request payload from LangGraph state."""
    context = {
        "stage": stage,
        "user_request": state.get("user_request", ""),
        "plan": state.get("plan", ""),
        "tool_name": state.get("tool_name", ""),
        "current_step": state.get("current_step", stage),
        "thread_id": state.get("thread_id", ""),
        "checkpoint_id": state.get("checkpoint_id", ""),
        "run_id": state.get("run_id", ""),
        "high_risk_action_flag": bool(state.get("high_risk_action_flag", False)),
    }
    observables = {
        "planner_executor_mismatch": float(state.get("planner_executor_mismatch", 0.0)),
        "tool_disagreement": float(state.get("tool_disagreement", 0.0)),
        "retry_count": int(state.get("retry_count", 0)),
        "unresolved_subgoal_count": int(state.get("unresolved_subgoal_count", 0)),
        "route_split_frequency": float(state.get("route_split_frequency", 0.0)),
        "retrieval_contradiction_rate": float(state.get("retrieval_contradiction_rate", 0.0)),
        "context_age_penalty": float(state.get("context_age_penalty", 0.0)),
    }
    history_state = {
        "previous_governance_action": state.get("governance_action", ""),
        "failed_tools": state.get("failed_tools", []),
        "stale_context_rounds": int(state.get("stale_context_rounds", 0)),
        "prior_branch_failures": int(state.get("prior_branch_failures", 0)),
    }
    resource_state = {
        "remaining_step_budget": int(state.get("remaining_step_budget", 0)),
        "human_confirmation_available": bool(state.get("human_confirmation_available", False)),
        "time_budget_seconds": float(state.get("time_budget_seconds", 0.0)),
    }
    return {
        "spec_id": "OKD-AI-003",
        "adapter_type": "agent",
        "observables": observables,
        "context": context,
        "history_state": history_state,
        "resource_state": resource_state,
        "policy_profile": policy_profile or {"profile_name": "default", "deterministic_mode": True},
    }


def decision_requires_interrupt(decision: dict[str, Any]) -> bool:
    return decision.get("recommended_action", "continue") in INTERRUPT_ACTIONS


def build_interrupt_payload(state: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "message": "Okada governance requested review",
        "recommended_action": decision.get("recommended_action", "continue"),
        "regime": decision.get("regime", "mixed"),
        "type_class": decision.get("type_class", "undefined"),
        "audit_trace_id": decision.get("audit_trace_id", ""),
        "first_visible_handle": decision.get("first_visible_handle", []),
        "tool_name": state.get("tool_name", ""),
        "plan": state.get("plan", ""),
        "user_request": state.get("user_request", ""),
    }


def derive_tool_policy(
    state: dict[str, Any],
    decision: dict[str, Any],
    *,
    default_allowed: list[str] | None = None,
) -> dict[str, list[str]]:
    action = decision.get("recommended_action", "continue")
    current_tool = state.get("tool_name", "")
    allowed = list(default_allowed or ([current_tool] if current_tool else []))
    blocked: list[str] = []

    if action in TOOL_RESTRICTING_ACTIONS and current_tool:
        blocked.append(current_tool)
        allowed = [tool for tool in allowed if tool != current_tool]

    if action == "constrained_continue" and not allowed:
        allowed = ["read_only_search"]
    elif action == "replan" and not allowed:
        allowed = ["read_only_search", "summarize_context"]

    return {
        "allow": sorted(set(filter(None, allowed))),
        "disable": sorted(set(filter(None, blocked))),
    }


def apply_governance_decision(state: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    mutated = deepcopy(state)
    action = decision.get("recommended_action", "continue")
    mutated["governance_action"] = action
    mutated["governance_regime"] = decision.get("regime", "mixed")
    mutated["audit_trace_id"] = decision.get("audit_trace_id", "")
    mutated["route_integrity_score"] = float(decision.get("scores", {}).get("route_integrity_score", 0.0))
    mutated["escalation_pressure_score"] = float(decision.get("scores", {}).get("escalation_pressure_score", 0.0))
    mutated["tool_policy"] = derive_tool_policy(mutated, decision)
    mutated["requires_interrupt"] = decision_requires_interrupt(decision)
    mutated["allow_continue"] = action in SAFE_CONTINUE_ACTIONS
    mutated["should_abort"] = action == "abort"
    mutated["should_replan"] = action == "replan"
    mutated["should_handoff"] = action == "human_handoff"
    return mutated


def merge_human_review(
    state: dict[str, Any],
    human_review: dict[str, Any] | None,
    *,
    default_action: str,
) -> dict[str, Any]:
    mutated = deepcopy(state)
    review = human_review or {}
    action = review.get("action", default_action)
    mutated["human_review_action"] = action
    mutated["human_review_notes"] = review.get("notes", "")
    if review.get("reviewer_id"):
        mutated["human_reviewer_id"] = review.get("reviewer_id")
    if review.get("approved_tool_subset") is not None:
        approved = [str(tool) for tool in review.get("approved_tool_subset") or []]
        disabled = mutated.get("tool_policy", {}).get("disable", [])
        mutated["tool_policy"] = {
            "allow": sorted(set(approved)),
            "disable": sorted(set(disabled)),
        }
    mutated["governance_action"] = action
    mutated["allow_continue"] = action in SAFE_CONTINUE_ACTIONS
    mutated["should_abort"] = action == "abort"
    mutated["should_handoff"] = action == "human_handoff"
    mutated["requires_interrupt"] = False
    return mutated


def build_audit_payload(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "audit_trace_id": state.get("audit_trace_id", ""),
        "spec_id": "OKD-AI-003",
        "adapter_type": "agent",
        "decision": {
            "action": state.get("governance_action", "continue"),
            "regime": state.get("governance_regime", "mixed"),
            "tool_policy": state.get("tool_policy", {}),
            "human_review_action": state.get("human_review_action", ""),
            "human_reviewer_id": state.get("human_reviewer_id", ""),
        },
        "raw_inputs": {
            "user_request": state.get("user_request", ""),
            "plan": state.get("plan", ""),
            "tool_name": state.get("tool_name", ""),
            "thread_id": state.get("thread_id", ""),
            "checkpoint_id": state.get("checkpoint_id", ""),
            "run_id": state.get("run_id", ""),
        },
        "derived_features": {
            "route_integrity_score": state.get("route_integrity_score", 0.0),
            "escalation_pressure_score": state.get("escalation_pressure_score", 0.0),
        },
    }


def build_langgraph_config(
    *,
    thread_id: str,
    user_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    configurable = {"thread_id": thread_id}
    if user_id:
        configurable["user_id"] = user_id
    if run_id:
        configurable["run_id"] = run_id
    return {"configurable": configurable}
