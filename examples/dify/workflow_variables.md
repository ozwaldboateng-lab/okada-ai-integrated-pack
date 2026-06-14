# Dify Workflow Variables for Okada Governance

This file defines the variables that should exist in a Dify workflow when wiring the Okada kernel into a RAG application.

## Input-side variables
- `user_query`
- `index_age`
- `source_freshness`
- `question_time_sensitivity`
- `retrieval_score_distribution`
- `grounding_confidence`
- `chunk_conflict_rate`
- `reranker_disagreement`
- `budget_remaining`

## Variables emitted by pre-retrieval governance
- `okada_regime`
- `okada_type_class`
- `okada_trust_state`
- `okada_recommended_action`
- `okada_retrieval_action`
- `okada_final_action`
- `okada_should_retrieve`
- `okada_should_abstain`
- `okada_require_fresh_source`
- `okada_rerank_again`
- `okada_deeper_retrieve`
- `okada_audit_trace_id`
- `okada_alternatives`
- `okada_context_contamination_score`
- `okada_freshness_gap_score`
- `okada_governance_available`

## Variables emitted by post-retrieval governance
- `okada_final_action`
- `okada_require_fresh_source`
- `okada_rerank_again`
- `okada_should_abstain`
- `okada_context_contamination_score`
- `okada_freshness_gap_score`
- `okada_governance_available`

## Variables emitted by fail-safe governance
- `okada_regime`
- `okada_type_class`
- `okada_trust_state`
- `okada_recommended_action`
- `okada_retrieval_action`
- `okada_final_action`
- `okada_should_retrieve`
- `okada_should_abstain`
- `okada_require_fresh_source`
- `okada_rerank_again`
- `okada_deeper_retrieve`
- `okada_audit_trace_id`
- `okada_alternatives`
- `okada_context_contamination_score`
- `okada_freshness_gap_score`
- `okada_governance_available`
- `okada_fail_safe_reason`

## Branching policy
- `okada_should_abstain == true` -> abstain response node
- `okada_deeper_retrieve == true` -> deeper retrieval node
- `okada_require_fresh_source == true` -> fresh-source retrieval node
- `okada_rerank_again == true` -> rerank node
- `okada_governance_available == false` -> fail-safe retrieval or canned fallback node
- else -> answer generation
