# 状態遷移設計

- Document ID: OAI-DD-STATE-001
- Version: 0.2

## 1. 共通 regime state
全 adapter は最小限次の regime state を持つ。
- `clean`
- `mixed`
- `contaminated`

補助 state:
- `recovering`
- `abstained`
- `handoff_pending`

## 2. 共通遷移ルール
- `clean -> mixed`: dominant route は残るが競合または残留が閾値超過
- `mixed -> clean`: dominant route が再優勢化し、競合/残留が収束
- `mixed -> contaminated`: dominant collapse または high-risk policy trigger
- `contaminated -> recovering`: intervention 実施済みで改善兆候あり
- `recovering -> clean`: trust / integrity が閾値回復
- `recovering -> contaminated`: intervention 失敗または再悪化

## 3. Monitoring specific
- `safe -> caution -> unsafe -> recovering -> safe`
- `unsafe -> human_review_pending` を許可

## 4. Drift specific
- `keep -> shadow -> rollback | retrain -> validating -> keep`

## 5. Agent specific
- `continue -> constrained_continue -> replan -> handoff_pending | abort`
- `handoff_pending -> continue` は人間修正後のみ許可

## 6. RAG specific
- `no_retrieval | standard_retrieval -> deeper_retrieve -> rerank_again -> answer | abstain`

## 7. Routing specific
- `cheap_only -> cheap_then_fallback_strong -> strong_only`
- `bounded_hybrid` と `branchwise_hybrid` は side state として扱う

## 8. state persistence
最低限保存する state:
- `current_regime`
- `previous_regime`
- `transition_reason`
- `last_intervention`
- `transition_timestamp`
