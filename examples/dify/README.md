# Dify Example (Gateway Unified)

Use Dify HTTP Request nodes against integration-gateway endpoints:
- `POST /integrations/dify/rag/pre-retrieval`
- `POST /integrations/dify/rag/post-retrieval`
- `POST /integrations/dify/fail-safe`

Pattern:
1. HTTP Request node sends `{payload, options}`.
2. Gateway returns `IntegrationResponse`.
3. Code node exports `transformed_payload` as workflow variables.

## Import Order

1. Add workflow variables from `workflow_variables.md`.
2. Import or recreate the pre-retrieval HTTP Request node using
   `http_request_payload_pre.json` and endpoint
   `/integrations/dify/rag/pre-retrieval`.
3. Attach `code_node_pre_retrieval.py` after the pre-retrieval HTTP Request
   node.
4. Add retrieval branches from `conditional_branch_matrix.md`.
5. Import or recreate the post-retrieval HTTP Request node using
   `http_request_payload_post.json` and endpoint
   `/integrations/dify/rag/post-retrieval`.
6. Attach `code_node_post_retrieval.py` after the post-retrieval HTTP Request
   node.
7. Add a fail-safe HTTP Request node for `/integrations/dify/fail-safe`, using
   `default_action=standard_retrieve` unless the workflow has a stricter local
   fallback.

`import_manifest.yaml` lists only integration-gateway endpoints. Dify nodes
should not call `/okada/diagnose` directly.

## Fail-Safe Branch Contract

When gateway access fails or returns no `transformed_payload`, code nodes emit:

- `okada_governance_available=false`
- `okada_recommended_action=standard_retrieve`
- `okada_retrieval_action=standard_retrieve`
- `okada_should_retrieve=true`
- `okada_should_abstain=false`

Route that branch to standard retrieval or a local fallback response. Do not
silently proceed as if governance succeeded.

## Preflight

With the kernel running:

```bash
OKADA_BASE_URL=http://localhost:8080 python scripts/dify_preflight.py
```

The preflight exercises pre-retrieval, post-retrieval, and fail-safe gateway
endpoints using the same payload files referenced by the manifest.

## Live Demo Matrix

Use `docs/36_dify_acceptance_matrix.md` for the compact clean/mixed/contaminated
walkthrough. The expected RAG cases are backed by `fixtures/e2e/rag_cases.jsonl`
and the generated report at `data/benchmarks/e2e_summary.json`.
