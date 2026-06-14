from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.contracts import PolicyProfile, Regime

CalibrationMode = Literal[
    "disabled",
    "suggest_only",
    "approval_gated",
    "shadow_challenger",
    "guarded_auto_adopt",
]

CalibrationScope = Literal["thresholds", "weights", "thresholds_and_weights"]
InvocationType = Literal["diagnose", "route", "intervene"]

WindowStrategy = Literal["request", "time", "request_or_time"]


SuiteBuildStrategy = Literal["recent", "success_weighted", "failure_weighted"]

SchedulerAction = Literal["skipped", "proposal_ready", "candidate_created", "auto_adopted"]
CandidateStatus = Literal["prepared", "shadow_ready", "eligible", "promoted", "rejected"]


class CalibrationOutcome(BaseModel):
    success: bool | None = None
    utility: float | None = None
    quality: float | None = None
    cost: float | None = None
    latency_ms: float | None = None
    catastrophic_failure: bool = False
    manual_override: bool = False
    grounded_accuracy: float | None = None
    stale_answer: bool = False


class WindowRecord(BaseModel):
    timestamp: datetime | None = None
    spec_id: str
    adapter_type: str
    invocation: InvocationType = "diagnose"
    observables: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    history_state: dict[str, Any] = Field(default_factory=dict)
    resource_state: dict[str, Any] = Field(default_factory=dict)
    expected_regime: Regime | None = None
    expected_action: str | None = None
    outcome: CalibrationOutcome | None = None
    source: str = "inline"


