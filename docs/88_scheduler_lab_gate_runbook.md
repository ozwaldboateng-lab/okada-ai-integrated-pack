# Scheduler Lab Gate Runbook

## Configure a plan

Add the following keys to `specs/okada-ai-spec/registry/policies/auto_calibration_scheduler_plans.yaml`:

```yaml
auto_run_calibration_lab: true
lab_suite_name: routing_replay_smoke
persist_lab_report: true
require_lab_gate: true
```

## Run a plan

```bash
curl -X POST http://localhost:8000/okada/auto-calibration/scheduler/run-plan \
  -H 'Content-Type: application/json' \
  -d '{"plan_name":"routing_guarded_daily","force":true}'
```

## Check the result

Look for:

- `lab_executed=true`
- non-null `lab_report_id`
- `lab_gain_vs_current`
- notes including `lab_suite=...`

## Failure modes

- If no suite is resolved and `require_lab_gate=false`, the scheduler continues without lab replay.
- If no suite is resolved and `require_lab_gate=true`, the scheduler blocks recommendation/adoption.
