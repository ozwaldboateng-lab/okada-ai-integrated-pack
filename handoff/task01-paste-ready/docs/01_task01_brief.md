# Task-01 Brief: Kernel Contract Hardening

## 目的
Okada Governance Kernel の API / schema / validation / error handling を強化し、
以後の LiteLLM / Dify / LangGraph / Open WebUI 連携の前提となる「契約」を安定化する。

## やること
- `/okada/diagnose`, `/okada/route`, `/okada/intervene`, `/okada/audit` の request/response 契約を点検する
- Pydantic モデル、JSON Schema、OpenAPI、バリデーション、エラー応答を整合させる
- 欠損値・未知 adapter・不正 payload に対する fail-safe を入れる
- 最低限のテストを追加・更新する
- runbook / README / docs が必要なら更新する

## 触ってよい範囲
- `app/`
- `api/`
- `schemas/`
- `tests/`
- `docs/`
- `README.md`

## 受け入れ条件
- 既存テストが通る
- 必要な新規テストが追加される
- OpenAPI / schema / 実装の契約が大きく矛盾しない
- 不正入力で 500 を出しにくくし、4xx 系へ寄せる
- 変更内容が README か docs から追える

## 触らないこと
- LiteLLM / Dify / LangGraph / Open WebUI の本格改造
- しきい値最適化
- benchmark の拡張
- 大規模なアーキテクチャ変更

## 目視比較観点
- 仕様準拠性
- 変更の自然さ
- fail-safe の入り方
- テストの質
- 作業ログや説明の分かりやすさ
