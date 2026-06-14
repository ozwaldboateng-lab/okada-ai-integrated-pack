# Dify Detailed Integration Design

## Goal
This document defines how to wire the Okada Governance Kernel into Dify with enough precision that a code-generation model or engineer can implement the workflow without guessing the control surfaces.

## Scope
This design covers:
- RAG governance through pre-retrieval and post-retrieval checks
- variable contract between Dify workflow nodes and the Okada kernel
- fail-safe behavior when the kernel is unavailable

It does not cover:
- custom Dify plugin development
- direct forking of Dify core
- non-RAG domain adapters

## Integration style
Use Dify as the orchestration shell:
1. Collect query and lightweight observables.
2. Call `/okada/diagnose` before retrieval.
3. Branch on retrieval policy.
4. After retrieval, summarize evidence.
5. Call `/okada/diagnose` again.
6. Branch on answer policy.
7. Generate or abstain.

## Required environment variables
- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`

## Node layout
- `start`
- `build_observables`
- `okada_pre_retrieval` (HTTP Request)
- `pre_retrieval_transform` (Code)
- `pre_retrieval_branch`
- `knowledge_retrieve` / `knowledge_retrieve_deeper`
- `retrieval_summary`
- `okada_post_retrieval` (HTTP Request)
- `post_retrieval_transform` (Code)
- `post_retrieval_branch`
- `answer_generation` / `abstain_response`

## Variable contract
Use `examples/dify/workflow_variables.md` as the source-of-truth contract.

## HTTP request design
Both pre and post retrieval calls use the same endpoint:
- method: `POST`
- endpoint: `/okada/diagnose`
- auth: Bearer token
- body type: JSON

Payload templates:
- `examples/dify/http_request_payload_pre.json`
- `examples/dify/http_request_payload_post.json`

## Code node design
Dify code nodes should remain thin:
- reshape the kernel response into branch variables
- do not reimplement governance logic in the code node
- avoid hidden defaults other than fail-safe routing

Files:
- `examples/dify/code_node_pre_retrieval.py`
- `examples/dify/code_node_post_retrieval.py`
- `examples/dify/retrieval_summary_transform.py`

## Fail-safe design
If the Okada kernel call fails:
- pre-retrieval: continue with `standard_retrieve`
- post-retrieval: continue with `answer_generation`
- always set `okada_governance_available = false`
- expose a fail-safe reason if Dify workflow variables allow it

## Audit strategy
Dify itself is not the source-of-truth for governance audit.
The kernel service persists its own audit trail.
Dify only needs to propagate:
- `okada_audit_trace_id`
- selected branch
- workflow execution id if available

## Minimal acceptance target
A Dify app is considered integrated when:
- it can call the kernel before retrieval
- it can call the kernel after retrieval
- it branches on the returned governance variables
- it survives kernel downtime with a declared fail-safe branch
