# Adapter Metric Aggregator Runbook

## Primary API

`POST /okada/auto-calibration/metrics/summarize`

Use this endpoint when you want a human-readable replay summary before proposing or adopting parameter changes.

## Typical flow

1. Resolve a calibration window.
2. Summarize metrics for that window.
3. Inspect adapter-specific metrics.
4. Run propose / validate.
5. Compare proposed thresholds against the summary.

## Notes

- Routing summaries emphasize promotion pressure and budget tightness.
- RAG summaries emphasize freshness, conflict and stale-answer exposure.
- Monitoring summaries emphasize unsafe signal accumulation.
- Drift summaries emphasize retrain pressure.
- Agent summaries emphasize escalation pressure and route fragmentation.
