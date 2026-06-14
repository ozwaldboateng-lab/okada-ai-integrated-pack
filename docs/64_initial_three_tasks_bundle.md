# 初回実装タスク3本セット

この文書は、Codex と Claude Code の両方に **同じ仕様・同じ順番** で投げるための最小 bundle を定義する。

## 目的

- 同じ repo を使って、両者に **スタンドアローンで同一タスク** を実装させる
- 役割分担はしない
- 厳密な自動比較より、**成果物と作業感の目視比較** を優先する
- ただし acceptance は固定し、最低限の品質線は揃える

## この3本を先に選ぶ理由

### Task 01: Kernel Contract Hardening
最も基礎的で、以後の全統合に効く。コード生成AIの「仕様理解」「型・境界の整理」「fail-safe の置き方」が見えやすい。

### Task 02: LiteLLM E2E Hardening
最短で gateway / routing / audit の価値が見えやすい。hook・環境変数・runbook まで含むので、実装体力が出やすい。

### Task 03: Dify RAG E2E Hardening
RAG 系の分岐・fail-safe・workflow 変数の扱いが見える。実用側の完成イメージに近い。

## 実行順

1. `task-01-kernel-contract-hardening.md`
2. `task-02-litellm-e2e-hardening.md`
3. `task-03-dify-rag-e2e-hardening.md`

## 運用ルール

- 両者とも `registry/`, `api/`, `schemas/`, `standalone/task-bundles/` を source of truth とする
- 1タスクごとに独立ブランチまたは独立ディレクトリで実行する
- task 01 が終わってから task 02/03 へ進む
- task 02 と task 03 は、task 01 採用後なら順不同でもよい
- 迷ったら **仕様優先 / fail-safe 優先 / テスト追加優先** とする

## 人間が見るべき観点

- 仕様への忠実さ
- コードの読みやすさ
- テストの張り方
- 実行手順のわかりやすさ
- 想定外入力への防御
- 無駄な広げすぎがないか
