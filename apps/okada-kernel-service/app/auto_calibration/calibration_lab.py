from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import yaml

from app.adapters.registry import registry
from app.auto_calibration.service import auto_calibration_service
from app.auto_calibration.store import calibration_lab_report_store
from app.config.settings import settings
from app.core.policy import resolve_policy
from app.models.auto_calibration import (
    AutoCalibrationRequest,
    CalibrationLabCase,
    CalibrationLabCaseResult,
    CalibrationLabReplayRequest,
    CalibrationLabReplayResponse,
    CalibrationLabReportRecord,
    CalibrationLabSuite,
    CalibrationLabSummary,
    WindowRecord,
)
from app.models.contracts import DiagnoseRequest, PolicyProfile


class CalibrationLabService:
    def __init__(self) -> None:
        self.fixture_dir = settings.auto_calibration_lab_fixture_dir
        self.report_dir = settings.auto_calibration_lab_report_dir
        self.manifest_path = self.fixture_dir / 'suite_manifest.yaml'

    def list_suites(self) -> list[CalibrationLabSuite]:
        manifest = self._load_manifest()
        suites: list[CalibrationLabSuite] = []
        for suite_name, raw in (manifest.get('suites') or {}).items():
            case_path = self.fixture_dir / str(raw.get('file', f'{suite_name}.jsonl'))
            case_count = self._count_cases(case_path)
            suites.append(CalibrationLabSuite(
                suite_name=suite_name,
                profile_name=str(raw.get('profile_name', 'default')),
                spec_id=str(raw.get('spec_id', '')),
                adapter_type=str(raw.get('adapter_type', '')),
                description=str(raw.get('description', '')),
                case_count=case_count,
            ))
        return suites

    def resolve_suite_name(
        self,
        *,
        profile_name: str,
        spec_id: str,
        adapter_type: str,
        preferred_suite_name: str | None = None,
    ) -> str | None:
        suites = self.list_suites()
        if preferred_suite_name:
            return preferred_suite_name if any(s.suite_name == preferred_suite_name for s in suites) else None
        exact = [s for s in suites if s.profile_name == profile_name and s.spec_id == spec_id and s.adapter_type == adapter_type]
        if exact:
            return exact[0].suite_name
        by_adapter = [s for s in suites if s.adapter_type == adapter_type]
        if by_adapter:
            return by_adapter[0].suite_name
        return None

    def replay(self, request: CalibrationLabReplayRequest) -> CalibrationLabReplayResponse:
        suites = {suite.suite_name: suite for suite in self.list_suites()}
        suite_name = request.suite_name or f"{request.adapter_type}_adhoc"
        suite = suites.get(suite_name)
        cases = request.cases or self._load_cases(suite_name)
        if not cases:
            raise ValueError(f'No calibration lab cases found for suite={suite_name}')

        current_policy = resolve_policy(request.current_policy or PolicyProfile(profile_name=request.profile_name))
        proposal_source = 'provided_policy'
        proposed_policy = request.proposed_policy
        if proposed_policy is None:
            if not request.generate_proposal_if_missing:
                raise ValueError('proposed_policy missing and generate_proposal_if_missing=false')
            proposal_window = request.window_records or self._cases_to_window_records(cases)
            proposal = auto_calibration_service.propose(
                AutoCalibrationRequest(
                    profile_name=request.profile_name,
                    spec_id=request.spec_id,
                    adapter_type=request.adapter_type,
                    calibration_scope=request.calibration_scope,
                    window_records=proposal_window,
                    use_recent_audits=request.use_recent_audits,
                    audit_limit=request.audit_limit,
                )
            )
            proposed_policy = proposal.proposed_policy
            proposal_source = 'generated_proposal'

        proposed_policy = resolve_policy(proposed_policy)

        results = [self._run_case(case, current_policy, proposed_policy) for case in cases]
        summary = self._summarize(suite_name=suite_name, results=results)

        report_id = None
        report_path = None
        if request.persist_report:
            report_id = str(uuid.uuid4())
            report_path = str(self._write_report(report_id=report_id, request=request, current_policy=current_policy, proposed_policy=proposed_policy, summary=summary, results=results, proposal_source=proposal_source))
            calibration_lab_report_store.append(
                CalibrationLabReportRecord.now(
                    report_id=report_id,
                    profile_name=request.profile_name,
                    spec_id=request.spec_id,
                    adapter_type=request.adapter_type,
                    suite_name=suite_name,
                    proposal_source=proposal_source,
                    summary=summary,
                    report_path=report_path,
                )
            )

        return CalibrationLabReplayResponse(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            suite_name=suite_name,
            current_policy=current_policy,
            proposed_policy=proposed_policy,
            proposal_source=proposal_source,
            summary=summary,
            results=results,
            report_id=report_id,
            report_path=report_path,
        )

    def list_history(self) -> list[CalibrationLabReportRecord]:
        return calibration_lab_report_store.list_records()

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {'suites': {}}
        return yaml.safe_load(self.manifest_path.read_text(encoding='utf-8')) or {'suites': {}}

    def _count_cases(self, path: Path) -> int:
        if not path.exists():
            return 0
        return sum(1 for line in path.read_text(encoding='utf-8').splitlines() if line.strip())

    def _load_cases(self, suite_name: str) -> list[CalibrationLabCase]:
        manifest = self._load_manifest()
        entry = (manifest.get('suites') or {}).get(suite_name)
        if entry is None:
            return []
        path = self.fixture_dir / str(entry.get('file', f'{suite_name}.jsonl'))
        if not path.exists():
            return []
        rows: list[CalibrationLabCase] = []
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                rows.append(CalibrationLabCase.model_validate(json.loads(line)))
        return rows


    def _cases_to_window_records(self, cases: list[CalibrationLabCase]) -> list[WindowRecord]:
        records: list[WindowRecord] = []
        for case in cases:
            req = DiagnoseRequest.model_validate(case.request)
            records.append(WindowRecord(
                spec_id=case.spec_id,
                adapter_type=case.adapter_type,
                invocation=case.mode,
                observables=req.observables,
                context=req.context,
                history_state=req.history_state,
                resource_state=req.resource_state,
                expected_action=case.baseline_action,
                source='calibration_lab_suite',
            ))
        return records

    def _invoke(self, case: CalibrationLabCase, policy: PolicyProfile) -> tuple[str, str]:
        request = DiagnoseRequest.model_validate(case.request)
        request.policy_profile = policy
        adapter = registry.get(case.adapter_type)
        if case.mode == 'route':
            decision = adapter.route(request, policy)
        elif case.mode == 'intervene':
            decision = adapter.intervene(request, policy)
        else:
            decision = adapter.diagnose(request, policy)
        return decision.recommended_action, decision.regime

    def _run_case(self, case: CalibrationLabCase, current_policy: PolicyProfile, proposed_policy: PolicyProfile) -> CalibrationLabCaseResult:
        current_action, current_regime = self._invoke(case, current_policy)
        proposed_action, proposed_regime = self._invoke(case, proposed_policy)
        baseline_score = float(case.score_table.get(case.baseline_action, 0.0))
        current_score = float(case.score_table.get(current_action, 0.0))
        proposed_score = float(case.score_table.get(proposed_action, 0.0))
        preferred = set(case.preferred_actions)
        return CalibrationLabCaseResult(
            scenario_id=case.scenario_id,
            mode=case.mode,
            baseline_action=case.baseline_action,
            current_action=current_action,
            proposed_action=proposed_action,
            preferred_actions=case.preferred_actions,
            current_score=current_score,
            proposed_score=proposed_score,
            baseline_score=baseline_score,
            current_gain_vs_baseline=round(current_score - baseline_score, 4),
            proposed_gain_vs_baseline=round(proposed_score - baseline_score, 4),
            proposed_gain_vs_current=round(proposed_score - current_score, 4),
            current_matches_preferred=current_action in preferred,
            proposed_matches_preferred=proposed_action in preferred,
            baseline_matches_preferred=case.baseline_action in preferred,
            current_regime=current_regime,
            proposed_regime=proposed_regime,
        )

    def _summarize(self, *, suite_name: str, results: list[CalibrationLabCaseResult]) -> CalibrationLabSummary:
        case_count = len(results)
        current_gain = round(sum(r.current_gain_vs_baseline for r in results), 4)
        proposed_gain = round(sum(r.proposed_gain_vs_baseline for r in results), 4)
        proposed_vs_current = round(sum(r.proposed_gain_vs_current for r in results), 4)
        current_wins = sum(1 for r in results if r.current_gain_vs_baseline > 0)
        proposed_wins = sum(1 for r in results if r.proposed_gain_vs_baseline > 0)
        proposed_current_wins = sum(1 for r in results if r.proposed_gain_vs_current > 0)
        current_pref_rate = round(sum(1 for r in results if r.current_matches_preferred) / case_count, 4) if case_count else 0.0
        proposed_pref_rate = round(sum(1 for r in results if r.proposed_matches_preferred) / case_count, 4) if case_count else 0.0
        notes = []
        if proposed_vs_current > 0:
            notes.append('proposed policy improves total utility over current policy on replay suite')
        if proposed_pref_rate >= current_pref_rate:
            notes.append('proposed policy matches preferred actions at least as often as current policy')
        return CalibrationLabSummary(
            suite_name=suite_name,
            case_count=case_count,
            current_total_gain_vs_baseline=current_gain,
            proposed_total_gain_vs_baseline=proposed_gain,
            proposed_total_gain_vs_current=proposed_vs_current,
            current_win_count_vs_baseline=current_wins,
            proposed_win_count_vs_baseline=proposed_wins,
            proposed_win_count_vs_current=proposed_current_wins,
            current_preferred_match_rate=current_pref_rate,
            proposed_preferred_match_rate=proposed_pref_rate,
            notes=notes,
        )

    def _write_report(
        self,
        *,
        report_id: str,
        request: CalibrationLabReplayRequest,
        current_policy: PolicyProfile,
        proposed_policy: PolicyProfile,
        summary: CalibrationLabSummary,
        results: list[CalibrationLabCaseResult],
        proposal_source: str,
    ) -> Path:
        report_path = self.report_dir / f'{report_id}.md'
        lines = [
            f'# Calibration Lab Report {report_id}',
            '',
            f'- profile_name: {request.profile_name}',
            f'- spec_id: {request.spec_id}',
            f'- adapter_type: {request.adapter_type}',
            f'- suite_name: {summary.suite_name}',
            f'- proposal_source: {proposal_source}',
            '',
            '## Summary',
            '',
            f'- current_total_gain_vs_baseline: {summary.current_total_gain_vs_baseline}',
            f'- proposed_total_gain_vs_baseline: {summary.proposed_total_gain_vs_baseline}',
            f'- proposed_total_gain_vs_current: {summary.proposed_total_gain_vs_current}',
            f'- current_preferred_match_rate: {summary.current_preferred_match_rate}',
            f'- proposed_preferred_match_rate: {summary.proposed_preferred_match_rate}',
            '',
            '## Policies',
            '',
            '### Current Policy',
            '```json',
            json.dumps(current_policy.model_dump(mode='json'), indent=2, ensure_ascii=False),
            '```',
            '',
            '### Proposed Policy',
            '```json',
            json.dumps(proposed_policy.model_dump(mode='json'), indent=2, ensure_ascii=False),
            '```',
            '',
            '## Case Results',
            '',
            '| scenario_id | baseline_action | current_action | proposed_action | current_gain | proposed_gain | proposed_vs_current |',
            '|---|---|---|---|---:|---:|---:|',
        ]
        for row in results:
            lines.append(
                f'| {row.scenario_id} | {row.baseline_action} | {row.current_action} | {row.proposed_action} | {row.current_gain_vs_baseline:.4f} | {row.proposed_gain_vs_baseline:.4f} | {row.proposed_gain_vs_current:.4f} |'
            )
        report_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return report_path


calibration_lab_service = CalibrationLabService()
