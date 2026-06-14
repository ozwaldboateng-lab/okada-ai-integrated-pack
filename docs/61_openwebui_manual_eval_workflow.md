# Open WebUI Manual Evaluation Workflow

Source plan: `fixtures/e2e/openwebui_manual_eval.json`

## Purpose
Verify that Open WebUI operators can see route-aware decisions and follow the
same trace into audit artifacts.

## Screens and Artifacts

| Step | Screen / Artifact | Expected Evidence |
|---|---|---|
| 1 | Open WebUI chat with `okada_governance_pipe.py` enabled | selected model and `okada_*` metadata are visible on the message |
| 2 | Open WebUI message metadata with `okada_audit_filter.py` enabled | `okada_filter_audit_payload` is attached |
| 3 | `data/audit/audit_records.jsonl` | trace id from the message has a persisted audit record |
| 4 | `data/benchmarks/e2e_summary.json` | fixture-backed routing and RAG outcomes are reviewable |
| 5 | `examples/openwebui/operator_console_contract.md` | visible fields match the operator contract |

## Manual Cases

| Case | Fixture ID | Adapter | Expected Action | Operator Check |
|---|---|---|---|---|
| Route promotion | `routing-hard-high-risk` | routing | `promote_strong_model` | Pipe selects the strong model and preserves `okada_audit_trace_id`. |
| RAG abstain review | `rag-stale-conflict` | rag | `abstain` | E2E summary shows contaminated RAG behavior for operator audit review. |

## Procedure
1. Start the preferred integrated stack from `docs/47_integrated_runbook.md`.
2. Install `examples/openwebui/okada_governance_pipe.py` and then
   `examples/openwebui/okada_audit_filter.py`.
3. Run `OKADA_BASE_URL=http://localhost:8080 python scripts/openwebui_preflight.py`.
4. Send a high-risk or high-complexity prompt through Open WebUI and confirm the
   Pipe exposes `selected_model`, `okada_action`, `okada_regime`, and
   `okada_audit_trace_id`.
5. Confirm the Filter attaches `metadata.okada_filter_audit_payload`.
6. Run `python scripts/e2e_compare.py --pretty` and inspect the two fixture IDs
   in the manual plan.
7. Match the Open WebUI trace id against `data/audit/audit_records.jsonl`.

## Pass Criteria
- The routing case is visible in Open WebUI with a strong-model promotion.
- The RAG case is visible in the E2E summary as an abstain decision.
- The operator can name the audit trace id and the artifact that contains it.
