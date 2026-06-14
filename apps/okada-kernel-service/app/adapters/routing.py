from __future__ import annotations

from app.adapters.base import AdapterDecision, BaseAdapter
from app.core.scoring import build_score_contract, normalize_routing_observables


class RoutingAdapter(BaseAdapter):
    name = "routing"

    def diagnose(self, request, policy):
        numeric = normalize_routing_observables(request.observables)
        risk_bonus = 0.0
        if request.context.get("high_risk_action_flag") or request.context.get("question_time_sensitivity") == "high":
            risk_bonus = policy.thresholds.get("high_risk_bonus", 0.15)

        score = build_score_contract(
            h_dom=1.0 - (numeric.get("complexity_proxy", 0.0) * 0.3 + numeric.get("latency_load_state", 0.0) * 0.2 + risk_bonus * 0.5),
            h_hist=(1.0 - numeric.get("historical_route_success", 1.0)) * 0.6 + numeric.get("budget_remaining", 0.0) * 0.0,
            h_comp=(
                numeric.get("retrieval_need_estimate", 0.0) * 0.4
                + numeric.get("latency_load_state", 0.0) * 0.3
                + (1.0 - numeric.get("budget_remaining", 1.0)) * 0.3
            ),
            policy=policy,
        )
        regime = score.regime

        type_class = "II" if numeric.get("retrieval_need_estimate",0.0) > 0.5 else "I"
        trust_state = "safe" if regime == "clean" else "caution" if regime == "mixed" else "unsafe"
        handles = []
        for key, value in sorted(numeric.items(), key=lambda kv: kv[1], reverse=True)[:3]:
            if value > 0:
                handles.append(key.replace(".", "_"))
        if not handles:
            handles = ["no_signal"]

        recommended_action = "cheap_route" if regime == "clean" else "bounded_hybrid" if regime == "mixed" else "promote_strong_model"
        alternatives = ["fallback_strong", "add_retrieval"] if regime != "clean" else ["cheap_route"]

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
