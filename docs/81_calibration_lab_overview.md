# Calibration Lab Overview

The calibration lab replays current and proposed policies over fixture suites and emits human-readable reports.

## Purpose
- compare current vs proposed policy on stable replay suites
- provide lightweight visualization before adoption
- save markdown reports and JSONL report history

## Flow
1. select suite
2. resolve current policy
3. resolve or generate proposed policy
4. replay each case under both policies
5. compute utility deltas and preferred-action match rates
6. persist report
