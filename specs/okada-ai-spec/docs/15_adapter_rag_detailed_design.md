# OKD-AI-004 詳細設計

- Document ID: OAI-DD-004
- Spec ID: OKD-AI-004

## 1. 目的
RAG adapter は retrieval の要否、深さ、再検索、stale source 警告、abstain を統御する。

## 2. 呼び出しタイミング
- query intake 後
- retrieval 結果取得後
- answer draft 後

## 3. 入力観測量
### 必須
- `retrieval_score_distribution`
- `source_freshness`
- `chunk_conflict_rate`
- `grounding_confidence`
- `index_age`

### 任意
- `reranker_disagreement`
- `source_priority`
- `source_of_truth_flag`
- `chunk_redundancy`
- `question_time_sensitivity`

## 4. feature construction
- `H_dom`: evidence-to-answer chain viability
- `H_hist`: stale index / stale cache / stale chunk carry-over
- `H_comp`: conflicting passages / competing documents / reranker split
- `V_first`: contradiction / stale cue / grounding failure
- `context_contamination_score`
- `freshness_gap_score`

## 5. Dify integration
### 推奨 workflow stage
1. query normalization
2. `okada_pre_retrieval`
3. retrieval node
4. `okada_post_retrieval`
5. optional re-retrieval / rerank branch
6. answer draft
7. `okada_pre_answer`
8. final answer or abstain

## 6. action policy
- clean + low retrieval need -> `no_retrieval` 可
- clean + retrieval need -> `standard_retrieval`
- mixed -> `deeper_retrieve` or `rerank_again`
- contaminated + low grounding -> `abstain`
- contaminated + stale time-sensitive -> `require_fresh_source`

## 7. source priority rule
`source_of_truth_flag` がある source は rank を上げるが、freshness と contradiction の検査は免除しない。

## 8. pseudocode
```text
if regime == clean and retrieval_need_low:
    action = no_retrieval
elif regime == clean:
    action = standard_retrieval
elif regime == mixed and freshness_gap_score >= T_fresh:
    action = deeper_retrieve
elif regime == contaminated and grounding_confidence < T_ground:
    action = abstain
else:
    action = rerank_again
```

## 9. 最小ベンチマーク
- fresh clean corpus
- stale corpus
- conflicting corpus
- mixed freshness corpus
- unanswerable query

## 10. 実装上の注意
- freshness と source priority を混同しない
- conflict は contradiction と diversity に分解する
- abstain は最終手段であり default ではない
