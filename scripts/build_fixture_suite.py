from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.auto_calibration.fixture_suite_builder import fixture_suite_builder_service
from app.models.auto_calibration import FixtureSuiteBuildRequest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a calibration lab fixture suite from window records")
    parser.add_argument("--input", required=True, help="Path to JSON array of WindowRecord objects")
    parser.add_argument("--profile-name", required=True)
    parser.add_argument("--spec-id", required=True)
    parser.add_argument("--adapter-type", required=True)
    parser.add_argument("--suite-name")
    parser.add_argument("--max-cases", type=int, default=50)
    parser.add_argument("--strategy", default="recent", choices=["recent", "success_weighted", "failure_weighted"])
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    request = FixtureSuiteBuildRequest(
        profile_name=args.profile_name,
        spec_id=args.spec_id,
        adapter_type=args.adapter_type,
        suite_name=args.suite_name,
        window_records=payload,
        max_cases=args.max_cases,
        strategy=args.strategy,
        overwrite=args.overwrite,
    )
    response = fixture_suite_builder_service.build_suite(request)
    print(response.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
