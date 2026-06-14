このリポジトリに対して task-01 を実装してください。

対象は Okada Governance Kernel の contract hardening です。
`/okada/diagnose`, `/okada/route`, `/okada/intervene`, `/okada/audit` の API / schema / validation / error handling を点検し、task-01 の範囲で改善してください。

重視すること:
- source of truth は `registry/*.yaml`, `api/*.yaml`, `schemas/*.json`, `docs/*.md`
- 既存設計を大きく崩さない
- fail-safe を強くする
- OpenAPI / schema / 実装の契約を揃える
- テストを追加して、変更を検証する
- docs または README に追跡可能な変更を残す

やらないこと:
- LiteLLM / Dify / LangGraph / Open WebUI の本格実装
- task-01 を越えた benchmark 拡張
- しきい値調整や optimizer 実装

望ましい進め方:
1. 現状の契約を読む
2. ズレと弱点を整理する
3. 最小の差分で hardening する
4. テストで確認する
5. 変更点と未着手点を明示して報告する

作業開始時に短い plan を示し、完了時には以下を必ずまとめてください。
- 何を変えたか
- なぜ必要だったか
- どのテストを追加・更新したか
- まだ残る弱点は何か
