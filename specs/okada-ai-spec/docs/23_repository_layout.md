# リポジトリ初期構成案

- Document ID: OAI-IMP-003
- Version: 0.3

## 1. 推奨レイアウト
```text
okada-ai/
├─ README.md
├─ pyproject.toml
├─ .env.example
├─ docker-compose.yml
├─ apps/
│  └─ okada-kernel-service/
│     ├─ app/
│     │  ├─ main.py
│     │  ├─ api/
│     │  ├─ core/
│     │  ├─ adapters/
│     │  ├─ audit/
│     │  ├─ config/
│     │  ├─ integrations/
│     │  └─ models/
│     └─ tests/
├─ specs/
│  └─ okada-ai-spec/   # 本仕様パック
├─ examples/
│  ├─ dify/
│  ├─ litellm/
│  ├─ langgraph/
│  └─ openwebui/
└─ scripts/
   ├─ validate_specs.py
   ├─ load_fixtures.py
   └─ smoke_test.py
```

## 2. 分離理由
- `apps/` は実装物
- `specs/` は仕様資産
- `examples/` は OSS 差し込み例
- `scripts/` は検証支援

## 3. 実装AIへの指示
コード生成AIには、`specs/okada-ai-spec/` を source of truth として読み込み、
`apps/okada-kernel-service/` を最初に生成させる。
