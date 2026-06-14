# Adapter Metric Aggregators

## Purpose

The calibration window resolver selects *which* records are replayed. Adapter metric aggregators summarize those replay windows into domain-shaped signals that are easier to inspect and tune.

This layer sits between:

- calibration window aggregation
- proposal generation / validation
- human review of candidate parameter changes

## Scope

Current first-wave support:

- routing
- rag
- monitoring
- drift
- agent

## Output contract

Each summary returns:

- common quality/cost/latency metrics
- adapter-specific metrics
- counts
- notes
- originating window summary

## Design intent

The purpose is not to replace outcome replay. The purpose is to make each calibration proposal legible in the vocabulary of the target adapter.
