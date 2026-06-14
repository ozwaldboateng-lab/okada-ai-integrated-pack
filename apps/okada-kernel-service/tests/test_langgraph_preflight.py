from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import langgraph_preflight  # noqa: E402


def test_langgraph_preflight_reports_missing_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OKADA_BASE_URL", raising=False)

    assert langgraph_preflight.check_env() == ["OKADA_BASE_URL"]


def test_langgraph_preflight_required_files_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(REPO_ROOT)

    assert langgraph_preflight.check_files() == []


def test_langgraph_preflight_gateway_smoke_calls_step_and_review(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    class DummyResponse:
        def __init__(self, payload: dict) -> None:
            self._payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self._payload

    def fake_post(url: str, json: dict, timeout: float) -> DummyResponse:
        calls.append(url)
        if url.endswith("/integrations/langgraph/step"):
            return DummyResponse(
                {
                    "transformed_payload": {
                        "governance_action": "human_handoff",
                        "requires_interrupt": True,
                        "audit_trace_id": "trace-lg",
                    }
                }
            )
        return DummyResponse({"transformed_payload": {"human_review_action": "constrained_continue"}})

    monkeypatch.setattr(langgraph_preflight.httpx, "post", fake_post)

    result = langgraph_preflight.run_gateway_smoke("http://localhost:8080")

    assert result["step_action"] == "human_handoff"
    assert result["review_action"] == "constrained_continue"
    assert [url.rsplit("/", 1)[-1] for url in calls] == ["step", "human-review"]
