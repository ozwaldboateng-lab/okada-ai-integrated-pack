# Task 02: LiteLLM E2E Hardening

## 目的

LiteLLM 連携を、雛形ではなく「起動し始められる」粒度まで詰める。

## 前提

Task 01 の kernel 契約が固まっていること。

## 対象範囲

- `examples/litellm/*`
- `app/integrations/litellm_runtime.py`
- `scripts/litellm_preflight.py`
- `ops/litellm/*`
- 必要な tests / docs

## やること

1. pre-route / post-audit の payload 流れを整理する
2. route map と環境変数の読み込みを明確にする
3. LiteLLM 側設定テンプレートを更新する
4. preflight と runbook を改善する
5. E2E 想定の tests を少し厚くする

## やらないこと

- 本物の外部モデル接続を大量に増やす
- Dify や LangGraph まで同時に直す
- route policy 自体を大きく書き換える

## 受け入れ条件

- LiteLLM 用の最小起動手順が docs から追える
- route map / env / hook の関係が以前より明確
- preflight が意味のある失敗理由を返す
- `pytest` が通る
- LiteLLM 連携まわりの tests が少なくとも 3 件以上増える

## 人間確認ポイント

- 起動手順が短く自然か
- env と config の責務が分かれているか
- hook の責務が増えすぎていないか

## 完了の目安

- 「LiteLLM 側を最初に繋ぐ」作業が、人間でも agent でも迷わず始められる状態
