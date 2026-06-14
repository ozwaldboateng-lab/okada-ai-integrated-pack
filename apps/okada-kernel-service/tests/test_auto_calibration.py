from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.core.policy import resolve_policy
from app.models.contracts import PolicyProfile

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
        {
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "invocation": "route",
            "observables": {
                "complexity_proxy": 0.55,
                "historical_route_success": 0.55,
                "budget_remaining": 0.4,
                "latency_load_state": 0.4,
                "retrieval_need_estimate": 0.5,
            },
            "context": {},
            "history_state": {},
            "resource_state": {},
            "expected_regime": "mixed",
            "expected_action": "bounded_hybrid",
            "outcome": {"success": True, "utility": 0.75, "quality": 0.8, "cost": 0.3, "latency_ms": 340},
        },
    ]


def test_auto_calibration_profiles_endpoint() -> None:
    response = client.get("/okada/auto-calibration/profiles")
    assert response.status_code == 200
    body = response.json()
    assert any(item["profile_name"] == "routing_default" for item in body)


def test_auto_calibration_propose_and_validate() -> None:
    propose_response = client.post(
        "/okada/auto-calibration/propose",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "window_records": _routing_window(),
        },
    )
    assert propose_response.status_code == 200, propose_response.text
    proposal = propose_response.json()
    assert "T_clean" in proposal["proposed_policy"]["thresholds"]
    assert "T_contam" in proposal["proposed_policy"]["thresholds"]

    validate_response = client.post(
        "/okada/auto-calibration/validate",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "proposed_policy": proposal["proposed_policy"],
            "window_records": _routing_window(),
        },
    )
    assert validate_response.status_code == 200, validate_response.text
    report = validate_response.json()
    assert "baseline_metrics" in report
    assert "candidate_metrics" in report
    assert report["mode"] == "guarded_auto_adopt"


def test_auto_calibration_adopt_updates_resolved_policy() -> None:
    proposal = client.post(
        "/okada/auto-calibration/propose",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "window_records": _routing_window(),
        },
    ).json()
    report = client.post(
        "/okada/auto-calibration/validate",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "proposed_policy": proposal["proposed_policy"],
            "window_records": _routing_window(),
        },
    ).json()
    adopt_response = client.post(
        "/okada/auto-calibration/adopt",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "proposed_policy": proposal["proposed_policy"],
            "validation_report": report,
            "operator_id": "tester",
            "force": True,
        },
    )
    assert adopt_response.status_code == 200, adopt_response.text
    body = adopt_response.json()
    assert body["adopted"] is True

    resolved = resolve_policy(PolicyProfile(profile_name="routing_default"))
    assert resolved.thresholds["T_clean"] == proposal["proposed_policy"]["thresholds"]["T_clean"]


def test_auto_calibration_validate_with_lab_replay() -> None:
    proposal = client.post(
        "/okada/auto-calibration/propose",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "window_records": _routing_window(),
        },
    ).json()
    validate_response = client.post(
        "/okada/auto-calibration/validate",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "proposed_policy": proposal["proposed_policy"],
            "window_records": _routing_window(),
            "run_calibration_lab": True,
            "lab_suite_name": "routing_replay_smoke",
            "persist_lab_report": True,
        },
    )
    assert validate_response.status_code == 200, validate_response.text
    report = validate_response.json()
    assert report["lab_summary"]["suite_name"] == "routing_replay_smoke"
    assert report["lab_report_id"]
