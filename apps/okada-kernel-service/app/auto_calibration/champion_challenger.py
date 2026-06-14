from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.auto_calibration.service import auto_calibration_service
from app.auto_calibration.store import (
    champion_challenger_history_store,
    champion_challenger_state_store,
)
from app.models.auto_calibration import (
    CandidatePrepareRequest,
    CandidatePrepareResponse,
    CandidatePromoteRequest,
    CandidatePromoteResponse,
    ChampionChallengerCandidate,
    ShadowEvaluateRequest,
    ShadowEvaluateResponse,
)


class ChampionChallengerService:
    def list_candidates(self, profile_name: str | None = None) -> list[ChampionChallengerCandidate]:
        candidates = champion_challenger_state_store.list_candidates()
        if profile_name:
            candidates = [c for c in candidates if c.profile_name == profile_name]
        return sorted(candidates, key=lambda c: c.created_at, reverse=True)

    def prepare_candidate(self, request: CandidatePrepareRequest) -> CandidatePrepareResponse:
        candidate = ChampionChallengerCandidate(
            candidate_id=str(uuid.uuid4()),
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            status="prepared",
            proposed_policy=request.proposed_policy,
            validation_report=request.validation_report,
            created_at=datetime.now(timezone.utc),
            operator_id=request.operator_id,
            promotion_eligible=request.validation_report.adoption_recommended,
        )
        champion_challenger_state_store.upsert_candidate(candidate)
        champion_challenger_history_store.append_json({
            "event": "candidate_prepared",
            "timestamp": candidate.created_at.isoformat(),
            "candidate": candidate.model_dump(mode="json"),
        })
        return CandidatePrepareResponse(candidate=candidate, message="Shadow challenger candidate prepared.")

    def evaluate_shadow(self, request: ShadowEvaluateRequest) -> ShadowEvaluateResponse:
        candidate = champion_challenger_state_store.get_candidate(request.candidate_id)
        if candidate is None:
            raise KeyError(f"Unknown candidate: {request.candidate_id}")
        report = auto_calibration_service.validate(
            auto_calibration_service.build_validation_request(
                profile_name=candidate.profile_name,
                spec_id=candidate.spec_id,
                adapter_type=candidate.adapter_type,
                proposed_policy=candidate.proposed_policy,
                window_records=request.window_records,
                use_recent_audits=request.use_recent_audits,
                audit_limit=request.audit_limit,
                run_calibration_lab=request.run_calibration_lab,
                lab_suite_name=request.lab_suite_name,
                persist_lab_report=request.persist_lab_report,
            )
        )
        candidate.shadow_runs += 1
        candidate.last_shadow_utility_gain = report.delta.utility_gain
        candidate.promotion_eligible = report.adoption_recommended
        candidate.status = "eligible" if report.adoption_recommended else "shadow_ready"
        candidate.last_lab_suite_name = report.lab_suite_name
        candidate.last_lab_gain_vs_current = report.lab_summary.proposed_total_gain_vs_current if report.lab_summary else None
        candidate.last_lab_report_id = report.lab_report_id
        champion_challenger_state_store.upsert_candidate(candidate)
        champion_challenger_history_store.append_json({
            "event": "shadow_evaluated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "candidate_id": candidate.candidate_id,
            "delta": report.delta.model_dump(mode="json"),
            "recommended": report.adoption_recommended,
        })
        notes = [f"shadow_runs={candidate.shadow_runs}"] + list(report.notes)
        return ShadowEvaluateResponse(
            candidate_id=candidate.candidate_id,
            profile_name=candidate.profile_name,
            baseline_metrics=report.baseline_metrics,
            challenger_metrics=report.candidate_metrics,
            delta=report.delta,
            promotion_eligible=report.adoption_recommended,
            notes=notes,
            lab_summary=report.lab_summary,
            lab_report_id=report.lab_report_id,
            lab_report_path=report.lab_report_path,
            lab_suite_name=report.lab_suite_name,
        )

    def promote(self, request: CandidatePromoteRequest) -> CandidatePromoteResponse:
        candidate = champion_challenger_state_store.get_candidate(request.candidate_id)
        if candidate is None:
            raise KeyError(f"Unknown candidate: {request.candidate_id}")
        if not candidate.promotion_eligible and not request.force:
            return CandidatePromoteResponse(candidate_id=request.candidate_id, promoted=False, message="Candidate not eligible for promotion.")
        adopt = auto_calibration_service.adopt(
            auto_calibration_service.build_adopt_request(
                profile_name=candidate.profile_name,
                spec_id=candidate.spec_id,
                adapter_type=candidate.adapter_type,
                proposed_policy=candidate.proposed_policy,
                validation_report=candidate.validation_report,
                operator_id=request.operator_id,
                force=request.force,
            )
        )
        candidate.status = "promoted" if adopt.adopted else candidate.status
        candidate.promoted_revision_id = adopt.revision_id
        champion_challenger_state_store.upsert_candidate(candidate)
        champion_challenger_history_store.append_json({
            "event": "candidate_promoted",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "candidate_id": candidate.candidate_id,
            "promoted": adopt.adopted,
            "revision_id": adopt.revision_id,
        })
        return CandidatePromoteResponse(
            candidate_id=candidate.candidate_id,
            promoted=adopt.adopted,
            revision_id=adopt.revision_id,
            message=adopt.message,
        )


champion_challenger_service = ChampionChallengerService()
