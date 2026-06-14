from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app


REPO_ROOT = Path(__file__).resolve().parents[3]
ACCEPTANCE_FIXTURE = REPO_ROOT / "fixtures" / "acceptance" / "kernel_adapter_acceptance.jsonl"


def _load_cases() -> list[dict[str, Any]]:
    with ACCEPTANCE_FIXTURE.open(encoding="utf-8") as fixture:
        return [json.loads(line) for line in fixture if line.strip()]


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["scenario_id"])
def test_kernel_adapter_acceptance_scenarios(case: dict[str, Any]) -> None:
    client = TestClient(app)
    mode = case["mode"]
    payload = {
        "spec_id": case["spec_id"],
        "adapter_type": case["adapter_type"],
        "observables": case["observables"],
        "context": case["context"],
        "history_state": case["history_state"],
        "resource_state": case["resource_state"],
    }

    response = client.post(f"/okada/{mode}", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["spec_id"] == case["spec_id"]
    assert body["regime"] == case["expected_regime"]
    assert body["recommended_action"] == case["expected_action"]
    assert body["trust_state"] == case["expected_trust_state"]
    assert body["audit_persisted"] is True
    assert body["audit_trace_id"]
    assert set(body["scores"]).issuperset({"H_dom", "H_hist", "H_comp", "R_diag"})
