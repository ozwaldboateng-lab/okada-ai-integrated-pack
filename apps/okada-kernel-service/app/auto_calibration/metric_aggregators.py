from __future__ import annotations

from statistics import mean
from typing import Iterable

from app.auto_calibration.store import metric_summary_history_store
from app.auto_calibration.window_aggregator import calibration_window_service


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = (len(ordered) - 1) * q
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    if lo == hi:
        return ordered[lo]
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac

from app.models.auto_calibration import (
    AdapterMetricSummaryRequest,
    AdapterMetricSummaryResponse,
    CalibrationSummary,
    CalibrationWindowRequest,
    CalibrationWindowSummary,
    WindowRecord,
)


class AdapterMetricAggregatorService:
    def _safe(self, value: object, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _mean(self, values: Iterable[float]) -> float:
        vals = list(values)
        return mean(vals) if vals else 0.0

    def _count_if(self, items: Iterable[bool]) -> int:
        return sum(1 for item in items if item)

    def _resolve_records(self, request: AdapterMetricSummaryRequest) -> tuple[list[WindowRecord], CalibrationWindowSummary, str]:
        if request.window_records:
            records = request.window_records
            summary = CalibrationWindowSummary(
                profile_name=request.profile_name,
                strategy="request",
                selected_count=len(records),
                available_count=len(records),
                backfilled_count=0,
                requested_min_requests=len(records),
                max_records=len(records),
                risk_class_breakdown={},
                invocation_breakdown={},
            )
            return records, summary, "inline"

        window_request = request.window_request or CalibrationWindowRequest(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            max_records=request.audit_limit,
            include_records=True,
        )
        if window_request.include_records is False:
            window_request = window_request.model_copy(update={"include_records": True})
        response = calibration_window_service.resolve(window_request)
        return response.records, response.summary, response.source_window

    def _common_summary(self, records: list[WindowRecord]) -> tuple[dict[str, float], dict[str, int]]:
        utilities = [self._safe(r.outcome.utility if r.outcome else None) for r in records]
        qualities = [self._safe(r.outcome.quality if r.outcome else None) for r in records]
        grounded = [self._safe(r.outcome.grounded_accuracy if r.outcome else None) for r in records]
        costs = [self._safe(r.outcome.cost if r.outcome else None) for r in records]
        latencies = [self._safe(r.outcome.latency_ms if r.outcome else None) for r in records]
        success_rate = self._mean([(r.outcome.success if r.outcome and r.outcome.success is not None else False) for r in records])
        abstain_rate = self._mean([r.expected_action == "abstain" for r in records])
        handoff_rate = self._mean([r.expected_action in {"human_handoff", "human_review"} for r in records])
        catastrophic_rate = self._mean([bool(r.outcome and r.outcome.catastrophic_failure) for r in records])
        common = {
            "mean_utility": round(self._mean(utilities), 4),
            "success_rate": round(success_rate, 4),
            "mean_quality": round(self._mean(qualities), 4),
            "grounded_accuracy": round(self._mean(grounded), 4),
            "mean_cost": round(self._mean(costs), 4),
            "p95_latency_ms": round(_quantile(latencies, 0.95) if latencies else 0.0, 4),
            "abstain_rate": round(abstain_rate, 4),
            "handoff_rate": round(handoff_rate, 4),
            "catastrophic_rate": round(catastrophic_rate, 4),
        }
        counts = {
            "record_count": len(records),
            "success_count": self._count_if((r.outcome.success if r.outcome and r.outcome.success is not None else False) for r in records),
            "catastrophic_count": self._count_if(bool(r.outcome and r.outcome.catastrophic_failure) for r in records),
        }
        return common, counts

    def _routing_metrics(self, records: list[WindowRecord]) -> dict[str, float]:
        complexities = [self._safe(r.observables.get("complexity_proxy")) for r in records]
        hist_success = [self._safe(r.observables.get("historical_route_success")) for r in records]
        budget = [self._safe(r.observables.get("budget_remaining"), 1.0) for r in records]
        load = [self._safe(r.observables.get("latency_load_state")) for r in records]
        retrieval_need = [self._safe(r.observables.get("retrieval_need_estimate")) for r in records]
        promotion = [max(0.0, c - hs + (1.0 - b) * 0.5 + l * 0.5 + rn * 0.4) for c, hs, b, l, rn in zip(complexities, hist_success, budget, load, retrieval_need)]
        return {
            "complexity_mean": round(self._mean(complexities), 4),
            "budget_tight_rate": round(self._mean([b < 0.4 for b in budget]), 4),
            "latency_load_mean": round(self._mean(load), 4),
            "retrieval_need_mean": round(self._mean(retrieval_need), 4),
            "promotion_pressure_mean": round(self._mean(promotion), 4),
        }

    def _rag_metrics(self, records: list[WindowRecord]) -> dict[str, float]:
        freshness = [self._safe(r.observables.get("source_freshness"), 0.5) for r in records]
        grounding = [self._safe(r.observables.get("grounding_confidence"), self._safe(r.outcome.grounded_accuracy if r.outcome else None)) for r in records]
        conflict = [self._safe(r.observables.get("chunk_conflict_rate")) for r in records]
        index_age = [self._safe(r.observables.get("index_age")) for r in records]
        stale_rate = [bool(r.outcome and r.outcome.stale_answer) for r in records]
        re_retrieve = [max(0.0, c + (1.0 - g) * 0.5 + (1.0 - f) * 0.5) for c, g, f in zip(conflict, grounding, freshness)]
        return {
            "freshness_mean": round(self._mean(freshness), 4),
            "grounding_confidence_mean": round(self._mean(grounding), 4),
            "conflict_mean": round(self._mean(conflict), 4),
            "index_age_mean": round(self._mean(index_age), 4),
            "stale_answer_rate": round(self._mean(stale_rate), 4),
            "re_retrieve_pressure_mean": round(self._mean(re_retrieve), 4),
        }

    def _monitoring_metrics(self, records: list[WindowRecord]) -> dict[str, float]:
        fallback = [self._safe(r.observables.get("fallback_rate")) for r in records]
        override = [self._safe(r.observables.get("override_rate")) for r in records]
        latency_instability = [self._safe(r.observables.get("latency_instability")) for r in records]
        output_shift = [self._safe(r.observables.get("output_shift_score")) for r in records]
        calibration = [self._safe(r.observables.get("calibration_error_trend")) for r in records]
        unsafe = [max(f, o, li, os, c) for f, o, li, os, c in zip(fallback, override, latency_instability, output_shift, calibration)]
        return {
            "fallback_rate_mean": round(self._mean(fallback), 4),
            "override_rate_mean": round(self._mean(override), 4),
            "latency_instability_mean": round(self._mean(latency_instability), 4),
            "output_shift_mean": round(self._mean(output_shift), 4),
            "unsafe_signal_mean": round(self._mean(unsafe), 4),
        }

    def _drift_metrics(self, records: list[WindowRecord]) -> dict[str, float]:
        feature_drift = [self._safe(r.observables.get("feature_drift_score")) for r in records]
        uncertainty = [self._safe(r.observables.get("uncertainty_drift")) for r in records]
        calibration_lag = [self._safe(r.observables.get("calibration_lag")) for r in records]
        performance_decay = [self._safe(r.observables.get("performance_decay_proxy")) for r in records]
        challenger = [self._safe(r.observables.get("challenger_disagreement")) for r in records]
        retrain = [fd * 0.3 + ud * 0.2 + cl * 0.2 + pd * 0.2 + ch * 0.1 for fd, ud, cl, pd, ch in zip(feature_drift, uncertainty, calibration_lag, performance_decay, challenger)]
        return {
            "feature_drift_mean": round(self._mean(feature_drift), 4),
            "uncertainty_drift_mean": round(self._mean(uncertainty), 4),
            "calibration_lag_mean": round(self._mean(calibration_lag), 4),
            "performance_decay_mean": round(self._mean(performance_decay), 4),
            "challenger_disagreement_mean": round(self._mean(challenger), 4),
            "retrain_pressure_mean": round(self._mean(retrain), 4),
        }

    def _agent_metrics(self, records: list[WindowRecord]) -> dict[str, float]:
        mismatch = [self._safe(r.observables.get("planner_executor_mismatch")) for r in records]
        tool_disagreement = [self._safe(r.observables.get("tool_disagreement")) for r in records]
        retries = [self._safe(r.observables.get("retry_count")) for r in records]
        unresolved = [self._safe(r.observables.get("unresolved_subgoal_count")) for r in records]
        route_split = [self._safe(r.observables.get("route_split_frequency")) for r in records]
        escalation = [m * 0.3 + td * 0.2 + min(rt / 5.0, 1.0) * 0.2 + min(u / 3.0, 1.0) * 0.15 + rs * 0.15 for m, td, rt, u, rs in zip(mismatch, tool_disagreement, retries, unresolved, route_split)]
        return {
            "planner_executor_mismatch_mean": round(self._mean(mismatch), 4),
            "tool_disagreement_mean": round(self._mean(tool_disagreement), 4),
            "retry_mean": round(self._mean(retries), 4),
            "unresolved_subgoal_mean": round(self._mean(unresolved), 4),
            "route_split_mean": round(self._mean(route_split), 4),
            "escalation_pressure_mean": round(self._mean(escalation), 4),
        }

    def summarize_records(self, *, profile_name: str | None, spec_id: str, adapter_type: str, records: list[WindowRecord], window_summary: CalibrationWindowSummary | None = None, source_window: str = "window_aggregated") -> AdapterMetricSummaryResponse:
        if not records:
            raise ValueError("No records available for metric aggregation.")

        common, counts = self._common_summary(records)
        if adapter_type == "routing":
            adapter_metrics = self._routing_metrics(records)
            notes = ["Routing summary emphasizes promotion pressure and budget tightness."]
        elif adapter_type == "rag":
            adapter_metrics = self._rag_metrics(records)
            notes = ["RAG summary emphasizes freshness, conflicts, and stale-answer exposure."]
        elif adapter_type == "monitoring":
            adapter_metrics = self._monitoring_metrics(records)
            notes = ["Monitoring summary emphasizes unsafe signal accumulation."]
        elif adapter_type == "drift":
            adapter_metrics = self._drift_metrics(records)
            notes = ["Drift summary emphasizes retrain pressure rather than detector replacement."]
        elif adapter_type == "agent":
            adapter_metrics = self._agent_metrics(records)
            notes = ["Agent summary emphasizes escalation pressure and route fragmentation."]
        else:
            adapter_metrics = {}
            notes = ["No adapter-specific metric aggregator registered; using common metrics only."]

        rdiags = []
        doms = []
        hists = []
        comps = []
        for record in records:
            resource = record.resource_state or {}
            hist = self._safe(resource.get("history_pressure"), self._safe(record.history_state.get("history_pressure")))
            comp = self._safe(resource.get("competitor_pressure"), self._safe(record.history_state.get("competitor_pressure")))
            dom = max(0.0, 1.0 - hist * 0.5 - comp * 0.5)
            doms.append(dom)
            hists.append(hist)
            comps.append(comp)
            rdiags.append((hist + comp) / max(dom, 1e-6))

        summary = CalibrationSummary(
            window_size=len(records),
            rdiag_p40=round(_quantile(rdiags, 0.40), 4) if rdiags else 0.0,
            rdiag_p80=round(_quantile(rdiags, 0.80), 4) if rdiags else 0.0,
            mean_h_dom=round(self._mean(doms), 4),
            mean_h_hist=round(self._mean(hists), 4),
            mean_h_comp=round(self._mean(comps), 4),
            adapter_metrics={**common, **adapter_metrics},
            counts=counts,
            notes=notes,
        )
        window_summary = window_summary or CalibrationWindowSummary(
            profile_name=profile_name,
            strategy="request",
            selected_count=len(records),
            available_count=len(records),
            backfilled_count=0,
            requested_min_requests=len(records),
            max_records=len(records),
            risk_class_breakdown={},
            invocation_breakdown={},
        )
        response = AdapterMetricSummaryResponse(
            profile_name=profile_name,
            spec_id=spec_id,
            adapter_type=adapter_type,
            summary=summary,
            window_summary=window_summary,
            source_window=source_window,
        )
        metric_summary_history_store.append_json({
            "event": "metric_summary_generated",
            "profile_name": profile_name,
            "spec_id": spec_id,
            "adapter_type": adapter_type,
            "source_window": source_window,
            "window_summary": window_summary.model_dump(mode="json"),
            "summary": summary.model_dump(mode="json"),
        })
        return response

    def summarize(self, request: AdapterMetricSummaryRequest) -> AdapterMetricSummaryResponse:
        records, window_summary, source_window = self._resolve_records(request)
        return self.summarize_records(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            records=records,
            window_summary=window_summary,
            source_window=source_window,
        )


adapter_metric_aggregator_service = AdapterMetricAggregatorService()
