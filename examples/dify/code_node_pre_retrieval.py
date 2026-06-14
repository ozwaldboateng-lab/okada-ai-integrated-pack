def main(gateway_response: dict) -> dict:
    transformed = gateway_response.get("transformed_payload", {})
    if transformed:
        return transformed
    return {
        "okada_regime": "mixed",
        "okada_trust_state": "undefined",
        "okada_recommended_action": "standard_retrieve",
        "okada_retrieval_action": "standard_retrieve",
        "okada_should_retrieve": True,
        "okada_should_abstain": False,
        "okada_deeper_retrieve": False,
        "okada_audit_trace_id": "",
        "okada_context_contamination_score": 0.0,
        "okada_freshness_gap_score": 0.0,
        "okada_governance_available": False,
    }
