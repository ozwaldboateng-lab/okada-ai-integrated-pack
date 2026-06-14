from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import openwebui_preflight  # noqa: E402


def test_openwebui_manifest_declares_packaged_artifacts() -> None:
    manifest = openwebui_preflight.load_manifest()

    assert manifest["install_order"] == ["okada-governance-pipe", "okada-audit-filter"]
    assert "OKADA_BASE_URL" in manifest["required_env"]
    assert {component["endpoint"] for component in manifest["components"]} == {
        "/integrations/openwebui/pipe",
        "/integrations/openwebui/filter",
    }
    assert openwebui_preflight.check_manifest(manifest) == []


def test_openwebui_manual_eval_plan_links_routing_rag_and_audit_artifacts() -> None:
    plan = openwebui_preflight.load_manual_eval_plan()

    assert openwebui_preflight.check_manual_eval_plan(plan) == []
    assert {case["adapter_type"] for case in plan["cases"]} == {"routing", "rag"}
    assert "data/audit/audit_records.jsonl" in plan["expected_artifacts"]
    assert "data/benchmarks/e2e_summary.json" in plan["expected_artifacts"]


def test_openwebui_preflight_gateway_smoke_calls_pipe_and_filter(monkeypatch) -> None:
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
        if url.endswith("/integrations/openwebui/pipe"):
            return DummyResponse(
                {
                    "transformed_payload": {
                        "selected_model": "gpt-4.1",
                        "metadata": {"okada_action": "promote_strong_model"},
                    }
                }
            )
        return DummyResponse(
            {
                "transformed_payload": {"metadata": {"okada_action": "human_review"}},
                "audit_payload": {"spec_id": "OKD-AI-001"},
            }
        )

    monkeypatch.setattr(openwebui_preflight.httpx, "post", fake_post)

    result = openwebui_preflight.run_gateway_smoke("http://localhost:8080")

    assert result["pipe_selected_model"] == "gpt-4.1"
    assert result["filter_audit_spec"] == "OKD-AI-001"
    assert [url.rsplit("/", 1)[-1] for url in calls] == ["pipe", "filter"]
