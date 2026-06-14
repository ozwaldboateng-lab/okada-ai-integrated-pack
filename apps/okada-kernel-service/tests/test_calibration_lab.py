from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_lab_suites_available() -> None:
    response = client.get('/okada/auto-calibration/lab/suites')
    assert response.status_code == 200, response.text
    body = response.json()
    names = {item['suite_name'] for item in body}
    assert 'routing_replay_smoke' in names
    assert 'rag_replay_smoke' in names


def test_lab_replay_generates_report_for_routing() -> None:
    response = client.post(
        '/okada/auto-calibration/lab/replay',
        json={
            'profile_name': 'routing_default',
            'spec_id': 'OKD-AI-005',
            'adapter_type': 'routing',
            'suite_name': 'routing_replay_smoke',
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['proposal_source'] == 'generated_proposal'
    assert body['report_id']
    assert body['report_path']
    assert body['summary']['case_count'] >= 2


def test_lab_history_appends_after_replay() -> None:
    before = client.get('/okada/auto-calibration/lab/history').json()
    replay = client.post(
        '/okada/auto-calibration/lab/replay',
        json={
            'profile_name': 'rag_default',
            'spec_id': 'OKD-AI-004',
            'adapter_type': 'rag',
            'suite_name': 'rag_replay_smoke',
        },
    )
    assert replay.status_code == 200, replay.text
    after = client.get('/okada/auto-calibration/lab/history').json()
    assert len(after) >= len(before) + 1
