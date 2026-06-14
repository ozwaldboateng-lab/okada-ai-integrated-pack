from __future__ import annotations

from app.adapters.base import AdapterDecision, BaseAdapter
from app.core.scoring import build_score_contract, normalize_drift_observables


class DriftAdapter(BaseAdapter):
    name = "mlops"

    def diagnose(self, request, policy):
        numeric = normalize_drift_observables(request.observables)
        score = build_score_contract(
            h_dom=1.0
            - (
                numeric.get("feature_drift_score", 0.0) * 0.4
                + numeric.get("uncertainty_drift", 0.0) * 0.3
                + numeric.get("performance_decay_proxy", 0.0) * 0.3
            ),
            h_hist=numeric.get("calibration_lag", 0.0) * 0.7 + numeric.get("label_delay", 0.0) * 0.3,
            h_comp=numeric.get("challenger_disagreement", 0.0) * 0.5 + numeric.get("label_drift_proxy", 0.0) * 0.5,
            policy=policy,
        )
        regime = score.regime

        type_class = "II" if numeric.get("challenger_disagreement",0.0) > 0 else "I"
        trust_state = "safe" if regime == "clean" else "caution" if regime == "mixed" else "unsafe"
        handles = []
        for key, value in sorted(numeric.items(), key=lambda kv: kv[1], reverse=True)[:3]:
            if value > 0:
                handles.append(key.replace(".", "_"))
        if not handles:
            handles = ["no_signal"]

        recommended_action = "keep" if regime == "clean" else "shadow_deploy" if regime == "mixed" else ("rollback" if numeric.get("rollback_candidate_available",0.0) > 0.5 else "retrain")
        alternatives = ["watch", "retrain"] if regime == "mixed" else ["keep"] if regime == "clean" else ["retrain", "rollback"]

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
