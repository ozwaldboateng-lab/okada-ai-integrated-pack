# Open WebUI Detailed Integration

## Goal
Use Open WebUI as the operator-facing surface for:
- route-aware access via Pipe functions
- trust-window tagging via Filters
- manual inspection of governance metadata and audit traces

Open WebUI is **not** the primary workflow engine. It is the console and manual review layer.

## Integration split
- **Pipe**: OKD-AI-005 Multi-model / Multi-strategy Routing Governance
- **Filter**: OKD-AI-001 Post-deployment Monitoring / Trust Window Governance
- **Optional Tool**: audit trace fetch / replay helper in a later phase

## Pipe placement
Input path:
1. User submits chat request.
2. Pipe extracts last user message, risk metadata, and budget hints.
3. Pipe calls `/okada/route`.
4. Pipe maps `recommended_action` to `cheap_model` or `strong_model`.
5. Pipe stores governance metadata on the request.

## Filter placement
Input path:
1. Filter inlet receives message body.
2. Filter calls `/okada/diagnose` with monitoring observables.
3. Filter writes regime / action / trust_state into metadata.
4. If configured, filter blocks contaminated traffic.

Output path:
1. Filter outlet attaches audit payload summary.
2. Operator can review the payload and trace id.

## Required metadata contract
- `okada_regime`
- `okada_action`
- `okada_type_class`
- `okada_trust_state`
- `okada_audit_trace_id`
- `okada_alternatives`

## Fail-safe policy
If Open WebUI cannot reach the kernel:
- do not crash the entire UI flow
- mark `okada_fail_safe_reason = governance_unavailable`
- default to `regime = mixed`, `action = continue`
- leave a visible audit hint for the operator

## Security note
Open WebUI extensions execute Python on the server side. Treat Pipe / Filter code as trusted code only.
