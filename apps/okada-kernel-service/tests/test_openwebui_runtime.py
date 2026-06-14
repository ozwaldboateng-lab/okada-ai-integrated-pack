from app.integrations.openwebui_runtime import (
    build_filter_audit_payload,
    build_filter_payload,
    build_openwebui_headers,
    build_pipe_payload,
    fail_safe_filter_variables,
    transform_filter_decision,
    transform_pipe_decision,
)


def test_build_pipe_payload_sets_routing_spec():
    body = {
        "chat_id": "chat-1",
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Need a thorough answer with sources."}],
        "metadata": {"budget_remaining": 0.8, "latency_load_state": 0.3},
    }
    payload = build_pipe_payload(body, user={"id": "u1"})
    assert payload["spec_id"] == "OKD-AI-005"
    assert payload["adapter_type"] == "routing"
    assert payload["context"]["user_id"] == "u1"


def test_transform_pipe_decision_promotes_strong_model():
    body = {"model": "gpt-4o-mini", "metadata": {}}
    decision = {
        "regime": "mixed",
        "recommended_action": "promote_strong_model",
        "audit_trace_id": "trace-1",
        "type_class": "II",
        "alternatives": ["cheap_route"],
    }
    transformed = transform_pipe_decision(body, decision, cheap_model_id="cheap", strong_model_id="strong")
    assert transformed["selected_model"] == "strong"
    assert transformed["metadata"]["okada_audit_trace_id"] == "trace-1"


def test_build_filter_payload_sets_monitoring_spec():
    body = {
        "chat_id": "chat-2",
        "messages": [{"role": "user", "content": "Hello"}],
        "metadata": {"fallback_rate": 0.3},
    }
    payload = build_filter_payload(body, user={"id": "u2"})
    assert payload["spec_id"] == "OKD-AI-001"
    assert payload["adapter_type"] == "monitoring"
    assert payload["context"]["chat_id"] == "chat-2"


def test_transform_filter_decision_and_failsafe_variables():
    body = {"metadata": {}}
    decision = {
        "regime": "contaminated",
        "recommended_action": "human_review",
        "audit_trace_id": "trace-2",
        "type_class": "III",
        "trust_state": "unsafe",
        "alternatives": ["alert"],
    }
    transformed = transform_filter_decision(body, decision)
    assert transformed["metadata"]["okada_regime"] == "contaminated"
    assert transformed["metadata"]["okada_trust_state"] == "unsafe"
    fail_safe = fail_safe_filter_variables()
    assert fail_safe["okada_fail_safe_reason"] == "governance_unavailable"


def test_build_filter_audit_payload_contains_monitoring_spec():
    body = {
        "chat_id": "chat-3",
        "messages": [{"role": "user", "content": "Check this"}],
        "metadata": {
            "okada_audit_trace_id": "trace-3",
            "okada_regime": "mixed",
            "okada_action": "watch",
            "okada_trust_state": "caution",
        },
    }
    payload = build_filter_audit_payload(body)
    assert payload["spec_id"] == "OKD-AI-001"
    assert payload["decision"]["action"] == "watch"


def test_build_openwebui_headers_supports_bearer_token():
    headers = build_openwebui_headers("secret-token")
    assert headers["Authorization"] == "Bearer secret-token"
