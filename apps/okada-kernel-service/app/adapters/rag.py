from __future__ import annotations

from app.adapters.base import AdapterDecision, BaseAdapter
from app.core.scoring import build_score_contract, normalize_rag_observables


class RagAdapter(BaseAdapter):
    name = "rag"

    def diagnose(self, request, policy):
        numeric = normalize_rag_observables(request.observables)
        risk_bonus = 0.0
        if request.context.get("high_risk_action_flag") or request.context.get("question_time_sensitivity") == "high":
            risk_bonus = policy.thresholds.get("high_risk_bonus", 0.15)

        score = build_score_contract(
            h_dom=1.0
            - (
                numeric.get("chunk_conflict_rate", 0.0) * 0.35
                + (1.0 - numeric.get("grounding_confidence", 1.0)) * 0.45
                + risk_bonus * 0.2
            ),
            h_hist=numeric.get("index_age", 0.0) * 0.6 + (1.0 - numeric.get("source_freshness", 1.0)) * 0.4,
            h_comp=(
                numeric.get("reranker_disagreement", 0.0) * 0.5
                + numeric.get("retrieval_score_distribution", 0.0) * 0.15
                + numeric.get("chunk_redundancy", 0.0) * 0.35
            ),
            policy=policy,
        )
        regime = score.regime

        type_class = "II" if numeric.get("chunk_conflict_rate",0.0) > 0 else "I"
        trust_state = "safe" if regime == "clean" else "caution" if regime == "mixed" else "unsafe"
        handles = []
        for key, value in sorted(numeric.items(), key=lambda kv: kv[1], reverse=True)[:3]:
            if value > 0:
                handles.append(key.replace(".", "_"))
        if not handles:
            handles = ["no_signal"]

        recommended_action = "no_retrieval" if regime == "clean" and numeric.get("grounding_confidence",0.0) > 0.8 else "deeper_retrieve" if regime == "mixed" else "abstain"
        alternatives = ["rerank_again", "require_fresh_source"] if regime != "clean" else ["standard_retrieval"]

        return AdapterDecision(
            normalized_inputs=numeric,
            derived_features=score.as_derived_features(),
            regime=regime,
            type_class=type_class,
            trust_state=trust_state,
            first_visible_handle=handles,
            recommended_action=recommended_action,
            alternatives=alternatives,
        )
