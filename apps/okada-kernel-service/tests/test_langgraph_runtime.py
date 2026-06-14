from __future__ import annotations

import json
from pathlib import Path

from app.benchmark.e2e_compare import load_cases, run_case
from app.integrations.langgraph_runtime import (
    apply_governance_decision,
    build_agent_governance_payload,
    build_audit_payload,
    build_interrupt_payload,
    build_langgraph_config,
    decision_requires_interrupt,
    derive_tool_policy,
    merge_human_review,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_build_agent_governance_payload_maps_state_fields() -> None:
    payload = build_agent_governance_payload(
        state={
            "user_request": "draft a response",
            "plan": "search then answer",
            "tool_name": "web_search",
            "thread_id": "thread-1",
            "checkpoint_id": "checkpoint-1",
            "run_id": "run-1",
            "planner_executor_mismatch": 0.7,
            "retry_count": 2,
            "remaining_step_budget": 4,
            "human_confirmation_available": True,
        },
        stage="before_tool",
    )
    assert payload["spec_id"] == "OKD-AI-003"
    assert payload["context"]["stage"] == "before_tool"
    assert payload["context"]["thread_id"] == "thread-1"
    assert payload["context"]["checkpoint_id"] == "checkpoint-1"
    assert payload["observables"]["planner_executor_mismatch"] == 0.7
    assert payload["resource_state"]["human_confirmation_available"] is True


def test_decision_requires_interrupt_for_handoff_and_abort() -> None:
    assert decision_requires_interrupt({"recommended_action": "human_handoff"}) is True
    assert decision_requires_interrupt({"recommended_action": "abort"}) is True
    assert decision_requires_interrupt({"recommended_action": "continue"}) is False


def test_apply_governance_decision_sets_control_flags() -> None:
    state = {"tool_name": "web_write"}
    decision = {
        "recommended_action": "replan",
        "regime": "mixed",
        "audit_trace_id": "trace-22",
        "scores": {"route_integrity_score": 0.32, "escalation_pressure_score": 0.74},
    }
    mutated = apply_governance_decision(state, decision)
    assert mutated["governance_action"] == "replan"
    assert mutated["should_replan"] is True
    assert mutated["allow_continue"] is True
    assert "web_write" in mutated["tool_policy"]["disable"]


def test_build_interrupt_payload_carries_review_context() -> None:
    payload = build_interrupt_payload(
        {"user_request": "send email", "plan": "draft then send", "tool_name": "mail_send"},
        {"recommended_action": "human_handoff", "regime": "contaminated", "audit_trace_id": "trace-9"},
    )
    assert payload["recommended_action"] == "human_handoff"
    assert payload["tool_name"] == "mail_send"
    assert payload["audit_trace_id"] == "trace-9"


def test_merge_human_review_overrides_default_action() -> None:
    merged = merge_human_review(
        {"governance_action": "human_handoff", "requires_interrupt": True},
        {"action": "constrained_continue", "notes": "allow read-only"},
        default_action="human_handoff",
    )
    assert merged["governance_action"] == "constrained_continue"
    assert merged["allow_continue"] is True
    assert merged["requires_interrupt"] is False


def test_resume_outcome_fixture_covers_approve_edit_abort() -> None:
    cases = json.loads((REPO_ROOT / "examples" / "langgraph" / "resume_outcomes.json").read_text(encoding="utf-8"))

    assert {case["human_review"]["action"] for case in cases} == {"continue", "constrained_continue", "abort"}
    for case in cases:
        merged = merge_human_review(
            case["interrupted_state"],
            case["human_review"],
            default_action=case["interrupted_state"]["governance_action"],
        )
        for key, expected_value in case["expected"].items():
            assert merged[key] == expected_value
        assert merged["requires_interrupt"] is False


def test_merge_human_review_applies_approved_tool_subset() -> None:
    merged = merge_human_review(
        {"tool_policy": {"allow": [], "disable": ["wiki_write"]}},
        {"action": "constrained_continue", "approved_tool_subset": ["read_only_search"], "reviewer_id": "operator-1"},
        default_action="human_handoff",
    )

    assert merged["tool_policy"]["allow"] == ["read_only_search"]
    assert merged["tool_policy"]["disable"] == ["wiki_write"]
    assert merged["human_reviewer_id"] == "operator-1"


def test_build_audit_payload_contains_agent_decision() -> None:
    payload = build_audit_payload(
        {
            "audit_trace_id": "trace-a",
            "user_request": "summarize",
            "plan": "read then summarize",
            "tool_name": "read_doc",
            "thread_id": "thread-a",
            "checkpoint_id": "checkpoint-a",
            "run_id": "run-a",
            "governance_action": "continue",
            "governance_regime": "clean",
            "tool_policy": {"allow": ["read_doc"], "disable": []},
            "human_reviewer_id": "operator-1",
        }
    )
    assert payload["spec_id"] == "OKD-AI-003"
    assert payload["decision"]["action"] == "continue"
    assert payload["decision"]["human_reviewer_id"] == "operator-1"
    assert payload["raw_inputs"]["thread_id"] == "thread-a"


def test_build_langgraph_config_returns_thread_scoped_config() -> None:
    config = build_langgraph_config(thread_id="t-1", user_id="u-1", run_id="r-1")
    assert config["configurable"]["thread_id"] == "t-1"
    assert config["configurable"]["user_id"] == "u-1"
    assert config["configurable"]["run_id"] == "r-1"


def test_derive_tool_policy_constrained_continue_defaults_to_read_only() -> None:
    policy = derive_tool_policy({"tool_name": "web_write"}, {"recommended_action": "constrained_continue"})
    assert "read_only_search" in policy["allow"]
    assert "web_write" in policy["disable"]


def test_agent_e2e_fixtures_cover_type_i_ii_iii_actions() -> None:
    agent_cases = [case for case in load_cases() if case["spec_id"] == "OKD-AI-003"]
    results = {result["scenario_id"]: result for result in [run_case(case) for case in agent_cases]}

    expected = {
        "agent-clean-linear-plan": ("I", "continue"),
        "agent-recoverable-noise": ("II", "continue"),
        "agent-derailment-no-human-risk": ("III", "human_handoff"),
    }
    for scenario_id, (type_class, action) in expected.items():
        assert results[scenario_id]["type_class"] == type_class
        assert results[scenario_id]["okada_action"] == action
