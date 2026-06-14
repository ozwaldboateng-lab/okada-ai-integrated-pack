# Adapter Proposal Generators

## Purpose
This document defines the adapter-specific proposal generators used by auto-calibration. Prior stages resolved a calibration window and produced adapter-aware summary metrics. This stage turns those summaries into candidate thresholds and weights with adapter-specific semantics.

## Design Rule
Proposal generation is no longer purely common-heuristic. It now follows:

1. Resolve replay window
2. Summarize adapter metrics
3. Generate candidate policy with adapter-specific strategy
4. Validate candidate against baseline
5. Adopt only if the profile gate allows it

## Adapter Strategies

### Routing
Uses `promotion_pressure_mean`, `budget_tight_rate`, `latency_load_mean`, and `complexity_mean` to shape `promotion_threshold`, plus small adjustments to `T_clean` and `T_contam`.

### RAG
Uses `freshness_mean`, `grounding_confidence_mean`, `conflict_mean`, `stale_answer_rate`, and `re_retrieve_pressure_mean` to shape `abstain_threshold`, `freshness_threshold`, and contamination boundaries.

### Monitoring
Uses `unsafe_signal_mean`, `override_rate_mean`, `output_shift_mean`, and `latency_instability_mean` to shape `unsafe_threshold` and risk-sensitive weights.

### Drift
Uses `retrain_pressure_mean`, `challenger_disagreement_mean`, `feature_drift_mean`, and `performance_decay_mean` to shape `retrain_threshold` and `rollback_threshold`.

### Agent
Uses `escalation_pressure_mean`, `planner_executor_mismatch_mean`, `retry_mean`, and `unresolved_subgoal_mean` to shape `escalation_threshold` and `handoff_threshold`.

## Safety Note
The generator only proposes candidates. The validation and adoption gates remain mandatory.
