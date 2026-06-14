from __future__ import annotations

import importlib.util
from pathlib import Path

from app.integrations.dify_runtime import (
    build_dify_headers,
    build_post_retrieval_payload,
    build_pre_retrieval_payload,
    fail_safe_variables,
    transform_kernel_response,
)


def _load_code_node_transform():
    path = Path(__file__).resolve().parents[3] / "examples" / "dify" / "code_node_transform.py"
    spec = importlib.util.spec_from_file_location("dify_code_node_transform", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


def test_build_pre_retrieval_payload_sets_rag_defaults() -> None:
    payload = build_pre_retrieval_payload(
        user_query="latest policy update",
        context={"index_age": 0.8, "source_freshness": 0.3, "question_time_sensitivity": 1.0},
    )
    assert payload["spec_id"] == "OKD-AI-004"
    assert payload["adapter_type"] == "rag"
    assert payload["context"]["stage"] == "pre_retrieval"
    assert payload["observables"]["index_age"] == 0.8
    assert payload["observables"]["source_freshness"] == 0.3


def test_build_post_retrieval_payload_derives_conflict_and_redundancy() -> None:
    payload = build_post_retrieval_payload(
        user_query="what changed?",
        retrieved_chunks=[
            {"source": "a.md", "chunk_id": 1, "freshness_score": 0.2, "conflict": True},
            {"source": "a.md", "chunk_id": 1, "freshness_score": 0.6},
            {"source": "b.md", "chunk_id": 4, "freshness_score": 0.8},
        ],
        retrieval_metadata={"grounding_confidence": 0.4, "reranker_disagreement": 0.5},
        context={"question_time_sensitivity": 0.9},
    )
    obs = payload["observables"]
    assert payload["context"]["stage"] == "post_retrieval"
    assert obs["grounding_confidence"] == 0.4
    assert obs["chunk_conflict_rate"] > 0.0
    assert obs["chunk_redundancy"] > 0.0
    assert obs["source_freshness"] > 0.0


def test_transform_kernel_response_exposes_dify_branch_variables() -> None:
    variables = transform_kernel_response(
        {
            "regime": "mixed",
            "type_class": "II",
            "trust_state": "caution",
            "recommended_action": "deeper_retrieve",
            "audit_trace_id": "trace-1",
            "alternatives": ["abstain"],
            "scores": {
                "context_contamination_score": 0.7,
                "freshness_gap_score": 0.8,
            },
        }
    )
    assert variables["okada_retrieval_action"] == "deeper_retrieve"
    assert variables["okada_deeper_retrieve"] is True
    assert variables["okada_should_retrieve"] is True
    assert variables["okada_governance_available"] is True


def test_fail_safe_variables_marks_governance_unavailable() -> None:
    variables = fail_safe_variables(reason="timeout")
    assert variables["okada_governance_available"] is False
    assert variables["okada_fail_safe_reason"] == "timeout"
    assert variables["okada_recommended_action"] == "standard_retrieve"


def test_dify_code_node_transform_has_missing_gateway_fallback() -> None:
    transform_code_node = _load_code_node_transform()
    variables = transform_code_node({})

    assert variables["okada_governance_available"] is False
    assert variables["okada_recommended_action"] == "standard_retrieve"
    assert variables["okada_should_retrieve"] is True
    assert variables["okada_fail_safe_reason"] == "missing_gateway_response"


def test_build_dify_headers_includes_bearer_token_when_present(monkeypatch) -> None:
    monkeypatch.setenv("OKADA_SHARED_TOKEN", "abc123")
    headers = build_dify_headers()
    assert headers["Authorization"] == "Bearer abc123"
    assert headers["Content-Type"] == "application/json"
