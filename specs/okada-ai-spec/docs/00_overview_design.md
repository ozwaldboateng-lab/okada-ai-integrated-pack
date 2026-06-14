# 岡田理論統合AIプラットフォーム 概要設計書

- Document ID: OAI-AD-001
- Version: 0.2
- Status: Draft

## 1. 目的
本システムの目的は、**既存のオープンソースAI基盤の上に岡田理論レイヤーを付加し、同一のモデル群・同一の知識源・同一の予算制約の下で、既存構成より高い end-to-end performance を示すAIシステムを構築すること**である。

ここでいう性能向上は、基盤モデル単体の知能向上ではなく、AIシステム全体としての以下の改善を指す。

- task success の向上
- 不要な retrieval / tool call / heavy model call の削減
- contaminated 状態の早期検知
- escalation / rollback / abstain の適切化
- 同品質でのコスト・レイテンシ削減
- 同コストでの品質向上

## 2. 設計方針
本システムは、新しい基盤モデルを訓練するものではない。設計方針は、**既存AI基盤の上に載る上位診断・統御層**として岡田理論を実装することである。

### 2.1 共通カーネル方式
岡田理論を各問題ごとに別実装するのではなく、共通の **Okada Governance Kernel** を中核に置き、その上に問題領域ごとの adapter を載せる。

### 2.2 既存OSS活用方式
既存のオープンソース基盤を活用し、最小改造で実現する。初期段階では fork を避け、extension point と外部サービス連携を優先する。

### 2.3 実装対象の限定
本システムは、以下の機能を主対象とする。
- RAG 統御
- multi-model routing
- agentic AI governance
- post-deployment monitoring
- MLOps drift intervention

### 2.4 監査可能性重視
すべての判定は、単一のスコア出力で終わらせず、**dominant route / retained history / competitor pressure / first visible handle** の分解を監査ログとして保持する。

## 3. システム化対象
### 3.1 First Wave
- Post-deployment Monitoring / Trust Window Governance
- MLOps Concept Drift Thresholding
- Agentic AI Route Contamination and Escalation Governance
- RAG Freshness / Context Contamination Governance
- Multi-model / Multi-strategy Routing Governance

### 3.2 Second Wave
- Industrial Anomaly Warning Layer
- Root-cause Prioritization Pre-layer
- Evaluation Contamination / Judge Leakage Auditor
- Inference-era Datacenter Energy / Latency Governance
- Quantum Optimization Diagnosis-driven Governance

### 3.3 Hold
- Drift-aware Intrusion Detection Governance
- Mitigation-to-Correction Handoff Governance

## 4. 全体構成
- **Dify**: アプリ本体、RAG、ワークフロー、分岐制御
- **LiteLLM**: モデル呼び出しゲートウェイ、routing、policy enforcement
- **LangGraph**: 長い agent 実行の制御、中断、再開、human handoff
- **Open WebUI**: 運用UI、手動検証、評価、監査確認
- **Okada Governance Kernel**: 岡田理論に基づく判定・統御の外部中核サービス

## 5. 論理アーキテクチャ
### 5.1 Presentation Layer
- Dify App UI
- Open WebUI
- Operator Dashboard
- Audit Screens

### 5.2 Orchestration Layer
- Dify Workflow / Chatflow
- LangGraph Runtime
- External Jobs / Periodic Monitoring

### 5.3 Governance Layer
- Okada Governance Kernel
- Domain Adapters
- Rule Evaluator
- Intervention Planner
- Audit Writer

### 5.4 Model Gateway Layer
- LiteLLM Proxy
- Routing Hooks
- Fallback Policy
- Cost / Latency / Usage Metrics

### 5.5 Data / Knowledge Layer
- Dify Knowledge
- Vector / Corpus Index
- Session History
- Route History
- Audit Log Store
- Observability Store

## 6. 本書の位置づけ
本書は概要設計である。実装に必要な詳細は次へ分離する。
- `docs/10_detailed_design_index.md`
- `registry/core/okd-ai-core-001.yaml`
- `registry/adapters/*.yaml`
- `api/okada-governance.openapi.yaml`
- `schemas/*.json`
