# Codegen Prompt: Open WebUI Detailed Integration

Implement the Open WebUI integration for the Okada AI kernel.

Requirements:
- Create a Pipe using OKD-AI-005 for routing decisions.
- Create a Filter using OKD-AI-001 for trust-window metadata.
- Use `OKADA_BASE_URL` and `OKADA_SHARED_TOKEN` environment variables.
- Keep a fail-safe path that does not crash the UI when the kernel is unavailable.
- Attach governance metadata fields to the body metadata.
- Preserve `okada_audit_trace_id` and `okada_alternatives`.
- Keep all logic operator-auditable.

Produce code that can be dropped into Open WebUI extensions with minimal edits.
