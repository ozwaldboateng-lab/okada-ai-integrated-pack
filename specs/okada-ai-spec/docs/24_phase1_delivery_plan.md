# Phase 1 実装デリバリ計画

- Document ID: OAI-IMP-004
- Version: 0.3

## 1. 目標
まずは「動くCore + stub adapter + stub integration」を作る。
完璧な scoring より、API・監査・責務分離を優先する。

## 2. デリバリ単位
### Delivery A
- FastAPI skeleton
- OpenAPI compliance
- pydantic models
- health endpoint
- basic config loader

### Delivery B
- audit persistence
- base adapter protocol
- core feature derivation helpers

### Delivery C
- routing adapter stub
- rag adapter stub
- fixture-driven unit tests

### Delivery D
- Dify HTTP client stub
- LiteLLM route-hook stub
- smoke test

### Delivery E
- agent adapter stub
- LangGraph middleware stub

### Delivery F
- monitoring adapter stub
- drift adapter stub
- audit query API for operator UI

## 3. Done criteria
各 delivery は以下を満たすこと。
- tests pass
- fixtures load
- audit record is emitted
- deterministic mode supported
