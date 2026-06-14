def main(okada_response: dict) -> dict:
    transformed = okada_response.get("transformed_payload", {})
    if transformed:
        return transformed
    if not okada_response:
        return {
            "okada_regime": "mixed",
            "okada_type_class": "undefined",
            "okada_trust_state": "governance_unavailable",
            "okada_recommended_action": "standard_retrieve",
            "okada_retrieval_action": "standard_retrieve",
            "okada_final_action": "standard_retrieve",
            "okada_should_retrieve": True,
            "okada_should_abstain": False,
            "okada_require_fresh_source": False,
            "okada_rerank_again": False,
            "okada_deeper_retrieve": False,
            "okada_audit_trace_id": "",
            "okada_alternatives": [],
            "okada_context_contamination_score": 0.0,
            "okada_freshness_gap_score": 0.0,
            "okada_governance_available": False,
            "okada_fail_safe_reason": "missing_gateway_response",
        }
    scores = okada_response.get("scores", {})
    return {
        "okada_regime": okada_response.get("regime", "mixed"),
        "okada_type_class": okada_response.get("type_class", "undefined"),
        "okada_trust_state": okada_response.get("trust_state", "undefined"),
        "okada_recommended_action": okada_response.get("recommended_action", "continue"),
        "okada_retrieval_action": okada_response.get("recommended_action", "continue"),
        "okada_final_action": okada_response.get("recommended_action", "continue"),
        "okada_should_retrieve": okada_response.get("recommended_action") in {"standard_retrieve", "deeper_retrieve"},
        "okada_should_abstain": okada_response.get("recommended_action") == "abstain",
        "okada_require_fresh_source": okada_response.get("recommended_action") == "require_fresh_source",
        "okada_rerank_again": okada_response.get("recommended_action") == "rerank_again",
        "okada_deeper_retrieve": okada_response.get("recommended_action") == "deeper_retrieve",
        "okada_audit_trace_id": okada_response.get("audit_trace_id", ""),
        "okada_alternatives": okada_response.get("alternatives", []),
        "okada_context_contamination_score": scores.get("context_contamination_score", 0.0),
        "okada_freshness_gap_score": scores.get("freshness_gap_score", 0.0),
        "okada_governance_available": True,
    }
