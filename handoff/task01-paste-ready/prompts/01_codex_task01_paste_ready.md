このリポジトリで task-01 を実装してください。

まずリポジトリを読んで、Okada Governance Kernel の API / schema / validation / error handling の現状を把握してください。
対象は `/okada/diagnose`, `/okada/route`, `/okada/intervene`, `/okada/audit` です。

目的:
- kernel contract hardening
- OpenAPI / schema / 実装の契約を揃える
- 不正入力時の fail-safe を強くする
- 必要なテストを追加する
- 必要なら docs / README を更新する

作業方針:
- source of truth は `registry/*.yaml`, `api/*.yaml`, `schemas/*.json`, `docs/*.md`
- 大規模な設計変更は禁止
- task-01 の範囲に限定する
- LiteLLM / Dify / LangGraph / Open WebUI の本格改造には入らない
- 変更は小さく、追跡しやすくする

最低限やってほしいこと:
1. 現状の契約と実装のズレを洗い出す
2. Pydantic モデルと schema と OpenAPI の整合を改善する
3. 不正 payload / 未知 adapter / 欠損値に対する 4xx 系ハンドリングを入れる
4. テストを追加・更新する
5. 変更内容を短くまとめる

完了条件:
- テストが通る
- 新規テストが追加される
- 契約のズレが減る
- 500 を減らす方向になっている

返答は、最初に短い実行計画、その後に変更着手、最後に変更点・テスト結果・残課題を整理して報告してください。
