from __future__ import annotations

import argparse
import json

from app.auto_calibration.calibration_lab import calibration_lab_service
from app.models.auto_calibration import CalibrationLabReplayRequest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile-name', required=True)
    parser.add_argument('--spec-id', required=True)
    parser.add_argument('--adapter-type', required=True)
    parser.add_argument('--suite-name', required=True)
    parser.add_argument('--no-generate', action='store_true')
    args = parser.parse_args()

    response = calibration_lab_service.replay(
        CalibrationLabReplayRequest(
            profile_name=args.profile_name,
            spec_id=args.spec_id,
            adapter_type=args.adapter_type,
            suite_name=args.suite_name,
            generate_proposal_if_missing=not args.no_generate,
        )
    )
    print(json.dumps(response.model_dump(mode='json'), indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
