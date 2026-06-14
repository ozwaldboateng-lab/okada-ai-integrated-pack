# 54. E2E Reporting

## Current state
The repository includes a lightweight fixture-based benchmark harness and summary file.

## Reporting loop
1. Run `python scripts/e2e_compare.py --pretty`.
2. Archive `data/benchmarks/e2e_summary.json`.
3. Run `python scripts/dev_status.py` for a condensed operator report.
4. Compare the Okada summary against the baseline before changing policy thresholds.

## Output artifact

By default, the command writes:

```bash
data/benchmarks/e2e_summary.json
```

Use `--fixture-dir` to point at an alternate fixture directory and `--output` to
write a different artifact path:

```bash
python scripts/e2e_compare.py \
  --fixture-dir fixtures/e2e \
  --output data/benchmarks/e2e_summary.json \
  --pretty
```

Use `--no-write` only when debugging stdout output and no artifact should be
updated.
