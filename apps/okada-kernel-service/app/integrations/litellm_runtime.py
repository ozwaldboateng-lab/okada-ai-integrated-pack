from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.models.contracts import AuditRecord, DiagnoseRequest

DEFAULT_ROUTE_MAP: dict[str, dict[str, Any]] = {
    "cheap_route": {"target_model": "cheap-default", "strategy": "single_pass"},
    "continue": {"target_model": "cheap-default", "strategy": "single_pass"},
    "promote_strong_model": {"target_model": "strong-default", "strategy": "single_pass"},
    "bounded_hybrid": {"target_model": "strong-default", "strategy": "bounded_hybrid"},
    "branchwise_hybrid": {"target_model": "strong-default", "strategy": "branchwise_hybrid"},
}


def load_route_map(path: str | None = None) -> dict[str, dict[str, Any]]:
    if not path:
        return deepcopy(DEFAULT_ROUTE_MAP)
    route_map_path = Path(path)
    if not route_map_path.exists():
        raise FileNotFoundError(f"Route map file not found: {route_map_path}")
    with route_map_path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("Route map must be a JSON object")
    return loaded


def build_routing_payload(data: dict[str, Any], *, policy_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = data.get("metadata", {}) or {}
    observables = {
        "complexity_proxy": metadata.get("complexity_proxy", 0.5),
        "historical_route_success": metadata.get("historical_route_success", 0.5),
        "risk_class": metadata.get("risk_class", "standard"),
        "question_time_sensitivity": metadata.get("question_time_sensitivity", 0.5),
        "retrieval_need_estimate": metadata.get("retrieval_need_estimate", 0.0),
        "budget_remaining": metadata.get("budget_remaining", 1.0),
        "latency_load_state": metadata.get("latency_load_state", 0.5),
    }
    resource_state = {
        "budget_remaining": metadata.get("budget_remaining", 1.0),
        "latency_load_state": metadata.get("latency_load_state", 0.5),
        "heavy_model_availability": metadata.get("heavy_model_availability", 1.0),
    }
    context = {
        "messages_count": len(data.get("messages", [])),
        "requested_model": data.get("model"),
        "temperature": data.get("temperature", 0.0),
        "max_tokens": data.get("max_tokens"),
    }
    history_state = {
        "recent_route": metadata.get("recent_route", ""),
        "previous_failures": metadata.get("previous_failures", 0),
        "recent_fallback_count": metadata.get("recent_fallback_count", 0),
    }
    return {
        "spec_id": "OKD-AI-005",
        "adapter_type": "routing",
        "observables": observables,
        "context": context,
        "history_state": history_state,
        "resource_state": resource_state,
        "policy_profile": policy_profile or {"profile_name": "default", "deterministic_mode": True},
    }


def build_routing_request(data: dict[str, Any], *, policy_profile: dict[str, Any] | None = None) -> DiagnoseRequest:
    return DiagnoseRequest.model_validate(build_routing_payload(data, policy_profile=policy_profile))


def apply_routing_decision(
    data: dict[str, Any],
    decision: dict[str, Any],
    *,
    route_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    mutated = deepcopy(data)
    route_map = route_map or deepcopy(DEFAULT_ROUTE_MAP)

    action = decision.get("recommended_action", "continue")
    mapping = route_map.get(action, route_map.get("continue", {"target_model": mutated.get("model")}))

    target_model = mapping.get("target_model") or mutated.get("model")
    strategy = mapping.get("strategy", "single_pass")

    mutated["model"] = target_model
    metadata = mutated.setdefault("metadata", {})
    metadata["okada_regime"] = decision.get("regime", "mixed")
    metadata["okada_action"] = action
    metadata["okada_strategy"] = strategy
    metadata["okada_audit_trace_id"] = decision.get("audit_trace_id", "")
    metadata["okada_type_class"] = decision.get("type_class", "undefined")
    metadata["okada_alternatives"] = decision.get("alternatives", [])
    return mutated


def build_audit_payload(data: dict[str, Any], *, response_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = data.get("metadata", {}) or {}
    decision = {
        "regime": metadata.get("okada_regime", "mixed"),
        "action": metadata.get("okada_action", "continue"),
        "strategy": metadata.get("okada_strategy", "single_pass"),
        "target_model": data.get("model"),
    }
    if response_summary:
        decision["response_summary"] = response_summary

    record = AuditRecord.now(
        audit_trace_id=metadata.get("okada_audit_trace_id", ""),
        spec_id="OKD-AI-005",
        adapter_type="routing",
        raw_inputs={
            "messages": data.get("messages", []),
            "model": data.get("model"),
            "metadata": metadata,
        },
        normalized_inputs={},
        derived_features={},
        decision=decision,
        alternatives=metadata.get("okada_alternatives", []),
        policy_snapshot={"profile_name": metadata.get("okada_policy_profile", "default")},
    )
    return record.model_dump(mode="json")
