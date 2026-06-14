from __future__ import annotations

from app.integrations.http_client import OkadaHttpClient
from app.integrations.openwebui_runtime import build_pipe_request


def route_for_openwebui(body: dict, base_url: str | None = None, *, user: dict | None = None) -> dict:
    client = OkadaHttpClient(base_url=base_url)
    request = build_pipe_request(body, user=user)
    result = client.route(request)
    return {
        "selected_action": result.recommended_action,
        "regime": result.regime,
        "audit_trace_id": result.audit_trace_id,
        "alternatives": result.alternatives,
    }
