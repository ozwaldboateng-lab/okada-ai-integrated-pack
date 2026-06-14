from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.adapters.registry import registry
from app.audit.store import audit_store
from app.auto_calibration.store import fixture_suite_build_history_store
from app.auto_calibration.window_aggregator import calibration_window_service
from app.config.settings import settings
from app.core.policy import resolve_policy
from app.models.auto_calibration import (
    CalibrationLabCase,
    CalibrationLabSuite,
    CalibrationWindowRequest,
    FixtureSuiteBuildRecord,
    FixtureSuiteBuildRequest,
    FixtureSuiteBuildResponse,
    FixtureSuiteBuildSummary,
    WindowRecord,
)
from app.models.contracts import DiagnoseRequest, PolicyProfile


SAFE_ACTIONS = [
    "abstain",
    "human_review",
    "rollback",
    "retrain",
    "abort",
    "shadow_validation",
    "watch",
    "deeper_retrieve",
    "standard_retrieve",
    "cheap_route",
    "promote_strong_model",
    "replan",
    "continue",
]


class FixtureSuiteBuilderService:
    def __init__(self) -> None:
        self.fixture_dir = settings.auto_calibration_lab_fixture_dir
        self.generated_dir = self.fixture_dir / "generated"
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.fixture_dir / "suite_manifest.yaml"

    def build_suite(self, request: FixtureSuiteBuildRequest) -> FixtureSuiteBuildResponse:
        records, source_window = self._resolve_records(request)
        if not records:
            raise ValueError("No records available for suite generation")
        selected = self._select_records(records, request.max_cases, request.strategy)
        suite_name = request.suite_name or self._default_suite_name(request)
        fixture_path = self.generated_dir / f"{suite_name}.jsonl"
        if fixture_path.exists() and not request.overwrite:
            raise ValueError(f"Suite already exists: {suite_name}")

        cases = [self._record_to_case(request, idx, rec) for idx, rec in enumerate(selected, start=1)]
        manifest_updated = False
        path_str: str | None = None
        if request.persist_suite:
            self._write_cases(fixture_path, cases)
            self._upsert_manifest(request=request, suite_name=suite_name, fixture_path=fixture_path, case_count=len(cases))
            manifest_updated = True
            path_str = str(fixture_path)

        summary = FixtureSuiteBuildSummary(
            suite_name=suite_name,
            case_count=len(cases),
            source_window=source_window,
            generated_from_records=len(selected),
            dropped_records=max(0, len(records) - len(selected)),
            strategy=request.strategy,
            notes=self._summary_notes(request=request, records=records, selected=selected),
        )
        record = FixtureSuiteBuildRecord.now(
            build_id=str(uuid.uuid4()),
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            suite_name=suite_name,
            fixture_path=path_str,
            summary=summary,
        )
        fixture_suite_build_history_store.append(record)

        return FixtureSuiteBuildResponse(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            suite_name=suite_name,
            fixture_path=path_str,
            manifest_updated=manifest_updated,
            summary=summary,
            preview_cases=cases[: min(5, len(cases))],
        )

    def list_history(self) -> list[FixtureSuiteBuildRecord]:
        return fixture_suite_build_history_store.list_records()

    def _resolve_records(self, request: FixtureSuiteBuildRequest) -> tuple[list[WindowRecord], str]:
        if request.window_records:
            return request.window_records, "inline"
        if request.window_request is not None:
            response = calibration_window_service.resolve(request.window_request)
            return response.records, response.source_window
        if request.use_recent_audits:
            records = self._records_from_recent_audits(
                spec_id=request.spec_id,
                adapter_type=request.adapter_type,
                profile_name=request.profile_name,
                limit=request.audit_limit,
            )
            return records, "recent_audits"
        window_request = CalibrationWindowRequest(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            include_records=True,
        )
        response = calibration_window_service.resolve(window_request)
        return response.records, response.source_window

    def _records_from_recent_audits(self, *, spec_id: str, adapter_type: str, profile_name: str, limit: int) -> list[WindowRecord]:
        rows = [r for r in audit_store.list_records() if r.spec_id == spec_id and r.adapter_type == adapter_type]
        rows = rows[-limit:]
        out: list[WindowRecord] = []
        for row in rows:
            raw = row.raw_inputs or {}
            request = raw.get("request") or {}
            out.append(
                WindowRecord(
                    timestamp=row.timestamp,
                    spec_id=spec_id,
                    adapter_type=adapter_type,
                    invocation=row.decision.get("mode", "diagnose") or "diagnose",
                    observables=request.get("observables", {}),
                    context=request.get("context", {}),
                    history_state=request.get("history_state", {}),
                    resource_state=request.get("resource_state", {}),
                    expected_regime=row.decision.get("regime"),
                    expected_action=row.decision.get("recommended_action"),
                    source=f"audit:{profile_name}",
                )
            )
        return out

    def _select_records(self, records: list[WindowRecord], max_cases: int, strategy: str) -> list[WindowRecord]:
        if max_cases <= 0:
            return []
        ordered = sorted(records, key=lambda r: r.timestamp or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        if strategy == "failure_weighted":
            failures = [r for r in ordered if r.outcome and (r.outcome.success is False or r.outcome.catastrophic_failure)]
            successes = [r for r in ordered if r not in failures]
            combined = failures + successes
            return combined[:max_cases]
        if strategy == "success_weighted":
            successes = [r for r in ordered if r.outcome and r.outcome.success is True]
            others = [r for r in ordered if r not in successes]
            combined = successes + others
            return combined[:max_cases]
        return ordered[:max_cases]

    def _record_to_case(self, request: FixtureSuiteBuildRequest, idx: int, record: WindowRecord) -> CalibrationLabCase:
        policy = resolve_policy(PolicyProfile(profile_name=request.profile_name)) if request.use_current_policy_baseline else PolicyProfile(profile_name=request.profile_name)
        baseline_action = record.expected_action or self._infer_baseline_action(record, policy)
        preferred_actions = [record.expected_action] if record.expected_action else [baseline_action]
        score_table = self._build_score_table(record=record, baseline_action=baseline_action, preferred_actions=preferred_actions, include_only_expected_action=request.include_only_expected_action)
        payload = {
            "spec_id": record.spec_id,
            "adapter_type": record.adapter_type,
            "observables": record.observables,
            "context": record.context,
            "history_state": record.history_state,
            "resource_state": record.resource_state,
            "counterfactual_candidates": [],
        }
        scenario_suffix = (record.timestamp.isoformat() if record.timestamp else f"row-{idx}").replace(":", "-")
        return CalibrationLabCase(
            scenario_id=f"generated-{request.adapter_type}-{scenario_suffix}",
            spec_id=record.spec_id,
            adapter_type=record.adapter_type,
            mode=record.invocation,
            request=payload,
            baseline_action=baseline_action,
            preferred_actions=preferred_actions,
            score_table=score_table,
            notes=[f"source={record.source}", f"expected_regime={record.expected_regime}", f"expected_action={record.expected_action}"],
        )

    def _infer_baseline_action(self, record: WindowRecord, policy: PolicyProfile) -> str:
        adapter = registry.get(record.adapter_type)
        request = DiagnoseRequest(
            spec_id=record.spec_id,
            adapter_type=record.adapter_type,
            observables=record.observables,
            context=record.context,
            history_state=record.history_state,
            resource_state=record.resource_state,
            policy_profile=policy,
        )
        if record.invocation == "route":
            return adapter.route(request, policy).recommended_action
        if record.invocation == "intervene":
            return adapter.intervene(request, policy).recommended_action
        return adapter.diagnose(request, policy).recommended_action

    def _build_score_table(self, *, record: WindowRecord, baseline_action: str, preferred_actions: list[str], include_only_expected_action: bool) -> dict[str, float]:
        table: dict[str, float] = {baseline_action: 0.55}
        if record.outcome and record.outcome.success is True:
            table[baseline_action] = 0.75
        if record.outcome and record.outcome.success is False:
            table[baseline_action] = 0.25
        if record.outcome and record.outcome.catastrophic_failure:
            table[baseline_action] = 0.0
        for action in preferred_actions:
            table[action] = max(table.get(action, 0.0), 1.0)
        if not include_only_expected_action:
            for action in SAFE_ACTIONS:
                table.setdefault(action, 0.15)
        return table

    def _default_suite_name(self, request: FixtureSuiteBuildRequest) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"generated_{request.profile_name}_{request.adapter_type}_{stamp}"
        return re.sub(r"[^a-zA-Z0-9_\-]", "_", base)

    def _write_cases(self, path: Path, cases: list[CalibrationLabCase]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            for case in cases:
                fh.write(case.model_dump_json())
                fh.write("\n")

    def _upsert_manifest(self, *, request: FixtureSuiteBuildRequest, suite_name: str, fixture_path: Path, case_count: int) -> None:
        manifest = {"suites": {}}
        if self.manifest_path.exists():
            manifest = yaml.safe_load(self.manifest_path.read_text(encoding="utf-8")) or {"suites": {}}
        suites = manifest.setdefault("suites", {})
        relative_file = fixture_path.relative_to(self.fixture_dir).as_posix()
        suites[suite_name] = {
            "profile_name": request.profile_name,
            "spec_id": request.spec_id,
            "adapter_type": request.adapter_type,
            "description": request.description or f"Generated from {request.adapter_type} logs",
            "file": relative_file,
            "case_count": case_count,
            "generated": True,
        }
        self.manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=True, allow_unicode=True), encoding="utf-8")

    def _summary_notes(self, *, request: FixtureSuiteBuildRequest, records: list[WindowRecord], selected: list[WindowRecord]) -> list[str]:
        notes = [f"strategy={request.strategy}", f"persist_suite={request.persist_suite}"]
        if request.use_recent_audits:
            notes.append("records sourced from recent audit log")
        if request.window_request is not None:
            notes.append("records sourced from calibration window request")
        if len(records) > len(selected):
            notes.append("records were truncated to max_cases")
        if request.use_current_policy_baseline:
            notes.append("baseline actions inferred from current policy when missing")
        return notes


fixture_suite_builder_service = FixtureSuiteBuilderService()
