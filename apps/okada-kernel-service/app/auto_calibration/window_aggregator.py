from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

import yaml

from app.audit.store import audit_store
from app.auto_calibration.store import calibration_window_history_store
from app.config.settings import settings
from app.models.auto_calibration import (
    CalibrationWindowRequest,
    CalibrationWindowResponse,
    CalibrationWindowSummary,
    WindowRecord,
    WindowStrategy,
)
from app.models.contracts import AuditRecord

SAFE_ACTIONS = {"abstain", "human_review", "rollback", "retrain", "abort", "shadow_validation", "watch"}


def audit_to_window_record(audit: AuditRecord) -> WindowRecord:
    raw = audit.raw_inputs or {}
    decision = audit.decision or {}
    success = decision.get("regime") == "clean" and decision.get("recommended_action") not in SAFE_ACTIONS
    utility = 1.0 if success else 0.5 if decision.get("regime") == "mixed" else 0.2
    quality = utility
    cost = raw.get("resource_state", {}).get("cost")
    latency_ms = raw.get("resource_state", {}).get("latency_ms")
    return WindowRecord(
        timestamp=audit.timestamp,
        spec_id=audit.spec_id,
        adapter_type=audit.adapter_type,
        invocation="diagnose",
        observables=dict(raw.get("observables") or {}),
        context=dict(raw.get("context") or {}),
        history_state=dict(raw.get("history_state") or {}),
        resource_state=dict(raw.get("resource_state") or {}),
        expected_regime=decision.get("regime"),
        expected_action=decision.get("recommended_action"),
        outcome={
            "success": success,
            "utility": utility,
            "quality": quality,
            "cost": cost,
            "latency_ms": latency_ms,
        },
        source="audit",
    )


class CalibrationWindowAggregatorService:
    def __init__(self) -> None:
        self.profile_catalog_path = settings.auto_calibration_profiles_path
        self._catalog_cache: dict[str, dict[str, Any]] | None = None

    def _load_catalog(self) -> dict[str, dict[str, Any]]:
        if self._catalog_cache is not None:
            return self._catalog_cache
        data = yaml.safe_load(self.profile_catalog_path.read_text(encoding="utf-8")) or {}
        self._catalog_cache = dict(data.get("profiles") or {})
        return self._catalog_cache

    def _profile_window_defaults(self, profile_name: str | None) -> dict[str, Any]:
        if not profile_name:
            return {}
        catalog = self._load_catalog()
        entry = catalog.get(profile_name) or {}
        return dict(entry.get("window") or {})

    def _resolve_strategy(self, request: CalibrationWindowRequest) -> tuple[WindowStrategy, int | None, int | None, int | None]:
        defaults = self._profile_window_defaults(request.profile_name)
        strategy = request.strategy or defaults.get("strategy") or "request_or_time"
        min_requests = request.min_requests if request.min_requests is not None else defaults.get("min_requests")
        max_age_hours = request.max_age_hours if request.max_age_hours is not None else defaults.get("max_age_hours")
        max_age_days = request.max_age_days if request.max_age_days is not None else defaults.get("max_age_days")
        return strategy, min_requests, max_age_hours, max_age_days

    def _age_delta(self, max_age_hours: int | None, max_age_days: int | None) -> timedelta | None:
        if max_age_days is not None:
            return timedelta(days=max_age_days)
        if max_age_hours is not None:
            return timedelta(hours=max_age_hours)
        return None

    def _filter_records(self, request: CalibrationWindowRequest, records: list[WindowRecord]) -> list[WindowRecord]:
        filtered = [r for r in records if r.spec_id == request.spec_id and r.adapter_type == request.adapter_type]
        if request.risk_class:
            filtered = [r for r in filtered if str(r.context.get("risk_class", "unknown")) == request.risk_class]
        if request.invocation:
            filtered = [r for r in filtered if r.invocation == request.invocation]
        if request.source:
            filtered = [r for r in filtered if r.source == request.source]
        return sorted(filtered, key=lambda r: r.timestamp or datetime.min.replace(tzinfo=timezone.utc))

    def resolve(self, request: CalibrationWindowRequest, *, audit_records: list[AuditRecord] | None = None) -> CalibrationWindowResponse:
        strategy, min_requests, max_age_hours, max_age_days = self._resolve_strategy(request)
        max_records = request.max_records or max(min_requests or 0, 1) * 2 if (request.max_records is None and min_requests) else request.max_records

        source_audits = audit_records if audit_records is not None else audit_store.list_records()
        converted = [audit_to_window_record(a) for a in source_audits]
        filtered = self._filter_records(request, converted)
        available_count = len(filtered)
        now = request.now or (filtered[-1].timestamp if filtered and filtered[-1].timestamp else datetime.now(timezone.utc))
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        age_delta = self._age_delta(max_age_hours, max_age_days)
        recent = filtered
        if age_delta is not None:
            cutoff = now - age_delta
            recent = [r for r in filtered if r.timestamp and r.timestamp >= cutoff]

        selected: list[WindowRecord]
        backfilled_count = 0
        if strategy == "time":
            selected = list(recent)
        elif strategy == "request":
            target = max_records or min_requests or available_count
            selected = filtered[-target:] if target else list(filtered)
        else:  # request_or_time
            selected = list(recent)
            if min_requests and len(selected) < min_requests:
                target = min(min_requests, available_count)
                selected = filtered[-target:]
                recent_ids = {id(r) for r in recent}
                backfilled_count = sum(1 for r in selected if id(r) not in recent_ids)

        if max_records is not None and len(selected) > max_records:
            selected = selected[-max_records:]

        risk_counts = Counter(str(r.context.get("risk_class", "unknown")) for r in selected)
        invocation_counts = Counter(r.invocation for r in selected)
        first_ts = selected[0].timestamp if selected else None
        last_ts = selected[-1].timestamp if selected else None
        effective_max_age_hours = None
        if age_delta is not None:
            effective_max_age_hours = round(age_delta.total_seconds() / 3600.0, 2)

        summary = CalibrationWindowSummary(
            profile_name=request.profile_name,
            strategy=strategy,
            selected_count=len(selected),
            available_count=available_count,
            backfilled_count=backfilled_count,
            requested_min_requests=min_requests,
            max_records=max_records,
            effective_max_age_hours=effective_max_age_hours,
            first_timestamp=first_ts,
            last_timestamp=last_ts,
            risk_class_breakdown=dict(risk_counts),
            invocation_breakdown=dict(invocation_counts),
        )
        response = CalibrationWindowResponse(
            profile_name=request.profile_name,
            spec_id=request.spec_id,
            adapter_type=request.adapter_type,
            strategy=strategy,
            records=selected if request.include_records else [],
            summary=summary,
            source_window="audit_aggregated",
        )
        calibration_window_history_store.append_json({
            "event": "window_resolved",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request": request.model_dump(mode="json"),
            "summary": response.summary.model_dump(mode="json"),
        })
        return response


calibration_window_service = CalibrationWindowAggregatorService()
