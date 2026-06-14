# Open WebUI Example (Gateway Unified)

Both the Pipe and the Filter call integration-gateway endpoints:
- `POST /integrations/openwebui/pipe`
- `POST /integrations/openwebui/filter`

## Packaged Artifacts

Install these files into Open WebUI in this order:

1. `okada_governance_pipe.py`
2. `okada_audit_filter.py`

`pipes_manifest.yaml` is the package index for operators. It lists the artifact
files, gateway endpoints, required environment variables, and valve names.

## Environment

Required:

```bash
OKADA_BASE_URL=http://localhost:8080
```

Optional:

```bash
OKADA_SHARED_TOKEN=change-me
OPENWEBUI_OKADA_CHEAP_MODEL_ID=gpt-4o-mini
OPENWEBUI_OKADA_STRONG_MODEL_ID=gpt-4.1
OPENWEBUI_OKADA_BLOCK_ON_CONTAMINATED=false
```

The Pipe exposes valves for `CHEAP_MODEL_ID`, `STRONG_MODEL_ID`,
`OKADA_BASE_URL`, and `OKADA_SHARED_TOKEN`. The Filter exposes valves for
`OKADA_BASE_URL` and `OKADA_SHARED_TOKEN`.

## Operator Flow

1. The Pipe calls `/integrations/openwebui/pipe` and returns a selected model plus
   Okada metadata.
2. The Filter calls `/integrations/openwebui/filter`, attaches audit metadata to
   the message body, and stores the generated audit payload under
   `metadata.okada_filter_audit_payload`.
3. The operator console should display the fields documented in
   `operator_console_contract.md`.

For the manual route-and-audit workflow, use
`docs/61_openwebui_manual_eval_workflow.md`. The workflow is backed by
`fixtures/e2e/openwebui_manual_eval.json` and includes one routing case plus
one RAG audit-review case.

## Preflight

With the kernel running:

```bash
OKADA_BASE_URL=http://localhost:8080 python scripts/openwebui_preflight.py
```

The preflight validates the manifest, confirms artifact files exist, and calls
both Open WebUI gateway endpoints.
