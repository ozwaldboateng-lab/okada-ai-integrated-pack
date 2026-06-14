from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _routing_window() -> list[dict]:
    return [
        {
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "invocation": "route",
            "observables": {
                "complexity_proxy": 0.85,
                "historical_route_success": 0.45,
                "budget_remaining": 0.35,
                "latency_load_state": 0.55,
                "retrieval_need_estimate": 0.7,
            },
            "context": {"risk_class": "high"},
            "history_state": {},
            "resource_state": {"history_pressure": 0.25, "competitor_pressure": 0.5},
            "expected_regime": "contaminated",
            "expected_action": "promote_strong_model",
            "outcome": {"success": False, "utility": 0.2, "quality": 0.2, "cost": 0.6, "latency_ms": 900},
        },
        {
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "invocation": "route",
            "observables": {
                "complexity_proxy": 0.25,
                "historical_route_success": 0.9,
                "budget_remaining": 0.8,
                "latency_load_state": 0.2,
                "retrieval_need_estimate": 0.1,
            },
            "context": {"risk_class": "low"},
            "history_state": {},
            "resource_state": {"history_pressure": 0.05, "competitor_pressure": 0.1},
            "expected_regime": "clean",
            "expected_action": "cheap_route",
            "outcome": {"success": True, "utility": 0.9, "quality": 0.95, "cost": 0.1, "latency_ms": 120},
        },
    ]


def _rag_window() -> list[dict]:
    return [
        {
            "spec_id": "OKD-AI-004",
            "adapter_type": "rag",
            "invocation": "diagnose",
            "observables": {
                "source_freshness": 0.4,
                "grounding_confidence": 0.5,
                "chunk_conflict_rate": 0.7,
                "index_age": 0.8,
            },
            "context": {"risk_class": "standard"},
            "history_state": {},
            "resource_state": {"history_pressure": 0.35, "competitor_pressure": 0.45},
            "expected_regime": "mixed",
            "expected_action": "deeper_retrieve",
            "outcome": {"success": True, "utility": 0.7, "quality": 0.72, "grounded_accuracy": 0.68, "stale_answer": True, "cost": 0.2, "latency_ms": 280},
        },
        {
            "spec_id": "OKD-AI-004",
            "adapter_type": "rag",
            "invocation": "diagnose",
            "observables": {
                "source_freshness": 0.95,
                "grounding_confidence": 0.9,
                "chunk_conflict_rate": 0.1,
                "index_age": 0.1,
            },
            "context": {"risk_class": "standard"},
            "history_state": {},
            "resource_state": {"history_pressure": 0.05, "competitor_pressure": 0.08},
            "expected_regime": "clean",
            "expected_action": "answer",
            "outcome": {"success": True, "utility": 0.95, "quality": 0.93, "grounded_accuracy": 0.94, "stale_answer": False, "cost": 0.12, "latency_ms": 150},
        },
    ]


def test_metric_summary_api_routing_returns_adapter_specific_metrics() -> None:
    response = client.post(
        "/okada/auto-calibration/metrics/summarize",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "window_records": _routing_window(),
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    metrics = body["summary"]["adapter_metrics"]
    assert "promotion_pressure_mean" in metrics
    assert "budget_tight_rate" in metrics
    assert body["summary"]["counts"]["record_count"] == 2


def test_metric_summary_api_rag_returns_freshness_metrics() -> None:
    response = client.post(
        "/okada/auto-calibration/metrics/summarize",
        json={
            "profile_name": "rag_default",
            "spec_id": "OKD-AI-004",
            "adapter_type": "rag",
            "window_records": _rag_window(),
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    metrics = body["summary"]["adapter_metrics"]
    assert "freshness_mean" in metrics
    assert "stale_answer_rate" in metrics
    assert metrics["stale_answer_rate"] > 0


def test_proposal_summary_includes_adapter_metrics() -> None:
    response = client.post(
        "/okada/auto-calibration/propose",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "window_records": _routing_window(),
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert "adapter_metrics" in body["summary"]
    assert "promotion_pressure_mean" in body["summary"]["adapter_metrics"]
