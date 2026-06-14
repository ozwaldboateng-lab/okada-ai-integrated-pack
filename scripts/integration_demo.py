from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[1]
LITELLM_ROUTE_MATRIX = REPO_ROOT / "examples" / "litellm" / "route_matrix.json"


def call(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    response.raise_for_status()
    return response.json()


def load_litellm_route_matrix(path: Path = LITELLM_ROUTE_MATRIX) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_litellm_route_matrix(client: TestClient) -> list[dict]:
    results: list[dict] = []
    for case in load_litellm_route_matrix():
        body = call(
            client,
            "/integrations/litellm/pre-route",
            {"payload": case["payload"], "options": {}},
        )
        transformed = body.get("transformed_payload", {})
        metadata = transformed.get("metadata", {})
        result = {
            "scenario_id": case["scenario_id"],
            "expected_action": case["expected_action"],
            "actual_action": metadata.get("okada_action"),
            "expected_model": case["expected_model"],
            "actual_model": transformed.get("model"),
            "audit_trace_id": metadata.get("okada_audit_trace_id", ""),
        }
        result["passed"] = (
            result["expected_action"] == result["actual_action"]
            and result["expected_model"] == result["actual_model"]
            and bool(result["audit_trace_id"])
        )
        results.append(result)
    return results


def main() -> None:
    client = TestClient(app)

    examples = [
        (
            "/integrations/litellm/pre-route",
            {
                "payload": {
                    "model": "cheap-default",
                    "messages": [{"role": "user", "content": "Give me a careful answer with citations."}],
                    "metadata": {
                        "complexity_proxy": 0.92,
                        "historical_route_success": 0.55,
                        "budget_remaining": 0.8,
                        "latency_load_state": 0.25,
                        "risk_class": "high",
                    },
                }
            },
        ),
        (
            "/integrations/dify/rag/post-retrieval",
            {
                "payload": {
                    "user_query": "Which source is freshest?",
                    "retrieved_chunks": [
                        {"source": "policy-old.md", "chunk_id": 0, "freshness_score": 0.2, "conflict": True},
                        {"source": "policy-new.md", "chunk_id": 1, "freshness_score": 0.9},
                    ],
                    "retrieval_metadata": {"grounding_confidence": 0.45, "reranker_disagreement": 0.4},
                    "context": {"question_time_sensitivity": 0.9},
                }
            },
        ),
        (
            "/integrations/langgraph/step",
            {
                "payload": {
                    "user_request": "Update the runbook and publish it",
                    "plan": "search -> compare -> write",
                    "tool_name": "wiki_write",
                    "planner_executor_mismatch": 0.8,
                    "tool_disagreement": 0.65,
                    "retry_count": 2,
                    "unresolved_subgoal_count": 1,
                    "route_split_frequency": 0.5,
                    "retrieval_contradiction_rate": 0.4,
                    "context_age_penalty": 0.5,
                    "remaining_step_budget": 2,
                    "human_confirmation_available": True,
                    "high_risk_action_flag": True,
                },
                "options": {"stage": "before_tool_call"},
            },
        ),
    ]

    for path, payload in examples:
        body = call(client, path, payload)
        print(f"\n=== {path} ===")
        print(f"integration: {body['integration']}")
        print(f"stage: {body['stage']}")
        if body.get("kernel_decision"):
            kd = body["kernel_decision"]
            print(f"regime/action: {kd.get('regime')} / {kd.get('recommended_action')}")
        if body.get("notes"):
            print(f"notes: {', '.join(body['notes'])}")

    print("\n=== LiteLLM route matrix ===")
    matrix_results = run_litellm_route_matrix(client)
    for result in matrix_results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"{status} {result['scenario_id']}: "
            f"action={result['actual_action']} model={result['actual_model']} audit={result['audit_trace_id']}"
        )
    if not all(result["passed"] for result in matrix_results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
