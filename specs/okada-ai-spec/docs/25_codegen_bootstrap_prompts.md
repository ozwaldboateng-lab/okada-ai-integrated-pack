# コード生成AI向けブートストラップ依頼文

- Document ID: OAI-IMP-005
- Version: 0.3

## 1. 初回依頼文
次の仕様を実装してください。

1. `specs/okada-ai-spec/registry/` を source of truth とする
2. `api/okada-governance.openapi.yaml` を満たす FastAPI server を生成する
3. `schemas/` に対応する pydantic models を生成する
4. `okada-kernel-service` を `apps/okada-kernel-service/` に作る
5. adapter base protocol を作る
6. monitoring / drift / agent / rag / routing の stub adapter を作る
7. fixtures を読み込む unit test を作る
8. audit record を JSONL で保存する簡易 persistence を作る
9. Dify / LiteLLM / LangGraph 向け integration stub を作る
10. 閾値は仮置きの config key として残し、固定値に焼き込まない

## 2. 生成禁止事項
- spec registry を無視して勝手な class 名へ変えない
- audit を省略しない
- single-file monolith にしない
- adapter ごとの非目的を跨いで実装しない
- Dify / LiteLLM / LangGraph / Open WebUI を直接 fork しない

## 3. 出力形式
- 生成したファイル一覧
- 実装した API endpoint 一覧
- テスト一覧
- 未実装 TODO 一覧
