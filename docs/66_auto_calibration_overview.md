# Auto-Calibration Manager 概要設計書

## 1. 目的
Auto-Calibration Manager の目的は、各 Okada adapter の閾値・重み・境界値を、一定スパンごとに直近ログと評価結果から再計算し、安全条件を満たす場合にのみ反映することである。

本機構は「勝手に自己改変する最適化器」ではない。
正しい位置づけは、**guardrail 付き self-tuning / semi-automatic recalibration manager** である。

## 2. 設計原則
1. 直接本番設定を書き換えない。
2. 候補設定の生成と採用を分離する。
3. 採用前に必ず replay 評価または shadow 評価を行う。
4. adapter ごとに更新可能パラメータの範囲を固定する。
5. 高リスク adapter は自動反映せず承認制にする。
6. すべての設定変更は audit trail に残す。

## 3. スコープ
対象 adapter:
- monitoring
- drift
- rag
- routing
- agent

対象パラメータ:
- threshold 系: `T_clean`, `T_contam`, abstain threshold, reroute threshold, escalation threshold
- weight 系: `W_dom`, `W_hist`, `W_comp`
- bonus / penalty 系: risk bonus, freshness penalty, tool conflict penalty

対象外:
- 基盤モデルの再学習
- detector 本体の置換
- feature 定義そのものの自動探索
- safety hard limit の自動解除

## 4. 基本アーキテクチャ
Auto-Calibration Manager は 5 サブコンポーネントで構成する。

### 4.1 Log Window Builder
指定スパンから校正対象ログを抽出する。

### 4.2 Candidate Generator
既存設定とログを入力として候補設定を生成する。

### 4.3 Replay Validator
候補設定を過去ログ・fixture・benchmark に対して再生評価する。

### 4.4 Adoption Gate
安全条件を評価し、`reject / shadow / adopt` を決める。

### 4.5 Config Publisher
採用設定を設定ストアに publish し、変更履歴を残す。

## 5. 更新フロー
1. 校正対象 adapter を選ぶ
2. window policy に従ってログを切り出す
3. candidate generator が候補設定を生成する
4. replay validator が baseline と challenger を比較する
5. adoption gate が受け入れ条件を判定する
6. 条件を満たした場合のみ publish する
7. 反映後も champion/challenger または post-adoption monitoring を行う
8. 悪化時は rollback する

## 6. スパン設計
### 6.1 短スパン向き
- routing: 6h / 12h / 1d
- rag: 12h / 1d

### 6.2 中スパン向き
- monitoring: 1d / 3d
- drift: 3d / 7d

### 6.3 長スパン向き
- agent: 7d / 14d / 30d

## 7. 更新モード
### 7.1 Suggest-Only
候補設定だけ作る。本番へは反映しない。

### 7.2 Approval-Gated
候補設定を作り、承認後に反映する。

### 7.3 Shadow-Challenger
候補設定を shadow として評価し、勝てば昇格する。

### 7.4 Guarded Auto-Adopt
低リスク adapter に対し、安全条件を満たす場合のみ自動採用する。

## 8. 安全条件
最低限以下を持つ。
- catastrophic failure rate が悪化しない
- success rate が許容以上に低下しない
- cost / latency 上限を超えない
- abstain / handoff が暴騰しない
- coverage が最小値を下回らない

## 9. adapter ごとの推奨更新方針
### 9.1 routing
- mode: Guarded Auto-Adopt
- reason: 数値的評価がしやすく、事故コストが比較的低い

### 9.2 rag
- mode: Shadow-Challenger -> Guarded Auto-Adopt
- reason: stale / grounding 誤判定の監視が必要

### 9.3 monitoring
- mode: Approval-Gated
- reason: false rollback / false alarm の社会コストがある

### 9.4 drift
- mode: Approval-Gated
- reason: retrain / rollback のコストが大きい

### 9.5 agent
- mode: Suggest-Only または Approval-Gated
- reason: 失敗の質が複雑で、高リスク action を伴う

## 10. source of truth
Auto-Calibration Manager に関する source of truth は以下。
1. `registry/core/okd-ai-core-002-auto-calibration.yaml`
2. `registry/policies/auto_calibration_profiles.yaml`
3. `api/okada-auto-calibration.openapi.yaml`
4. `schemas/*.json`

## 11. 主要出力
- candidate config
- validation report
- adoption decision
- rollback rule
- calibration audit record

## 12. 今後の詳細化対象
- candidate generation algorithm
- replay scoring formalism
- config publication contract
- adapter-specific metric bundle
