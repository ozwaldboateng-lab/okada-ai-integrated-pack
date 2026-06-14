from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.auto_calibration.window_aggregator import calibration_window_service
from app.main import app
from app.models.auto_calibration import CalibrationWindowRequest
from app.models.contracts import AuditRecord

client = TestClient(app)


def _audit(*, ts_offset_hours: int, spec_id: str = "OKD-AI-005", adapter_type: str = "routing", risk_class: str = "standard", complexity: float = 0.5) -> AuditRecord:
    now = datetime.now(timezone.utc)
    return AuditRecord(
        audit_trace_id=f"audit-{ts_offset_hours}-{risk_class}",
        timestamp=now - timedelta(hours=ts_offset_hours),
        spec_id=spec_id,
        adapter_type=adapter_type,
        raw_inputs={
            "observables": {
                "complexity_proxy": complexity,
                "historical_route_success": 0.7,
                "budget_remaining": 0.6,
                "latency_load_state": 0.3,
                "retrieval_need_estimate": 0.2,
            },
            "context": {"risk_class": risk_class},
            "history_state": {},
            "resource_state": {"latency_ms": 200 + ts_offset_hours, "cost": 0.1},
        },
        normalized_inputs={},
        derived_features={"H_dom": 0.6, "H_hist": 0.2, "H_comp": 0.2, "R_diag": 0.66},
        decision={"regime": "clean", "recommended_action": "cheap_route"},
        alternatives=[],
        policy_snapshot={},
    )



def test_window_aggregator_request_or_time_backfills(monkeypatch) -> None:
    audits = [
        _audit(ts_offset_hours=2, risk_class="high", complexity=0.9),
        _audit(ts_offset_hours=4, risk_class="standard", complexity=0.6),
        _audit(ts_offset_hours=30, risk_class="standard", complexity=0.4),
        _audit(ts_offset_hours=48, risk_class="standard", complexity=0.3),
    ]
    monkeypatch.setattr("app.auto_calibration.window_aggregator.audit_store.list_records", lambda: audits)
    response = calibration_window_service.resolve(
        CalibrationWindowRequest(
            profile_name="routing_default",
            spec_id="OKD-AI-005",
            adapter_type="routing",
            min_requests=3,
            max_age_hours=12,
        )
    )
    assert response.summary.available_count == 4
    assert response.summary.selected_count == 3
    assert response.summary.backfilled_count == 1
    assert response.summary.risk_class_breakdown["high"] == 1



def test_window_aggregator_api_filters_risk_class(monkeypatch) -> None:
    audits = [
        _audit(ts_offset_hours=1, risk_class="high"),
        _audit(ts_offset_hours=3, risk_class="standard"),
        _audit(ts_offset_hours=6, risk_class="high"),
    ]
    monkeypatch.setattr("app.auto_calibration.window_aggregator.audit_store.list_records", lambda: audits)
    response = client.post(
        "/okada/auto-calibration/windows/resolve",
        json={
            "profile_name": "routing_default",
            "spec_id": "OKD-AI-005",
            "adapter_type": "routing",
            "risk_class": "high",
            "max_records": 10,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["summary"]["selected_count"] == 2
    assert set(body["summary"]["risk_class_breakdown"].keys()) == {"high"}



def test_scheduler_run_plan_uses_aggregated_window(monkeypatch) -> None:
    audits = [
        _audit(ts_offset_hours=1, complexity=0.85),
        _audit(ts_offset_hours=2, complexity=0.25),
        _audit(ts_offset_hours=3, complexity=0.55),
    ]
    monkeypatch.setattr("app.auto_calibration.window_aggregator.audit_store.list_records", lambda: audits)
    response = client.post(
        "/okada/auto-calibration/scheduler/run-plan",
        json={
            "plan_name": "routing_guarded_daily",
            "force": True,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["proposal_created"] is True
    assert body["action"] in {"proposal_ready", "auto_adopted"}
