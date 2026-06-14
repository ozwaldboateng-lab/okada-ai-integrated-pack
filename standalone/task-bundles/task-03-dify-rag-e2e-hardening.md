# Task 03: Dify RAG E2E Hardening

## 目的

Dify 連携を、RAG 前後の governance を実装し始められる粒度まで詰める。

## 前提

Task 01 の kernel 契約が固まっていること。

## 対象範囲

- `examples/dify/*`
- `app/integrations/dify_runtime.py`
- `scripts/dify_preflight.py`
- `ops/dify/*`
- 必要な tests / docs

## やること

1. pre-retrieval / post-retrieval / fail-safe の payload 設計を整理する
2. Dify HTTP Request / Code Node 例を見やすくする
3. workflow variables の説明を強化する
4. preflight と runbook を改善する
5. Dify 連携まわりの tests を増やす

## やらないこと

- Dify 全体を export/import 可能な完成 workflow にすること
- LiteLLM や LangGraph の修正を同時に行うこと
- retrieval ロジック自体の大改造

## 受け入れ条件

- pre/post retrieval の流れが docs から追える
- `transformed_payload` と branch variables の意味が明確
- fail-safe の落としどころが定義されている
- `pytest` が通る
- Dify 連携まわりの tests が少なくとも 3 件以上増える

## 人間確認ポイント

- Dify に慣れていない人でも読めるか
- サンプル JSON とコード例が噛み合っているか
- fail-safe が実用的か

## 完了の目安

- 「Dify 側から kernel gateway を呼び、分岐へ反映する」最短経路が見える状態
