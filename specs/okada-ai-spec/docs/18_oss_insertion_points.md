# OSS差し込み部位詳細

- Document ID: OAI-DD-OSS-001
- Version: 0.2

## 1. Dify
### 1.1 推奨差し込みポイント
- Workflow の Code Node
- Branch 条件分岐の直前
- RAG retrieval node の前後
- Workflow 終端の audit push

### 1.2 主担当 spec
- OKD-AI-001
- OKD-AI-004
- 補助的に OKD-AI-002

### 1.3 実装メモ
- Code Node で Okada API を叩く
- response の `recommended_action` を branch condition へ流す
- workflow 実行 metadata を audit に渡す

## 2. LiteLLM
### 2.1 推奨差し込みポイント
- pre-call hook
- post-call hook
- fallback decision layer

### 2.2 主担当 spec
- OKD-AI-005
- 補助的に OKD-AI-001, OKD-AI-004

### 2.3 実装メモ
- request metadata を `/okada/route` に投げる
- selected route を proxy request に反映する
- post-call metrics を `/okada/audit` に送る

## 3. LangGraph
### 3.1 推奨差し込みポイント
- planner node 後
- tool-call middleware
- tool-result observer
- final answer gate

### 3.2 主担当 spec
- OKD-AI-003

### 3.3 実装メモ
- interrupt を `human_handoff` action に対応づける
- state persistence に `current_regime` と `last_intervention` を保存する

## 4. Open WebUI
### 4.1 推奨差し込みポイント
- pipeline / filter / tool としての監査ビュー
- operator dashboard
- manual review queue

### 4.2 主担当 spec
- 監査・手動検証全般
- second wave review workflows

### 4.3 実装メモ
- audit search UI
- route policy visibility
- manual action override UI
