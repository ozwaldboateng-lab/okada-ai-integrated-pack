# OKD-AI-CORE-001 詳細設計

- Document ID: OAI-DD-CORE-001
- Version: 0.2
- Spec ID: OKD-AI-CORE-001

## 1. 目的
Okada Governance Kernel は、全 domain adapter が共有する診断・統御の基底サービスである。
責務は、観測量の正規化、岡田特徴量生成、regime 判定、action 推奨、audit payload 生成に限定する。

## 2. 実装単位
推奨サービス名: `okada-governance-service`

推奨モジュール構成:
```text
okada_governance/
  app.py
  api/
    routes.py
    models.py
  core/
    normalizer.py
    feature_engine.py
    classifier.py
    router.py
    policy.py
    audit.py
  adapters/
    monitoring.py
    drift.py
    agent.py
    rag.py
    routing.py
  storage/
    audit_store.py
    policy_store.py
```

## 3. Request Lifecycle
1. request validation
2. adapter selection
3. observable normalization
4. derived feature construction
5. regime classification
6. action candidate generation
7. policy profile application
8. audit payload emission
9. response serialization

## 4. 核となる内部インターフェース
### 4.1 Adapter contract
各 adapter は次の関数群を実装する。
- `validate_observables(payload) -> ValidationResult`
- `normalize(payload) -> NormalizedInputs`
- `derive_features(normalized) -> DerivedFeatures`
- `classify(features, policy) -> Decision`
- `candidate_actions(decision, policy) -> list[str]`
- `build_audit(...) -> AuditRecord`

### 4.2 NormalizedInputs
必須キー:
- `normalized_observables`
- `missing_flags`
- `trend_features`
- `context_flags`
- `resource_flags`

### 4.3 DerivedFeatures
必須キー:
- `H_dom`
- `H_hist`
- `H_comp`
- `V_first`
- `R_diag`
- `S_trust`
- `regime_hint`
- `type_hint`

## 5. 共通計算骨格
### 5.1 分解比
```text
R_diag = (W_hist * abs(H_hist) + W_comp * abs(H_comp)) / (W_dom * abs(H_dom) + eps)
```

### 5.2 regime 判定骨格
```text
if H_dom >= T_dom_min and R_diag < T_clean_max:
    regime = clean
elif H_dom >= T_dom_survive and R_diag < T_contam_min:
    regime = mixed
else:
    regime = contaminated
```

### 5.3 action 候補骨格
- clean -> conservative no-op 系 action を優先
- mixed -> deepen / watch / replan / shadow 系 action を優先
- contaminated -> fallback / abstain / rollback / handoff 系 action を優先

## 6. Policy Profile
policy profile は request ごとに差し替え可能にする。
最低限の policy key は次。
- `thresholds.T_clean_max`
- `thresholds.T_contam_min`
- `thresholds.T_dom_min`
- `weights.W_dom`
- `weights.W_hist`
- `weights.W_comp`
- `actions.preferred_if_clean`
- `actions.preferred_if_mixed`
- `actions.preferred_if_contaminated`
- `audit.capture_raw_inputs`

## 7. エラー処理
### 7.1 validation error
- unknown spec_id
- adapter mismatch
- required observable missing
- wrong observable type

### 7.2 runtime error
- normalization failed
- policy profile unresolved
- adapter internal failure
- audit store unavailable

### 7.3 degraded mode
audit store が一時 unavailable でも、response は返す。ただし `audit_persisted=false` を出す。

## 8. 監査設計
各 response は必ず `audit_trace_id` を返す。
audit record には最低限次を保存する。
- raw_inputs
- normalized_inputs
- derived_features
- decision
- recommended_action
- alternatives
- caller metadata
- policy snapshot

## 9. テスト戦略
### 9.1 unit tests
- normalization invariants
- missing flag handling
- regime boundary handling
- policy override handling

### 9.2 contract tests
- all adapters satisfy core contract
- identical request under deterministic mode returns identical response

### 9.3 regression tests
- fixture replay
- previous audit replay consistency

## 10. 非目標
- ML model training
- automatic threshold fitting
- UI rendering
- observability collection itself
