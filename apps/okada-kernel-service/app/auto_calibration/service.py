from __future__ import annotations

import math
import uuid
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

import yaml

from app.adapters.registry import registry
from app.audit.store import audit_store
from app.auto_calibration.store import adopted_policy_store, auto_calibration_audit_store
from app.auto_calibration.window_aggregator import calibration_window_service
from app.auto_calibration.metric_aggregators import adapter_metric_aggregator_service
from app.auto_calibration.proposal_generators import proposal_generator_service
from app.config.settings import settings
from app.core.policy import resolve_policy
from app.models.auto_calibration import (
    AutoCalibrationAdoptRequest,
    AutoCalibrationAdoptResponse,
    AutoCalibrationAuditRecord,
    AutoCalibrationProposalResponse,
    AutoCalibrationRequest,
    AutoCalibrationValidationRequest,
    CalibrationWindowRequest,
    AutoCalibrationValidationResponse,
    CalibrationSummary,
    ProfileCatalogEntry,
    ValidationDelta,
    ValidationMetrics,
    WindowRecord,
)
from app.models.contracts import DiagnoseRequest, PolicyProfile


SAFE_ACTIONS = {"abstain", "human_review", "rollback", "retrain", "abort", "shadow_validation", "watch"}


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = (len(ordered) - 1) * q
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return ordered[lo]
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def _bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class AutoCalibrationService:
    def __init__(self) -> None:
        self.profile_catalog_path = settings.auto_calibration_profiles_path
        self._catalog_cache: dict[str, ProfileCatalogEntry] | None = None

    def _load_catalog(self) -> dict[str, ProfileCatalogEntry]:
        if self._catalog_cache is not None:
            return self._catalog_cache
        data = yaml.safe_load(self.profile_catalog_path.read_text(encoding="utf-8")) or {}
        profiles = {}
        for profile_name, raw in (data.get("profiles") or {}).items():
            profiles[profile_name] = ProfileCatalogEntry(
                profile_name=profile_name,
                adapter_type=str(raw.get("adapter_type", "")),
                mode=str(raw.get("mode", "suggest_only")),  # type: ignore[arg-type]
                mutable_thresholds=list((raw.get("mutable_parameters") or {}).get("thresholds", [])),
                mutable_weights=list((raw.get("mutable_parameters") or {}).get("weights", [])),
                adoption_gate=dict(raw.get("adoption_gate") or {}),
                rollback_gate=dict(raw.get("rollback_gate") or {}),
                window=dict(raw.get("window") or {}),
            )
        self._catalog_cache = profiles
        return profiles

    def list_profiles(self) -> list[ProfileCatalogEntry]:
        return list(self._load_catalog().values())

    def _profile_entry(self, profile_name: str, adapter_type: str) -> ProfileCatalogEntry:
        catalog = self._load_catalog()
        if profile_name in catalog:
            return catalog[profile_name]
        fallback = f"{adapter_type}_default"
        if fallback in catalog:
            return catalog[fallback]
        raise KeyError(f"Unknown auto-calibration profile: {profile_name}")

    def _resolve_window(
        self,
        *,
        profile_name: str,
        spec_id: str,
        adapter_type: str,
        window_records: list[WindowRecord],
        use_recent_audits: bool,
        audit_limit: int,
    ) -> list[WindowRecord]:
        if window_records:
            return window_records
        if use_recent_audits:
            resolved = calibration_window_service.resolve(
                CalibrationWindowRequest(
                    profile_name=profile_name,
                    spec_id=spec_id,
                    adapter_type=adapter_type,
                    max_records=audit_limit,
                )
            )
            return resolved.records
        return []

    def _run_policy(self, record: WindowRecord, policy: PolicyProfile) -> tuple[str, str]:
        adapter = registry.get(record.adapter_type)
        req = DiagnoseRequest(
            spec_id=record.spec_id,  # type: ignore[arg-type]
            adapter_type=record.adapter_type,  # type: ignore[arg-type]
            observables=record.observables,
            context=record.context,
            history_state=record.history_state,
            resource_state=record.resource_state,
            policy_profile=policy,
        )
        if record.invocation == "route":
            decision = adapter.route(req, policy)
        elif record.invocation == "intervene":
            decision = adapter.intervene(req, policy)
        else:
            decision = adapter.diagnose(req, policy)
        return decision.regime, decision.recommended_action

    def _summarize_features(self, records: list[WindowRecord], policy: PolicyProfile) -> CalibrationSummary:
        adapter = registry.get(records[0].adapter_type)
        rdiags: list[float] = []
        doms: list[float] = []
        hists: list[float] = []
        comps: list[float] = []
        for record in records:
            req = DiagnoseRequest(
                spec_id=record.spec_id,  # type: ignore[arg-type]
                adapter_type=record.adapter_type,  # type: ignore[arg-type]
                observables=record.observables,
                context=record.context,
                history_state=record.history_state,
                resource_state=record.resource_state,
                policy_profile=policy,
            )
            decision = adapter.diagnose(req, policy)
            doms.append(float(decision.derived_features.get("H_dom", 0.0)))
            hists.append(float(decision.derived_features.get("H_hist", 0.0)))
            comps.append(float(decision.derived_features.get("H_comp", 0.0)))
            rdiags.append(float(decision.derived_features.get("R_diag", 0.0)))
        base_summary = CalibrationSummary(
            window_size=len(records),
            rdiag_p40=round(_quantile(rdiags, 0.40), 4),
            rdiag_p80=round(_quantile(rdiags, 0.80), 4),
            mean_h_dom=round(mean(doms) if doms else 0.0, 4),
            mean_h_hist=round(mean(hists) if hists else 0.0, 4),
            mean_h_comp=round(mean(comps) if comps else 0.0, 4),
        )
        metric_summary = adapter_metric_aggregator_service.summarize_records(
            profile_name=policy.profile_name,
            spec_id=records[0].spec_id,
            adapter_type=records[0].adapter_type,
            records=records,
            source_window="proposal_inline",
        )
        base_summary.adapter_metrics = metric_summary.summary.adapter_metrics
        base_summary.counts = metric_summary.summary.counts
        base_summary.notes = metric_summary.summary.notes
        return base_summary


    def profile_mode(self, profile_name: str, adapter_type: str) -> str:
        return self._profile_entry(profile_name, adapter_type).mode

    def build_proposal_request(
        self,
        *,
        profile_name: str,
        spec_id: str,
        adapter_type: str,
        calibration_scope: str = "thresholds_and_weights",
        window_records: list[WindowRecord] | None = None,
        use_recent_audits: bool = False,
        audit_limit: int = 500,
        constraints: dict[str, float] | None = None,
    ) -> AutoCalibrationRequest:
        return AutoCalibrationRequest(
            profile_name=profile_name,
            spec_id=spec_id,
            adapter_type=adapter_type,
            calibration_scope=calibration_scope,
            window_records=window_records or [],
            use_recent_audits=use_recent_audits,
            audit_limit=audit_limit,
            constraints=constraints or {},
        )

    def build_validation_request(
        self,
        *,
        profile_name: str,
        spec_id: str,
        adapter_type: str,
        proposed_policy: PolicyProfile,
        window_records: list[WindowRecord] | None = None,
        use_recent_audits: bool = False,
        audit_limit: int = 500,
        run_calibration_lab: bool = False,
        lab_suite_name: str | None = None,
        persist_lab_report: bool = False,
    ) -> AutoCalibrationValidationRequest:
        return AutoCalibrationValidationRequest(
            profile_name=profile_name,
            spec_id=spec_id,
            adapter_type=adapter_type,
            proposed_policy=proposed_policy,
            window_records=window_records or [],
            use_recent_audits=use_recent_audits,
            audit_limit=audit_limit,
            run_calibration_lab=run_calibration_lab,
            lab_suite_name=lab_suite_name,
            persist_lab_report=persist_lab_report,
        )

    def build_adopt_request(
        self,
        *,
        profile_name: str,
        spec_id: str,
        adapter_type: str,
        proposed_policy: PolicyProfile,
        validation_report: AutoCalibrationValidationResponse,
        operator_id: str,
        force: bool = False,
    ) -> AutoCalibrationAdoptRequest:
        return AutoCalibrationAdoptRequest(
            profile_name=profile_name,
            spec_id=spec_id,
            adapter_type=adapter_type,
            proposed_policy=proposed_policy,
            validation_report=validation_report,
            operator_id=operator_id,
            force=force,
        )

    def propose(self, request: AutoCalibrationRequest) -> AutoCalibrationProposalResponse:
        entry = self._profile_entry(request.profile_name, request.adapter_type)
        current_policy = resolve_policy(PolicyProfile(profile_name=request.profile_name))
        records = self._resolve_window(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            window_records=request.window_records,
            use_recent_audits=request.use_recent_audits,
            audit_limit=request.audit_limit,
        )
        if not records:
            raise ValueError("No calibration window records available.")
        summary = self._summarize_features(records, current_policy)

        max_delta = float(request.constraints.get("max_threshold_delta", 0.25))
        generator_result = proposal_generator_service.generate(
            profile_name=request.profile_name,
            adapter_type=request.adapter_type,
            summary=summary,
            current_policy=current_policy,
            entry=entry,
            max_delta=max_delta,
        )
        thresholds = dict(current_policy.thresholds)
        weights = dict(current_policy.weights)

        if request.calibration_scope in {"thresholds", "thresholds_and_weights"}:
            thresholds.update(generator_result.thresholds)

        if request.calibration_scope in {"weights", "thresholds_and_weights"}:
            weights.update(generator_result.weights)

        proposed = PolicyProfile(
            profile_name=request.profile_name,
            deterministic_mode=True,
            thresholds=thresholds,
            weights=weights,
            preferred_actions=current_policy.preferred_actions,
        )
        notes = [
            f"Window size: {summary.window_size}",
            f"Calibration mode: {entry.mode}",
            f"Proposal generator: {generator_result.strategy_name}",
            f"Source window: {'audit' if request.use_recent_audits and not request.window_records else 'inline'}",
        ]
        notes.extend(generator_result.notes)
        return AutoCalibrationProposalResponse(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            mode=entry.mode,
            proposed_policy=proposed,
            summary=summary,
            mutable_parameters={
                "thresholds": entry.mutable_thresholds,
                "weights": entry.mutable_weights,
            },
            safety_notes=notes,
            source_window="audit" if request.use_recent_audits and not request.window_records else "inline",
        )

    def _metrics_for_policy(self, records: list[WindowRecord], policy: PolicyProfile) -> ValidationMetrics:
        utilities: list[float] = []
        successes: list[float] = []
        qualities: list[float] = []
        grounded: list[float] = []
        costs: list[float] = []
        latencies: list[float] = []
        abstains: list[float] = []
        handoffs: list[float] = []
        catastrophics: list[float] = []

        for record in records:
            regime, action = self._run_policy(record, policy)
            outcome = record.outcome
            success = float(outcome.success) if outcome and outcome.success is not None else float(action not in SAFE_ACTIONS and regime == "clean")
            quality = float(outcome.quality) if outcome and outcome.quality is not None else success
            grounded_accuracy = float(outcome.grounded_accuracy) if outcome and outcome.grounded_accuracy is not None else quality
            base_utility = float(outcome.utility) if outcome and outcome.utility is not None else quality
            cost = float(outcome.cost) if outcome and outcome.cost is not None else 0.0
            latency = float(outcome.latency_ms) if outcome and outcome.latency_ms is not None else 0.0
            catastrophic = float(bool(outcome and outcome.catastrophic_failure))
            expected_regime_bonus = 0.2 if record.expected_regime and regime == record.expected_regime else 0.0
            expected_action_bonus = 0.2 if record.expected_action and action == record.expected_action else 0.0
            cautious_bonus = 0.1 if catastrophic and action in SAFE_ACTIONS else 0.0
            over_caution_penalty = 0.1 if success and action in SAFE_ACTIONS else 0.0
            utility = base_utility + expected_regime_bonus + expected_action_bonus + cautious_bonus - over_caution_penalty - cost * 0.05 - latency / 10000.0 - catastrophic

            utilities.append(utility)
            successes.append(success)
            qualities.append(quality)
            grounded.append(grounded_accuracy)
            costs.append(cost)
            latencies.append(latency)
            abstains.append(float(action == "abstain"))
            handoffs.append(float(action in {"human_handoff", "human_review"}))
            catastrophics.append(catastrophic)

        sorted_latency = sorted(latencies)
        p95_latency = _quantile(sorted_latency, 0.95) if sorted_latency else 0.0
        return ValidationMetrics(
            utility=round(mean(utilities) if utilities else 0.0, 4),
            success_rate=round(mean(successes) if successes else 0.0, 4),
            quality=round(mean(qualities) if qualities else 0.0, 4),
            grounded_accuracy=round(mean(grounded) if grounded else 0.0, 4),
            mean_cost=round(mean(costs) if costs else 0.0, 4),
            p95_latency_ms=round(p95_latency, 4),
            abstain_rate=round(mean(abstains) if abstains else 0.0, 4),
            handoff_rate=round(mean(handoffs) if handoffs else 0.0, 4),
            catastrophic_rate=round(mean(catastrophics) if catastrophics else 0.0, 4),
        )

    def validate(self, request: AutoCalibrationValidationRequest) -> AutoCalibrationValidationResponse:
        entry = self._profile_entry(request.profile_name, request.adapter_type)
        baseline_policy = resolve_policy(PolicyProfile(profile_name=request.profile_name))
        records = self._resolve_window(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            window_records=request.window_records,
            use_recent_audits=request.use_recent_audits,
            audit_limit=request.audit_limit,
        )
        if not records:
            raise ValueError("No validation window records available.")
        baseline_metrics = self._metrics_for_policy(records, baseline_policy)
        candidate_metrics = self._metrics_for_policy(records, request.proposed_policy)
        delta = ValidationDelta(
            utility_gain=round(candidate_metrics.utility - baseline_metrics.utility, 4),
            success_drop=round(max(0.0, baseline_metrics.success_rate - candidate_metrics.success_rate), 4),
            quality_gain=round(candidate_metrics.quality - baseline_metrics.quality, 4),
            grounded_accuracy_gain=round(candidate_metrics.grounded_accuracy - baseline_metrics.grounded_accuracy, 4),
            cost_increase=round(max(0.0, candidate_metrics.mean_cost - baseline_metrics.mean_cost), 4),
            latency_increase=round(max(0.0, candidate_metrics.p95_latency_ms - baseline_metrics.p95_latency_ms), 4),
            abstain_increase=round(max(0.0, candidate_metrics.abstain_rate - baseline_metrics.abstain_rate), 4),
            handoff_increase=round(max(0.0, candidate_metrics.handoff_rate - baseline_metrics.handoff_rate), 4),
            catastrophic_increase=round(max(0.0, candidate_metrics.catastrophic_rate - baseline_metrics.catastrophic_rate), 4),
        )
        gate = entry.adoption_gate
        blocking: list[str] = []
        if gate.get("advisory_only"):
            blocking.append("Profile is advisory_only.")
        if delta.utility_gain < float(gate.get("min_utility_gain", -1e9)):
            blocking.append("Utility gain below required minimum.")
        if delta.grounded_accuracy_gain < float(gate.get("min_grounded_accuracy_gain", -1e9)):
            blocking.append("Grounded accuracy gain below required minimum.")
        if delta.quality_gain < float(gate.get("min_recovery_efficiency_gain", -1e9)):
            blocking.append("Quality gain below required minimum.")
        if delta.success_drop > float(gate.get("max_success_drop", 1e9)):
            blocking.append("Success drop exceeds gate.")
        if delta.cost_increase > float(gate.get("max_cost_increase", 1e9)):
            blocking.append("Cost increase exceeds gate.")
        if delta.latency_increase > float(gate.get("max_latency_increase", gate.get("max_p95_latency_increase", 1e9) * 1000 if "max_p95_latency_increase" in gate else 1e9)):
            blocking.append("Latency increase exceeds gate.")
        if delta.abstain_increase > float(gate.get("max_abstain_increase", 1e9)):
            blocking.append("Abstain increase exceeds gate.")
        if delta.catastrophic_increase > float(gate.get("catastrophic_increase", 1e9)):
            blocking.append("Catastrophic rate increase exceeds gate.")

        lab_summary = None
        lab_report_id = None
        lab_report_path = None
        if request.run_calibration_lab and request.lab_suite_name:
            from app.auto_calibration.calibration_lab import calibration_lab_service
            from app.models.auto_calibration import CalibrationLabReplayRequest

            lab_report = calibration_lab_service.replay(
                CalibrationLabReplayRequest(
                    profile_name=request.profile_name,
                    spec_id=request.spec_id,
                    adapter_type=request.adapter_type,
                    suite_name=request.lab_suite_name,
                    current_policy=baseline_policy,
                    proposed_policy=request.proposed_policy,
                    generate_proposal_if_missing=False,
                    persist_report=request.persist_lab_report,
                )
            )
            lab_summary = lab_report.summary
            lab_report_id = lab_report.report_id
            lab_report_path = lab_report.report_path
            min_lab_gain = float(gate.get("min_lab_gain_vs_current", -1e9))
            if lab_summary.proposed_total_gain_vs_current < min_lab_gain:
                blocking.append("Calibration lab gain vs current below required minimum.")
            min_match_delta = float(gate.get("min_lab_preferred_match_delta", -1e9))
            match_delta = round(lab_summary.proposed_preferred_match_rate - lab_summary.current_preferred_match_rate, 4)
            if match_delta < min_match_delta:
                blocking.append("Calibration lab preferred-match delta below required minimum.")
            if gate.get("require_lab_non_negative", False) and lab_summary.proposed_total_gain_vs_current < 0:
                blocking.append("Calibration lab replay is negative vs current.")

        adoption_recommended = not blocking
        notes = [f"Validation mode: {entry.mode}", f"Window size: {len(records)}"]
        if lab_summary is not None:
            notes.append(f"Calibration lab suite: {request.lab_suite_name}")
            notes.append(f"Calibration lab gain vs current: {lab_summary.proposed_total_gain_vs_current}")
        return AutoCalibrationValidationResponse(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            mode=entry.mode,
            baseline_metrics=baseline_metrics,
            candidate_metrics=candidate_metrics,
            delta=delta,
            adoption_recommended=adoption_recommended,
            blocking_reasons=blocking,
            notes=notes,
            lab_summary=lab_summary,
            lab_report_id=lab_report_id,
            lab_report_path=lab_report_path,
            lab_suite_name=request.lab_suite_name if lab_summary is not None else None,
        )

    def adopt(self, request: AutoCalibrationAdoptRequest) -> AutoCalibrationAdoptResponse:
        entry = self._profile_entry(request.profile_name, request.adapter_type)
        if not request.validation_report.adoption_recommended and not request.force:
            return AutoCalibrationAdoptResponse(
                profile_name=request.profile_name,
                spec_id=request.spec_id,
                adapter_type=request.adapter_type,
                adopted=False,
                message="Adoption blocked by validation gate.",
            )
        revision_id = str(uuid.uuid4())
        metadata = {
            "revision_id": revision_id,
            "spec_id": request.spec_id,
            "adapter_type": request.adapter_type,
            "mode": entry.mode,
        }
        adopted_policy_store.upsert(request.profile_name, request.proposed_policy, metadata=metadata)
        audit_record = AutoCalibrationAuditRecord.now(
            revision_id=revision_id,
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            mode=entry.mode,
            proposed_policy=request.proposed_policy,
            validation_report=request.validation_report,
            operator_id=request.operator_id,
        )
        auto_calibration_audit_store.append(audit_record)
        return AutoCalibrationAdoptResponse(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            adopted=True,
            revision_id=revision_id,
            stored_path=str(settings.adopted_policy_file),
            message="Calibration profile adopted.",
        )


auto_calibration_service = AutoCalibrationService()
