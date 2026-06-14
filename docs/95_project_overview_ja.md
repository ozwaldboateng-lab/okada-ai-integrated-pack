# Okada AI Integrated Pack 説明資料

## 1. これは何か

Okada AI Integrated Pack は、生成AIを業務システムやチャットUIに組み込むときに、
「そのまま答えさせてよいか」「強いモデルに切り替えるべきか」「人間確認に回すべきか」
「回答を控えるべきか」を判定するためのガバナンス用カーネルです。

中心にあるのは FastAPI 製の `Okada Kernel Service` です。外部ツールから送られてきた
入力を受け取り、リスクや信頼性の状態をスコア化し、推奨アクションと監査情報を返します。

このパックは、単体のAPIサーバーだけでなく、以下の外部ツールと接続するためのサンプル実装、
設定ファイル、検証スクリプトを含みます。

- LiteLLM
- Dify
- LangGraph
- Open WebUI

## 2. 解決しようとしている課題

生成AIを実運用に入れると、次のような問題が起きます。

- 難しい質問なのに安いモデルで処理してしまう
- 古い、矛盾した、根拠の弱い検索結果を使って回答してしまう
- エージェントが危険なツール操作へ進んでしまう
- UI上ではなぜその判断になったのか追跡できない
- 後から監査しようとしても、入力・判断・出力の記録が分散している

Okada Kernel は、これらを「各ツール側に個別実装する」のではなく、共通の判断サービスとして
集約することを目的にしています。

## 3. 全体像

```text
ユーザー / オペレーター
  -> Open WebUI / Dify / LangGraph / LiteLLM
      -> Okada Integration Gateway
          -> Okada Kernel Service
              -> 判定結果
              -> 推奨アクション
              -> 監査ログ
```

外部ツールは、それぞれの自然な payload を gateway endpoint に送ります。
gateway はそれを Okada Kernel 用の標準リクエストに変換し、判定結果を外部ツールで使いやすい形に戻します。

## 4. 主な機能

### 4.1 ガバナンス判定

Kernel は入力を見て、次のような状態を返します。

| 項目 | 意味 |
|---|---|
| `regime` | `clean`, `mixed`, `contaminated` のような信頼状態 |
| `type_class` | 問題のタイプ分類 |
| `trust_state` | `safe`, `caution`, `unsafe` などの運用向け状態 |
| `recommended_action` | 実行すべき推奨アクション |
| `alternatives` | 代替アクション |
| `audit_trace_id` | 後から追跡するための監査ID |

### 4.2 対応している判断領域

| 領域 | 例 |
|---|---|
| Monitoring | 出力品質や運用状態の監視 |
| MLOps / Drift | モデル劣化やロールバック判断 |
| Agent | LangGraph などのエージェント実行制御 |
| RAG | 検索結果の鮮度、矛盾、根拠不足の判定 |
| Routing | 安いモデル・強いモデル・ハイブリッド経路の選択 |

### 4.3 監査ログ

判断ごとに、入力、正規化後の値、スコア、推奨アクション、policy snapshot を保存できます。
現在は JSONL 形式の audit backend を持ち、将来的に別 backend に差し替えられる設計です。

## 5. 各ツールとの接続

### 5.1 LiteLLM

LiteLLM では、モデル呼び出し前に Okada Kernel へ問い合わせます。

例:

- 簡単な質問なら cheap model のまま進める
- 難しい、リスクが高い、検索が必要な質問なら strong model へ切り替える
- 必要に応じて bounded hybrid route を選ぶ

関連ファイル:

- `examples/litellm/okada_custom_handler.py`
- `examples/litellm/route_map.json`
- `examples/litellm/route_matrix.json`
- `scripts/litellm_preflight.py`

### 5.2 Dify

Dify では、RAG workflow の pre-retrieval / post-retrieval 段階で Okada Kernel に問い合わせます。

例:

- 検索前に、そもそも retrieval すべきか判定する
- 検索後に、取得チャンクが古い・矛盾している場合は abstain する
- gateway 障害時は fail-safe branch に流す

関連ファイル:

- `examples/dify/http_request_payload_pre.json`
- `examples/dify/http_request_payload_post.json`
- `examples/dify/http_request_payload_fail_safe.json`
- `examples/dify/code_node_pre_retrieval.py`
- `examples/dify/code_node_post_retrieval.py`
- `examples/dify/import_manifest.yaml`
- `scripts/dify_preflight.py`

