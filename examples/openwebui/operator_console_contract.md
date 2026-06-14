# Operator Console Contract

Open WebUI is the human-facing console for review and audit.

## Packaged artifacts
- Pipe: `okada_governance_pipe.py`
- Filter: `okada_audit_filter.py`
- Package index: `pipes_manifest.yaml`

Install the Pipe before the Filter so model routing metadata exists before
message audit metadata is attached.

## Metadata fields expected on messages
- `okada_regime`
- `okada_action`
- `okada_type_class`
- `okada_trust_state`
- `okada_audit_trace_id`
- `okada_alternatives`
- `okada_fail_safe_reason`
- `okada_filter_audit_payload`

## Required environment / valves
- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`
- `CHEAP_MODEL_ID`
- `STRONG_MODEL_ID`

## Operator actions supported
- continue
- watch
- human_review
- hold
- escalate

## Minimum review checklist
1. Confirm the visible handle is plausible.
2. Confirm the suggested action is proportionate.
3. Confirm the fallback / abstain was not triggered by transient noise.
4. Record notes against the trace id.

## Manual evaluation artifacts
- Workflow: `docs/61_openwebui_manual_eval_workflow.md`
- Plan: `fixtures/e2e/openwebui_manual_eval.json`
- Audit log: `data/audit/audit_records.jsonl`
- E2E summary: `data/benchmarks/e2e_summary.json`
