from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.integrations.dify_runtime import build_dify_headers as build_openwebui_headers
from app.models.contracts import AuditRecord, DiagnoseRequest


def _last_user_message(messages: list[dict[str, Any]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return str(message.get("content", ""))
    return ""


def build_pipe_payload(
    body: dict[str, Any],
    *,
    user: dict[str, Any] | None = None,
    history_state: dict[str, Any] | None = None,
    resource_state: dict[str, Any] | None = None,
    policy_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    messages = body.get("messages", [])
    metadata = body.get("metadata", {}) or {}
    observables = {
        "complexity_proxy": min(1.0, len(_last_user_message(messages)) / 2000.0),
        "historical_route_success": metadata.get("historical_route_success", 0.5),
        "risk_class": metadata.get("risk_class", "standard"),
        "question_time_sensitivity": metadata.get("question_time_sensitivity", 0.5),
    }
    context = {
        "messages_count": len(messages),
        "user_id": (user or {}).get("id", ""),
        "chat_id": body.get("chat_id", ""),
        "selected_model": body.get("model", ""),
    }
    return {
        "spec_id": "OKD-AI-005",
        "adapter_type": "routing",
        "observables": observables,
        "context": context,
        "history_state": history_state or {},
        "resource_state": resource_state or {
            "budget_remaining": metadata.get("budget_remaining", 1.0),
            "latency_load_state": metadata.get("latency_load_state", 0.5),
            "heavy_model_availability": metadata.get("heavy_model_availability", 1.0),
        },
        "policy_profile": policy_profile or {"profile_name": "default", "deterministic_mode": True},
    }



def build_pipe_request(
    body: dict[str, Any],
    *,
    user: dict[str, Any] | None = None,
    history_state: dict[str, Any] | None = None,
    resource_state: dict[str, Any] | None = None,
    policy_profile: dict[str, Any] | None = None,
) -> DiagnoseRequest:
    return DiagnoseRequest.model_validate(
        build_pipe_payload(
            body,
            user=user,
            history_state=history_state,
            resource_state=resource_state,
            policy_profile=policy_profile,
        )
    )



def transform_pipe_decision(
    body: dict[str, Any],
    decision: dict[str, Any],
    *,
    cheap_model_id: str,
    strong_model_id: str,
) -> dict[str, Any]:
    transformed = deepcopy(body)
    action = decision.get("recommended_action", "continue")
    selected_model = cheap_model_id
    if action in {"promote_strong_model", "bounded_hybrid", "branchwise_hybrid"}:
        selected_model = strong_model_id

    transformed["selected_model"] = selected_model
    transformed.setdefault("metadata", {})
    transformed["metadata"]["okada_regime"] = decision.get("regime", "mixed")
    transformed["metadata"]["okada_action"] = action
    transformed["metadata"]["okada_type_class"] = decision.get("type_class", "undefined")
    transformed["metadata"]["okada_alternatives"] = decision.get("alternatives", [])
    transformed["metadata"]["okada_audit_trace_id"] = decision.get("audit_trace_id", "")
    return transformed



def build_filter_payload(
    body: dict[str, Any],
    *,
    user: dict[str, Any] | None = None,
    history_state: dict[str, Any] | None = None,
    resource_state: dict[str, Any] | None = None,
    policy_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    messages = body.get("messages", [])
    metadata = body.get("metadata", {}) or {}
    observables = {
        "confidence_trend": metadata.get("confidence_trend", 0.5),
        "calibration_error_trend": metadata.get("calibration_error_trend", 0.2),
        "fallback_rate": metadata.get("fallback_rate", 0.1),
        "override_rate": metadata.get("override_rate", 0.0),
        "latency_instability": metadata.get("latency_instability", 0.1),
        "output_shift_score": metadata.get("output_shift_score", 0.1),
        "tool_failure_rate": metadata.get("tool_failure_rate", 0.0),
    }
    context = {
        "messages_count": len(messages),
        "last_user_message": _last_user_message(messages),
        "user_id": (user or {}).get("id", ""),
        "chat_id": body.get("chat_id", ""),
    }
    return {
        "spec_id": "OKD-AI-001",
        "adapter_type": "monitoring",
        "observables": observables,
        "context": context,
        "history_state": history_state or {},
        "resource_state": resource_state or {},
        "policy_profile": policy_profile or {"profile_name": "default", "deterministic_mode": True},
    }



def build_filter_request(
    body: dict[str, Any],
    *,
    user: dict[str, Any] | None = None,
    history_state: dict[str, Any] | None = None,
    resource_state: dict[str, Any] | None = None,
    policy_profile: dict[str, Any] | None = None,
) -> DiagnoseRequest:
    return DiagnoseRequest.model_validate(
        build_filter_payload(
            body,
            user=user,
            history_state=history_state,
            resource_state=resource_state,
            policy_profile=policy_profile,
        )
    )



def transform_filter_decision(body: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    transformed = deepcopy(body)
    transformed.setdefault("metadata", {})
    transformed["metadata"]["okada_regime"] = decision.get("regime", "mixed")
    transformed["metadata"]["okada_action"] = decision.get("recommended_action", "continue")
    transformed["metadata"]["okada_type_class"] = decision.get("type_class", "undefined")
    transformed["metadata"]["okada_trust_state"] = decision.get("trust_state", "undefined")
    transformed["metadata"]["okada_audit_trace_id"] = decision.get("audit_trace_id", "")
    transformed["metadata"]["okada_alternatives"] = decision.get("alternatives", [])
    transformed["metadata"]["okada_fail_safe_reason"] = ""
    return transformed



def fail_safe_filter_variables(*, default_action: str = "continue", default_regime: str = "mixed") -> dict[str, Any]:
    return {
        "okada_regime": default_regime,
        "okada_action": default_action,
        "okada_type_class": "undefined",
        "okada_trust_state": "undefined",
        "okada_audit_trace_id": "",
        "okada_alternatives": [],
        "okada_fail_safe_reason": "governance_unavailable",
    }



def build_filter_audit_payload(body: dict[str, Any], *, response_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = body.get("metadata", {}) or {}
    record = AuditRecord.now(
        audit_trace_id=metadata.get("okada_audit_trace_id", ""),
        spec_id="OKD-AI-001",
        adapter_type="monitoring",
        raw_inputs={
            "messages": body.get("messages", []),
            "chat_id": body.get("chat_id", ""),
            "metadata": metadata,
        },
        normalized_inputs={},
        derived_features={
            "confidence_trend": metadata.get("confidence_trend", 0.5),
            "fallback_rate": metadata.get("fallback_rate", 0.1),
        },
        decision={
            "regime": metadata.get("okada_regime", "mixed"),
            "action": metadata.get("okada_action", "continue"),
            "trust_state": metadata.get("okada_trust_state", "undefined"),
            "response_summary": response_summary or {},
        },
        alternatives=metadata.get("okada_alternatives", []),
        policy_snapshot={"profile_name": metadata.get("okada_policy_profile", "default")},
    )
    return record.model_dump(mode="json")
