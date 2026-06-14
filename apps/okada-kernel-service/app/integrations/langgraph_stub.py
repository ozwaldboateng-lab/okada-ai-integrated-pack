from __future__ import annotations

from app.integrations.http_client import OkadaHttpClient
from app.models.contracts import DiagnoseRequest


def langgraph_step_guard(request: DiagnoseRequest, base_url: str | None = None) -> dict:
    client = OkadaHttpClient(base_url=base_url)
    result = client.intervene(request)
    return {
        "allow_continue": result.recommended_action not in {"abort", "human_handoff"},
        "action": result.recommended_action,
        "regime": result.regime,
        "audit_trace_id": result.audit_trace_id,
    }
