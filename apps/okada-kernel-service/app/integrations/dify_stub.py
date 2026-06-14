from __future__ import annotations

from app.integrations.http_client import OkadaHttpClient
from app.models.contracts import DiagnoseRequest


def run_dify_governance_stub(request: DiagnoseRequest, base_url: str | None = None) -> dict:
    client = OkadaHttpClient(base_url=base_url)
    diagnosis = client.diagnose(request)
    return {
        "branch": diagnosis.recommended_action,
        "regime": diagnosis.regime,
        "audit_trace_id": diagnosis.audit_trace_id,
        "trust_state": diagnosis.trust_state,
    }
