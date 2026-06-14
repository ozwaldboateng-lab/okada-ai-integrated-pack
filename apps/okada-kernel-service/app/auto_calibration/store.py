from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config.settings import settings
from app.models.auto_calibration import (
    AutoCalibrationAuditRecord,
    ChampionChallengerCandidate,
    SchedulerRunResult,
    CalibrationLabReportRecord,
    FixtureSuiteBuildRecord,
)
from app.models.contracts import PolicyProfile


class JsonStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}\n", encoding="utf-8")

    def load_all(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def write_all(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class JsonlStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append_json(self, payload: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True))
            fh.write("\n")

    def list_json(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows


class AdoptedPolicyStore(JsonStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or settings.adopted_policy_file)

    def get(self, profile_name: str) -> dict[str, Any] | None:
        return self.load_all().get(profile_name)

    def upsert(self, profile_name: str, policy: PolicyProfile, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        current = self.load_all()
        entry = {
            "profile_name": profile_name,
            "thresholds": policy.thresholds,
            "weights": policy.weights,
            "preferred_actions": policy.preferred_actions,
        }
        if metadata:
            entry["metadata"] = metadata
        current[profile_name] = entry
        self.write_all(current)
        return entry


class AutoCalibrationAuditStore(JsonlStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or settings.auto_calibration_history_file)

    def append(self, record: AutoCalibrationAuditRecord) -> AutoCalibrationAuditRecord:
        self.append_json(record.model_dump(mode="json"))
        return record

    def list_records(self) -> list[AutoCalibrationAuditRecord]:
        return [AutoCalibrationAuditRecord.model_validate(item) for item in self.list_json()]


class SchedulerStateStore(JsonStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or settings.auto_calibration_scheduler_state_file)

    def get_plan_state(self, plan_name: str) -> dict[str, Any]:
        return self.load_all().get(plan_name, {})

    def upsert_plan_state(self, plan_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.load_all()
        current[plan_name] = payload
        self.write_all(current)
        return payload


class SchedulerRunHistoryStore(JsonlStore):
    def __init__(self, path: Path | None = None) -> None:
        path = path or settings.auto_calibration_dir / "scheduler_run_history.jsonl"
        super().__init__(path)

    def append(self, record: SchedulerRunResult) -> SchedulerRunResult:
        self.append_json(record.model_dump(mode="json"))
        return record

    def list_records(self) -> list[SchedulerRunResult]:
        return [SchedulerRunResult.model_validate(item) for item in self.list_json()]


class ChampionChallengerStateStore(JsonStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or settings.champion_challenger_state_file)

    def list_candidates(self) -> list[ChampionChallengerCandidate]:
        payload = self.load_all()
        return [ChampionChallengerCandidate.model_validate(item) for item in payload.get("candidates", {}).values()]

    def get_candidate(self, candidate_id: str) -> ChampionChallengerCandidate | None:
        payload = self.load_all()
        item = (payload.get("candidates") or {}).get(candidate_id)
        return ChampionChallengerCandidate.model_validate(item) if item else None

    def upsert_candidate(self, candidate: ChampionChallengerCandidate) -> ChampionChallengerCandidate:
        payload = self.load_all()
        payload.setdefault("candidates", {})[candidate.candidate_id] = candidate.model_dump(mode="json")
        self.write_all(payload)
        return candidate


class ChampionChallengerHistoryStore(JsonlStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or settings.champion_challenger_history_file)


class CalibrationWindowHistoryStore(JsonlStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or settings.auto_calibration_window_history_file)


class MetricSummaryHistoryStore(JsonlStore):
    def __init__(self, path: Path | None = None) -> None:
        path = path or settings.auto_calibration_dir / "metric_summary_history.jsonl"
        super().__init__(path)


adopted_policy_store = AdoptedPolicyStore()
auto_calibration_audit_store = AutoCalibrationAuditStore()
scheduler_state_store = SchedulerStateStore()
scheduler_run_history_store = SchedulerRunHistoryStore()
champion_challenger_state_store = ChampionChallengerStateStore()
champion_challenger_history_store = ChampionChallengerHistoryStore()
calibration_window_history_store = CalibrationWindowHistoryStore()
metric_summary_history_store = MetricSummaryHistoryStore()


class CalibrationLabReportStore(JsonlStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or settings.auto_calibration_lab_history_file)

    def append(self, record: CalibrationLabReportRecord) -> CalibrationLabReportRecord:
        self.append_json(record.model_dump(mode="json"))
        return record

    def list_records(self) -> list[CalibrationLabReportRecord]:
        return [CalibrationLabReportRecord.model_validate(item) for item in self.list_json()]


calibration_lab_report_store = CalibrationLabReportStore()


class FixtureSuiteBuildHistoryStore(JsonlStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or settings.auto_calibration_lab_builder_history_file)

    def append(self, record: FixtureSuiteBuildRecord) -> FixtureSuiteBuildRecord:
        self.append_json(record.model_dump(mode="json"))
        return record

    def list_records(self) -> list[FixtureSuiteBuildRecord]:
        return [FixtureSuiteBuildRecord.model_validate(item) for item in self.list_json()]


fixture_suite_build_history_store = FixtureSuiteBuildHistoryStore()
