# Calibration Window Runbook

## Basic endpoint
`POST /okada/auto-calibration/windows/resolve`

## Recommended usage
- routing: request-or-time, short age, capped record count
- rag: request-or-time, freshness-sensitive, optional risk filtering
- monitoring: time-heavy, longer windows
- agent: longer windows, likely advisory first

## Operational guidance
1. Start with `include_records=true` to inspect resolved windows.
2. Verify that the selected count is large enough.
3. Check `backfilled_count`.
4. If backfill dominates, widen cadence or lower the minimum request target.
5. Only then enable scheduler-driven proposal generation.

## Failure mode to watch
A very small high-risk segment may cause overfitting if used alone.
Prefer manual review or blended policies for sparse risk buckets.
