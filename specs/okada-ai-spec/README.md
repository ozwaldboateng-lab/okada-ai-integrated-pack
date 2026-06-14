# Okada AI Specification Pack

Version: 0.3  
Status: Draft  
Date: 2026-04-17

## 目的
このリポジトリは、岡田理論を既存AI基盤の上位診断・統御レイヤーとして実装するための、
**概要設計・詳細設計・仕様レジストリ・API定義・スキーマ・評価fixture・コード生成AI向け handoff** をまとめた仕様パックです。

このパックは次を満たすことを狙います。

- 人間が読める
- コード生成AIが分解しやすい
- 差分管理しやすい
- 概要設計から詳細設計へ連続的に参照できる
- 後で実装・評価・比較へそのまま伸ばしやすい

## source of truth
- 構造化された仕様定義: `registry/`
- 人間向け説明文書: `docs/`
- API定義: `api/`
- バリデーション用スキーマ: `schemas/`
- 例題・回帰テスト素材: `fixtures/`
- コード生成AI向け制約: `prompts/`

## 推奨利用順
1. `docs/00_overview_design.md` を読む
2. `docs/10_detailed_design_index.md` を読む
3. `registry/spec_registry.yaml` で全体一覧と状態を把握する
4. 個別仕様は `registry/core/` と `registry/adapters/` を source of truth として読む
5. 実装境界は `api/okada-governance.openapi.yaml` と `schemas/` を参照する
6. 生成AIへの handoff は `prompts/codegen_instructions.md` と `docs/20_codegen_handoff.md` を読む

## ディレクトリ構成
```text
okada-ai-spec/
├─ README.md
├─ CHANGELOG.md
├─ docs/
├─ registry/
├─ api/
├─ schemas/
├─ fixtures/
└─ prompts/
```

## 注意
- 本パックは論文ではなく仕様資産です。
- 閾値 `T_*` と重み `W_*` は暫定の識別子であり、後段で校正します。
- まずは意味論・責務分担・入出力・状態遷移を固定することを優先しています。
- 実装は `fork` より `external service + extension point` を優先します。


## v0.3 追加内容
- 実装部位設計の詳細化
- リポジトリ初期構成案
- サービス分割・責務分担
- コード生成AIへの初回ブートストラップ依頼文
- Phase 1 実装バックログ
