from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    audit_dir: Path
    audit_backend: str
    default_policy: str
    service_port: int
    service_name: str
    shared_token: str | None
    require_auth: bool
    spec_root: Path
    auto_calibration_dir: Path
    auto_calibration_profiles_path: Path
    adopted_policy_file: Path
    auto_calibration_history_file: Path
    auto_calibration_scheduler_plans_path: Path
    auto_calibration_scheduler_state_file: Path
    champion_challenger_state_file: Path
    champion_challenger_history_file: Path
    auto_calibration_window_history_file: Path
    auto_calibration_lab_fixture_dir: Path
    auto_calibration_lab_history_file: Path
    auto_calibration_lab_report_dir: Path
    auto_calibration_lab_builder_history_file: Path

    @classmethod
    def from_env(cls) -> "Settings":
        audit_dir = Path(os.getenv("OKADA_AUDIT_DIR", "./data/audit"))
        audit_backend = os.getenv("OKADA_AUDIT_BACKEND", "jsonl").lower()
        default_policy = os.getenv("OKADA_DEFAULT_POLICY", "default")
        service_port = int(os.getenv("OKADA_SERVICE_PORT", "8080"))
        service_name = os.getenv("OKADA_SERVICE_NAME", "okada-kernel")
        shared_token = os.getenv("OKADA_SHARED_TOKEN")
        require_auth = os.getenv("OKADA_REQUIRE_AUTH", "false").lower() in {"1", "true", "yes"}
        repo_root = Path(__file__).resolve().parents[4]
        spec_root = Path(os.getenv("OKADA_SPEC_ROOT", str(repo_root / "specs/okada-ai-spec")))
        auto_calibration_dir = Path(os.getenv("OKADA_AUTO_CALIBRATION_DIR", "./data/auto_calibration"))
        auto_calibration_profiles_path = Path(os.getenv("OKADA_AUTO_CALIBRATION_PROFILES", str(spec_root / "registry/policies/auto_calibration_profiles.yaml")))
        adopted_policy_file = Path(os.getenv("OKADA_ADOPTED_POLICY_FILE", str(auto_calibration_dir / "adopted_profiles.json")))
        auto_calibration_history_file = Path(os.getenv("OKADA_AUTO_CALIBRATION_HISTORY_FILE", str(auto_calibration_dir / "auto_calibration_history.jsonl")))
        auto_calibration_scheduler_plans_path = Path(os.getenv("OKADA_AUTO_CALIBRATION_SCHEDULER_PLANS", str(spec_root / "registry/policies/auto_calibration_scheduler_plans.yaml")))
        auto_calibration_scheduler_state_file = Path(os.getenv("OKADA_AUTO_CALIBRATION_SCHEDULER_STATE", str(auto_calibration_dir / "scheduler_state.json")))
        champion_challenger_state_file = Path(os.getenv("OKADA_CHAMPION_CHALLENGER_STATE", str(auto_calibration_dir / "champion_challenger_state.json")))
        champion_challenger_history_file = Path(os.getenv("OKADA_CHAMPION_CHALLENGER_HISTORY", str(auto_calibration_dir / "champion_challenger_history.jsonl")))
        auto_calibration_window_history_file = Path(os.getenv("OKADA_AUTO_CALIBRATION_WINDOW_HISTORY", str(auto_calibration_dir / "window_resolution_history.jsonl")))
        auto_calibration_lab_fixture_dir = Path(os.getenv("OKADA_AUTO_CALIBRATION_LAB_FIXTURE_DIR", str(repo_root / "fixtures/auto_calibration/lab")))
        auto_calibration_lab_history_file = Path(os.getenv("OKADA_AUTO_CALIBRATION_LAB_HISTORY", str(auto_calibration_dir / "calibration_lab_history.jsonl")))
        auto_calibration_lab_report_dir = Path(os.getenv("OKADA_AUTO_CALIBRATION_LAB_REPORT_DIR", str(auto_calibration_dir / "lab_reports")))
        auto_calibration_lab_builder_history_file = Path(os.getenv("OKADA_AUTO_CALIBRATION_LAB_BUILDER_HISTORY", str(auto_calibration_dir / "calibration_lab_builder_history.jsonl")))
        return cls(
            audit_dir=audit_dir,
            audit_backend=audit_backend,
            default_policy=default_policy,
            service_port=service_port,
            service_name=service_name,
            shared_token=shared_token,
            require_auth=require_auth,
            spec_root=spec_root,
            auto_calibration_dir=auto_calibration_dir,
            auto_calibration_profiles_path=auto_calibration_profiles_path,
            adopted_policy_file=adopted_policy_file,
            auto_calibration_history_file=auto_calibration_history_file,
            auto_calibration_scheduler_plans_path=auto_calibration_scheduler_plans_path,
            auto_calibration_scheduler_state_file=auto_calibration_scheduler_state_file,
            champion_challenger_state_file=champion_challenger_state_file,
            champion_challenger_history_file=champion_challenger_history_file,
            auto_calibration_window_history_file=auto_calibration_window_history_file,
            auto_calibration_lab_fixture_dir=auto_calibration_lab_fixture_dir,
            auto_calibration_lab_history_file=auto_calibration_lab_history_file,
            auto_calibration_lab_report_dir=auto_calibration_lab_report_dir,
            auto_calibration_lab_builder_history_file=auto_calibration_lab_builder_history_file,
        )


settings = Settings.from_env()
settings.audit_dir.mkdir(parents=True, exist_ok=True)
settings.auto_calibration_dir.mkdir(parents=True, exist_ok=True)
settings.auto_calibration_profiles_path.parent.mkdir(parents=True, exist_ok=True)
settings.auto_calibration_scheduler_plans_path.parent.mkdir(parents=True, exist_ok=True)
settings.auto_calibration_lab_fixture_dir.mkdir(parents=True, exist_ok=True)
settings.auto_calibration_lab_report_dir.mkdir(parents=True, exist_ok=True)
