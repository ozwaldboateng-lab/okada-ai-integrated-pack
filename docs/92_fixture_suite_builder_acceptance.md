# Fixture Suite Builder Acceptance

## Minimum acceptance criteria

1. can build a suite from inline `window_records`
2. writes a JSONL fixture file under the generated fixture directory
3. updates `suite_manifest.yaml`
4. built suite appears in `/lab/suites`
5. built suite can be replayed by `/lab/replay`
6. build history is persisted and queryable

## Quality expectations

- generated suites must be replay-safe
- suite size must respect `max_cases`
- `overwrite=false` must protect existing suites
- baseline action inference must be deterministic

## Explicit limitations

- generated suites are not assumed to be final benchmark artifacts
- preferred actions derived from logs remain provisional
- score tables are bootstrap-level and must remain inspectable
