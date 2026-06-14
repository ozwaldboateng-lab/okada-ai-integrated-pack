# Auto-Calibration Manager Runbook

## 1. 初期導入手順
1. adapter ごとに `calibration_profile` を割り当てる
2. log schema が最低限の observables を出していることを確認する
3. baseline config を `configs/current/*.yaml` に保存する
4. fixtures と replay evaluator を接続する
5. 最初は `suggest_only` で動かす

## 2. 運用レベル
### Level 0: Logging Only
校正は行わず、必要ログだけ収集する。

### Level 1: Suggest Only
候補設定と validation report を生成するが反映しない。

### Level 2: Approval Gated
report を人が確認し、承認時のみ反映する。

### Level 3: Shadow Challenger
候補設定を shadow 実行で比較する。

### Level 4: Guarded Auto-Adopt
低リスク adapter のみ自動反映を許す。

## 3. 反映前チェック
- replay case 数が十分か
- benchmark coverage を満たすか
- current baseline との差が説明可能か
- new config が allowed range を超えていないか
- recent incident period を window に含めすぎていないか

## 4. 反映後監視
- adoption window を別管理する
- rollout 後 1〜3 window は rollback sensitivity を高める
- pre/post comparison を保存する

## 5. rollback 条件例
- catastrophic failure rate > baseline + margin
- success rate < baseline - margin
- abstain rate > cap
- handoff rate > cap
- p95 latency > cap

## 6. 監査時に見るべきもの
- previous config
- candidate config
- validation summary
- adoption decision reason
- rollout scope
- rollback event history
