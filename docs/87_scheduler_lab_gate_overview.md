# Scheduler Lab Gate Overview

This document defines the scheduler-side automatic calibration lab replay gate.

## Goal

Allow scheduler plans to automatically run fixture replay suites during validation so that
proposal/adoption decisions are guarded by both recent audit windows and stable replay suites.

## Behavior

- Each scheduler plan may enable `auto_run_calibration_lab`.
- If enabled, the scheduler resolves a replay suite using:
  1. explicit `lab_suite_name`
  2. exact match on `(profile_name, spec_id, adapter_type)` from the suite manifest
  3. first suite matching `adapter_type`
- Validation receives:
  - `run_calibration_lab=true`
  - resolved `lab_suite_name`
  - `persist_lab_report` from the plan
- If `require_lab_gate=true` and no lab suite executes successfully, adoption is blocked.

## Intended first use

- `routing_guarded_daily` -> `routing_replay_smoke`
- `rag_shadow_daily` -> `rag_replay_smoke`

## Result fields

Scheduler results now include:

- `lab_executed`
- `lab_suite_name`
- `lab_report_id`
- `lab_gain_vs_current`
