# Fixture Suite Builder Runbook

## Main endpoint

`POST /okada/auto-calibration/lab/build-suite`

## Typical request

```json
{
  "profile_name": "routing_default",
  "spec_id": "OKD-AI-005",
  "adapter_type": "routing",
  "suite_name": "generated_routing_daily_guard",
  "window_records": [...],
  "max_cases": 50,
  "strategy": "failure_weighted",
  "overwrite": true
}
```

## Operational modes

### 1. Inline window records
Use when a scheduler or validation flow already has the resolved window.

### 2. Window-request driven
Use `window_request` when the builder should resolve the calibration window itself.

### 3. Recent-audit driven
Use `use_recent_audits=true` for quick suite generation from the audit log.

## Output

The builder returns:

- generated `suite_name`
- persisted `fixture_path`
- summary metadata
- preview cases

If persistence is enabled, it also updates:

- `fixtures/auto_calibration/lab/generated/*.jsonl`
- `fixtures/auto_calibration/lab/suite_manifest.yaml`
- build history JSONL

## Human review guidance

Generated suites should be treated as **candidate replay suites**, not authoritative benchmark suites.

Review at least:

- duplicated scenarios
- obviously noisy or contradictory preferred actions
- missing domain context
- stale cases that should not be replayed anymore

## Recommended first uses

- routing daily guard suites
- rag freshness / contamination refresh suites
- smoke replay coverage for scheduler lab gates
