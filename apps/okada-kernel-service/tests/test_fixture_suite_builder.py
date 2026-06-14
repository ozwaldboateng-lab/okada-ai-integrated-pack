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


def test_build_fixture_suite_persists_and_updates_manifest() -> None:
    suite_name = 'generated_routing_builder_smoke'
    response = client.post(
        '/okada/auto-calibration/lab/build-suite',
        json={
            'profile_name': 'routing_default',
            'spec_id': 'OKD-AI-005',
            'adapter_type': 'routing',
            'suite_name': suite_name,
            'window_records': _routing_window(),
            'overwrite': True,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['suite_name'] == suite_name
    assert body['manifest_updated'] is True
    assert body['summary']['case_count'] == 2
    assert body['fixture_path'].endswith(f'{suite_name}.jsonl')

    suites = client.get('/okada/auto-calibration/lab/suites').json()
    assert any(item['suite_name'] == suite_name for item in suites)


def test_generated_suite_can_be_replayed() -> None:
    suite_name = 'generated_routing_replay_smoke'
    build = client.post(
        '/okada/auto-calibration/lab/build-suite',
        json={
            'profile_name': 'routing_default',
            'spec_id': 'OKD-AI-005',
            'adapter_type': 'routing',
            'suite_name': suite_name,
            'window_records': _routing_window(),
            'overwrite': True,
        },
    )
    assert build.status_code == 200, build.text

    replay = client.post(
        '/okada/auto-calibration/lab/replay',
        json={
            'profile_name': 'routing_default',
            'spec_id': 'OKD-AI-005',
            'adapter_type': 'routing',
            'suite_name': suite_name,
            'persist_report': False,
        },
    )
    assert replay.status_code == 200, replay.text
    body = replay.json()
    assert body['suite_name'] == suite_name
    assert body['summary']['case_count'] == 2


def test_fixture_suite_build_history_appends() -> None:
    before = client.get('/okada/auto-calibration/lab/build-history').json()
    response = client.post(
        '/okada/auto-calibration/lab/build-suite',
        json={
            'profile_name': 'routing_default',
            'spec_id': 'OKD-AI-005',
            'adapter_type': 'routing',
            'suite_name': 'generated_routing_build_history',
            'window_records': _routing_window(),
            'overwrite': True,
        },
    )
    assert response.status_code == 200, response.text
    after = client.get('/okada/auto-calibration/lab/build-history').json()
    assert len(after) >= len(before) + 1
