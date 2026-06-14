# Scheduler Runbook

## Endpoints
- `GET /okada/auto-calibration/scheduler/plans`
- `GET /okada/auto-calibration/scheduler/status`
- `POST /okada/auto-calibration/scheduler/run-plan`
- `POST /okada/auto-calibration/scheduler/run-due`

## Typical loop
1. collect audit logs
2. run due scheduler plans
3. inspect results
4. evaluate any shadow challengers
5. promote only when eligible
