from __future__ import annotations

import json
import os
from pathlib import Path

import httpx


REQUIRED_ENV = ["OKADA_BASE_URL"]
REQUIRED_FILES = [
    Path("examples/langgraph/okada_agent_graph.py"),
    Path("examples/langgraph/state_schema.py"),
    Path("examples/langgraph/human_review_contract.yaml"),
    Path("examples/langgraph/checkpoint_config.example.json"),
]


def check_env() -> list[str]:
    return [key for key in REQUIRED_ENV if not os.getenv(key)]


def check_files() -> list[str]:
    return [str(path) for path in REQUIRED_FILES if not path.exists()]


def run_gateway_smoke(base_url: str) -> dict:
    state = {
        "thread_id": "preflight-thread",
        "checkpoint_id": "preflight-checkpoint",
        "run_id": "preflight-run",
        "user_request": "Review a high-risk tool call",
        "plan": "draft -> write",
        "current_step": "before_tool",
        "tool_name": "wiki_write",
        "planner_executor_mismatch": 0.9,
        "tool_disagreement": 0.8,
        "retry_count": 2,
        "unresolved_subgoal_count": 2,
        "route_split_frequency": 0.7,
        "retrieval_contradiction_rate": 0.6,
        "context_age_penalty": 0.5,
        "remaining_step_budget": 2,
        "human_confirmation_available": True,
        "high_risk_action_flag": True,
    }
    step = httpx.post(
        f"{base_url.rstrip('/')}/integrations/langgraph/step",
        json={"payload": state, "options": {"stage": "before_tool"}},
        timeout=10.0,
    )
    step.raise_for_status()
    step_payload = step.json()
    mutated = step_payload.get("transformed_payload", {})
    review = httpx.post(
        f"{base_url.rstrip('/')}/integrations/langgraph/human-review",
        json={
            "payload": {
                "state": mutated,
                "human_review": {"action": "constrained_continue", "notes": "preflight read-only"},
            },
            "options": {"default_action": mutated.get("governance_action", "human_handoff")},
        },
        timeout=10.0,
    )
    review.raise_for_status()
    return {
        "step_action": mutated.get("governance_action"),
        "requires_interrupt": mutated.get("requires_interrupt"),
        "review_action": review.json().get("transformed_payload", {}).get("human_review_action"),
    }


def main() -> int:
    missing_env = check_env()
    missing_files = check_files()

    report = {
        "missing_env": missing_env,
        "missing_files": missing_files,
        "ok": not missing_env and not missing_files,
    }
    if report["ok"]:
        try:
            report["gateway_smoke"] = run_gateway_smoke(os.environ["OKADA_BASE_URL"])
        except Exception as exc:
            report["ok"] = False
            report["gateway_smoke_error"] = str(exc)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
