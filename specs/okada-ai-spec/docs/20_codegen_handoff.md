# コード生成AIへの handoff 指示

- Document ID: OAI-DD-CODEGEN-001
- Version: 0.2

## 1. 前提
この仕様パックは、コード生成AIにそのまま読ませて実装骨格を作らせることを想定する。
実装AIは、まず `registry/` を source of truth として読み、次に `api/` と `schemas/` を参照し、最後に `docs/` を補助説明として使うこと。

## 2. 実装順序
1. `OKD-AI-CORE-001` の API server を作る
2. adapter interface を抽象 class / protocol として定義する
3. monitoring / drift / agent / rag / routing adapters を雛形実装する
4. audit persistence を追加する
5. OSS integration stubs を作る

## 3. 禁止事項
- 閾値を勝手に固定値へ埋め込まない
- `dominant / retained / competitor / visible handle` を省略しない
- 監査ログを optional 扱いにしない
- spec ごとの非目標を跨いで肥大化させない

## 4. 推奨成果物
- FastAPI server skeleton
- adapter base classes
- pydantic models generated from OpenAPI / JSON Schema
- example config files
- test skeletons loading `fixtures/*.jsonl`

## 5. 生成結果の受け入れ条件
- deterministic mode で再現可能
- fixtures が最低限読める
- audit record が保存される
- adapter ごとに unit tests がある
