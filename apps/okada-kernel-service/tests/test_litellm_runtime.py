from __future__ import annotations

from app.integrations.litellm_runtime import (
    apply_routing_decision,
    build_audit_payload,
    build_routing_payload,
)


def test_build_routing_payload_extracts_metadata() -> None:
    payload = build_routing_payload(
        {
            "model": "cheap-default",
            "messages": [{"role": "user", "content": "hello"}],
            "metadata": {
                "complexity_proxy": 0.8,
                "historical_route_success": 0.7,
                "budget_remaining": 0.4,
                "latency_load_state": 0.3,
                "risk_class": "high",
            },
        }
    )
    assert payload["spec_id"] == "OKD-AI-005"
    assert payload["observables"]["complexity_proxy"] == 0.8
    assert payload["observables"]["budget_remaining"] == 0.4
    assert payload["observables"]["latency_load_state"] == 0.3
    assert payload["resource_state"]["budget_remaining"] == 0.4


def test_apply_routing_decision_switches_model_and_metadata() -> None:
    data = {"model": "cheap-default", "messages": [], "metadata": {}}
    decision = {
        "regime": "mixed",
        "recommended_action": "promote_strong_model",
        "audit_trace_id": "trace-123",
        "type_class": "II",
        "alternatives": ["cheap_route"],
    }
    mutated = apply_routing_decision(data, decision)
    assert mutated["model"] == "strong-default"
    assert mutated["metadata"]["okada_action"] == "promote_strong_model"
    assert mutated["metadata"]["okada_strategy"] == "single_pass"


def test_build_audit_payload_contains_action_and_target_model() -> None:
    data = {
        "model": "strong-default",
        "messages": [{"role": "user", "content": "hi"}],
        "metadata": {
            "okada_regime": "mixed",
            "okada_action": "bounded_hybrid",
            "okada_strategy": "bounded_hybrid",
            "okada_audit_trace_id": "trace-xyz",
        },
    }
    payload = build_audit_payload(data)
    assert payload["decision"]["action"] == "bounded_hybrid"
    assert payload["decision"]["target_model"] == "strong-default"
    assert payload["audit_trace_id"] == "trace-xyz"
