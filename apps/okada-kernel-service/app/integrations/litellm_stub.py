from __future__ import annotations

from app.integrations.http_client import OkadaHttpClient
from app.models.contracts import DiagnoseRequest


def select_model_for_litellm(request: DiagnoseRequest, base_url: str | None = None) -> str:
    client = OkadaHttpClient(base_url=base_url)
    decision = client.route(request)
    mapping = {
        "cheap_route": "gpt-4o-mini",
        "bounded_hybrid": "gpt-4.1-mini",
        "promote_strong_model": "gpt-4.1",
        "continue": "gpt-4o-mini",
    }
    return mapping.get(decision.recommended_action, "gpt-4o-mini")
