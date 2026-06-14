# Calibration Lab Runbook

## Endpoints
- `GET /okada/auto-calibration/lab/suites`
- `POST /okada/auto-calibration/lab/replay`
- `GET /okada/auto-calibration/lab/history`

## Typical use
1. list suites
2. run replay with generated proposal
3. inspect markdown report under `data/auto_calibration/lab_reports/`
4. decide whether to continue to validation/adopt
