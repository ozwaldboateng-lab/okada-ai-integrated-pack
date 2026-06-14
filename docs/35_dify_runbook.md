# Dify Runbook

## Purpose
This runbook describes the shortest path for a human or code-generation model to stand up a Dify-side integration against the Okada kernel service.

## Preconditions
- Okada kernel service is running
- `OKADA_BASE_URL` is reachable from Dify
- `OKADA_SHARED_TOKEN` matches on both sides
- a Dify instance is available

## Step 1: create workflow shell
Create a new Dify workflow app for document Q&A.

## Step 2: define input variables
Add these start variables:
- `user_query`
- `index_age`
- `source_freshness`
- `question_time_sensitivity`

## Step 3: add pre-retrieval HTTP Request node
Configure:
- method: POST
- URL: `${OKADA_BASE_URL}/integrations/dify/rag/pre-retrieval`
- Authorization: `Bearer ${OKADA_SHARED_TOKEN}`
- Content-Type: `application/json`
- body from `examples/dify/http_request_payload_pre.json`

## Step 4: add pre-retrieval Code node
Paste `examples/dify/code_node_pre_retrieval.py`.

## Step 5: add retrieval branch
Map:
- abstain -> abstain node
- deeper retrieve -> deep retrieval node
- retrieve -> standard retrieval node
- else -> direct answer

## Step 6: add retrieval summary node
Paste `examples/dify/retrieval_summary_transform.py`.

## Step 7: add post-retrieval HTTP Request node
Configure:
- method: POST
- URL: `${OKADA_BASE_URL}/integrations/dify/rag/post-retrieval`
- Authorization: `Bearer ${OKADA_SHARED_TOKEN}`
- Content-Type: `application/json`
- body from `examples/dify/http_request_payload_post.json`.

## Step 8: add post-retrieval Code node
Paste `examples/dify/code_node_post_retrieval.py`.

## Step 9: add final branch
Map:
- require fresh source -> fresh-source retrieval
- rerank again -> rerank node
- abstain -> abstain node
- else -> answer generation

## Step 10: smoke test
Run at least:
- clean query with fresh sources
- time-sensitive query with stale sources
- conflicting-source query
- kernel unavailable query

Expected fixture-backed examples:

| Fixture scenario | Regime | Action | Branch |
|---|---|---|---|
| `rag-clean-grounded` | clean | `no_retrieval` | answer without extra retrieval |
| `rag-stale-low-conflict` | contaminated | `abstain` | abstention or fresh-source recovery |
| `rag-stale-conflict` | contaminated | `abstain` | abstention |

Run `python scripts/e2e_compare.py --pretty` and inspect the `OKD-AI-004`
rows in `data/benchmarks/e2e_summary.json` before a live Dify demo.

## Operational note
In early versions, do not hide governance output from operators.
Surface:
- regime
- recommended action
- audit trace id
- governance availability

## Offline / gateway-error behavior

Add a fail-safe HTTP Request node:

- URL: `${OKADA_BASE_URL}/integrations/dify/fail-safe`
- Body: `examples/dify/http_request_payload_fail_safe.json`
- Code node fallback: `examples/dify/code_node_transform.py`

When the gateway is unavailable or a gateway response is missing, expose:

- `okada_governance_available=false`
- `okada_recommended_action=standard_retrieve`
- `okada_should_retrieve=true`
- `okada_should_abstain=false`
- `okada_fail_safe_reason`

Route this branch to standard retrieval or a local fallback answer. Operators
should be able to distinguish fail-safe retrieval from a normal governed
decision.
