# Conditional Branch Matrix

## Pre-retrieval
- `no_retrieval` -> answer without RAG
- `standard_retrieve` -> normal knowledge retrieval
- `deeper_retrieve` -> large top-k + rerank
- `abstain` -> abstention answer template

## Post-retrieval
- `continue` -> final answer generation
- `rerank_again` -> rerank path
- `require_fresh_source` -> freshness recovery path
- `abstain` -> abstention answer template
