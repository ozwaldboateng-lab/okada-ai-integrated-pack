# OKD-AI-005 詳細設計

- Document ID: OAI-DD-005
- Spec ID: OKD-AI-005

## 1. 目的
routing adapter は、同一モデル群・同一予算の中で、どのモデル・どの strategy・どの retrieval depth を使うかを選ぶ。

## 2. 呼び出しタイミング
- LiteLLM pre-call hook
- first-pass 失敗後の fallback decision
- post-call audit aggregation

## 3. 入力観測量
### 必須
- `complexity_proxy`
- `budget_remaining`
- `latency_load_state`
- `risk_class`
- `historical_route_success`

### 任意
- `retrieval_need_estimate`
- `question_time_sensitivity`
- `compliance_level`
- `heavy_model_availability`
- `parallel_budget_flag`

## 4. feature construction
- `H_dom`: current best route viability
- `H_hist`: stale routing belief / recent burden / policy inertia
- `H_comp`: alternative route pressure
- `V_first`: mismatch between request profile and current route
- `route_stability_score`
- `promotion_pressure_score`

## 5. LiteLLM integration
### pre-call
- collect request metadata
- call `/okada/route`
- select model / reasoning profile / retrieval toggle

### post-call
- report chosen route, cost, latency, outcome class to `/okada/audit`

## 6. action policy
- cheap path only
- strong path only
- cheap then fallback strong
- strong only for high-risk
- bounded hybrid
- branchwise hybrid

## 7. pseudocode
```text
if risk_class == high and promotion_pressure_score >= T_promote:
    action = strong_only
elif regime == clean and budget_remaining is low:
    action = cheap_only
elif regime == mixed:
    action = cheap_then_fallback_strong
else:
    action = bounded_hybrid
```

## 8. 最小ベンチマーク
- easy low-risk queries
- hard reasoning queries
- retrieval-heavy queries
- latency-sensitive queries
- budget-stressed runs

## 9. 実装上の注意
- routing overhead 自体を監査する
- historical route success に decay を入れる
- model availability を policy profile で与える
