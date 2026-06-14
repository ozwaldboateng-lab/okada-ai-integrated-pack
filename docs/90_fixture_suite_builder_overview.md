# Fixture Suite Builder Overview

## Goal

Add a half-automatic path from **recent operational logs / calibration windows** to **replayable calibration lab suites**.

This layer closes the remaining gap between:

- real audit / window records, and
- reusable fixture suites for lab replay and scheduler lab gates.

## Position in the flow

The builder sits after window aggregation and before calibration lab replay.

```text
recent audits / window records
  -> window aggregator
  -> fixture suite builder
  -> calibration lab replay
  -> validation / scheduler lab gate / champion-challenger
```

## Responsibilities

- resolve source records from inline windows, window requests, or recent audits
- select a bounded subset according to a simple suite-build strategy
- derive `CalibrationLabCase` rows from `WindowRecord`
- infer baseline action when the source record does not already provide one
- persist generated suites under `fixtures/auto_calibration/lab/generated/`
- upsert entries into `suite_manifest.yaml`
- record build history for audit and repeatability

## Non-goals

- benchmark-quality scenario authoring
- semantic deduplication beyond bounded truncation
- automatic gold-label generation for every domain
- production-grade curation without human review

## Current strategies

- `recent`
- `success_weighted`
- `failure_weighted`

These are intentionally simple bootstrap strategies.

## Expected usage

1. collect recent audits or resolve a calibration window
2. build a generated suite
3. replay current vs proposed policy on the generated suite
4. optionally promote the generated suite into a manually curated benchmark later
