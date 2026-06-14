# アーキテクチャ設計メモ

## 1. アーキテクチャ原理
- 共通カーネル + domain adapter
- 外付けサービス優先
- 監査ログ中心
- ベースライン比較可能性を維持
- extension point から差し込み、初期 fork を禁止

## 2. 主要レイヤ
### 2.1 Presentation
- Dify App UI
- Open WebUI
- Operator Dashboard

### 2.2 Orchestration
- Dify Workflow / Chatflow
- LangGraph Graph Runtime
- External Job Runner

### 2.3 Governance
- Okada Governance Kernel
- Adapter Modules
- Policy Evaluator
- Intervention Planner
- Audit Writer

### 2.4 Model Gateway
- LiteLLM Proxy
- Routing Hooks
- Fallback Policy
- Cost / Latency Metrics

### 2.5 Data / Knowledge
- Knowledge store
- Vector index
- Session history
- Route history
- Audit log store
- Metrics / observability store

## 3. データフロー
### 3.1 RAG
query
-> pre-retrieval governance
-> retrieval
-> post-retrieval governance
-> answer draft
-> final governance
-> output
-> audit

### 3.2 Agent
task
-> planning
-> governance
-> tool selection
-> governance
-> tool execution
-> governance
-> answer
-> audit

### 3.3 Routing
request
-> LiteLLM pre-hook
-> route decision
-> model call
-> post-call audit

### 3.4 Monitoring
observability ingest
-> trend normalization
-> trust-window diagnose
-> action recommendation
-> operator review / automation
-> audit

## 4. システム境界
### 4.1 Kernel が持つもの
- feature derivation
- regime classification
- action suggestion
- audit payload generation

### 4.2 Adapter が持つもの
- observable dictionary
- normalization rules
- domain-specific features
- baseline mapping
- action policy mapping

### 4.3 OSS 側が持つもの
- app shell
- workflow execution
- model serving
- human interaction
- dashboard

## 5. 実装原則
- 低侵襲で始める
- 比較実験を壊さない
- 1つの spec は 1つの最小実装単位を持つ
- kernel の説明責務と adapter の意味責務を分離する
