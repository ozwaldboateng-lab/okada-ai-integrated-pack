# Auto-Calibration Integration Notes

This repository version integrates the Auto-Calibration Manager into the bootstrap Okada Kernel service.

## What is implemented
- FastAPI routes under `/okada/auto-calibration/*`
- profile catalog loading from `specs/okada-ai-spec/registry/policies/auto_calibration_profiles.yaml`
- proposal / validation / adopt flow
- adopted profile persistence under `data/auto_calibration/`
- policy resolution that can read adopted profiles by `profile_name`
- baseline tests for routing auto-calibration

## What is still bootstrap-grade
- replay scoring is heuristic, not benchmark-tuned
- adoption gates are genericized from profile YAML and should be refined per adapter
- only routing is directly covered by tests
- no scheduler/cron job is included yet; calibration is API-triggered
