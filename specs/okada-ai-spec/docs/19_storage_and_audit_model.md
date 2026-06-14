# ストレージ・監査モデル

- Document ID: OAI-DD-DATA-001
- Version: 0.2

## 1. 保存対象
### 1.1 AuditRecord
- `audit_trace_id`
- `timestamp`
- `spec_id`
- `adapter_type`
- `caller`
- `raw_inputs`
- `normalized_inputs`
- `derived_features`
- `decision`
- `recommended_action`
- `alternatives`
- `policy_snapshot`
- `audit_persisted`

### 1.2 RouteHistory
- `request_id`
- `selected_route`
- `candidate_routes`
- `cost`
- `latency`
- `success_label`
- `followup_action`

### 1.3 StateSnapshot
- `entity_id`
- `current_regime`
- `previous_regime`
- `last_intervention`
- `transition_timestamp`
- `state_payload`

## 2. 保存原則
- raw と normalized を分離
- derived_features は flatten せず構造で保持
- action と rationale を分離
- policy snapshot を必ず保存

## 3. 推奨ストア
- audit: document store または JSONB 対応 RDB
- route history: RDB または analytical store
- fixtures / baselines: Git 管理

## 4. retention
- audit は少なくとも benchmark 期間中は完全保存
- high-risk / aborted / rollback case は長期保存
- PII を扱う場合は raw_inputs を redaction 可能にする
