from __future__ import annotations

import os
from typing import Any


def build_dify_headers(shared_token: str | None = None) -> dict[str, str]:
    token = shared_token or os.getenv("OKADA_SHARED_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def build_pre_retrieval_payload(
    *,
    user_query: str,
    context: dict[str, Any] | None = None,
    history_state: dict[str, Any] | None = None,
    resource_state: dict[str, Any] | None = None,
    policy_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    history_state = history_state or {}
    resource_state = resource_state or {}

    observables = {
        "grounding_confidence": 0.0,
        "chunk_conflict_rate": 0.0,
        "index_age": float(context.get("index_age", 0.0)),
        "source_freshness": float(context.get("source_freshness", 0.5)),
        "retrieval_score_distribution": float(context.get("retrieval_score_distribution", 0.5)),
        "question_time_sensitivity": float(context.get("question_time_sensitivity", 0.5)),
        "chunk_redundancy": float(context.get("chunk_redundancy", 0.0)),
    }

    return {
        "spec_id": "OKD-AI-004",
        "adapter_type": "rag",
        "observables": observables,
        "context": {
            "user_query": user_query,
            "stage": "pre_retrieval",
            **context,
        },
        "history_state": history_state,
        "resource_state": resource_state,
        "policy_profile": policy_profile,
    }


def _extract_freshness(values: list[float]) -> float:
    if not values:
        return 0.0
    bounded = [min(1.0, max(0.0, v)) for v in values]
    return sum(bounded) / len(bounded)


def _extract_conflict(chunks: list[dict[str, Any]]) -> float:
    if not chunks:
        return 0.0
    conflict_flags = 0
    for chunk in chunks:
        if chunk.get("conflict") or chunk.get("contradiction"):
            conflict_flags += 1
    return conflict_flags / len(chunks)


def _extract_redundancy(chunks: list[dict[str, Any]]) -> float:
    if not chunks:
        return 0.0
    seen = set()
    duplicates = 0
    for chunk in chunks:
        key = (chunk.get("source"), chunk.get("chunk_id"), chunk.get("title"))
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates / len(chunks)


def build_post_retrieval_payload(
    *,
    user_query: str,
    retrieved_chunks: list[dict[str, Any]],
    retrieval_metadata: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    history_state: dict[str, Any] | None = None,
    resource_state: dict[str, Any] | None = None,
    policy_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    retrieval_metadata = retrieval_metadata or {}
    context = context or {}
    history_state = history_state or {}
    resource_state = resource_state or {}

    freshness_values = [
        float(chunk.get("freshness_score", chunk.get("source_freshness", 0.5)))
        for chunk in retrieved_chunks
    ]
    freshness = _extract_freshness(freshness_values)
    conflict = _extract_conflict(retrieved_chunks)
    redundancy = _extract_redundancy(retrieved_chunks)
    grounding_confidence = float(retrieval_metadata.get("grounding_confidence", max(0.0, 1.0 - conflict)))
    score_distribution = float(retrieval_metadata.get("retrieval_score_distribution", 0.5))
    index_age = float(retrieval_metadata.get("index_age", context.get("index_age", 0.0)))

    observables = {
        "grounding_confidence": grounding_confidence,
        "chunk_conflict_rate": conflict,
        "index_age": index_age,
        "source_freshness": freshness,
        "retrieval_score_distribution": score_distribution,
        "chunk_redundancy": redundancy,
        "reranker_disagreement": float(retrieval_metadata.get("reranker_disagreement", 0.0)),
        "question_time_sensitivity": float(context.get("question_time_sensitivity", 0.5)),
    }

    return {
        "spec_id": "OKD-AI-004",
        "adapter_type": "rag",
        "observables": observables,
        "context": {
            "user_query": user_query,
            "stage": "post_retrieval",
            "retrieved_count": len(retrieved_chunks),
            **context,
        },
        "history_state": history_state,
        "resource_state": resource_state,
        "policy_profile": policy_profile,
    }


def transform_kernel_response(okada_response: dict[str, Any]) -> dict[str, Any]:
    scores = okada_response.get("scores", {})
    action = okada_response.get("recommended_action", "continue")
    regime = okada_response.get("regime", "mixed")

    retrieval_action = action
    final_action = action
    should_abstain = action == "abstain"
    should_retrieve = action in {"standard_retrieve", "deeper_retrieve", "rerank_again", "require_fresh_source"}
    require_fresh_source = action == "require_fresh_source"
    rerank_again = action == "rerank_again"
    deeper_retrieve = action == "deeper_retrieve"

    return {
        "okada_regime": regime,
        "okada_type_class": okada_response.get("type_class", "undefined"),
        "okada_trust_state": okada_response.get("trust_state", "undefined"),
        "okada_recommended_action": action,
        "okada_retrieval_action": retrieval_action,
        "okada_final_action": final_action,
        "okada_should_retrieve": should_retrieve,
        "okada_should_abstain": should_abstain,
        "okada_require_fresh_source": require_fresh_source,
        "okada_rerank_again": rerank_again,
        "okada_deeper_retrieve": deeper_retrieve,
        "okada_audit_trace_id": okada_response.get("audit_trace_id", ""),
        "okada_alternatives": okada_response.get("alternatives", []),
        "okada_context_contamination_score": float(scores.get("context_contamination_score", 0.0)),
        "okada_freshness_gap_score": float(scores.get("freshness_gap_score", 0.0)),
        "okada_governance_available": True,
    }


def fail_safe_variables(
    *,
    reason: str,
    default_action: str = "standard_retrieve",
    default_regime: str = "mixed",
) -> dict[str, Any]:
    transformed = transform_kernel_response(
        {
            "regime": default_regime,
            "type_class": "undefined",
            "trust_state": "governance_unavailable",
            "recommended_action": default_action,
            "alternatives": [],
            "scores": {},
            "audit_trace_id": "",
        }
    )
    transformed["okada_governance_available"] = False
    transformed["okada_fail_safe_reason"] = reason
    return transformed
