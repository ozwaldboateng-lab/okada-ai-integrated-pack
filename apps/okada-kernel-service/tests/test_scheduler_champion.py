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
            "context": {"question_time_sensitivity": "high"},
            "history_state": {},
            "resource_state": {},
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
            "context": {},
            "history_state": {},
            "resource_state": {},
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
                "retrieval_score_distribution": 0.32,
                "source_freshness": 0.2,
                "chunk_conflict_rate": 0.65,
                "grounding_confidence": 0.28,
                "index_age": 0.75,
            },
            "context": {"question_time_sensitivity": "high"},
            "history_state": {},
            "resource_state": {},
            "expected_regime": "contaminated",
            "expected_action": "deeper_retrieve",
            "outcome": {"success": False, "utility": 0.3, "quality": 0.4, "grounded_accuracy": 0.35, "latency_ms": 650},
        },
        {
            "spec_id": "OKD-AI-004",
            "adapter_type": "rag",
            "invocation": "diagnose",
            "observables": {
                "retrieval_score_distribution": 0.88,
                "source_freshness": 0.95,
                "chunk_conflict_rate": 0.05,
                "grounding_confidence": 0.9,
                "index_age": 0.1,
            },
            "context": {},
            "history_state": {},
            "resource_state": {},
            "expected_regime": "clean",
            "expected_action": "standard_retrieve",
            "outcome": {"success": True, "utility": 0.92, "quality": 0.9, "grounded_accuracy": 0.93, "latency_ms": 180},
        },
    ]


def test_scheduler_plans_and_status() -> None:
    plans = client.get("/okada/auto-calibration/scheduler/plans")
    assert plans.status_code == 200
    assert any(item["plan_name"] == "routing_guarded_daily" for item in plans.json())

    status = client.get("/okada/auto-calibration/scheduler/status")
    assert status.status_code == 200
    assert any(item["plan_name"] == "routing_guarded_daily" for item in status.json())


def test_scheduler_run_plan_for_routing() -> None:
    response = client.post(
        "/okada/auto-calibration/scheduler/run-plan",
        json={
            "plan_name": "routing_guarded_daily",
            "window_records": _routing_window(),
            "force": True,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["proposal_created"] is True
    assert body["action"] in {"proposal_ready", "auto_adopted"}
    assert body["lab_executed"] is True
    assert body["lab_suite_name"] == "routing_replay_smoke"
    assert body["lab_report_id"] is not None


def test_shadow_candidate_prepare_evaluate_promote() -> None:
    proposal = client.post(
        "/okada/auto-calibration/propose",
        json={
            "profile_name": "rag_default",
            "spec_id": "OKD-AI-004",
            "adapter_type": "rag",
            "window_records": _rag_window(),
        },
    ).json()
    validation = client.post(
        "/okada/auto-calibration/validate",
        json={
            "profile_name": "rag_default",
            "spec_id": "OKD-AI-004",
            "adapter_type": "rag",
            "proposed_policy": proposal["proposed_policy"],
            "window_records": _rag_window(),
        },
    ).json()
    prepared = client.post(
        "/okada/auto-calibration/champion-challenger/prepare",
        json={
            "profile_name": "rag_default",
            "spec_id": "OKD-AI-004",
            "adapter_type": "rag",
            "proposed_policy": proposal["proposed_policy"],
            "validation_report": validation,
            "operator_id": "tester",
        },
    )
    assert prepared.status_code == 200, prepared.text
    candidate_id = prepared.json()["candidate"]["candidate_id"]

    evaluated = client.post(
        "/okada/auto-calibration/champion-challenger/evaluate",
        json={
            "candidate_id": candidate_id,
            "window_records": _rag_window(),
            "run_calibration_lab": True,
            "lab_suite_name": "rag_replay_smoke",
            "persist_lab_report": True,
        },
    )
    assert evaluated.status_code == 200, evaluated.text
    assert "promotion_eligible" in evaluated.json()
    assert evaluated.json()["lab_summary"]["suite_name"] == "rag_replay_smoke"

    promoted = client.post(
        "/okada/auto-calibration/champion-challenger/promote",
        json={
            "candidate_id": candidate_id,
            "operator_id": "tester",
            "force": True,
        },
    )
    assert promoted.status_code == 200, promoted.text
    assert promoted.json()["promoted"] is True


def test_scheduler_run_plan_for_rag_creates_candidate_with_lab() -> None:
    response = client.post(
        "/okada/auto-calibration/scheduler/run-plan",
        json={
            "plan_name": "rag_shadow_daily",
            "window_records": _rag_window(),
            "force": True,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["action"] == "candidate_created"
    assert body["lab_executed"] is True
    assert body["lab_suite_name"] == "rag_replay_smoke"
    assert body["candidate_id"] is not None
