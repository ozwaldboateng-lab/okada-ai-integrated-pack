from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_litellm_pre_route_endpoint_switches_to_strong_model() -> None:
    response = client.post(
        "/integrations/litellm/pre-route",
        json={
            "payload": {
                "model": "cheap-default",
                "messages": [{"role": "user", "content": "Need a careful answer"}],
                "metadata": {
                    "complexity_proxy": 0.95,
                    "historical_route_success": 0.55,
                    "budget_remaining": 0.7,
                    "latency_load_state": 0.2,
                    "risk_class": "high",
                },
            }
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["integration"] == "litellm"
    assert body["transformed_payload"]["metadata"]["okada_action"] in {
        "promote_strong_model",
        "bounded_hybrid",
        "branchwise_hybrid",
        "continue",
        "cheap_route",
    }



def test_dify_post_retrieval_endpoint_returns_branch_variables() -> None:
    response = client.post(
        "/integrations/dify/rag/post-retrieval",
        json={
            "payload": {
                "user_query": "What changed in the policy?",
                "retrieved_chunks": [
                    {"source": "old.md", "chunk_id": 0, "freshness_score": 0.1, "conflict": True},
                    {"source": "new.md", "chunk_id": 1, "freshness_score": 0.9},
                ],
                "retrieval_metadata": {"grounding_confidence": 0.4, "reranker_disagreement": 0.6},
                "context": {"question_time_sensitivity": 0.9},
            }
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["integration"] == "dify"
    assert "okada_recommended_action" in body["transformed_payload"]



def test_langgraph_step_endpoint_marks_interruptible_state() -> None:
    response = client.post(
        "/integrations/langgraph/step",
        json={
            "payload": {
                "user_request": "Summarize the latest docs and update the wiki",
                "plan": "search -> compare -> write",
                "tool_name": "wiki_write",
                "planner_executor_mismatch": 0.9,
                "tool_disagreement": 0.8,
                "retry_count": 3,
                "unresolved_subgoal_count": 2,
                "route_split_frequency": 0.7,
                "retrieval_contradiction_rate": 0.6,
                "context_age_penalty": 0.5,
                "remaining_step_budget": 2,
                "human_confirmation_available": True,
                "high_risk_action_flag": True,
            },
            "options": {"stage": "before_tool_call"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["integration"] == "langgraph"
    assert "governance_action" in body["transformed_payload"]
    assert "tool_policy" in body["audit_payload"]["decision"]



def test_openwebui_filter_endpoint_returns_audit_payload() -> None:
    response = client.post(
        "/integrations/openwebui/filter",
        json={
            "payload": {
                "chat_id": "chat-1",
                "messages": [{"role": "user", "content": "Why is the answer unstable?"}],
                "metadata": {
                    "confidence_trend": 0.25,
                    "calibration_error_trend": 0.7,
                    "fallback_rate": 0.4,
                    "override_rate": 0.3,
                    "latency_instability": 0.6,
                    "output_shift_score": 0.6,
                },
            },
            "options": {"user": {"id": "operator-1"}},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["integration"] == "openwebui"
    assert body["audit_payload"]["spec_id"] == "OKD-AI-001"
