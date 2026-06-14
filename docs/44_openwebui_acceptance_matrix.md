# Open WebUI Acceptance Matrix

## Functional acceptance
- Pipe can call `/okada/route` and return a selected model.
- Filter can call `/okada/diagnose` and add metadata.
- Filter outlet can attach audit payload summaries.
- Fail-safe metadata appears when the kernel is down.

## Governance acceptance
- Route decision is visible to the operator.
- Trust-state tagging is visible to the operator.
- Contaminated blocking is explicit, not silent.
- Alternatives are displayed or preserved in metadata.

## Safety acceptance
- No catastrophic UI failure when the kernel is unreachable.
- No hidden hard block without metadata.
- Operator can distinguish governance block vs infrastructure failure.

## Comparison acceptance
- With Pipe enabled, low-risk requests should remain on cheap route more often than strong-only baseline.
- With Filter enabled, suspicious sessions should show governance metadata more often than baseline UI.

## Manual workflow acceptance

Source: `fixtures/e2e/openwebui_manual_eval.json`

| Case | Fixture ID | Expected Artifact |
|---|---|---|
| route promotion | `routing-hard-high-risk` | `data/audit/audit_records.jsonl` |
| RAG abstain audit review | `rag-stale-conflict` | `data/benchmarks/e2e_summary.json` |
