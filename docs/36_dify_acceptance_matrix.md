# Dify Acceptance Matrix

| Scenario | Input Condition | Expected Governance Output | Expected Dify Branch |
|---|---|---|---|
| Clean RAG | Fresh sources, low conflict, good grounding | `regime=clean`, `action=continue` or `standard_retrieve` | normal retrieval / answer |
| Stale Corpus | High `index_age`, low freshness, time-sensitive query | `regime=mixed`, `action=deeper_retrieve` or `require_fresh_source` | deep retrieval or fresh-source branch |
| Contradictory Sources | Multiple conflicting chunks | `regime=mixed/contaminated`, `action=rerank_again` or `abstain` | rerank or abstain |
| Weak Grounding | Low grounding confidence after retrieval | `regime=contaminated`, `action=abstain` | abstain response |
| Kernel Down | HTTP failure / timeout | `governance_available=false` | fail-safe retrieval or baseline answer |

## Fixture-backed demo cases

Source: `fixtures/e2e/rag_cases.jsonl`

| Fixture scenario | Expected regime | Expected action | Operator note |
|---|---|---|---|
| `rag-clean-grounded` | `clean` | `no_retrieval` | Fresh, grounded context can answer without extra retrieval. |
| `rag-stale-low-conflict` | `contaminated` | `abstain` | Stale source freshness should not be hidden by low conflict. |
| `rag-stale-conflict` | `contaminated` | `abstain` | Conflicting and stale evidence should stop answer generation. |

## Numbered demo walkthrough

1. Start the kernel service and set `OKADA_BASE_URL`.
2. Run `python scripts/dify_preflight.py`.
3. Import variables from `examples/dify/workflow_variables.md`.
4. Add pre-retrieval HTTP and Code nodes from `examples/dify/`.
5. Add the retrieval branch using `examples/dify/conditional_branch_matrix.md`.
6. Add post-retrieval HTTP and Code nodes from `examples/dify/`.
7. Run a fresh-source query and confirm `rag-clean-grounded`-style behavior.
8. Run a stale-source query and confirm `rag-stale-low-conflict`-style behavior.
9. Run a conflicting-source query and confirm `rag-stale-conflict`-style behavior.
10. Stop or block the gateway and confirm the fail-safe branch exposes
    `okada_governance_available=false`.

## Minimum acceptance
The integration passes when all five cases are manually reproducible and the chosen branches match the matrix.
