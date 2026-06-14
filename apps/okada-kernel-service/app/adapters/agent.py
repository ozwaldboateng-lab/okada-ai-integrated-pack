from __future__ import annotations

from app.adapters.base import AdapterDecision, BaseAdapter
from app.core.scoring import build_score_contract, normalize_agent_observables


class AgentAdapter(BaseAdapter):
    name = "agent"

    def diagnose(self, request, policy):
        numeric = normalize_agent_observables(request.observables)
        risk_bonus = 0.0
        if request.context.get("high_risk_action_flag") or request.context.get("question_time_sensitivity") == "high":
            risk_bonus = policy.thresholds.get("high_risk_bonus", 0.15)

        score = build_score_contract(
            h_dom=1.0
            - (
                numeric.get("planner_executor_mismatch", 0.0) * 0.35
                + numeric.get("route_split_frequency", 0.0) * 0.25
                + numeric.get("retry_count", 0.0) * 0.2
                + risk_bonus * 0.2
            ),
            h_hist=numeric.get("context_age_penalty", 0.0) * 0.5 + numeric.get("unresolved_subgoal_count", 0.0) * 0.5,
            h_comp=numeric.get("tool_disagreement", 0.0) * 0.5 + numeric.get("retrieval_contradiction_rate", 0.0) * 0.5,
            policy=policy,
        )
        regime = score.regime

        type_class = "III" if numeric.get("route_split_frequency",0.0) > 0.5 else "II" if numeric.get("tool_disagreement",0.0) > 0 else "I"
        trust_state = "safe" if regime == "clean" else "caution" if regime == "mixed" else "unsafe"
        handles = []
        for key, value in sorted(numeric.items(), key=lambda kv: kv[1], reverse=True)[:3]:
            if value > 0:
                handles.append(key.replace(".", "_"))
        if not handles:
            handles = ["no_signal"]

        recommended_action = "continue" if regime == "clean" else "replan" if regime == "mixed" else ("abort" if request.context.get("high_risk_action_flag") else "human_handoff")
        alternatives = ["constrained_continue", "human_handoff"] if regime == "mixed" else ["continue"] if regime == "clean" else ["replan", "abort"]

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
