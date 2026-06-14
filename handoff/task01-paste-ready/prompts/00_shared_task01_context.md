# Shared Context for Task-01

あなたは、既存の Okada AI リポジトリに対して task-01 を実装する。
目的は、新機能の大量追加ではなく、Okada Governance Kernel の契約安定化である。

重要原則:
- source of truth は `registry/*.yaml`, `api/*.yaml`, `schemas/*.json`, `docs/*.md`
- 変更は task-01 の範囲に限定する
- 既存構成を壊さず、局所的・可逆的な改善を優先する
- 500 を起こしやすい入力経路には fail-safe を入れる
- テストとドキュメントを必要最小限で追従させる
- 実装後は、何を変えたか・なぜ変えたか・何をまだ変えていないかを明示する
