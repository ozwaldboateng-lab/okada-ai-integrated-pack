# 実装ブループリント

- Document ID: OAI-IMP-001
- Version: 0.3
- Status: Draft

## 1. 目的
本書は、概要設計書と詳細設計書を、コード生成AIがそのまま実装骨格へ変換できるレベルの
**実装ブループリント**へ落とすことを目的とする。

## 2. 実装の基本原則
1. 既存OSSを fork せず、external service + extension point を優先する。
2. source of truth は `registry/` と `api/` と `schemas/` とする。
3. Core を先に作り、adapter は後から載せる。
4. UI より先に API / audit / config を固定する。
5. すべての adapter は `dominant / retained / competitor / visible handle` を出す。

## 3. 初期成果物
Phase 1 で最低限必要な成果物は次の通り。

- FastAPI ベースの `okada-kernel-service`
- adapter 抽象インターフェース
- monitoring / drift / agent / rag / routing adapter の stub 実装
- audit persistence 層
- Dify 呼び出し用 HTTP client stub
- LiteLLM hook 用 HTTP client stub
- LangGraph middleware stub
- Open WebUI audit-view 用 query API

## 4. サービス分割
### 4.1 okada-kernel-service
役割:
- `/okada/diagnose`
- `/okada/route`
- `/okada/intervene`
- `/okada/audit`
- adapter registry
- policy profile loader
- audit persistence writer

### 4.2 integration-clients
役割:
- Dify workflow から呼ぶ client
- LiteLLM hook から呼ぶ client
- LangGraph middleware から呼ぶ client
- Open WebUI 向け read-model client

### 4.3 configuration package
役割:
- adapter config
- threshold placeholder
- weight placeholder
- policy profile definitions
- environment-specific overrides

## 5. 最初の優先順
### Step 1
Core API と pydantic models を固定する。

### Step 2
audit persistence を追加する。

### Step 3
routing adapter と rag adapter の stub を作る。

### Step 4
Dify / LiteLLM 向け integration stub を作る。

### Step 5
agent adapter と LangGraph middleware を作る。

### Step 6
monitoring / drift adapter を追加する。

## 6. 実装完了条件
- OpenAPI に対応する API が起動する
- fixtures を読み込んで最低限の response が返る
- audit record が保存される
- routing / rag / agent / monitoring / drift 各 adapter に stub test がある
- integration stub から end-to-end の dry run が可能
