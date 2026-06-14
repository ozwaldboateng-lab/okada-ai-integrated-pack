from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.main import app
from scripts.integration_demo import load_litellm_route_matrix, run_litellm_route_matrix


def test_litellm_route_matrix_has_three_outcomes() -> None:
    cases = load_litellm_route_matrix()

    assert len(cases) >= 3
    assert {case["expected_action"] for case in cases}.issuperset(
        {"cheap_route", "bounded_hybrid", "promote_strong_model"}
    )


def test_litellm_route_matrix_matches_gateway_outputs() -> None:
    results = run_litellm_route_matrix(TestClient(app))

    assert all(result["passed"] for result in results)
    assert all(result["audit_trace_id"] for result in results)
