# Lab-aware Validation and Champion/Challenger Overview

## Purpose
This specification extends auto-calibration validation so that an adapter proposal can be
checked not only against a live/recent calibration window, but also against a replay suite
from the calibration lab.

## Added behavior
- `/okada/auto-calibration/validate` accepts:
  - `run_calibration_lab`
  - `lab_suite_name`
  - `persist_lab_report`
- when enabled, validation runs a calibration-lab replay with:
  - current policy as champion
  - proposed policy as challenger
- validation may add blocking reasons if lab replay fails gate conditions
- validation response now exposes:
  - `lab_summary`
  - `lab_report_id`
  - `lab_report_path`
  - `lab_suite_name`

## Gate semantics
Profile gates may optionally include:
- `min_lab_gain_vs_current`
- `min_lab_preferred_match_delta`
- `require_lab_non_negative`

If omitted, lab replay is advisory unless the caller interprets it otherwise.

## Champion/challenger integration
Shadow evaluation now forwards the same lab replay controls into validation.
The candidate state records:
- `last_lab_suite_name`
- `last_lab_gain_vs_current`
- `last_lab_report_id`
