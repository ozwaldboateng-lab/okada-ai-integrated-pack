# Open WebUI Runbook

## 1. Environment
Set:
- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`
- optional model ids for Pipe configuration

## 2. Install sequence
1. Start the Okada kernel service.
2. Confirm `/healthz` is healthy.
3. Register Pipe and Filter into Open WebUI.
4. Apply metadata fields to the operator UI.
5. Run smoke conversation tests.

## 3. Smoke checks
- Low-risk prompt chooses cheap model.
- High-complexity prompt can promote to strong model.
- Filter metadata appears on the request.
- Contaminated blocking works when enabled.
- Fail-safe metadata appears when kernel is unavailable.

## 4. Manual evaluation workflow
Use `docs/61_openwebui_manual_eval_workflow.md` for the operator route-and-audit
walkthrough. It is backed by `fixtures/e2e/openwebui_manual_eval.json` and
requires one routing case plus one RAG audit-review case.

## 5. Operational checks
- Inspect `okada_audit_trace_id` for each routed request.
- Confirm operators can identify why the system chose a route.
- Confirm no request is silently dropped by the filter.

## 6. Rollback
If the integration causes UI issues:
- disable the Filter first
- keep the Pipe disabled until metadata issues are fixed
- fall back to standard Open WebUI routing
