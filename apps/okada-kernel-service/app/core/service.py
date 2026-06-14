from __future__ import annotations

import uuid

from app.adapters.base import AdapterDecision
from app.adapters.registry import registry
from app.audit.store import audit_store
from app.core.policy import resolve_policy
from app.models.contracts import AuditRecord, DiagnoseRequest, DiagnoseResponse


def _decision_to_response(spec_id: str, decision: AdapterDecision, audit_trace_id: str, audit_persisted: bool) -> DiagnoseResponse:
    scores = {k: float(v) for k, v in decision.derived_features.items() if isinstance(v, (int, float))}
    if "H_dom" not in scores:
        scores["H_dom"] = 0.0
    if "H_hist" not in scores:
        scores["H_hist"] = 0.0
    if "H_comp" not in scores:
        scores["H_comp"] = 0.0
    return DiagnoseResponse(
        spec_id=spec_id,
        regime=decision.regime,  # type: ignore[arg-type]
        type_class=decision.type_class,  # type: ignore[arg-type]
        trust_state=decision.trust_state,
        scores=scores,
        first_visible_handle=decision.first_visible_handle,
        recommended_action=decision.recommended_action,
        alternatives=decision.alternatives,
        audit_trace_id=audit_trace_id,
        audit_persisted=audit_persisted,
    )


class KernelService:
    def diagnose(self, request: DiagnoseRequest, *, persist_audit: bool = True) -> DiagnoseResponse:
        policy = resolve_policy(request.policy_profile)
        adapter = registry.get(request.adapter_type)
        decision = adapter.diagnose(request, policy)
        return self._audit_and_render(request, policy.model_dump(), decision, persist_audit)

    def route(self, request: DiagnoseRequest, *, persist_audit: bool = True) -> DiagnoseResponse:
        policy = resolve_policy(request.policy_profile)
        adapter = registry.get(request.adapter_type)
        decision = adapter.route(request, policy)
        return self._audit_and_render(request, policy.model_dump(), decision, persist_audit)

    def intervene(self, request: DiagnoseRequest, *, persist_audit: bool = True) -> DiagnoseResponse:
        policy = resolve_policy(request.policy_profile)
        adapter = registry.get(request.adapter_type)
        decision = adapter.intervene(request, policy)
        preferred = policy.preferred_actions.get(decision.regime, [])
        if preferred and decision.recommended_action not in preferred:
            decision.recommended_action = preferred[0]
        return self._audit_and_render(request, policy.model_dump(), decision, persist_audit)

    def create_audit(self, record: AuditRecord) -> AuditRecord:
        return audit_store.write(record)

    def list_audits(self) -> list[AuditRecord]:
        return audit_store.list_records()

    def _audit_and_render(self, request: DiagnoseRequest, policy_snapshot: dict, decision: AdapterDecision, persist_audit: bool) -> DiagnoseResponse:
        audit_trace_id = str(uuid.uuid4())
        persisted = False
        if persist_audit:
            record = AuditRecord.now(
                audit_trace_id=audit_trace_id,
                spec_id=request.spec_id,
                adapter_type=request.adapter_type,
                raw_inputs=request.model_dump(),
                normalized_inputs=decision.normalized_inputs,
                derived_features=decision.derived_features,
                decision={
                    "regime": decision.regime,
                    "type_class": decision.type_class,
                    "trust_state": decision.trust_state,
                    "recommended_action": decision.recommended_action,
                },
                alternatives=decision.alternatives,
                policy_snapshot=policy_snapshot,
            )
            audit_store.write(record)
            persisted = True
        return _decision_to_response(request.spec_id, decision, audit_trace_id, persisted)


kernel_service = KernelService()
