# OKD-AI-002 詳細設計

- Document ID: OAI-DD-002
- Spec ID: OKD-AI-002

## 1. 目的
MLOps drift adapter は、drift detector を置き換えず、その出力を intervention decision に変換する。

## 2. 呼び出しタイミング
- 定期 drift report 生成時
- challenger / champion 比較時
- quality alert 発生時

## 3. 入力観測量
### 必須
- `feature_drift_score`
- `uncertainty_drift`
- `calibration_lag`
- `performance_decay_proxy`

### 任意
- `challenger_disagreement`
- `label_delay`
- `label_drift_proxy`
- `retrain_cost_estimate`
- `rollback_candidate_available`

## 4. feature construction
- `H_dom`: champion still-validity score
- `H_hist`: old-distribution dependence + stale calibration + delayed corrective action
- `H_comp`: challenger pressure + new-distribution pressure
- `V_first`: earliest drift handle
- `retrain_pressure_score`
- `rollback_viability_score`

## 5. action policy
- clean -> `keep`
- mixed -> `watch` or `shadow_deploy`
- contaminated + rollback_viability high -> `rollback`
- contaminated + retrain pressure high -> `retrain`
- contaminated + both uncertain -> `human_approval`

## 6. decision notes
- retrain は drift score の大きさだけで決めない
- challenger disagreement は challenger 自身の安定性とセットで読む
- rollback candidate が stale な場合は viability を減点する

## 7. pseudocode
```text
features = derive_drift_features(normalized)
if features["rollback_viability_score"] >= T_rb and regime == contaminated:
    action = rollback
elif features["retrain_pressure_score"] >= T_rt and regime == contaminated:
    action = retrain
elif regime == mixed:
    action = shadow_deploy
else:
    action = keep
```

## 8. OSS 差し込み
- drift detector の出力は外部 service から ingest
- Dify は approval workflow の殻
- Open WebUI は operator approval / audit console

## 9. 監査出力
- retrain_pressure_score
- rollback_viability_score
- challenger pressure rationale
- intervention cost note

## 10. 最小ベンチマーク
- no drift
- transient drift
- recoverable drift
- hard concept shift
- false alarm

## 11. 実装上の注意
- detector score をそのまま regime に写さない
- retrain cost を policy profile で注入する
- label delay のある環境では quality decay proxy を重く見る
