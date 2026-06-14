# OSS統合マップ

## 1. 基本方針
- Dify = アプリ本体とRAGワークフロー
- LiteLLM = モデル呼び出しの関所
- LangGraph = 長い agent 実行の制御器
- Open WebUI = 運用・評価・監査の顔
- Okada Governance Kernel = 共通外部サービス

## 2. Spec 別の主担当

| Spec ID | 名称 | 主担当 | 副担当 | 実装形 |
|---|---|---|---|---|
| OKD-AI-CORE-001 | Okada Governance Kernel | External Service | Dify / LiteLLM / LangGraph / Open WebUI | Shared API |
| OKD-AI-001 | Post-deployment Monitoring | External Service | Dify / LiteLLM / Open WebUI | Monitoring service + dashboard |
| OKD-AI-002 | MLOps Concept Drift | External Service | Dify / Open WebUI | Intervention service |
| OKD-AI-003 | Agent Governance | LangGraph | LiteLLM / Open WebUI / Dify | Middleware + interrupt |
| OKD-AI-004 | RAG Governance | Dify | LiteLLM / Open WebUI | Workflow nodes + external call |
| OKD-AI-005 | Multi-model Routing | LiteLLM | Dify / Open WebUI | Pre-hook routing policy |

## 3. Dify でやること
- Knowledge 管理
- Workflow / Chatflow
- Code Node から `/okada/diagnose` 呼び出し
- Branch 分岐
- App 公開
- RAG 前後の governance ノード配置

## 4. LiteLLM でやること
- OpenAI互換 proxy
- pre-call routing
- request policy
- fallback
- post-call metrics
- `/okada/route` との接続

## 5. LangGraph でやること
- planner / executor state 管理
- stepwise governance
- interrupt_for_human
- resume
- constrained tool policy

## 6. Open WebUI でやること
- operator dashboard
- manual evaluation
- audit inspection
- route policy visualization
- human approval / review entry

## 7. 差し込み部位
### 7.1 RAG
- query intake 後
- retrieval 後
- answer draft 後

### 7.2 Agent
- plan 後
- tool selection 前
- tool result 後
- final answer 前

### 7.3 Routing
- model call 前
- model call 後

### 7.4 Monitoring / MLOps
- workflow 終端
- periodic metric aggregation
- operator review queue 作成前

## 8. 実装順序の指針
1. Kernel API を先に立てる
2. Dify と LiteLLM を接続する
3. RAG と routing を先に差す
4. Agent governance は LangGraph 側で別実装する
5. Open WebUI は監査面から追加する
