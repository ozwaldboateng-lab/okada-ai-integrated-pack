# Benchmark Policy

## 1. 原則
「同じ条件なのに高性能」を示すため、以下を固定する。

- model pool
- knowledge source
- allowed tools
- budget constraint
- number of runs
- benchmark set
- scoring rule

変えるのは **岡田理論レイヤーの有無** のみとする。

## 2. ベースライン
### RAG
- always retrieve
- top-k fixed retrieval
- reranker-only
- no abstention

### Routing
- fixed strongest
- fixed cheapest
- cost-only router
- confidence-only router
- static fallback

### Agent
- max_steps
- retry threshold
- timeout
- heuristic human handoff
- no governance

### Monitoring
- static threshold
- single drift score
- SLA-only

## 3. 主評価指標
- task success
- cost per success
- p95 latency
- retrieval waste
- tool-call waste
- stale answer reduction
- catastrophic failure reduction
- false retrain / rollback reduction
- abstention quality

## 4. 受け入れの考え方
- 品質だけでなくコストと遅延も見る
- handoff / abstain の過剰化を防ぐ
- 同一条件比較を崩す要因を排除する
