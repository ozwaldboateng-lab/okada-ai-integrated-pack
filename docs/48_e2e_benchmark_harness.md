# E2E Benchmark Harness

## Purpose
Provide the first comparison scaffold for the claim:

> under the same model pool, knowledge source, and budget conditions, the Okada-governed system can outperform a naive baseline as an end-to-end system.

This harness is not the final benchmark. It is the first deterministic and executable comparison scaffold.

## Structure
The harness consumes fixture lines from `fixtures/e2e/*.jsonl`.
Each fixture line contains:
- `scenario_id`
- `spec_id`
- `mode`
- `request`
- `baseline_action`
- `preferred_actions`
- `score_table`

The harness then:
1. executes the Okada kernel decision
2. reads the baseline action
3. scores both actions through the same score table
4. reports win/loss/tie and aggregate utility

## Why this matters
This keeps the experimental question focused on system decisions rather than model mythology.
The claim becomes measurable:
- does the Okada action match the preferred intervention more often?
- does it produce higher utility under the same scoring assumptions?

## Current scope
The harness currently includes:
- routing scenarios
- rag scenarios
- monitoring scenarios
- agent scenarios

## Case families

The fixture pack intentionally includes both favorable and stress cases:

- ambiguous routing: mid-cost prompts where bounded hybrid routing should beat
  unconditional strong-model promotion
- stale RAG: low-freshness or contradiction-prone retrieval contexts where
  abstain or fresh-source behavior can outperform deeper retrieval
- agent derailment: retry loops, split routes, and tool disagreement where
  handoff or replan is preferred over continuing blindly
- monitoring degradation: soft degradation and unsafe operator-facing signals
  that should trigger validation or review

## Not the final paper benchmark
This harness does **not** replace later real-world or dataset-level experiments.
It is a transition device between design-time specification and runtime benchmarking.
