# Calibration Window Aggregator Acceptance

The window aggregator is acceptable when:
- it resolves a non-empty replay window for adapters with recent traffic
- request-or-time mode backfills older records only when necessary
- time mode never leaks records older than the configured bound
- risk filtering is deterministic and auditable
- scheduler runs without inline `window_records` can still produce proposals
- a window resolution history entry is written for every request
