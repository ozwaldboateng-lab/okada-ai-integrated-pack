from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import litellm_preflight  # noqa: E402


def test_litellm_preflight_reports_missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OKADA_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE", raising=False)

    missing = litellm_preflight.check_env(["OKADA_BASE_URL", "OPENAI_API_BASE"])

    assert missing == ["OKADA_BASE_URL", "OPENAI_API_BASE"]


def test_litellm_preflight_rejects_missing_route_map(tmp_path: Path) -> None:
    ok, message = litellm_preflight.check_route_map(str(tmp_path / "missing.json"))

    assert ok is False
    assert "Route map does not exist" in message


def test_litellm_preflight_gateway_smoke_exercises_pre_and_post(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_post_json(base_url: str, path: str, payload: dict) -> dict:
        calls.append(path)
        if path == "/integrations/litellm/pre-route":
            return {
                "integration": "litellm",
                "transformed_payload": {
                    "model": "strong-default",
                    "metadata": {
                        "okada_action": "promote_strong_model",
                        "okada_audit_trace_id": "trace-1",
                    },
                },
            }
        return {"integration": "litellm", "audit_payload": {"audit_trace_id": "trace-1"}}

    monkeypatch.setattr(litellm_preflight, "post_json", fake_post_json)

    ok, message = litellm_preflight.run_gateway_smoke("http://localhost:8080", None)

    assert ok is True
    assert calls == ["/integrations/litellm/pre-route", "/integrations/litellm/post-audit"]
    assert "post-audit=OK" in message
