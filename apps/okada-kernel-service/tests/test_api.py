from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.core.policy import resolve_policy
from app.main import app
from app.models.contracts import PolicyProfile

client = TestClient(app)


def _payload(adapter_type: str, spec_id: str) -> dict:
    return {
        "spec_id": spec_id,
        "adapter_type": adapter_type,
        "observables": {
            "grounding_confidence": 0.3,
            "chunk_conflict_rate": 0.6,
            "index_age": 0.7,
            "source_freshness": 0.2,
            "budget_remaining": 0.5,
            "complexity_proxy": 0.7,
        },
        "context": {},
        "history_state": {},
        "resource_state": {},
    }


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_diagnose_rag() -> None:
    response = client.post("/okada/diagnose", json=_payload("rag", "OKD-AI-004"))
    assert response.status_code == 200
    body = response.json()
    assert body["spec_id"] == "OKD-AI-004"
    assert body["regime"] in {"clean", "mixed", "contaminated"}
    assert body["audit_persisted"] is True


def test_route_routing() -> None:
    payload = _payload("routing", "OKD-AI-005")
    response = client.post("/okada/route", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "recommended_action" in body
    assert body["audit_trace_id"]


def test_policy_registry_reads_threshold_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OKADA_POLICY_THRESHOLD_T_CLEAN", "0.12")

    policy = resolve_policy(None)

    assert policy.thresholds["T_clean"] == 0.12


def test_request_policy_profile_overrides_env_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OKADA_POLICY_THRESHOLD_T_CLEAN", "0.12")

    policy = resolve_policy(PolicyProfile(thresholds={"T_clean": 0.67}))

    assert policy.thresholds["T_clean"] == 0.67


def test_integration_route_uses_policy_registry_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OKADA_POLICY_THRESHOLD_T_CLEAN", "0.0")
    payload = {
        "integration": "litellm",
        "stage": "pre-route",
        "payload": {
            "model": "cheap-default",
            "messages": [{"role": "user", "content": "summarize"}],
            "metadata": {
                "complexity_proxy": 1.0,
                "historical_route_success": 1.0,
                "risk_class": "standard",
            },
        },
        "options": {},
    }

    response = client.post("/integrations/litellm/pre-route", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["kernel_decision"]["regime"] == "mixed"
    assert body["kernel_decision"]["recommended_action"] == "bounded_hybrid"
