from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import yaml

from app.auto_calibration.calibration_lab import calibration_lab_service
from app.auto_calibration.champion_challenger import champion_challenger_service
from app.auto_calibration.service import auto_calibration_service
from app.auto_calibration.store import scheduler_run_history_store, scheduler_state_store
from app.config.settings import settings
from app.models.auto_calibration import (
    CandidatePrepareRequest,
    SchedulerPlan,
    SchedulerPlanStatus,
    SchedulerRunRequest,
    SchedulerRunResult,
)


class AutoCalibrationSchedulerService:
    def __init__(self) -> None:
        self.plan_path = settings.auto_calibration_scheduler_plans_path
        self._cache: dict[str, SchedulerPlan] | None = None

    def _load_plans(self) -> dict[str, SchedulerPlan]:
        if self._cache is not None:
            return self._cache
        raw = yaml.safe_load(self.plan_path.read_text(encoding="utf-8")) or {}
        plans: dict[str, SchedulerPlan] = {}
        for plan_name, payload in (raw.get("plans") or {}).items():
            plans[plan_name] = SchedulerPlan(plan_name=plan_name, **payload)
        self._cache = plans
        return plans

    def list_plans(self) -> list[SchedulerPlan]:
        return list(self._load_plans().values())

    def plan_status(self, now: datetime | None = None) -> list[SchedulerPlanStatus]:
        now = now or datetime.now(timezone.utc)
        statuses: list[SchedulerPlanStatus] = []
        for plan in self.list_plans():
            state = scheduler_state_store.get_plan_state(plan.plan_name)
            last_run_at = datetime.fromisoformat(state["last_run_at"]) if state.get("last_run_at") else None
            next_due_at = (last_run_at + timedelta(hours=plan.cadence_hours)) if last_run_at else now
            statuses.append(SchedulerPlanStatus(
                plan_name=plan.plan_name,
                enabled=plan.enabled,
                last_run_at=last_run_at,
                next_due_at=next_due_at,
                due_now=bool(plan.enabled and next_due_at <= now),
                last_action=state.get("last_action"),
                profile_name=plan.profile_name,
                adapter_type=plan.adapter_type,
            ))
        return statuses

    def _record_state(self, result: SchedulerRunResult) -> None:
        scheduler_state_store.upsert_plan_state(result.plan_name, {
            "last_run_at": result.run_at.isoformat(),
            "last_action": result.action,
            "candidate_id": result.candidate_id,
            "adopted_revision_id": result.adopted_revision_id,
        })
        scheduler_run_history_store.append(result)

    def run_plan(self, request: SchedulerRunRequest) -> SchedulerRunResult:
        plans = self._load_plans()
        if not request.plan_name or request.plan_name not in plans:
            raise KeyError(f"Unknown scheduler plan: {request.plan_name}")
        plan = plans[request.plan_name]
        now = request.now or datetime.now(timezone.utc)
        if not plan.enabled:
            result = SchedulerRunResult(
                plan_name=plan.plan_name,
                profile_name=plan.profile_name,
                adapter_type=plan.adapter_type,
                mode=auto_calibration_service.profile_mode(plan.profile_name, plan.adapter_type),
                action="skipped",
                proposal_created=False,
                notes=["Plan disabled."],
                run_at=now,
            )
            self._record_state(result)
            return result

        lab_executed = False
        lab_suite_name = None
        lab_report_id = None
        lab_gain_vs_current = None
        if plan.auto_run_calibration_lab or plan.lab_suite_name:
            lab_suite_name = calibration_lab_service.resolve_suite_name(
                profile_name=plan.profile_name,
                spec_id=plan.spec_id,
                adapter_type=plan.adapter_type,
                preferred_suite_name=plan.lab_suite_name,
            )

        proposal = auto_calibration_service.propose(auto_calibration_service.build_proposal_request(
            profile_name=plan.profile_name,
            spec_id=plan.spec_id,
            adapter_type=plan.adapter_type,
            calibration_scope=plan.calibration_scope,
            window_records=request.window_records,
            use_recent_audits=plan.use_recent_audits if not request.window_records else False,
            audit_limit=plan.audit_limit,
            constraints=plan.constraints,
        ))
        validation = auto_calibration_service.validate(auto_calibration_service.build_validation_request(
            profile_name=plan.profile_name,
            spec_id=plan.spec_id,
            adapter_type=plan.adapter_type,
            proposed_policy=proposal.proposed_policy,
            window_records=request.window_records,
            use_recent_audits=plan.use_recent_audits if not request.window_records else False,
            audit_limit=plan.audit_limit,
            run_calibration_lab=bool(lab_suite_name),
            lab_suite_name=lab_suite_name,
            persist_lab_report=bool(lab_suite_name and plan.persist_lab_report),
        ))
        if lab_suite_name:
            lab_executed = validation.lab_summary is not None
            lab_report_id = validation.lab_report_id
            lab_gain_vs_current = validation.lab_summary.proposed_total_gain_vs_current if validation.lab_summary else None
        mode = validation.mode
        action = "proposal_ready"
        candidate_id = None
        adopted_revision_id = None
        notes = [f"validation_recommended={validation.adoption_recommended}"]
        if lab_suite_name:
            if validation.lab_summary is not None:
                notes.append(f"lab_suite={validation.lab_suite_name}")
                notes.append(f"lab_gain_vs_current={validation.lab_summary.proposed_total_gain_vs_current}")
            elif plan.require_lab_gate:
                notes.append("lab_required_but_not_executed")
        if plan.require_lab_gate and not validation.lab_summary:
            validation.adoption_recommended = False
            action = "proposal_ready"
            notes.append("Lab gate required; proposal not eligible without lab replay.")
        elif mode == "shadow_challenger" or plan.shadow_after_proposal:
            candidate = champion_challenger_service.prepare_candidate(CandidatePrepareRequest(
                profile_name=plan.profile_name,
                spec_id=plan.spec_id,
                adapter_type=plan.adapter_type,
                proposed_policy=proposal.proposed_policy,
                validation_report=validation,
                operator_id="scheduler",
            ))
            candidate_id = candidate.candidate.candidate_id
            action = "candidate_created"
            notes.append("Shadow challenger candidate created.")
        elif mode == "guarded_auto_adopt" and validation.adoption_recommended:
            adopt = auto_calibration_service.adopt(auto_calibration_service.build_adopt_request(
                profile_name=plan.profile_name,
                spec_id=plan.spec_id,
                adapter_type=plan.adapter_type,
                proposed_policy=proposal.proposed_policy,
                validation_report=validation,
                operator_id="scheduler",
                force=request.force,
            ))
            action = "auto_adopted" if adopt.adopted else "proposal_ready"
            adopted_revision_id = adopt.revision_id
            notes.append(adopt.message)
        result = SchedulerRunResult(
            plan_name=plan.plan_name,
            profile_name=plan.profile_name,
            adapter_type=plan.adapter_type,
            mode=mode,
            action=action,
            proposal_created=True,
            validation_recommended=validation.adoption_recommended,
            candidate_id=candidate_id,
            adopted_revision_id=adopted_revision_id,
            lab_executed=lab_executed,
            lab_suite_name=validation.lab_suite_name or lab_suite_name,
            lab_report_id=lab_report_id,
            lab_gain_vs_current=lab_gain_vs_current,
            notes=notes,
            run_at=now,
        )
        self._record_state(result)
        return result

    def run_due(self, now: datetime | None = None, *, force: bool = False) -> list[SchedulerRunResult]:
        now = now or datetime.now(timezone.utc)
        results: list[SchedulerRunResult] = []
        for status in self.plan_status(now=now):
            if status.due_now or force:
                results.append(self.run_plan(SchedulerRunRequest(plan_name=status.plan_name, now=now, force=force)))
        return results


scheduler_service = AutoCalibrationSchedulerService()
