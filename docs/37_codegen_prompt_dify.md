# Codegen Prompt: Dify Integration

Use this prompt with a code-generation model when you want it to build the Dify-side implementation from the spec pack.

---
Build a Dify workflow integration for the Okada Governance Kernel using the spec pack in this repository.

Requirements:
1. Treat `examples/dify/import_manifest.yaml` as the workflow build manifest.
2. Use `examples/dify/http_request_payload_pre.json` and `examples/dify/http_request_payload_post.json` as the request templates.
3. Use `examples/dify/code_node_pre_retrieval.py`, `examples/dify/code_node_post_retrieval.py`, and `examples/dify/retrieval_summary_transform.py` as the code-node source-of-truth.
4. Do not move governance logic into Dify nodes beyond reshaping variables.
5. Preserve the fail-safe behavior described in `docs/34_dify_detailed_integration.md`.
6. Output:
   - a Dify workflow build guide,
   - any Dify-importable JSON or YAML that can be generated,
   - environment variable instructions,
   - a smoke-test checklist.
7. Keep the branch variable names identical to `examples/dify/workflow_variables.md`.
---
