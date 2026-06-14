# Task 01: Kernel Contract Hardening

## 目的

`Okada Governance Kernel` の API 契約と fail-safe を硬くし、以後の統合タスクの土台にする。

## 対象範囲

- `apps/okada-kernel-service/app/api/routes_okada.py`
- `apps/okada-kernel-service/app/schemas/*`
- `api/okada-governance.openapi.yaml`
- `schemas/*.json`
- 必要な tests

## やること

1. `/okada/diagnose`, `/okada/route`, `/okada/intervene`, `/okada/audit` の request / response 契約を整える
2. 欠損フィールド・未知 adapter・空 observables などの fail-safe を明確化する
3. OpenAPI と Pydantic モデルのズレを減らす
4. 監査レコードの最低必須項目を固定する
5. tests を追加する

## やらないこと

- 新しい adapter を増やす
- ドメイン固有ロジックを深く実装する
- UI や外部OSSの接続まで広げる

## 受け入れ条件

- 主要4 endpoint に対して bad input の挙動が定義されている
- OpenAPI / schema / 実コードの整合性が以前より上がっている
- `pytest` が通る
- 新しい tests が少なくとも 4 件以上追加されている
- README か docs に、契約変更点が短く追記されている

## 人間確認ポイント

- 契約が読みやすいか
- 例外処理が雑ではないか
- 過剰抽象化していないか

## 完了の目安

- 「次の LiteLLM / Dify 作業で API 契約に迷わない」状態
