from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from app.models.auto_calibration import CalibrationSummary, ProfileCatalogEntry
from app.models.contracts import PolicyProfile



def _bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class ProposalGenerationResult:
    thresholds: dict[str, float] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    strategy_name: str = "common"


class ProposalGeneratorService:
    def _apply_threshold(self, current_value: float, target_value: float, max_delta: float, low: float, high: float) -> float:
        clipped = _bounded(target_value, current_value - max_delta, current_value + max_delta)
        return round(_bounded(clipped, low, high), 4)

    def _common_thresholds(
        self,
        *,
        summary: CalibrationSummary,
        current_policy: PolicyProfile,
        entry: ProfileCatalogEntry,
        max_delta: float,
    ) -> dict[str, float]:
        thresholds: dict[str, float] = {}
        target_clean = _bounded(summary.rdiag_p40, 0.15, 0.90)
        target_contam = _bounded(max(summary.rdiag_p80, target_clean + 0.15), target_clean + 0.05, 1.50)
        if "T_clean" in entry.mutable_thresholds:
            thresholds["T_clean"] = self._apply_threshold(current_policy.thresholds["T_clean"], target_clean, max_delta, 0.15, 0.90)
        if "T_contam" in entry.mutable_thresholds:
            thresholds["T_contam"] = self._apply_threshold(current_policy.thresholds["T_contam"], target_contam, max_delta, target_clean + 0.05, 1.50)
        return thresholds

    def _common_weights(self, *, summary: CalibrationSummary, entry: ProfileCatalogEntry) -> dict[str, float]:
        total = summary.mean_h_dom + summary.mean_h_hist + summary.mean_h_comp + 1e-6
        candidate_weights = {
            "W_dom": round(_bounded((summary.mean_h_dom / total) * 3.0, 0.5, 2.0), 4),
            "W_hist": round(_bounded((summary.mean_h_hist / total) * 3.0, 0.5, 2.0), 4),
            "W_comp": round(_bounded((summary.mean_h_comp / total) * 3.0, 0.5, 2.0), 4),
        }
        return {k: v for k, v in candidate_weights.items() if k in entry.mutable_weights}

    def _routing(
        self,
        *,
        summary: CalibrationSummary,
        current_policy: PolicyProfile,
        entry: ProfileCatalogEntry,
        max_delta: float,
    ) -> ProposalGenerationResult:
        metrics = summary.adapter_metrics
        thresholds = self._common_thresholds(summary=summary, current_policy=current_policy, entry=entry, max_delta=max_delta)
        promotion_pressure = float(metrics.get("promotion_pressure_mean", 0.0))
        budget_tight = float(metrics.get("budget_tight_rate", 0.0))
        latency_load = float(metrics.get("latency_load_mean", 0.0))
        complexity = float(metrics.get("complexity_mean", 0.0))

        if "promotion_threshold" in entry.mutable_thresholds:
            target = 0.35 + 0.45 * promotion_pressure + 0.15 * budget_tight + 0.10 * latency_load + 0.05 * complexity
            thresholds["promotion_threshold"] = self._apply_threshold(
                current_policy.thresholds.get("promotion_threshold", 0.6), target, max_delta, 0.2, 1.2
            )
        if "T_clean" in thresholds:
            thresholds["T_clean"] = self._apply_threshold(
                current_policy.thresholds["T_clean"], summary.rdiag_p40 + 0.05 * budget_tight, max_delta, 0.15, 0.90
            )
        if "T_contam" in thresholds:
            thresholds["T_contam"] = self._apply_threshold(
                current_policy.thresholds["T_contam"], max(summary.rdiag_p80, thresholds.get("T_clean", summary.rdiag_p40) + 0.15) + 0.05 * latency_load, max_delta, thresholds.get("T_clean", 0.2) + 0.05, 1.50
            )

        weights = self._common_weights(summary=summary, entry=entry)
        if "W_comp" in weights:
            weights["W_comp"] = round(_bounded(weights["W_comp"] + 0.15 * promotion_pressure + 0.10 * latency_load, 0.5, 2.0), 4)
        notes = [
            "Routing proposal generator emphasizes promotion pressure, budget tightness, and latency load.",
            f"promotion_pressure_mean={promotion_pressure:.4f}",
        ]
        return ProposalGenerationResult(thresholds=thresholds, weights=weights, notes=notes, strategy_name="routing")

    def _rag(
        self,
        *,
        summary: CalibrationSummary,
        current_policy: PolicyProfile,
        entry: ProfileCatalogEntry,
        max_delta: float,
    ) -> ProposalGenerationResult:
        metrics = summary.adapter_metrics
        thresholds = self._common_thresholds(summary=summary, current_policy=current_policy, entry=entry, max_delta=max_delta)
        freshness = float(metrics.get("freshness_mean", 0.5))
        grounding = float(metrics.get("grounding_confidence_mean", 0.5))
        conflict = float(metrics.get("conflict_mean", 0.0))
        stale_rate = float(metrics.get("stale_answer_rate", 0.0))
        re_retrieve = float(metrics.get("re_retrieve_pressure_mean", 0.0))

        if "abstain_threshold" in entry.mutable_thresholds:
            target = 0.30 + 0.25 * conflict + 0.20 * stale_rate + 0.20 * (1.0 - grounding) + 0.10 * re_retrieve
            thresholds["abstain_threshold"] = self._apply_threshold(
                current_policy.thresholds.get("abstain_threshold", 0.6), target, max_delta, 0.2, 1.2
            )
        if "freshness_threshold" in entry.mutable_thresholds:
            target = 0.20 + 0.45 * (1.0 - freshness) + 0.20 * stale_rate + 0.10 * conflict
            thresholds["freshness_threshold"] = self._apply_threshold(
                current_policy.thresholds.get("freshness_threshold", 0.5), target, max_delta, 0.1, 1.0
            )
        if "T_clean" in thresholds:
            thresholds["T_clean"] = self._apply_threshold(
                current_policy.thresholds["T_clean"], summary.rdiag_p40 + 0.03 * conflict + 0.04 * stale_rate, max_delta, 0.15, 0.90
            )
        if "T_contam" in thresholds:
            target_contam = max(summary.rdiag_p80, thresholds.get("T_clean", summary.rdiag_p40) + 0.15) + 0.08 * stale_rate + 0.05 * conflict
            thresholds["T_contam"] = self._apply_threshold(
                current_policy.thresholds["T_contam"], target_contam, max_delta, thresholds.get("T_clean", 0.2) + 0.05, 1.50
            )

        weights = self._common_weights(summary=summary, entry=entry)
        if "W_hist" in weights:
            weights["W_hist"] = round(_bounded(weights["W_hist"] + 0.20 * (1.0 - freshness) + 0.10 * stale_rate, 0.5, 2.0), 4)
        if "W_comp" in weights:
            weights["W_comp"] = round(_bounded(weights["W_comp"] + 0.15 * conflict, 0.5, 2.0), 4)
        notes = [
            "RAG proposal generator emphasizes freshness gaps, conflicts, stale answers, and grounding confidence.",
            f"stale_answer_rate={stale_rate:.4f}",
        ]
        return ProposalGenerationResult(thresholds=thresholds, weights=weights, notes=notes, strategy_name="rag")

    def _monitoring(
        self,
        *,
        summary: CalibrationSummary,
        current_policy: PolicyProfile,
        entry: ProfileCatalogEntry,
        max_delta: float,
    ) -> ProposalGenerationResult:
        metrics = summary.adapter_metrics
        thresholds = self._common_thresholds(summary=summary, current_policy=current_policy, entry=entry, max_delta=max_delta)
        unsafe_signal = float(metrics.get("unsafe_signal_mean", 0.0))
        override_rate = float(metrics.get("override_rate_mean", 0.0))
        output_shift = float(metrics.get("output_shift_mean", 0.0))
        latency_instability = float(metrics.get("latency_instability_mean", 0.0))

        if "unsafe_threshold" in entry.mutable_thresholds:
            target = 0.35 + 0.45 * unsafe_signal + 0.10 * override_rate + 0.10 * output_shift
            thresholds["unsafe_threshold"] = self._apply_threshold(
                current_policy.thresholds.get("unsafe_threshold", 0.8), target, max_delta, 0.5, 1.5
            )
        if "T_contam" in thresholds:
            thresholds["T_contam"] = self._apply_threshold(
                current_policy.thresholds["T_contam"], max(summary.rdiag_p80, thresholds.get("T_clean", summary.rdiag_p40) + 0.15) + 0.07 * latency_instability, max_delta, thresholds.get("T_clean", 0.2) + 0.05, 1.50
            )

        weights = self._common_weights(summary=summary, entry=entry)
        if "W_hist" in weights:
            weights["W_hist"] = round(_bounded(weights["W_hist"] + 0.10 * latency_instability, 0.5, 2.0), 4)
        if "W_comp" in weights:
            weights["W_comp"] = round(_bounded(weights["W_comp"] + 0.15 * unsafe_signal + 0.05 * override_rate, 0.5, 2.0), 4)
        notes = [
            "Monitoring proposal generator emphasizes unsafe signal accumulation and operator override pressure.",
            f"unsafe_signal_mean={unsafe_signal:.4f}",
        ]
        return ProposalGenerationResult(thresholds=thresholds, weights=weights, notes=notes, strategy_name="monitoring")

    def _drift(
        self,
        *,
        summary: CalibrationSummary,
        current_policy: PolicyProfile,
        entry: ProfileCatalogEntry,
        max_delta: float,
    ) -> ProposalGenerationResult:
        metrics = summary.adapter_metrics
        thresholds = self._common_thresholds(summary=summary, current_policy=current_policy, entry=entry, max_delta=max_delta)
        retrain_pressure = float(metrics.get("retrain_pressure_mean", 0.0))
        challenger = float(metrics.get("challenger_disagreement_mean", 0.0))
        feature_drift = float(metrics.get("feature_drift_mean", 0.0))
        performance_decay = float(metrics.get("performance_decay_mean", 0.0))

        if "retrain_threshold" in entry.mutable_thresholds:
            target = 0.30 + 0.40 * retrain_pressure + 0.15 * performance_decay + 0.10 * feature_drift
            thresholds["retrain_threshold"] = self._apply_threshold(
                current_policy.thresholds.get("retrain_threshold", 0.8), target, max_delta, 0.3, 1.5
            )
        if "rollback_threshold" in entry.mutable_thresholds:
            target = 0.30 + 0.35 * challenger + 0.20 * performance_decay + 0.10 * feature_drift
            thresholds["rollback_threshold"] = self._apply_threshold(
                current_policy.thresholds.get("rollback_threshold", 0.8), target, max_delta, 0.3, 1.5
            )

        weights = self._common_weights(summary=summary, entry=entry)
        if "W_hist" in weights:
            weights["W_hist"] = round(_bounded(weights["W_hist"] + 0.15 * retrain_pressure, 0.5, 2.0), 4)
        if "W_comp" in weights:
            weights["W_comp"] = round(_bounded(weights["W_comp"] + 0.15 * challenger, 0.5, 2.0), 4)
        notes = [
            "Drift proposal generator emphasizes retrain pressure and challenger disagreement.",
            f"retrain_pressure_mean={retrain_pressure:.4f}",
        ]
        return ProposalGenerationResult(thresholds=thresholds, weights=weights, notes=notes, strategy_name="drift")

    def _agent(
        self,
        *,
        summary: CalibrationSummary,
        current_policy: PolicyProfile,
        entry: ProfileCatalogEntry,
        max_delta: float,
    ) -> ProposalGenerationResult:
        metrics = summary.adapter_metrics
        thresholds = self._common_thresholds(summary=summary, current_policy=current_policy, entry=entry, max_delta=max_delta)
        escalation = float(metrics.get("escalation_pressure_mean", 0.0))
        mismatch = float(metrics.get("planner_executor_mismatch_mean", 0.0))
        retries = float(metrics.get("retry_mean", 0.0))
        unresolved = float(metrics.get("unresolved_subgoal_mean", 0.0))

        if "escalation_threshold" in entry.mutable_thresholds:
            target = 0.30 + 0.35 * escalation + 0.15 * mismatch + 0.10 * min(retries / 5.0, 1.0)
            thresholds["escalation_threshold"] = self._apply_threshold(
                current_policy.thresholds.get("escalation_threshold", 0.8), target, max_delta, 0.3, 1.5
            )
        if "handoff_threshold" in entry.mutable_thresholds:
            target = 0.35 + 0.35 * escalation + 0.15 * mismatch + 0.10 * min(unresolved / 3.0, 1.0)
            thresholds["handoff_threshold"] = self._apply_threshold(
                current_policy.thresholds.get("handoff_threshold", 0.9), target, max_delta, 0.3, 1.5
            )

        weights = self._common_weights(summary=summary, entry=entry)
        if "W_comp" in weights:
            weights["W_comp"] = round(_bounded(weights["W_comp"] + 0.20 * escalation + 0.05 * mismatch, 0.5, 2.0), 4)
        if "W_hist" in weights:
            weights["W_hist"] = round(_bounded(weights["W_hist"] + 0.10 * min(unresolved / 3.0, 1.0), 0.5, 2.0), 4)
        notes = [
            "Agent proposal generator emphasizes escalation pressure, mismatch severity, and unresolved residue.",
            f"escalation_pressure_mean={escalation:.4f}",
        ]
        return ProposalGenerationResult(thresholds=thresholds, weights=weights, notes=notes, strategy_name="agent")

    def _fallback(
        self,
        *,
        summary: CalibrationSummary,
        current_policy: PolicyProfile,
        entry: ProfileCatalogEntry,
        max_delta: float,
    ) -> ProposalGenerationResult:
        thresholds = self._common_thresholds(summary=summary, current_policy=current_policy, entry=entry, max_delta=max_delta)
        weights = self._common_weights(summary=summary, entry=entry)
        return ProposalGenerationResult(
            thresholds=thresholds,
            weights=weights,
            notes=["No adapter-specific proposal generator registered; using common heuristics."],
            strategy_name="common",
        )

    def generate(
        self,
        *,
        profile_name: str,
        adapter_type: str,
        summary: CalibrationSummary,
        current_policy: PolicyProfile,
        entry: ProfileCatalogEntry,
        max_delta: float,
    ) -> ProposalGenerationResult:
        strategies: dict[str, Callable[..., ProposalGenerationResult]] = {
            "routing": self._routing,
            "rag": self._rag,
            "monitoring": self._monitoring,
            "drift": self._drift,
            "agent": self._agent,
        }
        strategy = strategies.get(adapter_type, self._fallback)
        return strategy(summary=summary, current_policy=current_policy, entry=entry, max_delta=max_delta)


proposal_generator_service = ProposalGeneratorService()
