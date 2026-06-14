# Calibration Window Aggregator

## Purpose
The calibration window aggregator resolves an adapter-specific replay window from accumulated audit logs.
It exists to prevent auto-calibration from depending on fixed inline fixtures only.

## Core behavior
- reads recent audit records
- maps audit records into `WindowRecord`
- applies adapter/profile window policy
- supports `request`, `time`, and `request_or_time`
- backfills older records when time-window volume is insufficient
- can filter by `risk_class`, `invocation`, and `source`
- persists a window-resolution history entry for later inspection

## Why it matters
The project now has:
1. log accumulation
2. proposal / validate / adopt
3. scheduler / champion-challenger

The missing layer was deciding **which logs belong to the current calibration window**.
This module fills that gap.

## Current scope
Implemented for audit-backed windows.
Future extensions may include:
- benchmark-weighted windows
- stratified per-risk quotas
- champion/challenger split windows
- source-of-truth weighted replay windows
