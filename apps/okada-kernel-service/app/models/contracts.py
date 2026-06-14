from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


SpecId = Literal["OKD-AI-CORE-001", "OKD-AI-001", "OKD-AI-002", "OKD-AI-003", "OKD-AI-004", "OKD-AI-005"]
AdapterType = Literal["monitoring", "mlops", "agent", "rag", "routing", "anomaly", "rca", "eval", "infra", "security", "quantum"]
Regime = Literal["clean", "mixed", "contaminated"]
TypeClass = Literal["I", "II", "III", "undefined"]


class PolicyProfile(BaseModel):
    profile_name: str = "default"
    deterministic_mode: bool = True
    thresholds: dict[str, float] = Field(default_factory=dict)
    weights: dict[str, float] = Field(default_factory=dict)
    preferred_actions: dict[str, list[str]] = Field(default_factory=dict)


class DiagnoseRequest(BaseModel):
    spec_id: SpecId
    adapter_type: AdapterType
    observables: dict[str, Any]
    context: dict[str, Any]
    history_state: dict[str, Any]
    resource_state: dict[str, Any]
    policy_profile: PolicyProfile | None = None
    counterfactual_candidates: list[str] = Field(default_factory=list)


class DiagnoseResponse(BaseModel):
    spec_id: str
    regime: Regime
    type_class: TypeClass
    trust_state: str = "undefined"
    scores: dict[str, float]
    first_visible_handle: list[str] = Field(default_factory=list)
    recommended_action: str
    alternatives: list[str] = Field(default_factory=list)
    audit_trace_id: str
    audit_persisted: bool = False


class AuditRecord(BaseModel):
    audit_trace_id: str
    timestamp: datetime
    spec_id: str
    adapter_type: str
    raw_inputs: dict[str, Any]
    normalized_inputs: dict[str, Any]
    derived_features: dict[str, Any]
    decision: dict[str, Any]
    alternatives: list[str] = Field(default_factory=list)
    policy_snapshot: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def now(
        cls,
        *,
        audit_trace_id: str,
        spec_id: str,
        adapter_type: str,
        raw_inputs: dict[str, Any],
        normalized_inputs: dict[str, Any],
        derived_features: dict[str, Any],
        decision: dict[str, Any],
        alternatives: list[str],
        policy_snapshot: dict[str, Any],
    ) -> "AuditRecord":
        return cls(
            audit_trace_id=audit_trace_id,
            timestamp=datetime.now(timezone.utc),
            spec_id=spec_id,
            adapter_type=adapter_type,
            raw_inputs=raw_inputs,
            normalized_inputs=normalized_inputs,
            derived_features=derived_features,
            decision=decision,
            alternatives=alternatives,
            policy_snapshot=policy_snapshot,
        )


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
