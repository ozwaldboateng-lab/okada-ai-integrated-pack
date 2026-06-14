# OKD-AI-001 詳細設計

- Document ID: OAI-DD-001
- Spec ID: OKD-AI-001

## 1. 目的
post-deployment monitoring adapter は、本番運用中AIシステムの trust window を評価し、watch / shadow validation / rollback / retrain trigger / human review を選ぶ。

## 2. 呼び出しタイミング
- workflow 実行終端
- 定期監視バッチ
- 重大インシデント発報時

## 3. 入力観測量
### 必須
- `confidence_trend`
- `calibration_error_trend`
- `fallback_rate`
- `override_rate`
- `latency_instability`
- `output_shift_score`

### 任意
- `delayed_gt_disagreement`
- `tool_failure_rate`
- `complaint_rate`
- `recent_release_flag`

## 4. 正規化
- trend 系は `level`, `slope`, `volatility` に分解
- rate 系は stable baseline 比へ写像
- binary flag は `0/1` のまま残すが、重大 flag と一般 flag を分離

## 5. feature construction
- `H_dom`: confidence stability + low fallback + low override + low latency instability
- `H_hist`: calibration debt + release residue + unresolved degradation carry-over
- `H_comp`: complaint / delayed_gt_disagreement / tool failure pressure
- `V_first`: 最初に許容域外へ出た指標名と時刻
- `trust_window_score`: `H_dom - f(H_hist, H_comp)` の bounded score

## 6. 判定ロジック
### rule skeleton
- trust_window_score 高かつ R_diag 低 -> `safe/clean`
- trust_window_score 中程度かつ dominant route 残存 -> `caution/mixed`
- trust_window_score 低または dominant collapse -> `unsafe/contaminated`

### action mapping
- safe -> `continue`
- caution -> `watch` or `shadow_validation`
- unsafe + rollback candidate available -> `rollback`
- unsafe + persistent quality loss -> `retrain_trigger`
- unsafe + high-risk context -> `human_review`

## 7. 代表 pseudocode
```text
normalized = normalize_monitoring(observables)
features = derive_monitoring_features(normalized)
regime = classify_regime(features, policy)
if regime == clean:
    action = continue
elif regime == mixed:
    action = shadow_validation if features["V_first"].name in monitorable_handles else watch
else:
    action = rollback if context.rollback_available else retrain_trigger
```

## 8. 状態遷移
- `safe -> caution`
- `caution -> safe`
- `caution -> unsafe`
- `unsafe -> recovering`
- `recovering -> safe`

詳細遷移は `docs/17_state_machines.md` を参照。

## 9. Dify / LiteLLM / Open WebUI での差し込み
- Dify workflow 終端で aggregate metrics を作る
- LiteLLM から cost / error / fallback 系 observables を回収
- Open WebUI で operator queue を表示

## 10. 監査出力
- trust_window_score
- trigger handles
- rollback_viability
- retrain_pressure
- recommended_action rationale

## 11. 最小ベンチマーク
- stable operation
- soft degradation
- hard degradation
- false alarm scenario

## 12. 実装上の注意
- output_shift 単独で contaminated 判定しない
- release 直後の一過性ノイズを H_hist として扱う
- ground truth 遅延が大きい場合、 delayed_gt_disagreement を必須化しない
