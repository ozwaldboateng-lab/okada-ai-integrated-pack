from __future__ import annotations

from app.adapters.base import AdapterDecision, BaseAdapter
from app.core.scoring import build_score_contract, normalize_monitoring_observables


class MonitoringAdapter(BaseAdapter):
    name = "monitoring"

    def diagnose(self, request, policy):
        numeric = normalize_monitoring_observables(request.observables)
        risk_bonus = 0.0
        if request.context.get("high_risk_action_flag") or request.context.get("question_time_sensitivity") == "high":
            risk_bonus = policy.thresholds.get("high_risk_bonus", 0.15)

        score = build_score_contract(
            h_dom=1.0 - (
                numeric.get("fallback_rate", 0.0) * 0.4
                + numeric.get("override_rate", 0.0) * 0.3
                + numeric.get("latency_instability", 0.0) * 0.3
                + risk_bonus
            ),
            h_hist=numeric.get("calibration_error_trend", 0.0) * 0.6 + numeric.get("output_shift_score", 0.0) * 0.4,
            h_comp=(
                numeric.get("delayed_gt_disagreement", 0.0) * 0.5
                + numeric.get("tool_failure_rate", 0.0) * 0.25
                + numeric.get("complaint_rate", 0.0) * 0.25
            ),
            policy=policy,
        )
        regime = score.regime

        type_class = "I" if numeric.get("override_rate",0.0) > numeric.get("tool_failure_rate",0.0) else "II" if numeric.get("tool_failure_rate",0.0) > 0 else "undefined"
        trust_state = "safe" if regime == "clean" else "caution" if regime == "mixed" else "unsafe"
        handles = []
        for key, value in sorted(numeric.items(), key=lambda kv: kv[1], reverse=True)[:3]:
            if value > 0:
                handles.append(key.replace(".", "_"))
        if not handles:
            handles = ["no_signal"]

        recommended_action = "continue" if regime == "clean" else "shadow_validation" if regime == "mixed" else "human_review"
        alternatives = ["alert", "rollback"] if regime != "clean" else ["continue"]

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