class AutoCalibrationRequest(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    calibration_scope: CalibrationScope = "thresholds_and_weights"
    window_records: list[WindowRecord] = Field(default_factory=list)
    use_recent_audits: bool = False
    audit_limit: int = 500
    constraints: dict[str, float] = Field(default_factory=dict)
    dry_run: bool = True


class ProfileCatalogEntry(BaseModel):
    profile_name: str
    adapter_type: str
    mode: CalibrationMode
    mutable_thresholds: list[str] = Field(default_factory=list)
    mutable_weights: list[str] = Field(default_factory=list)
    adoption_gate: dict[str, Any] = Field(default_factory=dict)
    rollback_gate: dict[str, Any] = Field(default_factory=dict)
    window: dict[str, Any] = Field(default_factory=dict)


class CalibrationSummary(BaseModel):
    window_size: int
    rdiag_p40: float
    rdiag_p80: float
    mean_h_dom: float
    mean_h_hist: float
    mean_h_comp: float
    adapter_metrics: dict[str, float] = Field(default_factory=dict)
    counts: dict[str, int] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class AutoCalibrationProposalResponse(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    mode: CalibrationMode
    proposed_policy: PolicyProfile
    summary: CalibrationSummary
    mutable_parameters: dict[str, list[str]] = Field(default_factory=dict)
    safety_notes: list[str] = Field(default_factory=list)
    source_window: str = "inline"


class ValidationMetrics(BaseModel):
    utility: float
    success_rate: float
    quality: float
    grounded_accuracy: float
    mean_cost: float
    p95_latency_ms: float
    abstain_rate: float
    handoff_rate: float
    catastrophic_rate: float


class ValidationDelta(BaseModel):
    utility_gain: float
    success_drop: float
    quality_gain: float
    grounded_accuracy_gain: float
    cost_increase: float
    latency_increase: float
    abstain_increase: float
    handoff_increase: float
    catastrophic_increase: float


class AutoCalibrationValidationRequest(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    proposed_policy: PolicyProfile
    window_records: list[WindowRecord] = Field(default_factory=list)
    use_recent_audits: bool = False
    audit_limit: int = 500
    run_calibration_lab: bool = False
    lab_suite_name: str | None = None
    persist_lab_report: bool = False


class AutoCalibrationValidationResponse(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    mode: CalibrationMode
    baseline_metrics: ValidationMetrics
    candidate_metrics: ValidationMetrics
    delta: ValidationDelta
    adoption_recommended: bool
    blocking_reasons: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    lab_summary: CalibrationLabSummary | None = None
    lab_report_id: str | None = None
    lab_report_path: str | None = None
    lab_suite_name: str | None = None


class AutoCalibrationAdoptRequest(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    proposed_policy: PolicyProfile
    validation_report: AutoCalibrationValidationResponse
    operator_id: str = "system"
    force: bool = False


class AutoCalibrationAdoptResponse(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    adopted: bool
    revision_id: str | None = None
    stored_path: str | None = None
    message: str


class AutoCalibrationAuditRecord(BaseModel):
    revision_id: str
    timestamp: datetime
    profile_name: str
    spec_id: str
    adapter_type: str
    mode: CalibrationMode
    proposed_policy: PolicyProfile
    validation_report: AutoCalibrationValidationResponse
    operator_id: str

    @classmethod
    def now(
        cls,
        *,
        revision_id: str,
        profile_name: str,
        spec_id: str,
        adapter_type: str,
        mode: CalibrationMode,
        proposed_policy: PolicyProfile,
        validation_report: AutoCalibrationValidationResponse,
        operator_id: str,
    ) -> "AutoCalibrationAuditRecord":
        return cls(
            revision_id=revision_id,
            timestamp=datetime.now(timezone.utc),
            profile_name=profile_name,
            spec_id=spec_id,
            adapter_type=adapter_type,
            mode=mode,
            proposed_policy=proposed_policy,
            validation_report=validation_report,
            operator_id=operator_id,
        )


class SchedulerPlan(BaseModel):
    plan_name: str
    profile_name: str
    spec_id: str
    adapter_type: str
    enabled: bool = True
    cadence_hours: int = 24
    use_recent_audits: bool = True
    audit_limit: int = 200
    calibration_scope: CalibrationScope = "thresholds_and_weights"
    constraints: dict[str, float] = Field(default_factory=dict)
    shadow_after_proposal: bool = False
    auto_run_calibration_lab: bool = False
    lab_suite_name: str | None = None
    persist_lab_report: bool = False
    require_lab_gate: bool = False


class SchedulerPlanStatus(BaseModel):
    plan_name: str
    enabled: bool
    last_run_at: datetime | None = None
    next_due_at: datetime | None = None
    due_now: bool
    last_action: SchedulerAction | None = None
    profile_name: str
    adapter_type: str


class SchedulerRunRequest(BaseModel):
    plan_name: str | None = None
    now: datetime | None = None
    window_records: list[WindowRecord] = Field(default_factory=list)
    force: bool = False


class SchedulerRunResult(BaseModel):
    plan_name: str
    profile_name: str
    adapter_type: str
    mode: CalibrationMode
    action: SchedulerAction
    proposal_created: bool
    validation_recommended: bool | None = None
    candidate_id: str | None = None
    adopted_revision_id: str | None = None
    lab_executed: bool = False
    lab_suite_name: str | None = None
    lab_report_id: str | None = None
    lab_gain_vs_current: float | None = None
    notes: list[str] = Field(default_factory=list)
    run_at: datetime


class CandidatePrepareRequest(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    proposed_policy: PolicyProfile
    validation_report: AutoCalibrationValidationResponse
    operator_id: str = "system"


class ChampionChallengerCandidate(BaseModel):
    candidate_id: str
    profile_name: str
    spec_id: str
    adapter_type: str
    status: CandidateStatus
    proposed_policy: PolicyProfile
    validation_report: AutoCalibrationValidationResponse
    created_at: datetime
    operator_id: str
    shadow_runs: int = 0
    last_shadow_utility_gain: float | None = None
    promotion_eligible: bool = False
    promoted_revision_id: str | None = None
    last_lab_suite_name: str | None = None
    last_lab_gain_vs_current: float | None = None
    last_lab_report_id: str | None = None


class CandidatePrepareResponse(BaseModel):
    candidate: ChampionChallengerCandidate
    message: str


class ShadowEvaluateRequest(BaseModel):
    candidate_id: str
    window_records: list[WindowRecord] = Field(default_factory=list)
    use_recent_audits: bool = False
    audit_limit: int = 500
    run_calibration_lab: bool = False
    lab_suite_name: str | None = None
    persist_lab_report: bool = False


class ShadowEvaluateResponse(BaseModel):
    candidate_id: str
    profile_name: str
    baseline_metrics: ValidationMetrics
    challenger_metrics: ValidationMetrics
    delta: ValidationDelta
    promotion_eligible: bool
    notes: list[str] = Field(default_factory=list)
    lab_summary: CalibrationLabSummary | None = None
    lab_report_id: str | None = None
    lab_report_path: str | None = None
    lab_suite_name: str | None = None


class CandidatePromoteRequest(BaseModel):
    candidate_id: str
    operator_id: str = "system"
    force: bool = False


class CandidatePromoteResponse(BaseModel):
    candidate_id: str
    promoted: bool
    revision_id: str | None = None
    message: str


class CalibrationWindowRequest(BaseModel):
    profile_name: str | None = None
    spec_id: str
    adapter_type: str
    strategy: WindowStrategy | None = None
    min_requests: int | None = None
    max_records: int | None = None
    max_age_hours: int | None = None
    max_age_days: int | None = None
    risk_class: str | None = None
    invocation: InvocationType | None = None
    source: str | None = None
    include_records: bool = True
    now: datetime | None = None


class CalibrationWindowSummary(BaseModel):
    profile_name: str | None = None
    strategy: WindowStrategy
    selected_count: int
    available_count: int
    backfilled_count: int = 0
    requested_min_requests: int | None = None
    max_records: int | None = None
    effective_max_age_hours: float | None = None
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    risk_class_breakdown: dict[str, int] = Field(default_factory=dict)
    invocation_breakdown: dict[str, int] = Field(default_factory=dict)


class CalibrationWindowResponse(BaseModel):
    profile_name: str | None = None
    spec_id: str
    adapter_type: str
    strategy: WindowStrategy
    records: list[WindowRecord] = Field(default_factory=list)
    summary: CalibrationWindowSummary
    source_window: str = "audit_aggregated"


class AdapterMetricSummaryRequest(BaseModel):
    profile_name: str | None = None
    spec_id: str
    adapter_type: str
    window_records: list[WindowRecord] = Field(default_factory=list)
    use_recent_audits: bool = False
    audit_limit: int = 500
    window_request: CalibrationWindowRequest | None = None
    include_records: bool = False


class AdapterMetricSummaryResponse(BaseModel):
    profile_name: str | None = None
    spec_id: str
    adapter_type: str
    summary: CalibrationSummary
    window_summary: CalibrationWindowSummary
    source_window: str = "window_aggregated"
    records: list[WindowRecord] = Field(default_factory=list)


class CalibrationLabCase(BaseModel):
    scenario_id: str
    spec_id: str
    adapter_type: str
    mode: InvocationType = "diagnose"
    request: dict[str, Any]
    baseline_action: str
    preferred_actions: list[str] = Field(default_factory=list)
    score_table: dict[str, float] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class CalibrationLabSuite(BaseModel):
    suite_name: str
    profile_name: str
    spec_id: str
    adapter_type: str
    description: str = ""
    case_count: int = 0


class CalibrationLabReplayRequest(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    suite_name: str | None = None
    cases: list[CalibrationLabCase] = Field(default_factory=list)
    current_policy: PolicyProfile | None = None
    proposed_policy: PolicyProfile | None = None
    generate_proposal_if_missing: bool = True
    use_recent_audits: bool = False
    audit_limit: int = 500
    window_records: list[WindowRecord] = Field(default_factory=list)
    calibration_scope: CalibrationScope = "thresholds_and_weights"
    persist_report: bool = True


class CalibrationLabCaseResult(BaseModel):
    scenario_id: str
    mode: InvocationType
    baseline_action: str
    current_action: str
    proposed_action: str
    preferred_actions: list[str] = Field(default_factory=list)
    current_score: float
    proposed_score: float
    baseline_score: float
    current_gain_vs_baseline: float
    proposed_gain_vs_baseline: float
    proposed_gain_vs_current: float
    current_matches_preferred: bool
    proposed_matches_preferred: bool
    baseline_matches_preferred: bool
    current_regime: str
    proposed_regime: str


class CalibrationLabSummary(BaseModel):
    suite_name: str
    case_count: int
    current_total_gain_vs_baseline: float
    proposed_total_gain_vs_baseline: float
    proposed_total_gain_vs_current: float
    current_win_count_vs_baseline: int
    proposed_win_count_vs_baseline: int
    proposed_win_count_vs_current: int
    current_preferred_match_rate: float
    proposed_preferred_match_rate: float
    notes: list[str] = Field(default_factory=list)


class CalibrationLabReplayResponse(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    suite_name: str
    current_policy: PolicyProfile
    proposed_policy: PolicyProfile
    proposal_source: str
    summary: CalibrationLabSummary
    results: list[CalibrationLabCaseResult] = Field(default_factory=list)
    report_id: str | None = None
    report_path: str | None = None


class CalibrationLabReportRecord(BaseModel):
    report_id: str
    timestamp: datetime
    profile_name: str
    spec_id: str
    adapter_type: str
    suite_name: str
    proposal_source: str
    summary: CalibrationLabSummary
    report_path: str | None = None

    @classmethod
    def now(
        cls,
        *,
        report_id: str,
        profile_name: str,
        spec_id: str,
        adapter_type: str,
        suite_name: str,
        proposal_source: str,
        summary: CalibrationLabSummary,
        report_path: str | None = None,
    ) -> "CalibrationLabReportRecord":
        return cls(
            report_id=report_id,
            timestamp=datetime.now(timezone.utc),
            profile_name=profile_name,
            spec_id=spec_id,
            adapter_type=adapter_type,
            suite_name=suite_name,
            proposal_source=proposal_source,
            summary=summary,
            report_path=report_path,
        )


class FixtureSuiteBuildRequest(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    suite_name: str | None = None
    description: str = ""
    window_records: list[WindowRecord] = Field(default_factory=list)
    use_recent_audits: bool = False
    audit_limit: int = 500
    window_request: CalibrationWindowRequest | None = None
    max_cases: int = 50
    strategy: SuiteBuildStrategy = "recent"
    use_current_policy_baseline: bool = True
    include_only_expected_action: bool = False
    overwrite: bool = False
    persist_suite: bool = True


class FixtureSuiteBuildSummary(BaseModel):
    suite_name: str
    case_count: int
    source_window: str
    generated_from_records: int
    dropped_records: int = 0
    strategy: SuiteBuildStrategy
    notes: list[str] = Field(default_factory=list)


class FixtureSuiteBuildResponse(BaseModel):
    profile_name: str
    spec_id: str
    adapter_type: str
    suite_name: str
    fixture_path: str | None = None
    manifest_updated: bool = False
    summary: FixtureSuiteBuildSummary
    preview_cases: list[CalibrationLabCase] = Field(default_factory=list)


class FixtureSuiteBuildRecord(BaseModel):
    build_id: str
    timestamp: datetime
    profile_name: str
    spec_id: str
    adapter_type: str
    suite_name: str
    fixture_path: str | None = None
    summary: FixtureSuiteBuildSummary

    @classmethod
    def now(
        cls,
        *,
        build_id: str,
        profile_name: str,
        spec_id: str,
        adapter_type: str,
        suite_name: str,
        fixture_path: str | None,
        summary: FixtureSuiteBuildSummary,
    ) -> "FixtureSuiteBuildRecord":
        return cls(
            build_id=build_id,
            timestamp=datetime.now(timezone.utc),
            profile_name=profile_name,
            spec_id=spec_id,
            adapter_type=adapter_type,
            suite_name=suite_name,
            fixture_path=fixture_path,
            summary=summary,
        )
