from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.auto_calibration.champion_challenger import champion_challenger_service
from app.auto_calibration.metric_aggregators import adapter_metric_aggregator_service
from app.auto_calibration.scheduler import scheduler_service
from app.auto_calibration.calibration_lab import calibration_lab_service
from app.auto_calibration.fixture_suite_builder import fixture_suite_builder_service
from app.auto_calibration.service import auto_calibration_service
from app.auto_calibration.window_aggregator import calibration_window_service
from app.auto_calibration.store import auto_calibration_audit_store
from app.models.auto_calibration import (
    AutoCalibrationAdoptRequest,
    AutoCalibrationAdoptResponse,
    AutoCalibrationAuditRecord,
    AutoCalibrationProposalResponse,
    AutoCalibrationRequest,
    AutoCalibrationValidationRequest,
    AutoCalibrationValidationResponse,
    AdapterMetricSummaryRequest,
    AdapterMetricSummaryResponse,
    CalibrationWindowRequest,
    CalibrationWindowResponse,
    CandidatePrepareRequest,
    CandidatePrepareResponse,
    CandidatePromoteRequest,
    CandidatePromoteResponse,
    ChampionChallengerCandidate,
    CalibrationLabReplayRequest,
    CalibrationLabReplayResponse,
    CalibrationLabReportRecord,
    FixtureSuiteBuildRequest,
    FixtureSuiteBuildResponse,
    FixtureSuiteBuildRecord,
    CalibrationLabSuite,
    ProfileCatalogEntry,
    SchedulerPlan,
    SchedulerPlanStatus,
    SchedulerRunRequest,
    SchedulerRunResult,
    ShadowEvaluateRequest,
    ShadowEvaluateResponse,
)

router = APIRouter(prefix="/okada/auto-calibration", tags=["auto-calibration"])


@router.get("/profiles", response_model=list[ProfileCatalogEntry])
def list_profiles() -> list[ProfileCatalogEntry]:
    return auto_calibration_service.list_profiles()


@router.post("/propose", response_model=AutoCalibrationProposalResponse)
def propose(request: AutoCalibrationRequest) -> AutoCalibrationProposalResponse:
    try:
        return auto_calibration_service.propose(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/validate", response_model=AutoCalibrationValidationResponse)
def validate(request: AutoCalibrationValidationRequest) -> AutoCalibrationValidationResponse:
    try:
        return auto_calibration_service.validate(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/adopt", response_model=AutoCalibrationAdoptResponse)
def adopt(request: AutoCalibrationAdoptRequest) -> AutoCalibrationAdoptResponse:
    try:
        return auto_calibration_service.adopt(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/history", response_model=list[AutoCalibrationAuditRecord])
def history() -> list[AutoCalibrationAuditRecord]:
    return auto_calibration_audit_store.list_records()


@router.post("/windows/resolve", response_model=CalibrationWindowResponse)
def resolve_calibration_window(request: CalibrationWindowRequest) -> CalibrationWindowResponse:
    try:
        return calibration_window_service.resolve(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/metrics/summarize", response_model=AdapterMetricSummaryResponse)
def summarize_adapter_metrics(request: AdapterMetricSummaryRequest) -> AdapterMetricSummaryResponse:
    try:
        return adapter_metric_aggregator_service.summarize(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/scheduler/plans", response_model=list[SchedulerPlan])
def list_scheduler_plans() -> list[SchedulerPlan]:
    return scheduler_service.list_plans()


@router.get("/scheduler/status", response_model=list[SchedulerPlanStatus])
def scheduler_status() -> list[SchedulerPlanStatus]:
    return scheduler_service.plan_status()


@router.post("/scheduler/run-plan", response_model=SchedulerRunResult)
def run_scheduler_plan(request: SchedulerRunRequest) -> SchedulerRunResult:
    try:
        return scheduler_service.run_plan(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/scheduler/run-due", response_model=list[SchedulerRunResult])
def run_due_scheduler(request: SchedulerRunRequest) -> list[SchedulerRunResult]:
    try:
        return scheduler_service.run_due(now=request.now, force=request.force)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/champion-challenger/candidates", response_model=list[ChampionChallengerCandidate])
def list_candidates(profile_name: str | None = None) -> list[ChampionChallengerCandidate]:
    return champion_challenger_service.list_candidates(profile_name=profile_name)


@router.post("/champion-challenger/prepare", response_model=CandidatePrepareResponse)
def prepare_candidate(request: CandidatePrepareRequest) -> CandidatePrepareResponse:
    try:
        return champion_challenger_service.prepare_candidate(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/champion-challenger/evaluate", response_model=ShadowEvaluateResponse)
def evaluate_candidate(request: ShadowEvaluateRequest) -> ShadowEvaluateResponse:
    try:
        return champion_challenger_service.evaluate_shadow(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/champion-challenger/promote", response_model=CandidatePromoteResponse)
def promote_candidate(request: CandidatePromoteRequest) -> CandidatePromoteResponse:
    try:
        return champion_challenger_service.promote(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get('/lab/suites', response_model=list[CalibrationLabSuite])
def list_lab_suites() -> list[CalibrationLabSuite]:
    return calibration_lab_service.list_suites()


@router.post('/lab/replay', response_model=CalibrationLabReplayResponse)
def replay_calibration_lab(request: CalibrationLabReplayRequest) -> CalibrationLabReplayResponse:
    try:
        return calibration_lab_service.replay(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get('/lab/history', response_model=list[CalibrationLabReportRecord])
def calibration_lab_history() -> list[CalibrationLabReportRecord]:
    return calibration_lab_service.list_history()


@router.post('/lab/build-suite', response_model=FixtureSuiteBuildResponse)
def build_fixture_suite(request: FixtureSuiteBuildRequest) -> FixtureSuiteBuildResponse:
    try:
        return fixture_suite_builder_service.build_suite(request)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get('/lab/build-history', response_model=list[FixtureSuiteBuildRecord])
def fixture_suite_build_history() -> list[FixtureSuiteBuildRecord]:
    return fixture_suite_builder_service.list_history()
