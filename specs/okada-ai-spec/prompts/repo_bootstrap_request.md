# Repo Bootstrap Request

以下の仕様パックを source of truth として、新規リポジトリを bootstrap してください。

- `specs/okada-ai-spec/api/okada-governance.openapi.yaml`
- `specs/okada-ai-spec/schemas/*.json`
- `specs/okada-ai-spec/registry/core/*.yaml`
- `specs/okada-ai-spec/registry/adapters/*.yaml`
- `specs/okada-ai-spec/registry/integration/*.yaml`

要求:
1. Python 3.12 + FastAPI + pydantic v2 + pytest を使用する
2. `apps/okada-kernel-service/` にサービスを作る
3. `apps/okada-kernel-service/tests/` に fixture-driven tests を作る
4. `apps/okada-kernel-service/app/integrations/` に Dify/LiteLLM/LangGraph/Open WebUI の stub を作る
5. audit persistence は JSONL で始める
6. 閾値や重みは config として外出しする
7. `make test` 相当の実行方法を README に書く