### 5.3 LangGraph

LangGraph では、エージェントの step 実行前に Okada Kernel が判断を返します。

例:

- 続行してよい
- replan すべき
- human review に回す
- 危険なツール操作を abort する

関連ファイル:

- `examples/langgraph/okada_agent_graph.py`
- `examples/langgraph/human_review_contract.yaml`
- `examples/langgraph/resume_outcomes.json`
- `scripts/langgraph_preflight.py`

### 5.4 Open WebUI

Open WebUI では、Pipe と Filter を使って、モデル選択と監査情報の付与を行います。

例:

- Pipe が selected model と Okada metadata を返す
- Filter が message metadata に audit payload を付ける
- オペレーターが UI 上で `okada_action`, `okada_regime`, `okada_audit_trace_id` を確認できる

関連ファイル:

- `examples/openwebui/okada_governance_pipe.py`
- `examples/openwebui/okada_audit_filter.py`
- `examples/openwebui/pipes_manifest.yaml`
- `examples/openwebui/operator_console_contract.md`
- `docs/61_openwebui_manual_eval_workflow.md`
- `scripts/openwebui_preflight.py`

## 6. 検証済みの内容

APIキーなしで、以下はローカル確認済みです。

| 確認項目 | 結果 |
|---|---|
| 全体テスト | `111 passed, 1 warning` |
| E2E fixture 比較 | `12 cases`, `11 wins`, `1 loss`, `total_gain=6.29` |
| Kernel `/healthz` | `{"status":"ok"}` |
| LiteLLM preflight | 成功 |
| Dify preflight | 成功 |
| LangGraph preflight | 成功 |
| Open WebUI preflight | 成功 |
| E2E stack static preflight | 成功 |

実行済みの代表コマンド:

```powershell
python -m pytest -q
python scripts/e2e_compare.py --pretty --no-write
python scripts/litellm_preflight.py
python scripts/dify_preflight.py
python scripts/langgraph_preflight.py
python scripts/openwebui_preflight.py
python scripts/e2e_stack_preflight.py
```

## 7. まだ外部環境が必要な確認

以下は、コード上の準備はありますが、実アプリや外部環境での確認が必要です。

| 項目 | 必要なもの |
|---|---|
| Docker Compose 統合起動 | Docker Desktop |
| LiteLLM から実モデル応答 | OpenAI API key などの provider key |
| Dify workflow 実 import | Dify workspace |
| Open WebUI Pipe / Filter 実 install | Open WebUI instance |
| 実運用のモデル品質評価 | 実データ、実ユーザー導線、運用基準 |

## 8. APIキーについて

ChatGPT Plus / Pro の課金と OpenAI API の課金は別です。

このパックの構造確認、テスト、preflight の多くは API key なしで実行できます。
ただし、LiteLLM や Open WebUI から実際にモデル回答を返すには、OpenAI Platform などの API key が必要です。

## 9. 現在の制限

このパックは「最終調整済みの本番AI判定器」ではありません。

現在のスコアや threshold は、安定した接続・監査・検証のための bootstrap 値です。
本番利用する場合は、実データに基づいて calibration する必要があります。

主な制限:

- policy threshold / weight は暫定値
- Docker Desktop 上の integrated compose 実起動は未確認
- Dify / Open WebUI の実GUI操作は未確認
- 実モデル応答は API key 未設定のため未確認

## 10. リポジトリ状態

GitHub repository:

```text
https://github.com/ozwaldboateng-lab/okada-ai-integrated-pack.git
```

最新の確認済み commit:

```text
58253c4 Ignore generated runtime artifacts
```

Git 管理からは、Python cache、実行時 audit log、benchmark 出力、auto-calibration 履歴などの生成物を除外済みです。

## 11. 第三者に一言で説明するなら

Okada AI Integrated Pack は、Dify、LiteLLM、LangGraph、Open WebUI などの生成AI実行環境に対して、
「このAI処理をそのまま進めてよいか」を共通ルールで判定し、推奨アクションと監査ログを返す
ガバナンス用の統合パックです。

モデルそのものを作るものではなく、モデルやエージェントを安全に運用するための
判断レイヤーと接続サンプルを提供します。
